# coding=utf-8

"""Command which exports XNAT project data onto local disk"""

from copyxnat.xnat.commands import Command
from copyxnat.xnat.xnat_interface import XnatExperiment, XnatFile


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

    def _run(self, xnat_item, from_parent):
        self._recurse(xnat_item=xnat_item)

        if isinstance(xnat_item, XnatExperiment):
            xnat_item.ohif_generate_session()
        if isinstance(xnat_item, XnatFile):
            xnat_item.add_missing_metadata()

        return True
