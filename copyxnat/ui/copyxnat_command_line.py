# coding=utf-8

"""Command line processing"""

import argparse
from getpass import getpass

from copyxnat.xnat.run_command import run_command
from copyxnat.utils.versioning import get_version_string


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

    # Arguments for the export command
    subparsers.add_parser('export', help='Export XNAT projects to disk')

    # Arguments for the show command
    subparsers.add_parser('show', help='Show information about XNAT projects')

    # Arguments for the copy command
    copy_parser = subparsers.add_parser('copy', help='Show information about '
                                                     'XNAT projects')

    # Arguments for the check_datatypes command
    check_datatypes = subparsers.add_parser(
        'check_datatypes',
        help='Check if experiment data types on source XNAT are present on '
             'destination')

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

    parser.add_argument("-s", "--src_host", required=True,
                        help="Host name of the XNAT server containing the data"
                        )

    parser.add_argument("-u", "--src_user", required=True,
                        help="User name for accessing XNAT server containing "
                             "the data"
                        )

    parser.add_argument("-p", "--project", default=None,
                        help="Name of project containing the data"
                        )

    parser.add_argument("-c", "--cache_dir",
                        help="File path here local cache files are to be stored"
                        )

    for sub_parser in [copy_parser, check_datatypes]:
        sub_parser.add_argument("-d", "--dst_host",
                                help="Host name of the destionation XNAT "
                                     "server"
                                )

        sub_parser.add_argument("-w", "--dst_user",
                                help="User name for accessing the destination "
                                     "XNAT server"
                                )

        sub_parser.add_argument("-f", "--fix-scan-types",
                                action="store_true",
                                help="Fix undefined scan types on the copy",
                                )

    args = parser.parse_args(args)

    src_pw = getpass("Please enter the password for {}@{}:".
                     format(args.src_user, args.src_host))

    dst_host = args.dst_host if 'dst_host' in args else None
    dst_user = args.dst_user if 'dst_user' in args else None
    fix_scan_types = args.fix_scan_types if 'fix_scan_types' in args else False

    if dst_host:
        dst_pw = getpass("Please enter the password for {}@{}:".
                         format(args.dst_user, args.dst_host))
    else:
        dst_pw = None

    project_list = args.project.split(',') if 'project' in args and \
                                              args.project else None

    result = run_command(command_string=args.command,
                         src_host=args.src_host,
                         src_user=args.src_user,
                         src_pw=src_pw,
                         project_filter=project_list,
                         dst_host=dst_host,
                         dst_user=dst_user,
                         dst_pw=dst_pw,
                         verbose=args.verbose,
                         insecure=args.insecure,
                         fix_scan_types=fix_scan_types,
                         dry_run=args.dry_run
                         )

    print(result)
