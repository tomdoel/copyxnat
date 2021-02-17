# coding=utf-8

"""Wrap global settings for copyxnat"""


class AppSettings:
    """Wrap global settings for this utility"""

    def __init__(self,
                 fix_scan_types=False,
                 download_zips=False,
                 dry_run=False,
                 ignore_datatype_errors=False,
                 overwrite_existing=False,
                 metadata_only=False):
        """
        Create global application settings

        @param fix_scan_types: If True then ambiguous scan types will be
        modified on the destination XNAT server to match the expected scan type
        @param download_zips: If True then resources will be uploaded and
        downloaded as zip files, which is faster but individual file attributes
        will not be set when copying between servers
        @param dry_run: set to True to request that write operations are not
        made on the destination server, to allow testing. Note that some
        changes may still take place
        @param ignore_datatype_errors: Set to True to copy files even if the
        datatype is not present on the destination server
        @param overwrite_existing: If True then overwrite existing data may be
        overwritten
        @param metadata_only: If True then transfer metadata only
        XNAT server
        """
        self.dry_run = dry_run
        self.download_zips = download_zips
        self.fix_scan_types = fix_scan_types
        self.ignore_datatype_errors = ignore_datatype_errors
        self.overwrite_existing = overwrite_existing
        self.metadata_only = metadata_only
