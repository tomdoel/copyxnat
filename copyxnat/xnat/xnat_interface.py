# coding=utf-8

"""Abstraction for communicating with an XNAT server"""


import abc
import os

import pydicom
import urllib3
from pyxnat.core.errors import DatabaseError

from copyxnat.utils.network_utils import get_host
from copyxnat.config.app_settings import TransferMode
from copyxnat.xnat.xml_cleaner import XmlCleaner, XnatType


class XnatBase(abc.ABC):
    """Base class for an item in the XNAT data hierarchy"""

    def __init__(self, parent_cache, interface, label, read_only, xml_cleaner,
                 app_settings, reporter, parent):
        self.parent = parent
        self.interface = interface
        if not label:
            reporter.warning("An empty label was found for a {} type".
                             format(self._name))  # pylint: disable=no-member
        self.label = label or "unknown"
        self.cache = parent_cache.sub_cache(self._cache_subdir_name, label)  # pylint: disable=no-member
        self.read_only = read_only
        self.full_name = self.cache.full_name
        self.xml_cleaner = xml_cleaner
        self.reporter = reporter
        self.app_settings = app_settings
        self.label_map = {self._xml_id: label}  # pylint: disable=no-member
        if parent:
            for item_tag, item_label in parent.label_map.items():
                self.label_map[item_tag] = item_label

    def user_visible_info(self):
        """String representation of this object that can be shown to user"""
        level = self.cache.cache_level
        return '  '*level + '-({}) {}'.format(self._name, self.label)  # pylint: disable=no-member

    def get_children(self, ignore_filter) -> list:
        """Return XNAT child objects of this XNAT object"""

        # Iterate through XnatItem classes that are child types of this class,
        # but filter out ones the Command has indicated to exclude
        consider_types = [child for child in self._child_types if child not in  # pylint: disable=no-member
                          ignore_filter]

        for child_class in consider_types:

            # Call the defined PyXnatItem method to get the interfaces, and
            # wrap each in an XnatItem
            for item in getattr(self.interface, child_class.interface_method)():
                yield child_class.get_existing(interface=item, parent=self)

    @abc.abstractmethod
    def get_server(self):
        """Return the parent server object"""

    @abc.abstractmethod
    def metadata_missing(self):
        """Return True if this item or any parent requires metadata which could
        be found from the child Files"""

    @abc.abstractmethod
    def provide_metadata(self, metadata):
        """Supply missing metadata to parent items"""


