# coding=utf-8

"""Abstraction for communicating with an XNAT server"""


import abc
import os
import re
import time

from enum import Enum
from pyxnat.core.errors import DatabaseError
import six
import pydicom
import urllib3

from copyxnat.pyreporter.pyreporter import ProjectFailure
from copyxnat.utils.error_utils import message_from_exception
from copyxnat.utils.network_utils import get_host
from copyxnat.config.app_settings import TransferMode
from copyxnat.xnat.xnat_xml import xml_from_string


class XnatType(Enum):
    """Describe the type of XNAT item so cleaning can be performed"""

    SERVER = 'server'
    PROJECT = 'project'
    SUBJECT = 'subject'
    EXPERIMENT = 'experiment'
    SCAN = 'scan'
    ASSESSOR = 'assessor'
    RECONSTRUCTION = 'reconstruction'
    RESOURCE = 'resource'
    IN_RESOURCE = 'in_resource'
    OUT_RESOURCE = 'out_resource'
    FILE = 'file'


@six.add_metaclass(abc.ABCMeta)
class XnatBase(object):
    """Base class for an item in the XNAT data hierarchy"""

    def __init__(self, parent_cache, interface, label, read_only,
                 app_settings, reporter, parent):
        self.parent = parent
        self.interface = interface
        if not label:
            reporter.warning("An empty label was found for a {} type".
                             format(self.visible_name))
        self.label = label or "unknown"
        self.cache = parent_cache.sub_cache(self._cache_subdir_name, label)  # pylint: disable=no-member
        self.read_only = read_only
        self.full_name = self.cache.full_name
        self.reporter = reporter
        self.app_settings = app_settings
        self.label_map = {self.xnat_type: label}
        if parent:
            for item_tag, item_label in parent.label_map.items():
                self.label_map[item_tag] = item_label

    def full_label(self):
        """The full data hierarchy and label of this item"""
        if self.parent:
            return "{}/{}".format(self.parent.full_label(), self.label)
        return self.label

    def full_name_label(self):
        """Full data hierarchy of this item plus type"""
        return '({}) {}'.format(self.visible_name, self.full_label())

    def name_label(self):
        """Name and type of this object formatted for display to user"""
        return '({}) {}'.format(self.visible_name, self.label)

    def user_visible_info(self):
        """String representation of this object that can be shown to user"""
        level = self.cache.cache_level
        return '  '*level + '-' + self.name_label()

    def get_children(self, ignore_filter):
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

    @property
    @abc.abstractmethod
    def xnat_type(self):
        """Return the XnatType of this class"""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def visible_name(self):
        """Return the XnatType of this class"""
        raise NotImplementedError

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

        super(XnatItem, self).__init__(
            parent_cache=parent.cache,
            interface=interface,
            label=label,
            read_only=parent.read_only,
            reporter=parent.reporter,
            app_settings=parent.app_settings,
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
        :return: a new XnatItem corresponding to the interface
        """
        label = interface.get_label()
        return cls(interface=interface, label=label, parent=parent, exists=True)

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
        :return: new XnatItem wrapping the item fetched or created

        """

        cls = self.__class__
        valid_label = self._get_valid_label(label)
        if not valid_label:
            message = '{} is not a valid XNAT label'.format(label)
            self.reporter.error(message)
            raise ProjectFailure(message)
        if label != valid_label:
            self.reporter.warning('{} is not a valid XNAT label. Substituting '
                                  'with {}'.format(label, valid_label))
        interface = self.interface.create(parent=parent.interface,
                                          label=valid_label)

        return cls(interface=interface,
                   label=label,
                   parent=parent)

    @staticmethod
    def _get_valid_label(label):
        """Replace any sequences of invalid characters with _ and strip leading
        and trailing whitespace.
        Note: Dots are permitted as they appear to be tolerated even though they
        might not be valid labels"""
        return re.sub(r'[^A-Za-z0-9_\-.]+', '_', label).strip()

    def create_on_server(self, create_params, local_file):
        """Create this item on the XNAT server"""

        if self.app_settings.dry_run:
            self.reporter.warning('DRY RUN: did not create {} {} with file {}'.
                                  format(self.visible_name,
                                         self.label,
                                         local_file))

        else:
            if self.read_only:
                raise RuntimeError(
                    'Programming error: attempting to create item '
                    'with file {} in read-only mode on server {}'.
                    format(local_file, self.full_name))

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
    def export(self, app_settings):
        """Save this item to the cache"""

    @abc.abstractmethod
    def create_from_source(self, src_item, xml_cleaner):
        """
        Create this item on this server by fetching the item from the source and
        applying XML cleaning where required

        :src_item: the item from which to cope the file or XML
        :xml_cleaner: XmlCleaner to modify the XML as required
        """

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

    def _provide_metadata(self, metadata):
        pass

    def project_server_path(self):
        """Return XNAT server archive path"""
        return self.parent.project_server_path()


@six.add_metaclass(abc.ABCMeta)
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
        return xml_from_string(self.get_xml_string())

    def create_from_source(self, src_item, xml_cleaner):

        # Note that cleaning will modify the xml_root object passed in
        cleaned_xml_root = xml_cleaner.clean_xml(
            xml_root=src_item.get_xml(),
            src_item=src_item,
            dst_item=self
        )

        local_file = self.cache.write_xml(
            cleaned_xml_root, self._xml_filename)  # pylint: disable=no-member

        self.create_on_server(create_params=None, local_file=local_file)

        if local_file:
            os.remove(local_file)

    def export(self, app_settings):
        src_xml_root = self.get_xml()
        return self.cache.write_xml(src_xml_root, self._xml_filename)  # pylint: disable=no-member


@six.add_metaclass(abc.ABCMeta)
class XnatFileContainerItem(XnatItem):
    """Base wrapper for resource items"""

    def create_from_source(self, src_item, xml_cleaner):
        if self.app_settings.transfer_mode == TransferMode.ZIP:
            folder_path = self.cache.make_output_path()
            local_file = src_item.interface.download_zip_file(folder_path)
        else:
            local_file = None

        attributes = src_item.interface.resource_attributes()
        self.create_on_server(create_params=attributes, local_file=local_file)

        if local_file:
            os.remove(local_file)

    def export(self, app_settings):
        folder_path = self.cache.make_output_path()

        if not self.app_settings.transfer_mode == TransferMode.ZIP:
            return folder_path

        return self.interface.download_zip_file(folder_path)

    def user_visible_info(self):
        base_string = super(XnatFileContainerItem, self).user_visible_info()
        attrs = self.interface.resource_attributes()
        attr_string = ' (content:{}, format:{}, tags:{}, category: {}, ' \
                      'file count:{} size:{} bytes)'.format(
                                        attrs.get('resource_content'),
                                        attrs.get('resource_format'),
                                        attrs.get('resource_tags'),
                                        attrs.get('resource_category'),
                                        attrs.get('resource_file_count'),
                                        attrs.get('resource_size')
                                    )

        return base_string + attr_string


class XnatFile(XnatItem):
    """Base wrapper for file items"""

    visible_name = 'File'
    xnat_type = XnatType.FILE
    _cache_subdir_name = 'files'
    interface_method = 'files'
    _child_types = []

    def create_from_source(self, src_item, xml_cleaner):
        folder_path = self.cache.make_output_path()
        attributes = src_item.interface.file_attributes()
        local_file = src_item.interface.download_file(folder_path, self.label)
        self.create_on_server(create_params=attributes,
                              local_file=local_file)
        if local_file:
            self.add_missing_metadata(local_file=local_file)
            os.remove(local_file)

    def export(self, app_settings):
        if not app_settings.transfer_mode == TransferMode.FILE:
            return None

        folder_path = self.cache.make_output_path()
        return self.interface.download_file(folder_path, self.label)

    def user_visible_info(self):
        base_string = super(XnatFile, self).user_visible_info()
        attrs = self.interface.file_attributes()
        attr_string = ' (content:{}, format:{}, collection:{}, ' \
                      'tags:{}, size:{} bytes)'.format(
                      attrs.get('file_content'),
                      attrs.get('file_format'),
                      attrs.get('file_collection'),
                      attrs.get('file_tags'),
                      attrs.get('file_size'),
        )

        return base_string + attr_string

    def add_missing_metadata(self, local_file=None):
        """Update parent items using metadata from this file"""

        if self.app_settings.add_missing_metadata and self.metadata_missing():
            tmp_local_file = None
            if not local_file:
                folder_path = self.cache.make_output_path()
                tmp_local_file = self.interface.download_file(folder_path,
                                                              self.label)
                local_file = tmp_local_file

            metadata = self._parse_metadata(local_file)

            if metadata:
                self.provide_metadata(metadata)

            if tmp_local_file:
                os.remove(tmp_local_file)

    def _parse_metadata(self, local_file):
        metadata = {}
        try:
            if pydicom.misc.is_dicom(local_file):
                tags = pydicom.dcmread(
                    local_file,
                    stop_before_pixels=True,
                    specific_tags=['SeriesInstanceUID']
                )
                if 'SeriesInstanceUID' in tags:
                    metadata['series_instance_uid'] = \
                        tags['SeriesInstanceUID'].value

        except Exception as exc:  # pylint: disable=broad-except
            self.reporter.warning('Error when attempting to parse file {}: '
                                  'Error: {}'.format(
                                      local_file,
                                      message_from_exception(exc)))
        return metadata


class XnatResource(XnatFileContainerItem):
    """Wrapper for access to an XNAT resource"""

    visible_name = 'Resource'
    xnat_type = XnatType.RESOURCE
    _cache_subdir_name = 'resources'
    interface_method = 'resources'
    _child_types = [XnatFile]


class XnatInResource(XnatFileContainerItem):
    """Wrapper for access to an XNAT resource"""

    visible_name = 'In_Resource'
    xnat_type = XnatType.IN_RESOURCE
    _cache_subdir_name = 'in_resources'
    interface_method = 'in_resources'
    _child_types = [XnatFile]

    def get_or_create_child(self, parent, label):  # pylint: disable=useless-return
        self.reporter.warning('CopyXnat is not able to copy in-resources. This '
                              'in-resource item {} will be '
                              'skipped.'.format(label))
        return None


class XnatOutResource(XnatFileContainerItem):
    """Wrapper for access to an XNAT resource"""

    visible_name = 'Out_Resource'
    xnat_type = XnatType.OUT_RESOURCE
    _cache_subdir_name = 'out_resources'
    interface_method = 'out_resources'
    _child_types = [XnatFile]


class XnatReconstruction(XnatParentItem):
    """Wrapper for access to an XNAT assessor"""

    _cache_subdir_name = 'reconstructions'
    visible_name = 'Reconstruction'
    _xml_filename = 'metadata_reconstruction.xml'
    xnat_type = XnatType.RECONSTRUCTION
    interface_method = 'reconstructions'
    _child_types = [XnatInResource, XnatOutResource]

    def get_or_create_child(self, parent, label):  # pylint: disable=useless-return
        self.reporter.warning('CopyXnat is not able to copy reconstructions. '
                              'This reconstruction item {} will be '
                              'skipped.'.format(label))
        return None


class XnatAssessor(XnatParentItem):
    """Wrapper for access to an XNAT assessor"""

    visible_name = 'Assessor'
    _cache_subdir_name = 'assessors'
    _xml_filename = 'metadata_assessor.xml'
    xnat_type = XnatType.ASSESSOR
    interface_method = 'assessors'
    _child_types = [XnatInResource, XnatOutResource]

    def rebuild_catalog(self):
        uri = 'data/services/refresh/catalog?' \
              'options=populateStats%2Cappend%2Cdelete%2Cchecksum&' \
              'resource=/archive/projects/{}/subjects/{}/experiments/{}'.format(
                self.label_map[XnatProject.xnat_type],
                self.label_map[XnatSubject.xnat_type],
                self.get_id())
        if not self.get_server().does_request_succeed(uri=uri, method='POST'):
            self.reporter.warning(
                'Failure executing catalog rebuild POST {}'.format(uri))


class XnatScan(XnatParentItem):
    """Wrapper for access to an XNAT scan"""

    visible_name = 'Scan'
    _xml_filename = 'metadata_scan.xml'
    _cache_subdir_name = 'scans'
    xnat_type = XnatType.SCAN
    interface_method = 'scans'
    _child_types = [XnatResource]

    def __init__(self, interface, label, parent, exists=None):
        self._metadata = {'UID': None}
        super(XnatScan, self).__init__(interface, label, parent, exists)

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

    visible_name = 'Experiment'
    _xml_filename = 'metadata_session.xml'
    _cache_subdir_name = 'experiments'
    xnat_type = XnatType.EXPERIMENT
    interface_method = 'experiments'
    _child_types = [XnatScan, XnatAssessor, XnatReconstruction, XnatResource]

    def post_create(self):
        if self.app_settings.ohif_rebuild:
            self.ohif_generate_session()

        if self.app_settings.clear_caches:
            self.get_server().clear_data_caches()

        # Give XNAT a little buffer time to process the session
        time.sleep(30)

    def ohif_generate_session(self):
        """Trigger regeneration of OHIF session data"""

        if self.get_server().ohif_present():
            uri = 'xapi/viewer/projects/{}/experiments/{}'.format(
                self.label_map[XnatProject.xnat_type],
                self.get_id())
            if not self.get_server().does_request_succeed(uri=uri,
                                                          method='POST'):
                self.reporter.warning(
                    'Failure executing OHIF reset POST {}'.format(uri))

    def rebuild_catalog(self):
        uri = 'data/services/refresh/catalog?' \
              'options=populateStats%2Cappend%2Cdelete%2Cchecksum&' \
              'resource=/archive/projects/{}/subjects/{}/experiments/{}'.format(
                self.label_map[XnatProject.xnat_type],
                self.label_map[XnatSubject.xnat_type],
                self.get_id())
        if not self.get_server().does_request_succeed(uri=uri, method='POST'):
            self.reporter.warning(
                'Failure executing catalog rebuild POST {}'.format(uri))

    def progress_update(self, reporter):
        reporter.next_progress()
        self.reporter.log('Completed {} {}'.format(self.visible_name,
                                                   self.full_name))

class XnatSubject(XnatParentItem):
    """Wrapper for access to an XNAT subject"""

    visible_name = 'Subject'
    _xml_filename = 'metadata_subject.xml'
    _cache_subdir_name = 'subjects'
    xnat_type = XnatType.SUBJECT
    interface_method = 'subjects'
    _child_types = [XnatExperiment, XnatResource]


class XnatProject(XnatParentItem):
    """Wrapper for access to an XNAT project"""

    visible_name = 'Project'
    _xml_filename = 'metadata_project.xml'
    _cache_subdir_name = 'projects'
    xnat_type = XnatType.PROJECT
    interface_method = 'projects'
    _child_types = [XnatSubject, XnatResource]

    def __init__(self, interface, label, parent, exists=None):
        self._cached_experiment_list = None
        super(XnatProject, self).__init__(interface, label, parent, exists)

    def project_server_path(self):
        return "{}/{}".format(self.parent.get_archive_path().rstrip('/'),
                              self.label)

    def progress_update(self, reporter):
        self.reporter.log('Completed {} {}'.format(self.visible_name,
                                                   self.full_name))

    def experiment_in_cache(self, label):
        """Return True if this experiment label is in the cached list of
        existing experiment labels for this project. The list will be created
        on first access. True indicates an experiment already exists (assuming
        no experiment deletion), but False does not necessarily indicate a
        experiment does not exist (as it may have been created since the list
        was populated)
        """
        if self._cached_experiment_list is None:
            self._cached_experiment_list = \
                self.get_server().interface.experiment_list(self.label)
        return label in self._cached_experiment_list


class XnatServer(XnatBase):
    """Access an XNAT server"""

    visible_name = 'Server'
    _cache_subdir_name = 'servers'
    _child_types = [XnatProject]
    xnat_type = XnatType.SERVER

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

        if params.authenticate and not params.pwd:
            params.pwd = reporter.get_password(
                "Please enter the password for {}@{}:".format(params.user,
                                                              params.host))

        interface = factory.create(params=params, read_only=read_only)

        self.ohif = None
        self._project_name_metadata = None
        self._archive_path = None

        host = get_host(params.host)
        self.host = host
        self._projects = None
        super(XnatServer, self).__init__(parent_cache=base_cache,
                                         interface=interface,
                                         label=host,
                                         read_only=read_only,
                                         app_settings=app_settings,
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
        interface = self.interface.project(label)
        return XnatProject(interface=interface, label=label, parent=self)

    def logout(self):
        """Disconnect from this server"""
        self.interface.logout()

    def num_experiments(self, project):
        """Return number of experiments in this project"""
        return self.interface.num_experiments(project)

    def does_request_succeed(self, uri, method='GET'):
        """Execute a REST call on the server and return True if it succeeds"""

        if self.app_settings.dry_run:
            self.reporter.warning('DRY RUN: will not execute call {} {}'.
                                  format(method, uri))
            return False

        if self.read_only and method != 'GET':
            raise RuntimeError('Programming error: attempting {} request {} in '
                               'read-only mode to server {}'.
                               format(method, uri, self.full_name))

        try:
            self.interface.request(uri=uri, method=method)
            self.reporter.debug('Success executing {} call {}'.format(method,
                                                                      uri))
            return True

        except Exception as exc:  # pylint: disable=broad-except
            self.reporter.debug('Failure executing {} call {}: {}'. format(
                method, uri, message_from_exception(exc)))
            return False

    def request_string(self, uri, error_on_failure=True):
        """Execute a REST call on the server and return string"""
        try:
            return self.interface.request_string(uri)

        except Exception as exc:
            message = 'Failure executing GET call {}: {}'.format(
                uri, message_from_exception(exc))
            if error_on_failure:
                self.reporter.error(message)
            else:
                self.reporter.log(message)
            raise exc

    def request_json_property(self, uri):
        """Execute a REST call on the server and return string"""
        try:
            return self.interface.request_json_property(uri)

        except Exception as exc:
            self.reporter.error('Failure executing GET call {}: {}'.format(
                uri, message_from_exception(exc)))
            raise exc

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

    def clear_data_caches(self):
        """Sends request to monitoring service to clear the nrg data caches"""

        uri = 'monitoring?action=clear_caches&cacheId=nrg'

        # Ignore return value because this call returns HTML which some
        # XNAT backends interpret as an error
        self.get_server().does_request_succeed(uri=uri, method='GET')

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
                    self.request_string(uri='xapi/siteConfig/archivePath',
                                        error_on_failure=False)
            except DatabaseError as exc:
                self.reporter.log('Error reading XNAT archive path. '
                                  'This will occur with older XNAT versions. '
                                  'Will try using a legacy API. Error: {}'.
                                  format(str(exc)))
                self._archive_path = \
                    self.request_json_property(
                        'REST/services/settings/archivePath')
        return self._archive_path

    def metadata_missing(self):
        return False

    def provide_metadata(self, metadata):
        pass

    def get_server(self):
        return self
