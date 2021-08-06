# coding=utf-8

"""SimpleXnat wrappers for the XNAT REST API"""

import abc
import os
import zipfile

import six

from copyxnat.xnat_backend.lazy_list import LazyList
from copyxnat.xnat_backend.utis import Utils
from copyxnat.xnat_backend.xnat_rest_client import XnatRestClient


@six.add_metaclass(abc.ABCMeta)
class SimpleXnatBase(object):
    """Base class for an item in the XNAT REST hierarchy"""

    @abc.abstractmethod
    def read_uri(self):
        """Return URI of this XNAT item relative to the XNAT REST interface as
        used for read operations"""

    @abc.abstractmethod
    def write_uri(self):
        """Return URI of this XNAT item relative to the XNAT REST interface as
        used for write operations"""

    def _lazy_list(self, cls_type):
        return LazyList(parent=self, wrapper_cls=cls_type)


class SimpleXnatServer(SimpleXnatBase):
    """Interface to XNAT REST API"""

    def __init__(self, params, read_only):
        self.rest_client = XnatRestClient(params=params, read_only=read_only)
        self.cached_project_list = self._lazy_list(SimpleXnatProject)
        self._cached_datatypes = None

    def read_uri(self):
        return 'data'

    def write_uri(self):
        return 'data'

    def project_list(self):
        """Return array of project ids"""
        return self.cached_project_list.get_labels()

    def project_name_metadata(self):
        """Return list of dictionaries containing project name metadata"""

        return [
            {'ID': metadata['ID'],
             'name': metadata['name'],
             'secondary_ID': metadata['secondary_ID']
             } for metadata in self.cached_project_list.get_all_metadata()
        ]

    def projects(self):
        """Return item's projects as an array of SimpleXnatProjects"""
        return self.cached_project_list.yield_items()

    def project(self, label):
        """Return SimpleXnatProject project"""
        return SimpleXnatProject.create(parent=self, label=label)

    def datatypes(self):
        """Return datatypes on this server"""

        if not self._cached_datatypes:
            self._cached_datatypes = \
                [element['ELEMENT_NAME'] for element in
                    self.rest_client.request_json_property(
                        '/data/search/elements')]
        return self._cached_datatypes

    def logout(self):
        """Disconnect from server"""
        self.rest_client.logout()

    def experiment_list(self, project):
        """Return list of experiments in this project"""

        experiments = self.rest_client.request_json_property(
            'data/projects/{}/experiments'.format(project))
        return [exp['label'] for exp in experiments]

    def num_experiments(self, project):
        """Return number of experiments in this project"""
        return len(self.rest_client.request_json_property(
            'data/projects/{}/experiments'.format(project)))

    def request(self, uri, method):
        """Execute a REST call on the server"""
        self.rest_client.request(uri=uri, method=method)

    def request_string(self, uri):
        """Execute a REST call on the server and return string"""
        return self.rest_client.request_string(uri)

    def request_json_property(self, uri):
        """Execute a REST call on the server and return JSON response"""
        return self.rest_client.request_json_property(uri)