# pylint: disable=too-many-public-methods
class XnatItem(XnatBase):
    """Base class for data-level item in the XNAT data hierarchy. Used for all
    non-root items (ie all items other than XnatServer) """

    def __init__(self, interface, label, parent, exists=None):
        self._datatype = None
        self._id = None
        self._exists_on_server = exists

        super().__init__(parent_cache=parent.cache,
                         interface=interface,
                         label=label,
                         read_only=parent.read_only,
                         reporter=parent.reporter,
                         app_settings=parent.app_settings,
                         xml_cleaner=parent.xml_cleaner,
                         parent=parent)

    def datatype(self):
        """Return datatype name of the underlying XNAT item"""
        if self._datatype is None:
            if not self.exists_on_server():
                raise RuntimeError('Attempt to access datatype before object '
                                   'has been created in item {}'.
                                   format(self.full_name))
            self._datatype = self.interface.datatype()
        return self._datatype

    def get_id(self):
        """Return XNAT ID of the underlying XNAT item"""

        if self._id is None:
            if not self.exists_on_server():
                raise RuntimeError('Attempt to access id before object '
                                   'has been created in item {}'.
                                   format(self.full_name))
            self._id = self.interface.get_id()
        return self._id

    @classmethod
    def get_existing(cls, interface, parent):
        """
        Return XnatItem for the provided interface which must represent an
        item that already exists on the server. Error if it does not exist.
        :return: a new XnatItem corresponding to the inteerface
        """
        label = interface.get_label()
        return cls(interface=interface, label=label, parent=parent, exists=True)

    def copy(self, destination_parent, app_settings, dst_label=None):
        """
        Make a copy of this item on a different server, if it doesn't already
        exist, and return an XnatItem interface to the duplicate item.

        :destination_parent: parent XnatItem under which to make the duplicate
        :app_settings: global settings
        :dst_label: label for destination object, or None to use source label
        :return: a new XnatItem corresponding to the duplicate item
        """
        duplicate = self.duplicate(destination_parent, app_settings, dst_label)
        return duplicate

    def duplicate(self, destination_parent, app_settings, dst_label=None):
        """
        Make a copy of this item on a different server, if it doesn't already
        exist, and return an XnatItem interface to the duplicate item.

        :destination_parent: parent XnatItem under which to make the duplicate
        :dst_label: label for destination object, or None to use source label
        :return: a new XnatItem corresponding to the duplicate item
        """

        label = dst_label or self.label
        copied_item = self.get_or_create_child(parent=destination_parent,
                                               label=label)

        if copied_item.exists_on_server():
            if app_settings.overwrite_existing:
                self.reporter.warning("Updating existing {} {}".
                                      format(self._name, label))  # pylint: disable=no-member
                write_dst = True
            else:
                self.reporter.warning("{} {} already exists on the destination "
                                      "server existing data will not be "
                                      "modified. Use the --overwrite_existing "
                                      "option to allow updating of existing "
                                      "data".format(self._name, label))  # pylint: disable=no-member
                write_dst = False
        else:
            write_dst = True

        if write_dst:
            self.create(dst_item=copied_item)

        return copied_item

    def progress_update(self, reporter):
        """Update the user about current progress"""

    def get_or_create_child(self, parent, label):
        """
        Create an XNAT item under the specified parent if it does not already
        exist, and return an XnatItem wrapper that can be used to access this
        item.

        :parent: The XnatItem under which the child will be created if it does
            not already exist
        :label: The identifier used to find or create the child item
        :create_params: Additional parameters needed to create child item
        :local_file: path to a local file containing the resource or XML data
            that should be used to create this object on the server if
            it doesn't already exist
        :dry_run: if True then no change will be made on the destination server
        :return: new XnatItem wrapping the item fetched or created

        """

        cls = self.__class__
        interface = self.interface.create(parent_pyxnatitem=parent.interface,
                                          label=label)

        return cls(interface=interface,
                   label=label,
                   parent=parent)

    def create_on_server(self, create_params, local_file):
        """Create this item on the XNAT server"""
        if self.read_only:
            raise RuntimeError('Programming error: attempting to create item '
                               'with file {} in read-only mode on server {}'.
                               format(local_file, self.full_name))

        if self.app_settings.dry_run:
            self.reporter.warning('DRY RUN: did not create {} {} with file {}'.
                                  format(self._name, self.label, local_file))  # pylint: disable=protected-access, no-member
        else:
            self.interface.create_on_server(
                local_file=local_file,
                create_params=create_params,
                overwrite=self.app_settings.overwrite_existing,
                reporter=self.reporter
            )

    def exists_on_server(self):
        """Return True if item already exists on the XNAT server"""

        # If the cached value is not True then we check the server to determine
        # the exists status. Once it does exist we no longer need to check the
        # server.
        if not self._exists_on_server:
            self._exists_on_server = self.interface.exists()
        return self._exists_on_server

    @abc.abstractmethod
    def export(self, app_settings) -> str:
        """Save this item to the cache"""

    @abc.abstractmethod
    def create(self, dst_item):
        """
        Create a local file copy of this item, with any required
        cleaning so that it is ready for upload to the destination server

        :destination_parent: parent XnatItem under which to make the duplicate
        :label: The identifier used to find or create the child item
        :return: tuple of local file path, additional creation parameters
        """

    def ohif_generate_session(self):
        """Trigger regeneration of OHIF session data"""

    def get_server(self):
        """Return the parent XnatServer object"""
        return self.parent.get_server()

    def rebuild_catalog(self):
        """Send a catalog refresh request"""

    def post_create(self):
        """Post-processing after item creation"""

    def metadata_missing(self):
        """Return True if this item or any parent requires metadata which could
        be found from the child Files"""
        return self._metadata_missing() or self.parent.metadata_missing()

    def provide_metadata(self, metadata):
        self._provide_metadata(metadata)
        self.parent.provide_metadata(metadata)

    def get_attribute(self, name):
        """Return the specified XNAT attribute from this item"""
        return self.interface.get_attribute(name)

    def set_attribute(self, name, value):
        """Set the specified XNAT attribute of this item"""
        if self.read_only:
            raise RuntimeError('Programming error: attempting to set attribute '
                               '{} to {} in read-only mode on server {}'.
                               format(name, value, self.full_name))

        return self.interface.set_attribute(name, value)

    def _metadata_missing(self):  # pylint: disable=no-self-use
        return False

    def _provide_metadata(self, metadata):  # pylint: disable=no-self-use
        pass

    def project_server_path(self):
        """Return XNAT server archive path"""
        return self.parent.project_server_path()


