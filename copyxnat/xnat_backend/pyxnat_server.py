# coding=utf-8

"""Wrappers for communicating between copyxnat items and pyXNAT backend items"""

import abc
import json
import os

import six
from pyxnat import Interface


class PyXnatServer(object):
    """Wrapper around pyXNAT server interface"""

    def __init__(self, params):
        self._interface = Interface(server=params.host,
                                    user=params.user,
                                    password=params.pwd,
                                    verify=not params.insecure)

    def fetch_interface(self):
        """Return the pyxnat interface to this server"""
        return self._interface

    def project_list(self):
        """Return array of project ids"""
        return self.fetch_interface().inspect.project_values()

    def project_name_metadata(self):
        """Return list of dictionaries containing project name metadata"""

        return [
            {'ID': project['id'],
             'name': project['name_csv'],
             'secondary_ID': project['secondary_id']
             } for project in self.fetch_interface().select(
                'xnat:projectData',
                ['xnat:projectData/ID',
                 'xnat:projectData/name',
                 'xnat:projectData/secondary_ID']).all()
        ]

    def projects(self):
        """Return array of PyXnatProject projects"""
        for label in self.project_list():
            yield self.project(label=label)

    def project(self, label):
        """Return PyXnatProject project"""
        return PyXnatProject.create(self, label)

    def datatypes(self):
        """Return datatypes on this server"""
        return self.fetch_interface().inspect.datatypes()

    def logout(self):
        """Disconnect from server"""
        self.fetch_interface().close_jsession()

    def num_experiments(self, project):
        """Return number of experiments in this project"""
        return len(
            self.fetch_interface()._get_json('/REST/projects/{}/experiments'.  # pylint: disable=protected-access
                format(project)))

    def experiment_list(self, project):
        """Return list of experiments in this project"""

        exps = self.fetch_interface()._get_json('/REST/projects/{}/experiments'.  # pylint: disable=protected-access
                format(project))
        return [exp['label'] for exp in exps]

    def request(self, uri, method):
        """Execute a REST call on the server"""
        self.fetch_interface()._exec(uri=uri, method=method)  # pylint: disable=protected-access

    def request_string(self, uri):
        """Execute a REST call on the server and return string"""
        result = self.fetch_interface()._exec(uri, 'GET')  # pylint: disable=protected-access
        return result.decode("utf-8")

    def request_json_property(self, uri):
        """Execute a REST call on the server and return string"""
        result = self.fetch_interface()._exec(uri, 'GET')  # pylint: disable=protected-access
        return json.loads(result.decode("utf-8"))["ResultSet"]['Result']


@six.add_metaclass(abc.ABCMeta)
class PyXnatItem(object):
    """Abstraction of wrappers around pyXnat interfaces"""
    def __init__(self, interface, label=None):
        self._label = label
        self._interface = interface

    def fetch_interface(self):
        """Return the pyxnat interface to this item"""
        return self._interface

    @classmethod
    def create(cls, parent, label):
        """Create a new child item of this class type from given parent"""
        return cls(
            interface=cls.create_interface(
                parent=parent.fetch_interface(),
                label=label),
            label=label
        )

    def create_on_server(self, local_file, create_params, overwrite, reporter):  # pylint: disable=unused-argument
        """Create this item on the XNAT server if it does not already exist"""

        self.fetch_interface().create(xml=local_file,
                                      allowDataDeletion=False,
                                      overwrite=overwrite)

    def datatype(self):
        """Return the XNAT datatype of this item"""
        return self.fetch_interface().datatype()

    def get_xml_string(self):
        """Return XML representation of this XNAT item"""
        return self.fetch_interface().get()

    def exists(self):
        """Return True if the item already exists on the server"""
        return self.fetch_interface().exists()

    def get_label(self):
        """Return the XNAT label of this item, or ID if the label is empty"""
        if self._label is None:
            self._label = self.fetch_interface().label() or \
                             self.fetch_interface().id()
        return self._label

    def get_id(self):
        """Return the XNAT ID of this item"""
        return self.fetch_interface().id()

    def get_attribute(self, name):
        """Return the specified attribute from this item"""
        return self.fetch_interface().attrs.get(name)

    def set_attribute(self, name, value):
        """Return the specified attribute from this item"""
        self.fetch_interface().attrs.set(name, value)

    @classmethod
    @abc.abstractmethod
    def create_interface(cls, parent, label):
        """Create a pyXnat child interface from the given pyXnat parent"""


class PyXnatItemWithResources(PyXnatItem):
    """Wrapper around a pyxnat interface that can contain resources"""

    @classmethod
    @abc.abstractmethod
    def create_interface(cls, parent, label):
        """Create a pyXnat child interface from the given pyXnat parent"""

    def resources(self):
        """Return item's resources as an array of PyXnatResource wrappers"""
        for resource in self.fetch_interface().resources():
            yield PyXnatResource(interface=resource)