@six.add_metaclass(abc.ABCMeta)
class SimpleXnatItem(SimpleXnatBase):
    """Abstraction of wrappers around XNAT REST API interfaces"""

    def __init__(self, parent, label, metadata):

        if not label:
            raise ValueError('Label has not been set')

        self._parent = parent
        self.rest_client = parent.rest_client
        self._label = label
        self._metadata = metadata
        self._read_uri = None
        self._write_uri = None
        self._id = None
        self._datatype = None

    def get_id(self):
        """Return the XNAT ID of this item"""
        if not self._id:
            metadata = self.get_metadata()
            if not metadata:
                raise ValueError('Cannot get ID until item has been created')

            rest_id = None
            for next_id in self.rest_id_keys:
                if (not rest_id) and metadata[next_id]:
                    rest_id = metadata[next_id]
            if not rest_id:
                raise ValueError('Could not find a suitable unique key in the '
                                 'metadata to identify this item')
            self._id = rest_id
        return self._id

    def label(self):
        """Return the XNAT label of this item"""
        if not self._label:
            raise ValueError('Label has not been set')
        return self._label

    def read_uri(self):
        if not self._read_uri:
            rest_id = self.get_id()
            parent_uri = self._parent.read_uri()
            self._read_uri = '{}/{}/{}'.format(parent_uri,
                                               self.rest_type,
                                               rest_id)
        return self._read_uri

    def write_uri(self):
        if not self._write_uri:
            rest_label = self.label()
            parent_uri = self._parent.write_uri()
            self._write_uri = '{}/{}/{}'.format(parent_uri,
                                                self.rest_type,
                                                rest_label)
        return self._write_uri

    def get_metadata(self):
        """Return XNAT metadata for this item"""
        if not self._metadata:
            property_name = self.parent_container_list
            self._metadata = getattr(self._parent, property_name).\
                get_metadata(self._label)
        return self._metadata

    def add_to_parent(self):
        """Update parent's metadata to show existance of new item"""
        return getattr(self._parent, self.parent_container_list).add_new\
            (self._label)

    @classmethod
    def find_label(cls, metadata):
        """Find a valid label from the given metadata dictionary"""
        label = None
        for next_label in cls.label_keys:
            if (not label) and metadata[next_label]:
                label = metadata[next_label]
        if not label:
            raise ValueError('Could not find a suitable label key in the '
                             'metadata to identify this item')
        return label

    @classmethod
    def get_existing(cls, parent, label, metadata):
        """Create a new child item of this class type from given parent"""
        return cls(
            parent=parent,
            label=label,
            metadata=metadata
        )

    @classmethod
    def create(cls, parent, label):
        """Create a new child item of this class type from given parent"""
        return cls(
            parent=parent,
            label=label,
            metadata=None
        )

    def create_on_server(self, local_file, create_params, overwrite, reporter):  # pylint: disable=unused-argument
        """Create this item on the XNAT server if it does not already exist"""

        if not local_file:
            raise ValueError('No filename component to {}'.format(local_file))

        self.rest_client.upload_file(
            method='put',
            uri=self.write_uri(),
            file_path=local_file,
            qs_params=Utils.optional_params({
                'overwrite': overwrite,
                'inbody': 'true',
                'allowDataDeletion': 'false'
            })
        )
        self.add_to_parent()

    def datatype(self):
        """Return the XNAT datatype of this item. This will be cached if
        not empty"""

        if not self._datatype:
            # Try to get datatype from parent's metadata
            self._datatype = self.get_metadata().get('xsiType')
            if not self._datatype:
                # If it's not set there, get it using a REST call
                meta = self.rest_client.meta(self.read_uri())
                self._datatype = meta.get('xsi:type')

        return self._datatype

    def get_xml_string(self):
        """Return XML representation of this XNAT item"""
        return self.rest_client.request_string(uri=self.read_uri(),
                                               qs_params={'format': 'xml'})

    def exists(self):
        """Return True if the item already exists on the server"""
        return self.get_metadata() is not None

    def get_label(self):
        """Return the XNAT label of this item"""
        return self._label

    def get_attribute(self, name):
        """Return the specified attribute from this item"""
        return self.get_metadata().get(name)

    @property
    @abc.abstractmethod
    def rest_type(self):
        """Return the type specifier used in the REST URL"""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def label_keys(self):
        """Name of the dictionary key in the item's metadata dict which will be
        used to match items between servers. In most cases `label` is
        appropriate if it exists for this item's metadata"""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def rest_id_keys(self):
        """List of the dictionary keys in the item's metadata dict which can be
        used to as part of the REST URI to fetch a resource or metadata. The
        first key in the list which has a non-empty value in the dict will be
        used. In most cases `ID` is appropriate, but does not exist for all
        items. `label` can often be used if it exists but may be empty for some
        types of resource collections."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def optional(self):
        """True if this type is not guaranteed to exist in its parent's schema.
        For example, some experiment types might not include scans, so querying
        for scans might return a 404 error. If this property is set to True,
        then a 404 error will be returned as en empty array.

        For example, experiments derive from type subjectAssessorData. This
        does not itself have scans, but many experiments derive from the subtype
        imageSessionData which does include scans. But another experiment type
        derived from subjectAssessorData might not have scans. This flag allows
        us to process experiments with and without scans without having to
        parse the schema."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parent_container_list(self):
        """Name of the parent property which contains the LazyList object which
        can be queried to get the metadata for this item."""
        raise NotImplementedError


