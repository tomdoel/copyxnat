# coding=utf-8

"""
Command which checks if destination server has all the
scan datatypes that are present on the source server
"""

from copyxnat.xnat.xnat_interface import XnatExperiment
from copyxnat.xnat.commands import Command, CommandReturn


class CheckDatatypesCommand(Command):
    """
    Command which checks if destination server has all the
    scan datatypes that are present on the source server
    """
    NAME = 'Check Datatypes'
    COMMAND_LINE = 'check_datatypes'
    USE_DST_SERVER = True
    CACHE_TYPE = 'cache'
    HELP = 'Check if session data types on source XNAT are present on ' \
           'destination'

    def run(self, xnat_item, from_parent):  # pylint: disable=unused-argument

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
                self.inputs.reporter.verbose_log(
                    'OK: session datatype {} is on destination server.'.
                        format(datatype))
            recurse = False
        else:
            recurse = True

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

        return CommandReturn(recurse=recurse)

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