class XnatParentItem(XnatItem):
    """
    Base class for item in the XNAT data hierarchy which can contain
    resources and child items
    """

    def get_xml_string(self):
        """Get an XML string representation of this item"""
        return self.interface.get_xml_string()

    def get_xml(self):
        """Get an XML representation of this item"""
        return XmlCleaner.xml_from_string(self.get_xml_string())

    def create(self, dst_item):

        # Note that cleaning will modify the xml_root object passed in
        cleaned_xml_root = self.clean(
            xml_root=self.get_xml(),
            destination_parent=dst_item.parent,
            label=dst_item.label
        )
        local_file = self.cache.write_xml(
            cleaned_xml_root, self._xml_filename)  # pylint: disable=no-member

        dst_item.create_on_server(create_params=None, local_file=local_file)

        if local_file:
            os.remove(local_file)

    def clean(self, xml_root, destination_parent, label):  # pylint: disable=unused-argument
        """
        Modify XML values for items copied between XNAT projects, to allow
        for changes in unique identifiers.

        :xml_root: parent XML node for the xml contents to be modified
        :fix_scan_types: if True then ambiguous scan types will be corrected
        :destination_parent: parent XnatItem under which to make the duplicate
        :label: label for destination object
        :return: the modified xml_root
        """
        return self.xml_cleaner.clean(
            xml_root=xml_root,
            fix_scan_types=self.app_settings.fix_scan_types,
            src_path=self.project_server_path(),
            dst_path=destination_parent.project_server_path(),
            remove_files=(not self.app_settings.transfer_mode ==
                              TransferMode.rsync)
        )

    def copy(self, destination_parent, app_settings, dst_label=None):
        duplicate = super().copy(destination_parent, app_settings, dst_label)

        if duplicate:
            # Update the ID maps are used to modify tags in child items
            id_src = self.get_id()
            id_dst = duplicate.get_id()
            self.xml_cleaner.add_tag_remaps(
                xnat_type=self._xml_id,  # pylint: disable=no-member
                id_src=id_src,
                id_dst=id_dst
            )

        return duplicate

    def export(self, app_settings):
        src_xml_root = self.get_xml()
        return self.cache.write_xml(src_xml_root, self._xml_filename)  # pylint: disable=no-member


class XnatFileContainerItem(XnatItem):
    """Base wrapper for resource items"""

    def create(self, dst_item):
        if self.app_settings.transfer_mode == TransferMode.zip:
            folder_path = self.cache.make_output_path()
            local_file = self.interface.download_zip_file(folder_path)
        else:
            local_file = None

        dst_item.create_on_server(create_params=None, local_file=local_file)

        if local_file:
            os.remove(local_file)

    def export(self, app_settings):
        folder_path = self.cache.make_output_path()

        if not self.app_settings.transfer_mode == TransferMode.zip:
            return folder_path

        return self.interface.download_zip_file(folder_path)


