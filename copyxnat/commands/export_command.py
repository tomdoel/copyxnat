# coding=utf-8

"""Command which exports XNAT project data onto local disk"""

from copyxnat.xnat.commands import Command, CommandReturn


class ExportCommand(Command):
    """Command which exports XNAT project data onto local disk"""

    NAME = 'Download'
    COMMAND_LINE = 'export'
    USE_DST_SERVER = False
    CACHE_TYPE = 'downloads'
    HELP = 'Export XNAT projects to disk'

    def run(self, xnat_item, from_parent):  # pylint: disable=unused-argument
        return_value = xnat_item.export(self.inputs.app_settings)
        return CommandReturn(to_children=return_value)
