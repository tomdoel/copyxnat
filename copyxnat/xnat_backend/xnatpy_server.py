# coding=utf-8

"""Wrappers for communicating between copyxnat items and pyXNAT backend items"""

import abc
import json
import os

from xnat import connect
from xnat.inspect import Inspect


class XnatPyServer(object):
    """Wrapper around XnatPy server interface"""

    def __init__(self, params):
        self._interface = connect(params.host,
                                  user=params.user,
                                  password=params.pwd,
                                  verify=not params.insecure,
                                  extension_types=False)
                                  # no_parse_model=True)

    def fetch_interface(self):
        """Return the pyxnat interface to this server"""
        return self._interface

    def project_list(self):
        """Return array of project ids"""
        return self.fetch_interface().projects.keys()

    def project_name_metadata(self):
        """Return list of dictionaries containing project name metadata"""

        raise NotImplementedError('This method is not yet supported')

        # return [
        #     {'ID': project['id'],
        #      'name': project['name_csv'],
        #      'secondary_ID': project['secondary_id']
        #      } for project in self.fetch_interface().select(
        #         'xnat:projectData',
        #         ['xnat:projectData/ID',
        #          'xnat:projectData/name',
        #          'xnat:projectData/secondary_ID']).all()
        # ]

    def projects(self):
        """Return array of XnatPyProject projects"""
        for label in self.project_list():
            yield self.project(label=label)

    def project(self, label):
        """Return XnatPyProject project"""
        return XnatPyProject.create(self, label)

    def datatypes(self):
        """Return datatypes on this server"""

        raise NotImplementedError('This method is not yet supported')

#         return self.fetch_interface().inspect.datatypes()

    def logout(self):
        """Disconnect from server"""
        self.fetch_interface().disconnect()

    def num_experiments(self, project):
        """Return number of experiments in this project"""
        return len(self.fetch_interface().experiments)

    def does_request_succeed(self, uri, reporter, method):
        """Execute a REST call on the server and return True if it succeeds"""

        raise NotImplementedError('This method is not yet supported')

#         try:
#             self.fetch_interface()._exec(uri, method)  # pylint: disable=protected-access
#             reporter.debug('Success executing {} call {}'.format(method, uri))
#             return True
#
#         except Exception as exc:  # pylint: disable=broad-except
#             reporter.debug('Failure executing {} call {}: {}'. format(
#                 method, uri, str(exc)))
#             return False

    def request_string(self, uri, reporter, error_on_failure):
        """Execute a REST call on the server and return string"""

        raise NotImplementedError('This method is not yet supported')

#         try:
#             result = self.fetch_interface()._exec(uri, 'GET')  # pylint: disable=protected-access
#             return result.decode("utf-8")
#
#         except Exception as exc:
#             message = 'Failure executing GET call {}: {}'.format(uri, exc)
#             if error_on_failure:
#                 reporter.error(message)
#             else:
#                 reporter.log(message)
#             raise exc

    def request_json_property(self, uri, reporter):
        """Execute a REST call on the server and return string"""

        raise NotImplementedError('This method is not yet supported')

#         try:
#             result = self.fetch_interface()._exec(uri, 'GET')  # pylint: disable=protected-access
#             return json.loads(result.decode("utf-8"))["ResultSet"]['Result']
#
#         except Exception as exc:
#             reporter.error('Failure executing GET call {}: {}'.format(uri, exc))
#             raise exc


class XnatPyItem(abc.ABC):
    """Abstraction of wrappers around xnatPy interfaces"""
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

        raise NotImplementedError('This method is not yet supported')

#         self.fetch_interface().create(xml=local_file,
#                                       allowDataDeletion=False,
#                                       overwrite=overwrite)

    def datatype(self):
        """Return the XNAT datatype of this item"""

        raise NotImplementedError('This method is not yet supported')

#         return self.fetch_interface().datatype()

    def get_xml_string(self):
        """Return XML representation of this XNAT item"""
        raise NotImplementedError('This method is not yet supported')

#         return self.fetch_interface().get()

    def exists(self):
        """Return True if the item already exists on the server"""
        raise NotImplementedError('This method is not yet supported')