class XnatFile(XnatItem):
    """Base wrapper for file items"""

    _name = 'File'
    _xml_id = XnatType.file
    _cache_subdir_name = 'files'
    interface_method = 'files'
    _child_types = []

    def create(self, dst_item):
        folder_path = self.cache.make_output_path()
        attributes = self.interface.file_attributes()
        local_file = self.interface.download_file(folder_path, self.label)
        dst_item.create_on_server(create_params=attributes,
                                  local_file=local_file)
        if local_file:
            self._add_missing_metadata(local_file=local_file)
            os.remove(local_file)

    def copy(self, destination_parent, app_settings, dst_label=None):
        if not app_settings.transfer_mode == TransferMode.file:
            return None
        return super().copy(destination_parent=destination_parent,
                            app_settings=app_settings,
                            dst_label=dst_label)

    def export(self, app_settings):
        if not app_settings.transfer_mode == TransferMode.file:
            return None

        folder_path = self.cache.make_output_path()
        return self.interface.download_file(folder_path, self.label)

    def user_visible_info(self):
        base_string = super().user_visible_info()
        attrs = self.interface.file_attributes()
        attr_string = ' (content:{}, format:{}, tags:{})'.format(
            attrs.get('file_content'),
            attrs.get('file_format'),
            attrs.get('file_tags'))

        return base_string + attr_string

    def ohif_generate_session(self):
        # Use files to supply missing metadata
        self._add_missing_metadata()

    def _add_missing_metadata(self, local_file=None):
        tmp_local_file = None
        if not local_file:
            folder_path = self.cache.make_output_path()
            tmp_local_file = self.interface.download_file(folder_path,
                                                          self.label)
            local_file = tmp_local_file

        if self.metadata_missing():
            metadata = self._parse_metadata(local_file)

            if metadata:
                self.provide_metadata(metadata)

        if tmp_local_file:
            os.remove(tmp_local_file)

    def _parse_metadata(self, local_file):  # pylint: disable=no-self-use
        metadata = {}
        try:
            if pydicom.misc.is_dicom(local_file):
                tags = pydicom.dcmread(
                    local_file,
                    stop_before_pixels=True,
                    specific_tags=[
                        pydicom.datadict.tag_for_keyword('SeriesInstanceUID')]
                )
                if 'SeriesInstanceUID' in tags:
                    metadata['series_instance_uid'] = \
                        tags['SeriesInstanceUID'].value

        except Exception as exc:  # pylint: disable=broad-except
            self.reporter.warning('Error when attempting to parse file {}: '
                                  'Error: {}'.format(local_file, str(exc)))
        return metadata


class XnatResource(XnatFileContainerItem):
    """Wrapper for access to an XNAT resource"""

    _name = 'Resource'
    _xml_id = XnatType.resource
    _cache_subdir_name = 'resources'
    interface_method = 'resources'
    _child_types = [XnatFile]


class XnatInResource(XnatFileContainerItem):
    """Wrapper for access to an XNAT resource"""

    _name = 'In_Resource'
    _xml_id = XnatType.in_resource
    _cache_subdir_name = 'in_resources'
    interface_method = 'in_resources'
    _child_types = [XnatFile]


class XnatOutResource(XnatFileContainerItem):
    """Wrapper for access to an XNAT resource"""

    _name = 'Out_Resource'
    _xml_id = XnatType.out_resource
    _cache_subdir_name = 'out_resources'
    interface_method = 'out_resources'
    _child_types = [XnatFile]


class XnatReconstruction(XnatParentItem):
    """Wrapper for access to an XNAT assessor"""

    _name = 'Reconstruction'
    _cache_subdir_name = 'reconstructions'
    _xml_filename = 'metadata_reconstruction.xml'
    _xml_id = XnatType.reconstruction
    interface_method = 'reconstructions'
    _child_types = [XnatInResource, XnatOutResource]


class XnatAssessor(XnatParentItem):
    """Wrapper for access to an XNAT assessor"""

    _name = 'Assessor'
    _cache_subdir_name = 'assessors'
    _xml_filename = 'metadata_assessor.xml'
    _xml_id = XnatType.assessor
    interface_method = 'assessors'
    _child_types = [XnatInResource, XnatOutResource]

    def rebuild_catalog(self):
        uri = 'data/services/refresh/catalog?' \
              'options=populateStats%2Cappend%2Cdelete%2Cchecksum&' \
              'resource=/archive/projects/{}/subjects/{}/experiments/{}'.format(
                self.label_map[XnatProject._xml_id],  # pylint: disable=protected-access
                self.label_map[XnatSubject._xml_id],  # pylint: disable=protected-access
                self.get_id())
        if not self.get_server().does_request_succeed(uri=uri, method='POST'):
            self.reporter.warning(
                'Failure executing catalog rebuild POST {}'.format(uri))


