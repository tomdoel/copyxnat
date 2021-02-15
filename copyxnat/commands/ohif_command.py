# coding=utf-8

"""Command which exports XNAT project data onto local disk"""

from copyxnat.xnat.commands import Command


class OhifCommand(Command):
    """Command which exports XNAT project data onto local disk"""

    NAME = 'Ohif'
    VERB = 'reset'
    COMMAND_LINE = 'ohif'
    USE_DST_SERVER = False
    MODIFY_SRC_SERVER = True
    MODIFY_DST_SERVER = False
    CACHE_TYPE = 'cache'
    HELP = 'Reset the OHIF viewer session data so it will find all images'

    def _run(self, xnat_item, from_parent):  # pylint: disable=unused-argument
        self._recurse(xnat_item=xnat_item)
        xnat_item.ohif_generate_session()
