# coding=utf-8

"""Command which copies XNAT projects between servers"""
from copyxnat.config.app_settings import TransferMode
from copyxnat.xnat.xnat_interface import XnatProject, XnatExperiment, \
    XnatFile, XnatResource, XnatOutResource, XnatInResource
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

        mode = inputs.app_settings.transfer_mode
        if mode == TransferMode.zip:
            self.ignore_filter = [XnatFile]
        elif mode in [TransferMode.rsync, TransferMode.meta]:
            self.ignore_filter = [XnatResource, XnatFile, XnatInResource,
                                  XnatOutResource]

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

        missing_session_type = False
        if isinstance(xnat_item, XnatExperiment):
            datatype = xnat_item.datatype()
            missing_session_type = datatype not in self.dst_datatypes

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
                        'to the destination server. To force copying of the '
                        'data, use --ignore-datatype-errors '.
                            format(item_id, datatype))
                    return

        dst_copy = xnat_item.copy(
            destination_parent=from_parent,
            app_settings=self.inputs.app_settings,
            dst_label=dst_name)

        if isinstance(xnat_item, XnatProject) and \
                self.inputs.app_settings.transfer_mode == TransferMode.rsync:
            self.inputs.rsync.rsync_project_data(
                src_project_path=xnat_item.project_server_path(),
                dst_project_path=dst_copy.project_server_path(),
                src_label=xnat_item.label
            )

        self._recurse(xnat_item=xnat_item, to_children=dst_copy)

        if dst_copy and not missing_session_type:
            dst_copy.post_create()
