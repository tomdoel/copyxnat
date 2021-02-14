# coding=utf-8

"""Commands defining actions that can be performed with copyxnat"""
from abc import abstractmethod


class Command:
    """Wraps a command function and its input variables"""

    def __init__(self, inputs, scope):
        self.scope = scope
        self.inputs = inputs
        self.outputs = None
        self.ignore_filter = []

    def run(self, xnat_item, from_parent=None):
        """
        Run this command recursively on the xnat_item and its children

        :xnat_item: The source server XnatItem to process
        :from_parent: The value returned by this function when it was run on
        this xnat_item's parent
        """
        self._run(xnat_item=xnat_item, from_parent=from_parent)
        self._update_progress(xnat_item=xnat_item)

    def _recurse(self, xnat_item, to_children=None):
        for child in xnat_item.get_children(self.ignore_filter):
            self.run(xnat_item=child, from_parent=to_children)

    def _update_progress(self, xnat_item):
        xnat_item.progress_update(reporter=self.inputs.reporter)

    @abstractmethod
    def _run(self, xnat_item, from_parent):
        """
        Function that will be run on items in the XNAT server. The
        implementation must call self._recurse() to recursively iterate
        through child items

        :xnat_item: The source server XnatItem to process
        :from_parent: The value returned by this function when it was run on
        this xnat_item's parent
        """

    def print_results(self):
        """Output results to user"""
        self.inputs.reporter.verbose_log(
            "Result of running {} on {}: {}".format(self.NAME, self.scope,  ## pylint:disable=no-member
                                                    self.outputs))


class AppSettings:
    """Wrap global settings for this utility"""

    def __init__(self,
                 fix_scan_types=False,
                 download_zips=False,
                 dry_run=False,
                 ignore_datatype_errors=False,
                 overwrite_existing=False):
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
        @param overwrite_existing: Set to True to overwrite existing data on the
        XNAT server
        """
        self.dry_run = dry_run
        self.download_zips = download_zips
        self.fix_scan_types = fix_scan_types
        self.ignore_datatype_errors = ignore_datatype_errors
        self.overwrite_existing = overwrite_existing


class CommandInputs:
    """Wrap global input variables for a command"""
    def __init__(self, dst_xnat, reporter, app_settings, dst_project=None):
        self.dst_project = dst_project
        self.app_settings = app_settings
        self.reporter = reporter
        self.dst_xnat = dst_xnat
