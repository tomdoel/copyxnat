# coding=utf-8

"""Command which exports XNAT project data onto local disk"""

from copyxnat.xnat.commands import Command


class ExportCommand(Command):
    """Command which exports XNAT project data onto local disk"""

    NAME = 'Download'
    VERB = 'download'
    COMMAND_LINE = 'export'
    USE_DST_SERVER = False
    MODIFY_SRC_SERVER = False
    MODIFY_DST_SERVER = False
    CACHE_TYPE = 'downloads'
    HELP = 'Export XNAT projects to disk'

    def _run(self, xnat_item, from_parent):  # pylint: disable=unused-argument
        xnat_item.export(self.inputs.app_settings)
        self._recurse(xnat_item=xnat_item)
