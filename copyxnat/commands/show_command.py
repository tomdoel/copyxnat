# coding=utf-8

"""Command which displays contents of XNAT projects"""
import os

from copyxnat.xnat.commands import Command, CommandReturn


class ShowCommand(Command):
    """Command which displays contents of XNAT projects"""

    NAME = 'Show'
    VERB = 'examine'
    COMMAND_LINE = 'show'
    USE_DST_SERVER = False
    CACHE_TYPE = 'cache'
    HELP = 'Show information about XNAT projects'

    def run(self, xnat_item, from_parent):  # pylint: disable=unused-argument
        if self.outputs is None:
            self.outputs = ''
        self.outputs += xnat_item.user_visible_info() + os.linesep
        self.inputs.reporter.output(xnat_item.user_visible_info())
        return CommandReturn()

    def print_results(self):
        """Output results to user"""
        print("Contents of {}:".format(self.scope))  ## pylint:disable=no-member
        print(self.outputs)
