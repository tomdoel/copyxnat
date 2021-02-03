# coding=utf-8

"""Commands defining actions that can be performed with copyxnat"""
import abc


class Command:
    """Wraps a command function and its input variables"""

    def __init__(self, inputs, scope, initial_result=None):
        self.scope = scope
        self.outputs = initial_result
        self.inputs = inputs

    @abc.abstractmethod
    def run(self, xnat_item, from_parent):
        """Function that will be run on each item in the XNAT server"""

    def print_results(self):
        """Output results to user"""
        print("Result of running {} on {}:".format(self.NAME, self.scope))  ## pylint:disable=no-member
        print(self.outputs)


class CommandInputs:
    """Wrap global input variables for a command"""
    def __init__(self, dst_xnat, reporter, fix_scan_types, dst_project=None):
        self.dst_project = dst_project
        self.fix_scan_types = fix_scan_types
        self.reporter = reporter
        self.dst_xnat = dst_xnat


class CommandReturn:
    """Class for return values for a command function call"""

    def __init__(self, to_children=None, recurse=True):
        self.to_children = to_children
        self.recurse = recurse
