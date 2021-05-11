# coding=utf-8

"""Wrap global settings for copyxnat"""

from enum import Enum

import appdirs


class TransferMode(Enum):
    """Defines how resource files (images etc) will be transferred"""
    FILE = 'file'  # Transfer file-by-file
    ZIP = 'zip'  # Transfer resource collections as a zip file
    RSYNC = 'rsync'  # Transfer resource files using rsync
    META = 'meta'  # Do not transfer resource files


class AppSettings:
    """Wrap global settings for this utility"""

    def __init__(self,
                 fix_scan_types=False,
                 dry_run=False,
                 ignore_datatype_errors=False,
                 overwrite_existing=False,
                 transfer_mode=TransferMode.FILE,
                 data_dir=None,
                 verbose=False,
                 skip_existing=False,
                 subject_limit=None
                 ):
        """
        Create global application settings

        @param fix_scan_types: If True then ambiguous scan types will be
        modified on the destination XNAT server to match the expected scan type
        @param dry_run: set to True to request that write operations are not
        made on the destination server, to allow testing. Note that some
        changes may still take place
        @param ignore_datatype_errors: Set to True to copy files even if the
        datatype is not present on the destination server
        @param overwrite_existing: If True then overwrite existing data may be
        overwritten
        @param transfer_mode: See TransferMode enum
        @param data_dir: Local directory for logs, downloads, cache files
        @param subject_limit: Maximum number of new subjects to process
        @param verbose: True to show debugging output
        XNAT server
        """
        self.skip_existing = skip_existing
        self.dry_run = dry_run
        self.fix_scan_types = fix_scan_types
        self.ignore_datatype_errors = ignore_datatype_errors
        self.overwrite_existing = overwrite_existing
        self.transfer_mode = TransferMode(transfer_mode)
        self.data_dir = data_dir or appdirs.user_data_dir('copyxnat')
        self.verbose = verbose
        self.subject_limit = subject_limit