@six.add_metaclass(abc.ABCMeta)
class SimpleXnatItemWithResources(SimpleXnatItem):
    """Wrapper around a XNAT REST API interface that can contain resources"""

    def __init__(self, parent, label, metadata):
        super(SimpleXnatItemWithResources, self).__init__(
            parent=parent, label=label, metadata=metadata)
        self.resource_list = self._lazy_list(SimpleXnatResource)

    def resources(self):
        """Return item's resources as an array of SimpleXnatResources"""
        return self.resource_list.yield_items()


@six.add_metaclass(abc.ABCMeta)
class SimpleXnatItemWithInOutResources(SimpleXnatItem):
    """Wrapper around an XNAT interface that can contain resources"""

    def __init__(self, parent, label, metadata):
        super(SimpleXnatItemWithInOutResources, self).__init__(
            parent=parent, label=label, metadata=metadata)
        self.in_resource_list = self._lazy_list(SimpleXnatInResource)
        self.out_resource_list = self._lazy_list(SimpleXnatOutResource)

    def in_resources(self):
        """Return array of SimpleXnatInResources for this item"""
        return self.in_resource_list.yield_items()

    def out_resources(self):
        """Return array of SimpleXnatOutResources for this item"""
        return self.out_resource_list.yield_items()


@six.add_metaclass(abc.ABCMeta)
class SimpleXnatResourceBase(SimpleXnatItem):
    """Wrapper around an XNAT resource interface"""

    label_keys = ['label', 'xnat_abstractresource_id']
    rest_id_keys = ['label', 'xnat_abstractresource_id']

    def __init__(self, parent, label, metadata):
        super(SimpleXnatResourceBase, self).__init__(
            parent=parent, label=label, metadata=metadata)
        self.file_list = self._lazy_list(SimpleXnatFile)

    def files(self):
        """Return array of SimpleXnatFiles for this resource container"""
        return self.file_list.yield_items()

    def create_on_server(self, local_file, create_params, overwrite, reporter):

        if not self.exists():
            self.rest_client.request(
                uri=self.write_uri(),
                method='put',
                qs_params=Utils.optional_params({
                    'format': create_params['resource_format'] or None,
                    'content': create_params['resource_content'] or None,
                    'tags': create_params["resource_tags"] or None
                })
            )
            self.add_to_parent()

        if local_file:
            file_name = os.path.basename(local_file)
            if not file_name:
                raise ValueError('No filename component to {}'.format(
                    local_file))
            file_uri = '{}/files/{}'.format(self.write_uri(), file_name)
            self.rest_client.upload_file(
                method='post',
                uri=file_uri,
                file_path=local_file,
                qs_params=Utils.optional_params({
                    'format': create_params['resource_format'] or None,
                    'content': create_params['resource_content'] or None,
                    'tags': create_params["resource_tags"] or None,
                    'overwrite': overwrite,
                    'inbody': 'true',
                    'extract': 'true',
                    'allowDataDeletion': 'false'
                 })

            )
        else:
            reporter.debug("Resource is empty or zip download is "
                           "disabled")

    def download_zip_file(self, save_dir):
        """Get zip file from server and save to disk"""

        # Omit the save command if there are no files
        files = len(list(self.files()))
        if not files:
            return None

        # Download the zip file from XNAT
        orig_zip_path = os.path.join(save_dir, self.get_label() + '_orig.zip')
        self.rest_client.download_file(
            file_path=orig_zip_path,
            uri=self.read_uri() + '/files',
            qs_params={'format': 'zip'})

        # Remove the hierarchical folder structure from the downloaded zip file
        # by repackiging into a new zip file
        new_zip_path = os.path.join(save_dir, self.get_label() + '.zip')
        with zipfile.ZipFile(orig_zip_path, 'r') as orig_zip:
            with zipfile.ZipFile(new_zip_path, 'w') as new_zip:

                # Iterate through all files in the zip
                for zip_info in orig_zip.infolist():

                    # Get the filename relative to the resource root
                    new_path = zip_info.filename.split('/files/', 1)[1]

                    # Modify the destination filename to remove the path prefix
                    zip_info.filename = new_path

                    # Extract out the file to the new destination
                    orig_zip.extract(member=zip_info, path=save_dir)
                    extracted_file = os.path.join(save_dir, new_path)

                    # Add the extracted file to the new archive with the
                    new_zip.write(filename=extracted_file,
                                  arcname=new_path)

                    # Delete the extracted file
                    os.remove(extracted_file)

        # Delete the original zip file
        os.remove(orig_zip_path)

        # Return path to the new zip file
        return new_zip_path

    def resource_attributes(self):
        """Get dict or resource attributes"""

        attrs = self.get_metadata()
        if not attrs:
            raise ValueError('Item has not yet been created')
        return {'resource_content': attrs.get('content'),
                'resource_tags': attrs.get('tags'),
                'resource_format': attrs.get('format'),
                'resource_category': attrs.get('category'),
                'resource_file_count': attrs.get('file_count'),
                'resource_size': attrs.get('Size')
                }