#         return self.fetch_interface().exists()

    def get_label(self):
        """Return the XNAT label of this item, or ID if the label is empty"""
        if self._label is None:
            self._label = self.fetch_interface().label or \
                             self.fetch_interface().id
        return self._label

    def get_id(self):
        """Return the XNAT ID of this item"""
        return self.fetch_interface().id

    def get_attribute(self, name):
        """Return the specified attribute from this item"""

        raise NotImplementedError('This method is not yet supported')

#         return self.fetch_interface().attrs.get(name)

    def set_attribute(self, name, value):
        """Return the specified attribute from this item"""

        raise NotImplementedError('This method is not yet supported')

#         self.fetch_interface().attrs.set(name, value)

    @classmethod
    @abc.abstractmethod
    def create_interface(cls, parent, label):
        """Create a pyXnat child interface from the given pyXnat parent"""


class XnatPyItemWithResources(XnatPyItem):
    """Wrapper around a pyxnat interface that can contain resources"""

    @classmethod
    @abc.abstractmethod
    def create_interface(cls, parent, label):
        """Create a xnatpy child interface from the given xnatpy parent"""

    def resources(self):
        """Return item's resources as an array of XnatPyResource wrappers"""
        for resource in self.fetch_interface().resources.values():
            yield XnatPyResource(interface=resource)


class XnatPyItemWithInOutResources(XnatPyItem):
    """Wrapper around a pyxnat interface that can contain resources"""

    @classmethod
    @abc.abstractmethod
    def create_interface(cls, parent, label):
        """Create a pyXnat child interface from the given pyXnat parent"""

    def in_resources(self):
        """Return item's in resources as an array of PyXnatResource wrappers"""

        raise NotImplementedError('This method is not yet supported')

#         for in_resource in self.fetch_interface().in_resources():
#             yield PyXnatInResource(interface=in_resource)

    def out_resources(self):
        """Return item's out resources as an array of PyXnatResource wrappers"""

        raise NotImplementedError('This method is not yet supported')

#         for out_resource in self.fetch_interface().out_resources():
#             yield PyXnatOutResource(interface=out_resource)


class XnatPyResourceBase(XnatPyItem):
    """Wrapper around a xnatpy resource interface"""

    @classmethod
    @abc.abstractmethod
    def create_interface(cls, parent, label):
        """Create a pyXnat child interface from the given pyXnat parent"""

    def create_on_server(self, local_file, create_params, overwrite, reporter):

        raise NotImplementedError('This method is not yet supported')

#         interface = self.fetch_interface()
#         if not interface.exists():
#             interface.create(
#                 params={'content': create_params["resource_content"],
#                         'format': create_params["resource_format"],
#                         'tags': create_params["resource_tags"],
#                         'event_reason': ''})
#
#         if local_file:
#             interface.put_zip(
#                 zip_location=local_file,
#                 extract=True,
#                 overwrite=overwrite
#             )
#         else:
#             reporter.debug("Resource is empty or zip download is "
#                                  "disabled")

    def download_zip_file(self, save_dir):
        """Get zip file from server and save to disk"""

        raise NotImplementedError('This method is not yet supported')

#         # Omit the save command if there are no files
#         files = self.fetch_interface().files().fetchall('obj')
#         if not files:
#             return None
#
#         return self.fetch_interface().get(save_dir, extract=False)

    def files(self):
        """Return item's files as an array of PyXnatFile wrappers"""
        for file in self.fetch_interface().files:
            f = file
            yield XnatPyFile(interface=file, label=file, parent=self)

    def resource_attributes(self):
        """Get file from server and save to disk"""

        attrs = self.fetch_interface().data
        return {'resource_content': attrs.get('content'),
                'resource_format': attrs.get('format'),
                'resource_tags': attrs.get('tags')}


