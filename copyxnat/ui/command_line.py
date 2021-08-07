# coding=utf-8

"""Command line processing"""

import argparse
import sys
import traceback

import six

from copyxnat.commands.find_commands import find_command
from copyxnat.commands import find_commands
from copyxnat.api.run_command import run_command
from copyxnat.pyreporter.console import AnsiCodes
from copyxnat.utils.error_utils import message_from_exception, UserError
from copyxnat.utils.versioning import get_version_string
from copyxnat.config.server_params import XnatServerParams
from copyxnat.config.app_settings import AppSettings


def run_command_line(args):
    """Run the copyxnat with the specified command-line arguments

    :returns: status code 0=success, 1=failure
    """

    command, src_params, dst_params, project_list, app_settings = \
        _parse_command_line(args)

    try:
        run_command(command=command,
                    src_params=src_params,
                    dst_params=dst_params,
                    project_filter=project_list,
                    app_settings=app_settings
                    )
        return 0

    except Exception as exc:  # pylint: disable=broad-except
        _show_exception_to_user(exc)
        return 1


def run_entry_point():
    """Entry point for copyxnat application where parameters are parsed from
    the command-line

    :returns: status code 0=success, 1=failure
    """

    return run_command_line(sys.argv[1:])


def _show_exception_to_user(exc):
    message = AnsiCodes.RED + "CopyXnat could not complete due to the " \
                              "following error: {}" + AnsiCodes.END
    if isinstance(exc, UserError):
        six.print_(message.format(exc.user_friendly_message), file=sys.stderr)
    else:
        six.print_(message.format(message_from_exception(exc)), file=sys.stderr)
        six.print_("If you think this may be a bug, please create an issue at "
                   "https://github.com/tomdoel/copyxnat/issues and include "
                   "the following error details:", file=sys.stderr)
        traceback.print_exc()


def _parse_command_line(args):

    parser = argparse.ArgumentParser(
        description='CopyXnat: Utility for downloading or copying projects '
                    'between XNAT servers')
    version_string = get_version_string()
    friendly_version_string = version_string if version_string else 'unknown'

    parser.add_argument(
        "--version",
        action='version',
        version=friendly_version_string
    )

    parser.add_argument("-c", "--cache-dir",
                        help="File path here local cache files are to be stored"
                        )

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True
    for command in find_commands.commands():
        sub_parser = subparsers.add_parser(command.COMMAND_LINE,
                                           help=command.HELP)

        # Arguments common to all commands
        sub_parser.add_argument(
            "-y", "--dry-run", action="store_true",
            help="Do not modify the destination"
        )
        sub_parser.add_argument(
            "-k", "--insecure", action="store_true",
            help="Do not enforce strict SSL certificate checks"
        )
        sub_parser.add_argument(
            "-v", "--verbose", action="store_true",
            help="Show verbose output"
        )
        sub_parser.add_argument(
            "-s", "--src-host", required=True,
            help="Host name of the XNAT server containing the data"
        )
        sub_parser.add_argument(
            "-u", "--src-user", required=True,
            help="User name for accessing XNAT server containing the data"
        )
        sub_parser.add_argument(
            "-i", "--rsync-src-user", default=None,
            help="When using rsync transfer, ssh username for source server "
                 "(this is not the XNAT username)"
        )
        sub_parser.add_argument(
            "-p", "--project", default=None,
            help="Name of project containing the data"
        )
        sub_parser.add_argument(
            "-n", "--skip-existing", action="store_true",
            help="Skip session and all children if it already exists on the "
                 "destination server"
        )
        sub_parser.add_argument(
            "-t", "--transfer-mode", default='file',
            choices=['file', 'zip', 'rsync', 'meta'],
            help="Choose how resource files will be transferred. "
                 "The file method is the safest and copies files"
                 "individually and maintains their attributes. "
                 "The zip method copies each resource folder as a "
                 "zip archive. The rsync option is a more "
                 "experimental approach which should be used with "
                 "caution. It requires you to have ssh keys set up "
                 "and you must supply the account usernames. The "
                 "meta option only copies metadata and requires you"
                 " to have manually transferred the files over "
                 "first."
        )
        sub_parser.add_argument(
            "-l", "--limit-subjects", type=int, default=None,
            help="Limit number of new subjects to transfer"
        )
        sub_parser.add_argument(
            "-b", "--backend", default='pyxnat',
            choices=['pyxnat', 'simplexnat'],
            help="Select the XNAT backend"
        )

    for command in find_commands.commands():
        command_key = command.COMMAND_LINE
        sub_parser = subparsers.choices[command_key]

        if command.USE_DST_SERVER:
            sub_parser.add_argument("-d", "--dst-host", required=True,
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

            sub_parser.add_argument("-g", "--ohif-rebuild",
                                    action="store_true",
                                    help="Ask the OHIF viewer to regenerate "
                                         "experiment metadata "
                                         "after an experiment modification."
                                    )

            sub_parser.add_argument("-r", "--clear-caches",
                                    action="store_true",
                                    help="Ask the monitoring service to clear"
                                         "Java caches after each session upload"
                                    )

    args = parser.parse_args(args)

    # Command class
    command = find_command(args.command)

    # Source server parameters object
    src_rsync = args.rsync_src_user if 'rsync_src_user' in args else None
    src_params = XnatServerParams(host=args.src_host,
                                  user=args.src_user,
                                  rsync_user=src_rsync,
                                  insecure=args.insecure)

    # Destination server parameters object
    if command.USE_DST_SERVER:
        dst_host = args.dst_host if 'dst_host' in args else None
        dst_user = args.dst_user if 'dst_user' in args else None
        dst_rsync = args.rsync_dst_user if 'rsync_dst_user' in args else None
        dst_params = XnatServerParams(host=dst_host,
                                      user=dst_user,
                                      rsync_user=dst_rsync,
                                      insecure=args.insecure)
    else:
        dst_params = None

    # Project list
    project_list = args.project.split(',') if 'project' in args and \
                                              args.project else None

    # Application settings
    app_settings = AppSettings(
        fix_scan_types=_optional(args, 'fix_scan_types', False),
        ignore_datatype_errors=_optional(args, 'ignore_datatype_errors', False),
        dry_run=args.dry_run,
        overwrite_existing=_optional(args, 'overwrite_existing', False),
        transfer_mode=args.transfer_mode,
        data_dir=args.cache_dir,
        verbose=args.verbose,
        skip_existing=_optional(args, 'skip_existing', None),
        subject_limit=args.limit_subjects,
        ohif_rebuild=_optional(args, 'ohif_rebuild', None),
        clear_caches=_optional(args, 'clear_caches', None),
        backend=args.backend
    )

    return command, src_params, dst_params, project_list, app_settings


def _optional(args, param, default):
    return getattr(args, param) if param in args else default
