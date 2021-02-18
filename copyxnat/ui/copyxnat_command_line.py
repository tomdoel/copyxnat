# coding=utf-8

"""Command line processing"""

import argparse
from getpass import getpass

from copyxnat.commands.find_commands import find_command
from copyxnat.commands import find_commands
from copyxnat.api.run_command import run_command
from copyxnat.utils.versioning import get_version_string
from copyxnat.config.server_params import XnatServerParams
from copyxnat.config.app_settings import AppSettings


def main(args=None):
    """Entry point for copyxnat application"""

    parser = argparse.ArgumentParser(description='copyxnat')

    version_string = get_version_string()
    friendly_version_string = version_string if version_string else 'unknown'
    parser.add_argument(
        "--version",
        action='version',
        version=friendly_version_string
    )

    subparsers = parser.add_subparsers(dest='command')

    for command in find_commands.commands():
        subparsers.add_parser(command.COMMAND_LINE, help=command.HELP)

    # Arguments common to all commands
    parser.add_argument("-y", "--dry_run",
                        action="store_true",
                        help="Do not modify the destination",
                        )

    parser.add_argument("-k", "--insecure",
                        action="store_true",
                        help="Do not enforce strict SSL certificate checks",
                        )

    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Show verbose output",
                        )

    parser.add_argument("-s", "--src-host", required=True,
                        help="Host name of the XNAT server containing the data"
                        )

    parser.add_argument("-u", "--src-user", required=True,
                        help="User name for accessing XNAT server containing "
                             "the data"
                        )

    parser.add_argument("-i", "--rsync-src-user",
                        default=None,
                        help="When using rsync transfer, ssh username for "
                             "source server (this is not the XNAT username)"
                        )

    parser.add_argument("-p", "--project", default=None,
                        help="Name of project containing the data"
                        )

    parser.add_argument("-c", "--cache-dir",
                        help="File path here local cache files are to be stored"
                        )

    parser.add_argument("-z", "--download-zips",
                        action="store_true",
                        help="Download each resource as a zip "
                             "instead of individual files",
                        )

    parser.add_argument("-t", "--transfer-mode",
                        default='file',
                        choices=['file', 'zip', 'rsync', 'meta'],
                        help="Choose how resource files will be transferred. "
                             "The file method is the safest and copies files"
                             "individually and maintains their attributes."
                             "The zip method copies each resource folder as a "
                             "zip archive. The rsync option is a more "
                             "experimental approach which should be used with "
                             "caution. It requires you to have ssh keys set up "
                             "and you must supply the account usernames. The "
                             "meta option only copies metadata and requires you"
                             " to have manually transferred the files over "
                             "first."
                        )

    for command in find_commands.commands():
        command_key = command.COMMAND_LINE
        sub_parser = subparsers.choices[command_key]

        if command.USE_DST_SERVER:
            sub_parser.add_argument("-d", "--dst-host",
                                    help="Host name of the destination XNAT "
                                         "server"
                                    )

            sub_parser.add_argument("-w", "--dst-user",
                                    help="User name for accessing the "
                                         "destination XNAT server"
                                    )

            sub_parser.add_argument("-f", "--fix-scan-types",
                                    action="store_true",
                                    help="Fix undefined scan types on the copy",
                                    )

            sub_parser.add_argument("-j", "--rsync-dst-user",
                                    default=None,
                                    help="When using rsync transfer, ssh "
                                         "username for destination server "
                                         "(this is not the XNAT username)"
                                    )

        if command.MODIFY_DST_SERVER:
            sub_parser.add_argument("-m", "--ignore-datatype-errors",
                                    action="store_true",
                                    help="Copy data to destination server even "
                                         "if the datatype is not known"
                                    )

            sub_parser.add_argument("-o", "--overwrite-existing",
                                    action="store_true",
                                    help="Overwrite existing data on the"
                                         "destination server"
                                    )

    args = parser.parse_args(args)

    command = find_command(args.command)

    src_pw = getpass("Please enter the password for {}@{}:".
                     format(args.src_user, args.src_host))

    src_rsync = args.rsync_src_user if 'rsync_src_user' in args else None

    fix_scan_types = args.fix_scan_types if 'fix_scan_types' in args else False
    verbose = args.verbose if 'verbose' in args else False
    overwrite_existing = args.overwrite_existing if \
        'overwrite_existing' in args else False
    ignore_datatype_errors = args.ignore_datatype_errors if \
        'ignore_datatype_errors' in args else False

    transfer_mode = args.transfer_mode

    project_list = args.project.split(',') if 'project' in args and \
                                              args.project else None

    src_params = XnatServerParams(host=args.src_host,
                                  user=args.src_user,
                                  pwd=src_pw,
                                  rsync_user=src_rsync,
                                  insecure=args.insecure)

    if command.USE_DST_SERVER:
        dst_host = args.dst_host if 'dst_host' in args else None
        dst_user = args.dst_user if 'dst_user' in args else None
        dst_rsync = args.rsync_dst_user if 'rsync_dst_user' in args else None
        dst_pw = getpass("Please enter the password for {}@{}:".
                         format(args.dst_user, args.dst_host))

        dst_params = XnatServerParams(host=dst_host,
                                      user=dst_user,
                                      pwd=dst_pw,
                                      rsync_user=dst_rsync,
                                      insecure=args.insecure)
    else:
        dst_params = None

    app_settings = AppSettings(
        fix_scan_types=fix_scan_types,
        ignore_datatype_errors=ignore_datatype_errors,
        dry_run=args.dry_run,
        overwrite_existing=overwrite_existing,
        transfer_mode=transfer_mode,
        data_dir=args.cache_dir,
        verbose=verbose
    )

    result = run_command(command=command,
                         src_params=src_params,
                         dst_params=dst_params,
                         project_filter=project_list,
                         app_settings=app_settings
                         )

    if verbose:
        print(result)