class XnatScan(XnatParentItem):
    """Wrapper for access to an XNAT scan"""

    _name = 'Scan'
    _xml_filename = 'metadata_scan.xml'
    _cache_subdir_name = 'scans'
    _xml_id = XnatType.scan
    interface_method = 'scans'
    _child_types = [XnatResource]

    def __init__(self, interface, label, parent, exists=None):
        self._metadata = {'UID': None}
        super().__init__(interface, label, parent, exists)

    def _metadata_missing(self):
        if not self._metadata['UID']:
            self._metadata['UID'] = self.get_attribute('UID')
        return not all(self._metadata.values())

    def _provide_metadata(self, metadata):
        if (not self._metadata['UID']) and ('series_instance_uid' in metadata):
            uid = metadata['series_instance_uid']
            current_uid = self.get_attribute('UID')
            if current_uid:
                if not current_uid == uid:
                    self.reporter.warning(
                        'The scan UID is {} but a DICOM file has a series '
                        'instance UID of {}. Will not modify the scan UID'.
                        format(current_uid, uid))
            else:
                self.reporter.warning('Setting Scan UID to {}'.format(uid))
                self.interface.set_attribute('UID', uid)


class XnatExperiment(XnatParentItem):
    """Wrapper for access to an XNAT experiment"""

    _name = 'Experiment'
    _xml_filename = 'metadata_session.xml'
    _cache_subdir_name = 'experiments'
    _xml_id = XnatType.experiment
    interface_method = 'experiments'
    _child_types = [XnatScan, XnatAssessor, XnatReconstruction, XnatResource]

    def post_create(self):
        self.ohif_generate_session()

    def ohif_generate_session(self):
        if self.get_server().ohif_present():
            uri = 'xapi/viewer/projects/{}/experiments/{}'.format(
                self.label_map[XnatProject._xml_id],  # pylint: disable=protected-access
                self.get_id())
            if not self.get_server().does_request_succeed(uri=uri,
                                                          method='POST'):
                self.reporter.warning(
                    'Failure executing OHIF reset POST {}'.format(uri))

    def rebuild_catalog(self):
        uri = 'data/services/refresh/catalog?' \
              'options=populateStats%2Cappend%2Cdelete%2Cchecksum&' \
              'resource=/archive/projects/{}/subjects/{}/experiments/{}'.format(
                self.label_map[XnatProject._xml_id],  # pylint: disable=protected-access
                self.label_map[XnatSubject._xml_id],  # pylint: disable=protected-access
                self.get_id())
        if not self.get_server().does_request_succeed(uri=uri, method='POST'):
            self.reporter.warning(
                'Failure executing catalog rebuild POST {}'.format(uri))

    def progress_update(self, reporter):
        reporter.next_progress()


class XnatSubject(XnatParentItem):
    """Wrapper for access to an XNAT subject"""

    _name = 'Subject'
    _xml_filename = 'metadata_subject.xml'
    _cache_subdir_name = 'subjects'
    _xml_id = XnatType.subject
    interface_method = 'subjects'
    _child_types = [XnatExperiment, XnatResource]


class XnatProject(XnatParentItem):
    """Wrapper for access to an XNAT project"""

    _name = 'Project'
    _xml_filename = 'metadata_project.xml'
    _cache_subdir_name = 'projects'
    _xml_id = XnatType.project
    interface_method = 'projects'
    _child_types = [XnatSubject, XnatResource]

    def clean(self, xml_root, destination_parent, label):
        disallowed = destination_parent.get_disallowed_project_ids(label=label)
        cleaned_xml_root = self.xml_cleaner.make_project_names_unique(
            xml_root=xml_root,
            disallowed_ids=disallowed
        )

        # Note: we do not try to remap files specified at the project level
        return self.xml_cleaner.clean(
            xml_root=cleaned_xml_root,
            fix_scan_types=self.app_settings.fix_scan_types,
            src_path=None,
            dst_path=None,
            remove_files=True
        )

    def project_server_path(self):
        return "{}/{}".format(self.parent.get_archive_path(), self.label)


