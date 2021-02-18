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
        self.inputs.reporter.debug(
            "Result of running {} on {}: {}".format(self.NAME, self.scope,  ## pylint:disable=no-member
                                                    self.outputs))


class CommandInputs:
    """Wrap global input variables for a command"""
    def __init__(self, dst_xnat, reporter, app_settings, rsync,
                 dst_project=None):
        self.dst_project = dst_project
        self.app_settings = app_settings
        self.reporter = reporter
        self.dst_xnat = dst_xnat
        self.rsync = rsync