class PyXnatItemWithInOutResources(PyXnatItem):
    """Wrapper around a pyxnat interface that can contain resources"""

    @classmethod
    @abc.abstractmethod
    def create_interface(cls, parent, label):
        """Create a pyXnat child interface from the given pyXnat parent"""

    def in_resources(self):
        """Return item's in resources as an array of PyXnatResource wrappers"""
        for in_resource in self.fetch_interface().in_resources():
            yield PyXnatInResource(interface=in_resource)

    def out_resources(self):
        """Return item's out resources as an array of PyXnatResource wrappers"""
        for out_resource in self.fetch_interface().out_resources():
            yield PyXnatOutResource(interface=out_resource)


class PyXnatResourceBase(PyXnatItem):
    """Wrapper around a pyxnat resource interface"""

    @classmethod
    @abc.abstractmethod
    def create_interface(cls, parent, label):
        """Create a pyXnat child interface from the given pyXnat parent"""

    def create_on_server(self, local_file, create_params, overwrite, reporter):
        interface = self.fetch_interface()
        if not interface.exists():
            interface.create(
                params={'content': create_params["resource_content"],
                        'format': create_params["resource_format"],
                        'tags': create_params["resource_tags"],
                        'event_reason': ''})

        if local_file:
            interface.put_zip(
                zip_location=local_file,
                extract=True,
                overwrite=overwrite
            )
        else:
            reporter.debug("Resource is empty or zip upload is disabled")

    def download_zip_file(self, save_dir):
        """Get zip file from server and save to disk"""

        # Omit the save command if there are no files
        files = self.fetch_interface().files().fetchall('obj')
        if not files:
            return None

        return self.fetch_interface().get(save_dir, extract=False)

    def files(self):
        """Return item's files as an array of PyXnatFile wrappers"""
        for file in self.fetch_interface().files():
            yield PyXnatFile(interface=file)

    def resource_attributes(self):
        """Return dict of resource attributes"""

        attrs = self.fetch_interface().attributes()
        return {'resource_content': attrs.get('content'),
                'resource_format': attrs.get('format'),
                'resource_tags': attrs.get('tags')}


class PyXnatResource(PyXnatResourceBase):
    """Wrapper around a pyxnat resource interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.resource(label)


class PyXnatInResource(PyXnatResourceBase):
    """Wrapper around a pyxnat in resource interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.in_resource(label)


class PyXnatOutResource(PyXnatResourceBase):
    """Wrapper around a pyxnat out resource interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.out_resource(label)


class PyXnatFile(PyXnatItem):
    """Wrapper around a pyxnat file interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.file(label)

    def create_on_server(self, local_file, create_params, overwrite, reporter):
        if local_file:
            self.fetch_interface().put(
                local_file,
                content=create_params["file_content"] or None,
                format=create_params["file_format"] or None,
                tags=create_params["file_tags"] or None,
                overwrite=overwrite
            )
        else:
            reporter.log_verbose("Resource is empty or upload is by zip")

    def download_file(self, save_dir, label):
        """Get file from server and save to disk"""

        if not label:
            raise ValueError('No file label!')

        # If label is a path, extract out only the name to be used for the file
        _, name = os.path.split(label) or 'file'

        file_path = os.path.join(save_dir, name)
        self.fetch_interface().get(file_path)
        return file_path

    def file_attributes(self):
        """Return dict of file attributes"""

        attrs = self.fetch_interface().attributes()
        return {'file_content': attrs.get('file_content'),
                'file_format': attrs.get('file_format'),
                'file_tags': attrs.get('file_tags'),
                'file_size': attrs.get('Size')}


class PyXnatProject(PyXnatItemWithResources):
    """Wrapper around a pyxnat project interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.select('/project/{}'.format(label))

    def subjects(self):
        """Return array of PyXnatSubject wrappers for this project"""
        for subject in self.fetch_interface().subjects():
            yield PyXnatSubject(interface=subject)


class PyXnatSubject(PyXnatItemWithResources):
    """Wrapper around a pyxnat subject interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.subject(label)

    def experiments(self):
        """Return array of PyXnatExperiment wrappers for this subject"""
        for experiment in self.fetch_interface().experiments():
            yield PyXnatExperiment(interface=experiment)


class PyXnatExperiment(PyXnatItemWithResources):
    """Wrapper around a pyxnat experiment interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.experiment(label)

    def scans(self):
        """Return array of PyXnatScan wrappers for this experiment"""
        for scan in self.fetch_interface().scans():
            yield PyXnatScan(interface=scan)

    def assessors(self):
        """Return array of PyXnatAssessor wrappers for this experiment"""
        for assessor in self.fetch_interface().assessors():
            yield PyXnatAssessor(interface=assessor)

    def reconstructions(self):
        """Return array of PyXnatReconstruction wrappers for this experiment"""
        for reconstruction in self.fetch_interface().reconstructions():
            yield PyXnatReconstruction(interface=reconstruction)


class PyXnatScan(PyXnatItemWithResources):
    """Wrapper around a pyxnat scan interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.scan(label)


class PyXnatAssessor(PyXnatItemWithInOutResources):
    """Wrapper around a pyxnat assessor interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.assessor(label)


class PyXnatReconstruction(PyXnatItemWithInOutResources):
    """Wrapper around a pyxnat reconstruction interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.reconstruction(label)