class XnatPyResource(XnatPyResourceBase):
    """Wrapper around a pyxnat resource interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.resources[label]


class XnatPyInResource(XnatPyResourceBase):
    """Wrapper around a pyxnat in resource interface"""

    @classmethod
    def create_interface(cls, parent, label):
        raise NotImplementedError('This method is not yet supported')

#         return parent.in_resource(label)


class XnatPyOutResource(XnatPyResourceBase):
    """Wrapper around a pyxnat out resource interface"""

    @classmethod
    def create_interface(cls, parent, label):
        raise NotImplementedError('This method is not yet supported')

#         return parent.out_resource(label)


class XnatPyFile(XnatPyItem):
    """Wrapper around a xnatpy file interface"""

    def __init__(self, interface, label=None, parent=None):
        self._label = label
        self._interface = interface
        self._parent = parent

    @classmethod
    def create(cls, parent, label):
        return cls(
            interface=cls.create_interface(
                parent=parent.fetch_interface(),
                label=label),
            label=label,
            parent=parent
        )

    @classmethod
    def create_interface(cls, parent, label):
        return parent.file(label)

    def get_label(self):
        """Return the XNAT label of this item, or ID if the label is empty"""
        if self._label is None:
            self._label = self.fetch_interface()
        return self._label

    def get_id(self):
        """Return the XNAT ID of this item"""
        return self.fetch_interface()

    def create_on_server(self, local_file, create_params, overwrite, reporter):

        raise NotImplementedError('This method is not yet supported')

#         if local_file:
#             self.fetch_interface().put(
#                 local_file,
#                 content=create_params["file_content"] or None,
#                 format=create_params["file_format"] or None,
#                 tags=create_params["file_tags"] or None,
#                 overwrite=overwrite
#             )
#         else:
#             reporter.log_verbose("Resource is empty or zip download is "
#                                  "disabled")

    def download_file(self, save_dir, label):
        """Get file from server and save to disk"""

        raise NotImplementedError('This method is not yet supported')

#         if not label:
#             raise ValueError('No file label!')
#
#         # If label is a path, extract out only the name to be used for the file
#         _, name = os.path.split(label) or 'file'
#
#         file_path = os.path.join(save_dir, name)
#         self.fetch_interface().get(file_path)
#         return file_path

    def file_attributes(self):
        """Get file from server and save to disk"""

        i = self.fetch_interface()
        attrs = self._parent.fetch_interface().data
        return {'file_content': attrs.get('file_content'),
                'file_format': attrs.get('file_format'),
                'file_tags': attrs.get('file_tags')}


class XnatPyProject(XnatPyItemWithResources):
    """Wrapper around a pyxnat project interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.projects[label]

    def subjects(self):
        """Return array of XnatPySubject wrappers for this project"""
        for subject in self.fetch_interface().subjects.values():
            yield XnatPySubject(interface=subject)


class XnatPySubject(XnatPyItemWithResources):
    """Wrapper around a pyxnat subject interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.subjects[label]

    def experiments(self):
        """Return array of XnatPyExperiment wrappers for this subject"""
        for experiment in self.fetch_interface().experiments.values():
            yield XnatPyExperiment(interface=experiment)


class XnatPyExperiment(XnatPyItemWithResources):
    """Wrapper around a pyxnat experiment interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.experiments[label]

    def scans(self):
        """Return array of PyXnatScan wrappers for this experiment"""
        for scan in self.fetch_interface().scans.values():
            yield XnatPyScan(interface=scan)

    def assessors(self):
        """Return array of XnatPyAssessor wrappers for this experiment"""
        for assessor in self.fetch_interface().assessors.values():
            yield XnatPyAssessor(interface=assessor)

    def reconstructions(self):
        """Return array of XnatPyReconstruction wrappers for this experiment"""
        print('Reconstructions not currently supported!')
        return []
        # for reconstruction in self.fetch_interface().reconstructions.values():
        #     yield XnatPyReconstruction(interface=reconstruction)


class XnatPyScan(XnatPyItemWithResources):
    """Wrapper around a pyxnat scan interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.scans[label]

    def get_label(self):
        """Return the XNAT label of this item, or ID if the label is empty"""
        if self._label is None:
            self._label = self.fetch_interface().id
        return self._label


class XnatPyAssessor(XnatPyItemWithInOutResources):
    """Wrapper around a xnatPy assessor interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.assessors[label]


class XnatPyReconstruction(XnatPyItemWithInOutResources):
    """Wrapper around a pyxnat reconstruction interface"""

    @classmethod
    def create_interface(cls, parent, label):
        return parent.reconstructions[label]
