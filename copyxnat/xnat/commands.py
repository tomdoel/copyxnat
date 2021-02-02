# coding=utf-8

"""Commands defining actions that can be performed with copyxnat"""
import abc
import os

from copyxnat.xnat.xnat_interface import XnatExperiment, XnatProject


def commands() -> dict:
    """Return a dictionary containing factories for all commands"""
    return {'export': ExportCommand,
            'show': ShowCommand,
            'copy': CopyCommand,
            'check_datatypes': CheckDatatypesCommand,
            }


class Command:
    """Wraps a command function and its input variables"""
    def __init__(self, inputs, scope, initial_result=None):
        self.scope = scope
        self.outputs = initial_result
        self.inputs = inputs

    @abc.abstractmethod
    def run(self, xnat_item, from_parent):
        """Function that will be run on each item in the XNAT server"""

    def print_results(self):
        print("Result of running {} on {}:".format(self.NAME, self.scope))
        print(self.outputs)


class CommandInputs:
    def __init__(self, dst_xnat, reporter, fix_scan_types, dst_project=None):
        self.dst_project = dst_project
        self.fix_scan_types = fix_scan_types
        self.reporter = reporter
        self.dst_xnat = dst_xnat


class CommandReturn:
    """Class for return values for a command function call"""
    def __init__(self, to_children=None, recurse=True):
        self.to_children = to_children
        self.recurse = recurse


class ExportCommand(Command):
    NAME = 'Download'
    USE_DST_SERVER = False
    CACHE_TYPE = 'downloads'

    def run(self, xnat_item, from_parent):  # pylint: disable=unused-argument
        """Command which exports XNAT project data onto local disk"""
        return_value = xnat_item.export()
        return CommandReturn(to_children=return_value)


class ShowCommand(Command):
    NAME = 'Show'
    USE_DST_SERVER = False
    CACHE_TYPE = 'cache'

    def run(self, xnat_item, from_parent):  # pylint: disable=unused-argument
        """Command which displays contents of XNAT projects"""
        if self.outputs is None:
            self.outputs = ''
        self.outputs += xnat_item.user_visible_info() + os.linesep
        # print(xnat_item.user_visible_info())
        return CommandReturn()


class CopyCommand(Command):
    NAME = 'Copy'
    USE_DST_SERVER = True
    CACHE_TYPE = 'cache'

    def run(self, xnat_item, from_parent):
        """Command which copies XNAT projects between servers"""

        # Override the project name
        dst_name = self.inputs.dst_project if isinstance(xnat_item, XnatProject) \
            else None

        copied_item = xnat_item.duplicate(
            destination_parent=from_parent,
            fix_scan_types=self.inputs.fix_scan_types,
            dst_label=dst_name,
            dry_run=self.inputs.reporter.dry_run)
        return CommandReturn(to_children=copied_item)


class CheckDatatypesCommand(Command):
    NAME = 'Check Datatypes'
    USE_DST_SERVER = True
    CACHE_TYPE = 'cache'

    def run(self, xnat_item, from_parent):  # pylint: disable=unused-argument
        """
        Command which checks if destination server has all the
        scan datatypes that are present on the source server
        """

        # On first run, set up the outputs
        if self.outputs is None:
            self.outputs = {
                'datatypes_on_dest': self.inputs.dst_xnat.datatypes(),
                'missing_session_datatypes': set(),
                'ids_with_empty_datatypes': set(),
                'required_experiment_datatypes': set()
            }

        datatype = xnat_item.interface.datatype()
        if isinstance(xnat_item, XnatExperiment):
            self.outputs['required_experiment_datatypes'].add(datatype)

            if datatype not in self.outputs['datatypes_on_dest']:
                self.outputs['missing_session_datatypes'].add(datatype)
                self.inputs.reporter.verbose_log(
                    'Session datatype {} needs to be added to '
                    'destination server. '.format(datatype))

            else:
                self.inputs.reporter.verbose_log('OK: session datatype {} is on '
                                     'destination server.'.format(datatype))
        if datatype:
            self.inputs.reporter.verbose_log(
                'Known datatype for {} {} {}'.format(xnat_item._name,  # pylint: disable=protected-access
                                                     xnat_item.label,
                                                     xnat_item.full_name))

        else:
            item_id = '{} {} {}'.format(xnat_item._name,  # pylint: disable=protected-access
                                        xnat_item.label,
                                        xnat_item.full_name)

            self.inputs.reporter.verbose_log('Empty datatype for {}'.format(
                item_id))
            self.outputs['ids_with_empty_datatypes'].add(item_id)

        return CommandReturn()

    def print_results(self):
        missing = self.outputs['missing_session_datatypes']
        if missing:
            print("Project {}: These datatypes need to be added to destination"
                  " server:".format(self.scope))
            for datatype in missing:
                print('- {}'.format(datatype))
        else:
            print("Project {}: All datatypes present on destination server".
                  format(self.scope))

        empty = self.outputs['ids_with_empty_datatypes']
        if empty:
            print("Project {}: items with undefined datatype on source server:".
                  format(self.scope))
            for item in empty:
                print('- {}'.format(item))