class XnatServer(XnatBase):
    """Access an XNAT server"""

    _name = 'Server'
    _cache_subdir_name = 'servers'
    _child_types = [XnatProject]
    _xml_id = XnatType.server

    def __init__(self,
                 factory,
                 params,
                 app_settings,
                 base_cache,
                 reporter,
                 read_only
                 ):

        self.params = params
        if params.insecure:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        interface = factory.create(params=params)

        self.ohif = None
        self._project_name_metadata = None
        self._archive_path = None

        label = get_host(params.host)
        self._projects = None
        super().__init__(parent_cache=base_cache,
                         interface=interface,
                         label=label,
                         read_only=read_only,
                         app_settings=app_settings,
                         xml_cleaner=XmlCleaner(reporter=reporter),
                         reporter=reporter,
                         parent=None)

    def datatypes(self):
        """Return all the session datatypes in use on this server"""
        return self.interface.datatypes()

    def project_list(self):
        """Return array of project ids"""
        return self.interface.project_list()

    def project_name_metadata(self):
        """Return list of dictionaries containing project name metadata"""
        if self._project_name_metadata is None:
            self._project_name_metadata = self.interface.project_name_metadata()
        return self._project_name_metadata

    def project(self, label):
        """Return XnatProject for this project id"""
        return XnatProject.get_existing(
            interface=self.interface.project(label),
            parent=self)

    def logout(self):
        """Disconnect from this server"""
        self.interface.logout()

    def num_experiments(self, project):
        """Return number of experiments in this project"""
        return self.interface.num_experiments(project)

    def does_request_succeed(self, uri, method='GET'):
        """Execute a REST call on the server and return True if it succeeds"""

        if self.read_only and method != 'GET':
            raise RuntimeError('Programming error: attempting {} request {} in '
                               'read-only mode to server {}'.
                               format(method, uri, self.full_name))

        return self.interface.does_request_succeed(
            uri=uri, reporter=self.reporter, method=method)

    def request_string(self, uri):
        """Execute a REST call on the server and return string"""
        return self.interface.request_string(uri=uri, reporter=self.reporter)

    def ohif_present(self):
        """Return True if the OHIF viewer plugin is installed on server"""

        if self.ohif is None:
            self.ohif = self.does_request_succeed(
                uri='xapi/plugins/ohifViewerPlugin')

            if self.ohif:
                self.reporter.log('OHIF viewer found on server {}'.format(
                    self.full_name))
            else:
                self.reporter.log('OHIF viewer not found on server {}'.format(
                    self.full_name))

        return self.ohif

    def get_disallowed_project_ids(self, label):
        """
        Return list of project names and secondary IDs that cannot be used
        for the destination project because they are already in use by other
        projects on this server. If the project already exists (which imples
        the project is being udated) then its IDs are permitted (ie they will
        not be included in the disallowed lists).

        :param label: the label of the current project
        :return: list of IDs (names and secondary_IDs) used by other projects
        """

        disallowed_ids = []
        for project in self.project_name_metadata():
            if not project["ID"] == label:
                disallowed_ids.append(project["ID"])
                disallowed_ids.append(project["name"])
                disallowed_ids.append(project["secondary_ID"])
        return disallowed_ids

    def get_archive_path(self):
        """Return the XNAT server's local data archive path"""

        if not self._archive_path:
            try:
                self._archive_path = \
                    self.request_string('xapi/siteConfig/archivePath')
            except DatabaseError as exc:
                self.reporter.log('Error reading XNAT archive path. '
                                  'This will occur with older XNAT versions. '
                                  'Will try using a legacy API. Error: {}'.
                                  format(str(exc)))
                self._archive_path = \
                    self.interface.request_json_property(
                        uri='REST/services/settings/archivePath',
                        reporter=self.reporter)
        return self._archive_path

    def metadata_missing(self):  # pylint: disable=no-self-use
        return False

    def provide_metadata(self, metadata):  # pylint: disable=no-self-use
        pass

    def get_server(self):
        return self
