# coding=utf-8

"""Wrappers for communicating between copyxnat items and pyXNAT backend items"""

import abc
import os

from pyxnat import Interface, Inspector


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
        return [project['ID'] for project in
                self.fetch_interface()._get_json('/REST/projects')] # pylint: disable=protected-access

    def projects(self):
        """Return array of PyXnatProject projects"""
        return [self.project(label) for label in self.project_list()]

    def project(self, label):
        """Return PyXnatProject project"""
        return PyXnatProject.create(self, label)

    def datatypes(self):
        """Return datatypes on this server"""
        return Inspector(self.fetch_interface()).datatypes()

    def logout(self):
        """Disconnect from server"""
        self._interface.close_jsession()

    def num_experiments(self, project):
        """Return number of experiments in this project"""
        return len(
            self.fetch_interface()._get_json('/REST/projects/{}/experiments'.  # pylint: disable=protected-access
                format(project)))


class PyXnatItem(abc.ABC):
    """Abstraction of wrappers around pyXnat interfaces"""
    def __init__(self, interface):
        self._interface = interface

    def fetch_interface(self):
        """Return the pyxnat interface to this item"""
        return self._interface

    def create_on_server(self, local_file, create_params):  # pylint: disable=unused-argument
        """Create this item on the XNAT server if it does not already exist"""

        interface = self.fetch_interface()
        if not interface.exists():
            interface.create(xml=local_file, allowDataDeletion=False)

    def datatype(self):
        """Return the XNAT datatype of this item"""
        return self.fetch_interface().datatype()

    def get_xml_string(self):
        """Return XML representation of this XNAT item"""
        return self.fetch_interface().get()


class PyXnatItemWithResources(PyXnatItem):
    """Wrapper around a pyxnat interface that can contain resources"""

    @classmethod
    @abc.abstractmethod
    def create(cls, parent_pyxnatitem, label):
        """
        Create a new wrapper object of this class
        @param parent_pyxnatitem: parent PyXnatItem of the item to be created
        @param label: XNAT label of the item being created
        """

    def resources(self):
        """Return item's resources as an array of PyXnatResource wrappers"""
        return [PyXnatResource(resource)
                for resource in
                self.fetch_interface().resources().fetchall('obj')]

    def in_resources(self):
        """Return item's in resources as an array of PyXnatResource wrappers"""
        return [PyXnatInResource(in_resource)
                for in_resource in
                    self.fetch_interface().in_resources().fetchall('obj')]

    def out_resources(self):
        """Return item's out resources as an array of PyXnatResource wrappers"""
        return [PyXnatOutResource(out_resource)
                for out_resource in
                    self.fetch_interface().out_resources().fetchall('obj')]


class PyXnatResourceBase(PyXnatItem):
    """Wrapper around a pyxnat resource interface"""

    @classmethod
    def create(cls, parent_pyxnatitem, label):
        """
        Create a new resource wrapper
        @param parent_pyxnatitem: parent PyXnatItem of the item to be created
        @param label: XNAT label of the item being created
        """
        return cls(
            interface=parent_pyxnatitem.fetch_interface().resource(label))

    def create_on_server(self, local_file, create_params):
        interface = self.fetch_interface()
        if not interface.exists():
            interface.create()
            if local_file:
                interface.put_zip(zip_location=local_file, extract=True)
            else:
                print("Resource is empty or zip download is disabled")

    def download_zip_file(self, save_dir):
        """Get zip file from server and save to disk"""

        # Omit the save command if there are no files
        files = self.fetch_interface().files().fetchall('obj')
        if not files:
            return None

        return self.fetch_interface().get(save_dir, extract=False)

    def files(self):
        """Return item's files as an array of PyXnatFile wrappers"""
        return [PyXnatFile(file)
                for file in
                self.fetch_interface().files().fetchall('obj')]


class PyXnatResource(PyXnatResourceBase):
    """Wrapper around a pyxnat resource interface"""


class PyXnatInResource(PyXnatResourceBase):
    """Wrapper around a pyxnat in resource interface"""


class PyXnatOutResource(PyXnatResourceBase):
    """Wrapper around a pyxnat out resource interface"""


