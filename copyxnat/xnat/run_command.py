# coding=utf-8

"""API for running the specified command on XNAT servers"""


from copyxnat.pyreporter.pyreporter import PyReporter
from copyxnat.xnat.commands import command_factory
from copyxnat.xnat.copy_cache import CacheBox
from copyxnat.xnat_backend.server_factory import ServerFactory
from copyxnat.xnat.xnat_interface import XnatServer, XnatServerParams


def run_command(command, src_host, src_user, src_pw, dst_host=None,
                dst_user=None, dst_pw=None, project_filter=None, verbose=False,
                insecure=False, dry_run=False, backend='pyxnat', reporter=None,
                cache_dir=None, fix_scan_types=False):
    """Runs the command on the specified XNAT servers

    @param command: the command class to run
    @param src_host: hostname of XNAT server containing source data
    @param src_user: username on source XNAT server
    @param src_pw:  password on source XNAT server
    @param dst_host: hostname of XNAT destination server
    @param dst_user: username on destination XNAT server
    @param dst_pw: password on destination XNAT server
    @param project_filter: array of project names to process or None to process
    all projects visible on the server. If a project name needs to be different
    on the source and destination servers, the string should be of the form
    src_project_name:dst_project_name
    @param verbose: set to True for verbose output for debugging
    @param insecure: set to True if using server with self-signed certificates
    @param dry_run: set to True to request that write operations are not made
    on the destination server, to allow testing. Note that some changes may
    still take place
    @param backend: the Python library used to interact with the XNAT
    servers. Defaults to `pyxnat`
    @param reporter: PyReporter object for user input/output and logging
    @param fix_scan_types: Set to True to fix incorrect scan types when copying
    @param cache_dir: Directory where downloaded or cached files will be stored
    """
    if not reporter:
        reporter = PyReporter(dry_run=dry_run, verbose=verbose)

    cache_box = CacheBox(root_path=cache_dir)
    cache_type = command.CACHE_TYPE

    base_cache = cache_box.new_cache(cache_type=cache_type)

    factory = ServerFactory(backend)
    src_params = XnatServerParams(host=src_host, user=src_user, pwd=src_pw,
                                  insecure=insecure, read_only=True)
    src_xnat = XnatServer(factory=factory, params=src_params,
                          base_cache=base_cache, reporter=reporter)
    if dst_host and command.USE_DST_SERVER:
        dst_params = XnatServerParams(host=dst_host, user=dst_user, pwd=dst_pw,
                                      insecure=insecure, read_only=False)
        dst_xnat = XnatServer(factory=factory, params=dst_params,
                              base_cache=base_cache, reporter=reporter)
    else:
        dst_xnat = None

    reporter.info('Running {} command'.format(command.NAME))

    result = run_command_on_servers(command=command,
                                    src_xnat_server=src_xnat,
                                    dst_xnat_server=dst_xnat,
                                    project_filter=project_filter,
                                    fix_scan_types=fix_scan_types,
                                    reporter=reporter
                                    )

    src_xnat.logout()
    if dst_host and command.USE_DST_SERVER:
        dst_xnat.logout()

    output_path = src_xnat.cache.full_path()
    reporter.message('Output files are in {}'.format(output_path))
    return result


def resolve_projects(single_project_filter):
    """Return source and destination project names from a src:dst string"""
    mapping = single_project_filter.split(':')
    src_project = mapping[0]
    dst_project = mapping[1] if len(mapping) > 1 else src_project
    return src_project, dst_project


def run_command_on_servers(command, src_xnat_server, dst_xnat_server,
                           reporter, fix_scan_types=False, project_filter=None):
    """
    Runs the specified command on the specified XnatServer objects

    @param command: command class
    @param src_xnat_server: Source XnatServer
    @param dst_xnat_server: Destination XnatServer, if required for this command
    @param reporter: PyReporter object for user input/output and logging
    @param project_filter: array of project names to process or None to process
    all projects visible on the server. If a project name needs to be different
    on the source and destination servers, the string should be of the form
    src_project_name:dst_project_name
    """

    server_projects = src_xnat_server.project_list()
    if not server_projects:
        reporter.warning("No visible projects found on the server")

    # Allow project_filter to be a single string
    if isinstance(project_filter, str):
        project_filter = [project_filter]

    if project_filter:
        # If project filter specified then we process specified projects
        projects_to_process = []
        for project in project_filter:
            src_project, _ = resolve_projects(project)
            if src_project in server_projects:
                projects_to_process.append(project)
            else:
                reporter.warning("Skipping project {}: not found on server".
                                 format(src_project))

    else:
        # If no project filter specified then we process all visible projects
        projects_to_process = server_projects

    global_results = {'result': None}

    for project in projects_to_process:
        src_project, dst_project = resolve_projects(project)
        command_w = command_factory(command=command,
                                    dst_xnat=dst_xnat_server,
                                    dst_project=dst_project,
                                    fix_scan_types=fix_scan_types,
                                    initial_result=global_results['result'],
                                    reporter=reporter)

        server_project = src_xnat_server.project(src_project)
        num_sessions = src_xnat_server.num_experiments(src_project)

        reporter.start_progress(
            message='{} {} sessions for {}'.format(command.NAME,
                                                   num_sessions,
                                                   server_project.label),
            max_iter=num_sessions)
        server_project.run_recursive(
            function=command_w.function,
            from_parent=dst_xnat_server,
            reporter=reporter)
        reporter.complete_progress()

        # Retrieve results from project run to pass to next run
        global_results = command_w.outputs_function()

    return global_results
