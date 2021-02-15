# coding=utf-8

"""Command which copies XNAT projects between servers"""

from copyxnat.xnat.xnat_interface import XnatProject, XnatExperiment, XnatFile
from copyxnat.xnat.commands import Command


class CopyCommand(Command):
    """Command which copies XNAT projects between servers"""

    NAME = 'Copy'
    VERB = 'copy'
    COMMAND_LINE = 'copy'
    USE_DST_SERVER = True
    MODIFY_SRC_SERVER = False
    MODIFY_DST_SERVER = True
    CACHE_TYPE = 'cache'
    HELP = 'Copy projects between server, or duplicate on same server'

    def __init__(self, inputs, scope):
        super().__init__(inputs, scope)
        self.dst_datatypes = inputs.dst_xnat.datatypes()
        if inputs.app_settings.download_zips:
            self.ignore_filter = [XnatFile]

    def _run(self, xnat_item, from_parent):

        dst_name = None

        if isinstance(xnat_item, XnatProject):
            dst_name = self.inputs.dst_project
            if dst_name in from_parent.\
                    get_disallowed_project_ids(label=dst_name):
                raise RuntimeError('Cannot copy this project because the '
                                   'destination project ID {} is already '
                                   'being used as the Project Title or Running '
                                   'Title of another project on the '
                                   'destination server. You must choose a '
                                   'different Project ID to make a new copy. '
                                   'If you are trying to update an existing '
                                   'copy, you must specify the Project ID of '
                                   'destination project, not the Project Title '
                                   'or Running Title.'.format(dst_name))

        datatype = xnat_item.datatype()

        missing_session_type = isinstance(xnat_item, XnatExperiment) and \
                               datatype not in self.dst_datatypes

        if missing_session_type:
            item_id = '{} {}'.format(xnat_item._name, xnat_item.full_name)  # pylint: disable=protected-access

            if self.inputs.app_settings.ignore_datatype_errors:
                self.inputs.reporter.warning(
                    'datatype {} is missing on the destination server but '
                    '{} will be copied anyway because '
                    '--ignore-datatype-errors was specified.'.format(
                        datatype, item_id))
            else:
                self.inputs.reporter.warning(
                    'Did not copy {} because datatype {} needs to be added '
                    'to the destination server. To force copying of the data  '
                    'use --ignore-datatype-errors '.format(item_id, datatype))
                return

        dst_copy = xnat_item.copy(
            destination_parent=from_parent,
            app_settings=self.inputs.app_settings,
            dst_label=dst_name)
        self._recurse(xnat_item=xnat_item, to_children=dst_copy)

        if dst_copy and not missing_session_type:
            dst_copy.post_create()
