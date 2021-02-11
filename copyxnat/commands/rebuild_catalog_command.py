# coding=utf-8

"""
Command which rebuilds the catalog for sessions of specified projects
"""

from copyxnat.xnat.commands import Command, CommandReturn


class RebuildCatalogCommand(Command):
    """Command which rebuilds the catalog for sessions of specified projects"""

    NAME = 'Rebuild Catalog'
    VERB = 'rebuild'
    COMMAND_LINE = 'rebuild-catalog'
    USE_DST_SERVER = False
    CACHE_TYPE = 'cache'
    HELP = 'Request a rebuild of the XNAT catalog to fix data issues'

    def run_pre(self, xnat_item, from_parent):  # pylint: disable=unused-argument
        xnat_item.rebuild_catalog()
        return CommandReturn()
