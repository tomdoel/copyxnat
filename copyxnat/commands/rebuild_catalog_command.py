# coding=utf-8

"""
Command which rebuilds the catalog for sessions of specified projects
"""

from copyxnat.xnat.commands import Command


class RebuildCatalogCommand(Command):
    """Command which rebuilds the catalog for sessions of specified projects"""

    NAME = 'Rebuild Catalog'
    VERB = 'rebuild'
    COMMAND_LINE = 'rebuild-catalog'
    USE_DST_SERVER = False
    MODIFY_DST_SERVER = False
    CACHE_TYPE = 'cache'
    HELP = 'Request a rebuild of the XNAT catalog to fix data issues'

    def _run(self, xnat_item, from_parent):  # pylint: disable=unused-argument
        xnat_item.rebuild_catalog()
        self._recurse(xnat_item=xnat_item)