class SimpleXnatResource(SimpleXnatResourceBase):
    """Wrapper around an XNAT resource interface"""

    rest_type = 'resources'
    parent_container_list = 'resource_list'
    optional = False


class SimpleXnatInResource(SimpleXnatResourceBase):
    """Wrapper around an XNAT in-resource"""

    rest_type = 'in/resources'
    parent_container_list = 'in_resource_list'
    optional = False


class SimpleXnatOutResource(SimpleXnatResourceBase):
    """Wrapper around an XNAT out-resource"""

    rest_type = 'out/resources'
    parent_container_list = 'out_resource_list'
    optional = False


class SimpleXnatFile(SimpleXnatItem):
    """Wrapper around an XNAT file interface"""

    rest_type = 'files'
    label_keys = ['Name']
    rest_id_keys = ['Name']
    parent_container_list = 'file_list'
    optional = False

    def create_on_server(self, local_file, create_params, overwrite, reporter):
        if local_file:
            file_name = os.path.basename(local_file)
            if not file_name:
                raise ValueError('No filename component to {}'.format(
                    local_file))
            file_uri = self.write_uri()
            self.rest_client.upload_file(
                method='post',
                uri=file_uri,
                file_path=local_file,
                qs_params=Utils.optional_params({
                    'format': create_params["file_format"] or None,
                    'content': create_params["file_content"] or None,
                    'tags': create_params["file_tags"] or None,
                    'overwrite': overwrite,
                    'inbody': 'true',
                    'allowDataDeletion': 'false'
                    })
            )
            self.add_to_parent()

        else:
            reporter.log_verbose("Resource is empty or upload is by zip")

    def download_file(self, save_dir, label):
        """Get file from server and save to disk"""

        if not label:
            raise ValueError('No file label!')

        # If label is a path, extract out only the name to be used for the file
        _, name = os.path.split(label) or 'file'

        file_path = os.path.join(save_dir, name)
        self.rest_client.download_file(file_path=file_path,
                                       uri=self.read_uri(),
                                       qs_params={})
        return file_path

    def file_attributes(self):
        """Get file from server and save to disk"""

        attrs = self.get_metadata()
        if not attrs:
            raise ValueError('Item has not yet been created')
        return {'file_content': attrs.get('file_content'),
                'file_format': attrs.get('file_format'),
                'file_collection': attrs.get('collection'),
                'file_tags': attrs.get('file_tags'),
                'file_size': attrs.get('Size')
                }


