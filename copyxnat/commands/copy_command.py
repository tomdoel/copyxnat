# coding=utf-8

"""Command which copies XNAT projects between servers"""
from copyxnat.config.app_settings import TransferMode
from copyxnat.xnat.xml_cleaner import XmlCleaner
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
        self.xml_cleaner = XmlCleaner(app_settings=inputs.app_settings,
                                      reporter=inputs.reporter)

        mode = inputs.app_settings.transfer_mode
        if mode == TransferMode.zip:
            self.ignore_filter = [XnatFile]
        elif mode in [TransferMode.rsync, TransferMode.meta]:
            self.ignore_filter = [XnatResource, XnatFile, XnatInResource,
                                  XnatOutResource]

    def _run(self, xnat_item, from_parent):

        # Get the destination label for this item. Normally the same as the
        # input label except a different destination project label may be
        # selected
        label = self._choose_label(xnat_item)

        # Ensure that project label is valid before continuing
        self._enforce_valid_project_names(from_parent=from_parent,
                                          xnat_item=xnat_item,
                                          label=label)

        # Check for missing session types and decide whether to continue
        if not self._check_session_types(xnat_item=xnat_item):
            return

        # Create the interface to the destination item. At this point the item
        # may already exist on the server but if not, it will not be created
        dst_copy = xnat_item.get_or_create_child(parent=from_parent,
                                                 label=label)

        # Create the item on the destination server
        if self._should_create(dst_copy=dst_copy, xnat_item=xnat_item,
                               label=label):
            dst_copy.create_from_source(src_item=xnat_item,
                                        xml_cleaner=self.xml_cleaner)

        # Update the XML cleaner with new before and after IDs
        self.xml_cleaner.add_tag_remaps(src_item=xnat_item, dst_item=dst_copy)

        # In rsync mode, do the sync after the project is created but before
        # before recursion to the child items
        self._rsync(dst_copy, xnat_item)

        # Recursion to the child items
        self._recurse(xnat_item=xnat_item, to_children=dst_copy)

        # Tasks that are run after the item is created and after recursion to
        # child items
        if dst_copy:
            dst_copy.post_create()

    def _should_create(self, dst_copy, xnat_item, label):
        if dst_copy.exists_on_server():
            if self.inputs.app_settings.overwrite_existing:
                self.inputs.reporter.info(
                    "Updating existing {} {}".format(xnat_item._name, label))  # pylint: disable=no-member, protected-access
                write_dst = True
            else:
                self.inputs.reporter.info(
                    "{} {} already exists on the destination "
                    "server existing data will not be "
                    "modified. Use the --overwrite_existing "
                    "option to allow updating of existing "
                    "data".format(xnat_item._name, label))  # pylint: disable=no-member, protected-access
                write_dst = False
        else:
            write_dst = True
        return write_dst

    def _check_session_types(self, xnat_item):
        """Check for missing session datatypes, Return True to continue copy"""

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
                    return False
        return True

    def _choose_label(self, xnat_item):
        if isinstance(xnat_item, XnatProject):
            return self.inputs.dst_project or xnat_item.label
        return xnat_item.label

    def _rsync(self, dst_copy, xnat_item):
        if self.inputs.app_settings.transfer_mode == TransferMode.rsync and \
                isinstance(xnat_item, XnatProject):
            self.inputs.rsync.rsync_project_data(
                src_project_path=xnat_item.project_server_path(),
                dst_project_path=dst_copy.project_server_path(),
                src_label=xnat_item.label
            )

    @staticmethod
    def _enforce_valid_project_names(from_parent, xnat_item, label):
        if isinstance(xnat_item, XnatProject):
            if label in from_parent.get_disallowed_project_ids(label=label):
                raise RuntimeError('Cannot copy this project because the '
                                   'destination project ID {} is already '
                                   'being used as the Project Title or Running '
                                   'Title of another project on the '
                                   'destination server. You must choose a '
                                   'different Project ID to make a new copy. '
                                   'If you are trying to update an existing '
                                   'copy, you must specify the Project ID of '
                                   'destination project, not the Project Title '
                                   'or Running Title.'.format(label))
