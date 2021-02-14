# coding=utf-8

"""Wrappers for communicating between copyxnat items and pyXNAT backend items"""

import abc
import os

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
        self._interface.close_jsession()

    def num_experiments(self, project):
        """Return number of experiments in this project"""
        return len(
            self.fetch_interface()._get_json('/REST/projects/{}/experiments'.  # pylint: disable=protected-access
                format(project)))

    def request(self, uri, method, reporter, warn_on_fail):
        """Execute a REST call on the server and return True if it succeeds"""
        try:
            self.fetch_interface()._exec(uri, method)  # pylint: disable=protected-access
            return True
        except Exception as exc:  # pylint: disable=broad-except
            message = 'Failure executing {} call {}: {}'.\
                format(method, uri, exc)
            if warn_on_fail:
                reporter.warning(message)
            else:
                reporter.verbose_log(message)
            return False


class PyXnatItem(abc.ABC):
    """Abstraction of wrappers around pyXnat interfaces"""
    def __init__(self, interface):
        self._interface = interface

    def fetch_interface(self):
        """Return the pyxnat interface to this item"""
        return self._interface

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
        """Return the XNAT label of this item"""
        return self.fetch_interface().label()

    def get_id(self):
        """Return the XNAT ID of this item"""
        return self.fetch_interface().id()


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
        for resource in self.fetch_interface().resources():
            yield PyXnatResource(interface=resource)

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
    def create(cls, parent_pyxnatitem, label):
        """
        Create a new resource wrapper
        @param parent_pyxnatitem: parent PyXnatItem of the item to be created
        @param label: XNAT label of the item being created
        """
        return cls(
            interface=parent_pyxnatitem.fetch_interface().resource(label))

    def create_on_server(self, local_file, create_params, overwrite, reporter):
        interface = self.fetch_interface()
        if not interface.exists():
            interface.create()
        if local_file:
            interface.put_zip(
                zip_location=local_file,
                extract=True,
                overwrite=overwrite
            )
        else:
            reporter.verbose_log("Resource is empty or zip download is "
                                 "disabled")

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
        return cls(interface=parent_pyxnatitem.fetch_interface().file(label))

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
            reporter.log_verbose("Resource is empty or zip download is "
                                 "disabled")

    def download_file(self, save_dir):
        """Get file from server and save to disk"""

        label = self.get_label()
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

    @classmethod
    def create(cls, parent_pyxnatitem, label):
        return cls(
            interface=parent_pyxnatitem.fetch_interface().select(
                '/project/{}'.format(label)))

    def subjects(self):
        """Return array of PyXnatSubject wrappers for this project"""
        for subject in self.fetch_interface().subjects():
            yield PyXnatSubject(interface=subject)


class PyXnatSubject(PyXnatItemWithResources):
    """Wrapper around a pyxnat subject interface"""

    @classmethod
    def create(cls, parent_pyxnatitem, label):
        return cls(
            interface=parent_pyxnatitem.fetch_interface().subject(label))

    def experiments(self):
        """Return array of PyXnatExperiment wrappers for this subject"""
        for experiment in self.fetch_interface().experiments():
            yield PyXnatExperiment(interface=experiment)


class PyXnatExperiment(PyXnatItemWithResources):
    """Wrapper around a pyxnat experiment interface"""

    @classmethod
    def create(cls, parent_pyxnatitem, label):
        return cls(
            interface=parent_pyxnatitem.fetch_interface().experiment(label))

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
