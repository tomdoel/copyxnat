# coding=utf-8

"""Command which copies XNAT projects between servers"""

from copyxnat.xnat.xnat_interface import XnatProject
from copyxnat.xnat.commands import Command, CommandReturn


class CopyCommand(Command):
    """Command which copies XNAT projects between servers"""

    NAME = 'Copy'
    COMMAND_LINE = 'copy'
    USE_DST_SERVER = True
    CACHE_TYPE = 'cache'
    HELP = 'Copy projects between server, or duplicate on same server'

    def run(self, xnat_item, from_parent):

        # Override the project name
        dst_name = self.inputs.dst_project if \
            isinstance(xnat_item, XnatProject) else None

        copied_item = xnat_item.duplicate(
            destination_parent=from_parent,
            app_settings=self.inputs.app_settings,
            dst_label=dst_name,
            dry_run=self.inputs.reporter.dry_run)
        return CommandReturn(to_children=copied_item)
