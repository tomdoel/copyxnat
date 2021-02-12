# coding=utf-8

"""Command which copies XNAT projects between servers"""

from copyxnat.xnat.xnat_interface import XnatProject
from copyxnat.xnat.commands import Command


class CopyCommand(Command):
    """Command which copies XNAT projects between servers"""

    NAME = 'Copy'
    VERB = 'copy'
    COMMAND_LINE = 'copy'
    USE_DST_SERVER = True
    CACHE_TYPE = 'cache'
    HELP = 'Copy projects between server, or duplicate on same server'

    def _run(self, xnat_item, from_parent):

        # Override the project name
        dst_name = self.inputs.dst_project if \
            isinstance(xnat_item, XnatProject) else None

        dst_copy = xnat_item.copy(
            destination_parent=from_parent,
            app_settings=self.inputs.app_settings,
            dst_label=dst_name,
            dry_run=self.inputs.reporter.dry_run)
        self._recurse(xnat_item=xnat_item, to_children=dst_copy)
        dst_copy.post_create()
