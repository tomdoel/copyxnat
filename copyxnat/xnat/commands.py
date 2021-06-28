# coding=utf-8

"""Commands defining actions that can be performed with copyxnat"""
from abc import abstractmethod

from copyxnat.xnat.xnat_interface import XnatSubject


class Command(object):
    """Wraps a command function and its input variables"""

    def __init__(self, inputs, scope):
        self.scope = scope
        self.inputs = inputs
        self.outputs = None
        self.ignore_filter = []
        self.initial_from_parent = None
        self.processed_counts = inputs.processed_counts
        self.limit_reached = False

    def run(self, xnat_item):
        """
        Run this command recursively on the xnat_item and its children

        :xnat_item: The source server XnatItem to process
        :returns: True if the command was actually run on any item
        """
        processed = self._run(xnat_item=xnat_item,
                              from_parent=self.initial_from_parent)
        self._update_progress(xnat_item=xnat_item)
        return processed

    def run_next(self, xnat_item, from_parent=None):
        """
        Run this command recursively on the xnat_item and its children.
        This method is called recursively from within the _run() method

        :xnat_item: The source server XnatItem to process
        :from_parent: The value returned by this function when it was run on
        this xnat_item's parent
        :returns: True if the command was actually run on any item
        """
        processed = self._run(xnat_item=xnat_item, from_parent=from_parent)
        self._update_progress(xnat_item=xnat_item)
        return processed

    def _recurse(self, xnat_item, to_children=None):
        any_processed = False
        for child in xnat_item.get_children(self.ignore_filter):

            processed = self.run_next(xnat_item=child, from_parent=to_children)

            if processed:
                any_processed = True

                # Update counts for number of items processed of each type
                self.processed_counts[child.xnat_type] = \
                    self.processed_counts.get(child.xnat_type, 0) + 1

                # If maximum processed items limit exceeded, exit early
                if self._limit_exceeded(child):
                    self.limit_reached = True
                    self.inputs.reporter.log(
                        'Skipping further subject processing as subject limit '
                        'has been exceeded.')
                    break

        return any_processed

    def _limit_exceeded(self, child):
        return self.inputs.app_settings.subject_limit is not None and \
          isinstance(child, XnatSubject) and \
          self.processed_counts.get(child.xnat_type, 0) >= \
          self.inputs.app_settings.subject_limit

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

        :returns: True if the command was actually run on any item
        """

    def print_results(self):
        """Output results to user"""
        self.inputs.reporter.debug(
            "Result of running {} on {}: {}".format(self.NAME, self.scope,  ## pylint: disable=no-member
                                                    self.outputs))


class CommandInputs:
    """Wrap global input variables for a command"""
    def __init__(self, dst_xnat, reporter, app_settings, rsync,
                 processed_counts, dst_project=None):
        self.dst_project = dst_project
        self.app_settings = app_settings
        self.reporter = reporter
        self.dst_xnat = dst_xnat
        self.processed_counts = processed_counts
        self.rsync = rsync