class PyXnatFile(PyXnatItem):
    """Wrapper around a pyxnat file interface"""

    @classmethod
    def create(cls, parent_pyxnatitem, label):
        """
        Create a new file wrapper
        @param parent_pyxnatitem: parent PyXnatItem of the item to be created
        @param label: XNAT label of the item being created
        """
        return cls(
            interface=parent_pyxnatitem.fetch_interface().file(label))

    def create_on_server(self, local_file, create_params):
        interface = self.fetch_interface()
        if not interface.exists():
            if local_file:
                interface.put(local_file,
                              content=create_params["file_content"] or None,
                              format=create_params["file_format"] or None,
                              tags=create_params["file_tags"] or None
                              )
            else:
                print("Resource is empty or zip download is disabled")

    def download_file(self, save_dir):
        """Get file from server and save to disk"""

        label = self.fetch_interface().label()
        if not label:
            raise ValueError('No file label!')
        file_path = os.path.join(save_dir, label)
        self.fetch_interface().get(file_path)
        return file_path

    def file_attributes(self):
        """Get file from server and save to disk"""

        attrs = self.fetch_interface().attributes()
        return {'file_content': attrs.get('file_content'),
                'file_format': attrs.get('file_format'),
                'file_tags': attrs.get('file_tags')}


class PyXnatProject(PyXnatItemWithResources):
    """Wrapper around a pyxnat project interface"""

    @staticmethod
    def get_disallowed_project_ids(server, label):
        """
        Return arrays of project names and secondary IDs that cannot be used
        for the destination project because they are already in use by other
        projects on this server. If the project already exists then the name
        and ID it is currently using are allowed (ie they will not be included
        in the disallowed lists).

        :param server: the XnatServer from which to get the disallowed IDs
        :param label: the label of the project which
        :return:
        """
        project_list = {project['ID']: project for project in
            server.fetch_interface()._get_json('/REST/projects')}  # pylint: disable=protected-access

        disallowed_secondary_ids = []
        disallowed_names = []
        for pr_id, project in project_list.items():
            if not pr_id == label:
                disallowed_names.append(project["name"])
                disallowed_secondary_ids.append(project["secondary_ID"])
        return {"names": disallowed_names,
                "secondary_ids": disallowed_secondary_ids}

    @classmethod
    def create(cls, parent_pyxnatitem, label):
        return cls(
            interface=parent_pyxnatitem.fetch_interface().select(
                '/project/{}'.format(label)))

    def subjects(self):
        """Return array of PyXnatSubject wrappers for this project"""
        return [PyXnatSubject(subject) for subject in
                self.fetch_interface().subjects().fetchall('obj')]


class PyXnatSubject(PyXnatItemWithResources):
    """Wrapper around a pyxnat subject interface"""

    @classmethod
    def create(cls, parent_pyxnatitem, label):
        return cls(
            interface=parent_pyxnatitem.fetch_interface().subject(label))

    def experiments(self):
        """Return array of PyXnatExperiment wrappers for this subject"""
        return [PyXnatExperiment(expmt) for expmt in
                self.fetch_interface().experiments().fetchall('obj')]


class PyXnatExperiment(PyXnatItemWithResources):
    """Wrapper around a pyxnat experiment interface"""

    @classmethod
    def create(cls, parent_pyxnatitem, label):
        return cls(
            interface=parent_pyxnatitem.fetch_interface().experiment(label))

    def scans(self):
        """Return array of PyXnatScan wrappers for this experiment"""
        return [PyXnatScan(scan)
                for scan in self.fetch_interface().scans().fetchall('obj')]

    def assessors(self):
        """Return array of PyXnatAssessor wrappers for this experiment"""
        return [PyXnatAssessor(assessor) for assessor in
                self.fetch_interface().assessors().fetchall('obj')]

    def reconstructions(self):
        """Return array of PyXnatReconstruction wrappers for this experiment"""
        return [PyXnatReconstruction(reconstruction) for reconstruction in
                self.fetch_interface().reconstructions().fetchall('obj')]


class PyXnatScan(PyXnatItemWithResources):
    """Wrapper around a pyxnat scan interface"""

    @classmethod
    def create(cls, parent_pyxnatitem, label):
        return cls(interface=parent_pyxnatitem.fetch_interface().scan(label))


class PyXnatAssessor(PyXnatItemWithResources):
    """Wrapper around a pyxnat assessor interface"""

    @classmethod
    def create(cls, parent_pyxnatitem, label):
        return cls(
            interface=parent_pyxnatitem.fetch_interface().assessor(label))


class PyXnatReconstruction(PyXnatItemWithResources):
    """Wrapper around a pyxnat reconstruction interface"""

    @classmethod
    def create(cls, parent_pyxnatitem, label):
        return cls(interface=parent_pyxnatitem.fetch_interface().
                   reconstruction(label))
