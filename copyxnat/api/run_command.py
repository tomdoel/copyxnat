# coding=utf-8

"""API for running the specified command on XNAT servers"""


from copyxnat.pyreporter.pyreporter import PyReporter, ProjectFailure
from copyxnat.utils.rsync import ProjectRsync
from copyxnat.xnat.commands import CommandInputs
from copyxnat.config.app_settings import AppSettings
from copyxnat.xnat.copy_cache import CacheBox
from copyxnat.xnat_backend.server_factory import ServerFactory
from copyxnat.xnat.xnat_interface import XnatServer


def run_command(command, src_params, dst_params=None, project_filter=None,
                app_settings=None, backend='pyxnat',
                reporter=None):
    """Runs the command on the specified XNAT servers

    @param command: the command class to run
    @param src_params: XnatServerParams for source server
    @param dst_params: XnatServerParams for destination server
    @param project_filter: array of project names to process or None to process
    all projects visible on the server. If a project name needs to be different
    on the source and destination servers, the string should be of the form
    src_project_name:dst_project_name
    @param app_settings: Global settings; if None then defaults will be used
    @param backend: the Python library used to interact with the XNAT
    servers. Defaults to `pyxnat`
    @param reporter: PyReporter object for user input/output and logging
    """
    if not reporter:
        reporter = PyReporter(data_dir=app_settings.data_dir,
                              verbose=app_settings.verbose)

    if not app_settings:
        app_settings = AppSettings()

    cache_box = CacheBox(root_path=app_settings.data_dir)
    cache_type = command.CACHE_TYPE

    base_cache = cache_box.new_cache(cache_type=cache_type)

    factory = ServerFactory(backend)

    src_xnat = XnatServer(factory=factory,
                          params=src_params,
                          base_cache=base_cache,
                          app_settings=app_settings,
                          reporter=reporter,
                          read_only=not command.MODIFY_SRC_SERVER)

    if dst_params and command.USE_DST_SERVER:
        dst_xnat = XnatServer(factory=factory,
                              params=dst_params,
                              base_cache=base_cache,
                              app_settings=app_settings,
                              reporter=reporter,
                              read_only=not command.MODIFY_DST_SERVER)
    else:
        dst_xnat = None

    reporter.debug('Running {} command'.format(command.NAME))

    result = run_command_on_servers(command=command,
                                    src_xnat_server=src_xnat,
                                    dst_xnat_server=dst_xnat,
                                    project_filter=project_filter,
                                    app_settings=app_settings,
                                    reporter=reporter
                                    )

    src_xnat.logout()
    if dst_params and command.USE_DST_SERVER:
        dst_xnat.logout()

    output_path = src_xnat.cache.full_path()
    reporter.debug('Output files are in {}'.format(output_path))
    return result


def resolve_projects(single_project_filter):
    """Return source and destination project names from a src:dst string"""
    mapping = single_project_filter.split(':')
    src_project = mapping[0]
    dst_project = mapping[1] if len(mapping) > 1 else src_project
    return src_project, dst_project


def run_command_on_servers(command, src_xnat_server, dst_xnat_server,
                           reporter, app_settings, project_filter=None):
    """
    Runs the specified command on the specified XnatServer objects

    @param command: command class
    @param src_xnat_server: Source XnatServer
    @param dst_xnat_server: Destination XnatServer, if required for this command
    @param reporter: PyReporter object for user input/output and logging
    @param app_settings: holds global parameters
    @param project_filter: array of project names to process or None to process
    all projects visible on the server. If a project name needs to be different
    on the source and destination servers, the string should be of the form
    src_project_name:dst_project_name
    """

    projects_list = _projects_to_process(
        project_filter=project_filter,
        src_xnat_server=src_xnat_server,
        reporter=reporter)

    rsync = ProjectRsync(
        cache=src_xnat_server.cache,
        src_params=src_xnat_server.params,
        dst_params=dst_xnat_server.params,
        dry_run=app_settings.dry_run,
        reporter=reporter)

    global_results = {}

    for project in projects_list:
        try:
            src_project, dst_project = resolve_projects(project)
            inputs = CommandInputs(dst_xnat=dst_xnat_server,
                                   dst_project=dst_project,
                                   app_settings=app_settings,
                                   rsync=rsync,
                                   reporter=reporter)
            project_command = command(inputs=inputs, scope=project)

            server_project = src_xnat_server.project(src_project)
            num_sessions = src_xnat_server.num_experiments(src_project)

            reporter.start_progress(
                message="{:>20}: {:>3} sessions to {} ".format(
                    server_project.label, num_sessions, command.VERB),
                max_iter=num_sessions)

            project_command.run(server_project, dst_xnat_server)

            reporter.complete_progress()

            # Output results for current project
            project_results = project_command.outputs
            project_command.print_results()

            # Aggregate results across all projects
            global_results[project] = project_results
        except ProjectFailure as project_exception:
            reporter.warning('Failed to copy project {}. Error:{}'.format(
                src_project, str(project_exception)))

    return global_results


def _projects_to_process(project_filter, src_xnat_server, reporter):
    server_projects = src_xnat_server.project_list()
    if not server_projects:
        reporter.warning("No visible projects found on the server")
    # Allow project_filter to be a single string
    if isinstance(project_filter, str):
        project_filter = [project_filter]
    if project_filter:
        # If project filter specified then we process specified projects
        final_project_list = []
        for project in project_filter:
            src_project, _ = resolve_projects(project)
            if src_project in server_projects:
                final_project_list.append(project)
            else:
                reporter.warning("Skipping project {}: not found on server".
                                 format(src_project))

    else:
        # If no project filter specified then we process all visible projects
        final_project_list = server_projects

    return final_project_list
