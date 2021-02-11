# coding=utf-8

"""Commands defining actions that can be performed with copyxnat"""


class Command:
    """Wraps a command function and its input variables"""

    def __init__(self, inputs, scope):
        self.scope = scope
        self.inputs = inputs
        self.outputs = None
        self.ignore_filter = []

    def run_pre(self, xnat_item, from_parent):
        """
        Function that will be run on each item in the XNAT server before
        being run on its children

        :xnat_item: The source server XnatItem to process
        :from_parent: The value returned by this function when it was run on
        this xnat_item's parent
        """

    def run_post(self, xnat_item, from_parent, from_pre):
        """
        Function that will be run on each item in the XNAT server after being
        run on its children
        :xnat_item: The source server XnatItem to process
        :from_parent: The value returned by this function when it was run on
        this xnat_item's parent
        from_pre: The value returned by the run_pre command when it was run
        on this xnat_item
        """

    def print_results(self):
        """Output results to user"""
        print("Result of running {} on {}:".format(self.NAME, self.scope))  ## pylint:disable=no-member
        print(self.outputs)


class AppSettings:
    """Wrap global settings for this utility"""

    def __init__(self, fix_scan_types=False, download_zips=False,
                 dry_run=False):
        self.dry_run = dry_run
        self.download_zips = download_zips
        self.fix_scan_types = fix_scan_types


class CommandInputs:
    """Wrap global input variables for a command"""
    def __init__(self, dst_xnat, reporter, app_settings, dst_project=None):
        self.dst_project = dst_project
        self.app_settings = app_settings
        self.reporter = reporter
        self.dst_xnat = dst_xnat


class CommandReturn:
    """Class for return values for a command function call"""

    def __init__(self, to_children=None, recurse=True):
        self.to_children = to_children
        self.recurse = recurse