class SimpleXnatProject(SimpleXnatItemWithResources):
    """Wrapper around an XNAT project interface"""

    rest_type = 'projects'
    label_keys = ['ID']
    rest_id_keys = ['ID']
    parent_container_list = 'cached_project_list'
    optional = False

    def __init__(self, parent, label, metadata):
        super(SimpleXnatProject, self).__init__(
            parent=parent, label=label, metadata=metadata)
        self.subject_list = self._lazy_list(SimpleXnatSubject)

    def subjects(self):
        """Return array of SimpleXnatSubjects for this project"""
        return self.subject_list.yield_items()


class SimpleXnatSubject(SimpleXnatItemWithResources):
    """Wrapper around an XNAT subject interface"""

    rest_type = 'subjects'
    label_keys = ['label']
    rest_id_keys = ['ID']
    parent_container_list = 'subject_list'
    optional = False

    def __init__(self, parent, label, metadata):
        super(SimpleXnatSubject, self).__init__(
            parent=parent, label=label, metadata=metadata)
        self.experiment_list = self._lazy_list(SimpleXnatExperiment)

    def experiments(self):
        """Return array of SimpleXnatExperiments for this subject"""
        return self.experiment_list.yield_items()


class SimpleXnatExperiment(SimpleXnatItemWithResources):
    """Wrapper around an XNAT experiment interface"""

    rest_type = 'experiments'
    label_keys = ['label']
    rest_id_keys = ['ID']
    parent_container_list = 'experiment_list'
    optional = False

    def __init__(self, parent, label, metadata):
        super(SimpleXnatExperiment, self).__init__(
            parent=parent, label=label, metadata=metadata)
        self.scan_list = self._lazy_list(SimpleXnatScan)
        self.assessor_list = self._lazy_list(SimpleXnatAssessor)
        self.reconstruction_list = self._lazy_list(SimpleXnatReconstruction)

    def scans(self):
        """Return array of SimpleXnatScans for this experiment"""
        return self.scan_list.yield_items()

    def assessors(self):
        """Return array of SimpleXnatAssessors for this experiment"""
        return self.assessor_list.yield_items()

    def reconstructions(self):
        """Return array of SimpleXnatReconstructions for this experiment"""
        return self.reconstruction_list.yield_items()


class SimpleXnatScan(SimpleXnatItemWithResources):
    """Wrapper around an XNAT interface for items which can contain resources"""

    rest_type = 'scans'
    label_keys = ['ID']
    rest_id_keys = ['ID']
    parent_container_list = 'scan_list'
    optional = True  # not necessarily present in a derived subjectAssessorData


class SimpleXnatAssessor(SimpleXnatItemWithInOutResources):
    """Wrapper around a pyxnat assessor interface"""

    rest_type = 'assessors'
    label_keys = ['label']
    rest_id_keys = ['ID']
    parent_container_list = 'assessor_list'
    optional = True  # not necessarily present in a derived subjectAssessorData


class SimpleXnatReconstruction(SimpleXnatItemWithInOutResources):
    """Wrapper around an XNAT reconstruction"""

    rest_type = 'reconstructions'
    label_keys = ['ID']
    rest_id_keys = ['ID']
    parent_container_list = 'reconstruction_list'
    optional = True  # not necessarily present in a derived subjectAssessorData
