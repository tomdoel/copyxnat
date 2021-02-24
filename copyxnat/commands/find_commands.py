# coding=utf-8

"""Commands defining actions that can be performed with copyxnat"""
from copyxnat.commands.check_datatypes_command import CheckDatatypesCommand
from copyxnat.commands.compare_command import CompareCommand
from copyxnat.commands.copy_command import CopyCommand
from copyxnat.commands.export_command import ExportCommand
from copyxnat.commands.show_command import ShowCommand
from copyxnat.commands.ohif_command import OhifCommand
from copyxnat.commands.rebuild_catalog_command import RebuildCatalogCommand


def find_command(command_string):
    """Return Command with matching command line string"""
    for command in commands():
        if command.COMMAND_LINE == command_string:
            return command
    raise ValueError('Command not found')


def commands():
    """Return array of available commands"""
    return [ExportCommand,
            ShowCommand,
            CopyCommand,
            CheckDatatypesCommand,
            OhifCommand,
            RebuildCatalogCommand,
            CompareCommand
            ]
