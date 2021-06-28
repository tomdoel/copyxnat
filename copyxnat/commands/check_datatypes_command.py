# coding=utf-8

"""
Command which checks if destination server has all the
scan datatypes that are present on the source server
"""

from copyxnat.xnat.xnat_interface import XnatExperiment, XnatScan, \
    XnatAssessor, XnatResource, XnatFile, XnatInResource, XnatOutResource
from copyxnat.xnat.commands import Command


class CheckDatatypesCommand(Command):
    """
    Command which checks if destination server has all the
    scan datatypes that are present on the source server
    """
    NAME = 'Check Datatypes'
    VERB = 'check'
    COMMAND_LINE = 'check-datatypes'
    USE_DST_SERVER = True
    MODIFY_SRC_SERVER = False
    MODIFY_DST_SERVER = False
    CACHE_TYPE = 'cache'
    HELP = 'Check if session data types on source XNAT are present on ' \
           'destination'

    SUPPLEMENTAL_DATATYPE_INFO = {
        'proc:genProcData':
            'This datatype can be added by installing the DAX plugin '
            '(https://github.com/VUIIS/dax)',
        'icr:roiCollectionData':
            'This datatype can be added by installing the XNAT-OHIF Viewer '
            'Plugin (https://bitbucket.org/icrimaginginformatics/'
            'ohif-viewer-xnat-plugin)',
    }

    def __init__(self, inputs, scope):
        super(CheckDatatypesCommand, self).__init__(inputs, scope)
        self.outputs = {
            'datatypes_on_dest': inputs.dst_xnat.datatypes(),
            'missing_session_datatypes': set(),
            'missing_assessor_datatypes': set(),
            'ids_with_empty_datatypes': set(),
            'required_experiment_datatypes': set(),
            'required_assessor_datatypes': set()
        }
        self.ignore_filter = [XnatScan, XnatResource,
                              XnatInResource, XnatOutResource, XnatFile]

    def _run(self, xnat_item, from_parent):

        datatype = xnat_item.datatype()
        if isinstance(xnat_item, XnatExperiment):
            self.outputs['required_experiment_datatypes'].add(datatype)

            if datatype not in self.outputs['datatypes_on_dest']:
                self.outputs['missing_session_datatypes'].add(datatype)
                self.inputs.reporter.debug(
                    'Session datatype {} needs to be added to '
                    'destination server. '.format(datatype))

            else:
                self.inputs.reporter.debug(
                    'OK: session datatype {} is on destination server.'.
                        format(datatype))

        if isinstance(xnat_item, XnatAssessor):
            self.outputs['required_assessor_datatypes'].add(datatype)

            if datatype not in self.outputs['datatypes_on_dest']:
                self.outputs['missing_assessor_datatypes'].add(datatype)
                self.inputs.reporter.debug(
                    'Assessor datatype {} needs to be added to '
                    'destination server. '.format(datatype))

            else:
                self.inputs.reporter.debug(
                    'OK: assessor datatype {} is on destination server.'.
                        format(datatype))

        if datatype:
            self.inputs.reporter.debug(
                'Known datatype for {} {} {}'.format(xnat_item.visible_name,
                                                     xnat_item.label,
                                                     xnat_item.full_name))

        else:
            item_id = '{} {} {}'.format(xnat_item.visible_name,
                                        xnat_item.label,
                                        xnat_item.full_name)

            self.inputs.reporter.debug('Empty datatype for {}'.format(
                item_id))
            self.outputs['ids_with_empty_datatypes'].add(item_id)

        self._recurse(xnat_item=xnat_item)
        return True

    def print_results(self):
        self._print("Project {}:".format(self.scope))
        empty = self.outputs['ids_with_empty_datatypes']
        if empty:
            self._print(" - Some items on the source server have an undefined "
                  "datatype. This might indicate a problem with the source data"
                  " or the source server datatype configuration:")
            for item in empty:
                self._print('   - {}'.format(item))

        missing_session = self.outputs['missing_session_datatypes']
        if missing_session:
            self._print(" - Session datatypes need to be added to destination "
                  "server:")
            for datatype in missing_session:
                self._print('   - {}'.format(datatype))
                if datatype in self.SUPPLEMENTAL_DATATYPE_INFO:
                    self._print('    - {}'.format(
                        self.SUPPLEMENTAL_DATATYPE_INFO[datatype]))

        missing_assessor = self.outputs['missing_assessor_datatypes']
        if missing_assessor:
            self._print(" - Assessor datatypes need to be added to destination "
                  "server:")
            for datatype in missing_assessor:
                self._print('   - {}'.format(datatype))
                if datatype in self.SUPPLEMENTAL_DATATYPE_INFO:
                    self._print('    - {}'.format(
                        self.SUPPLEMENTAL_DATATYPE_INFO[datatype]))

        if not (missing_session or missing_assessor or empty):
            self._print(" - OK")

    def _print(self, string):
        self.inputs.reporter.output(string)
