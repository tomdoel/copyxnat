# coding=utf-8

"""Abstraction for communicating with an XNAT server"""


import abc
import os

import urllib3

from copyxnat.xnat.xml_cleaner import XmlCleaner, XnatType


class XnatServerParams:
    """Encapsulates parameters used to access an XNAT server"""

    def __init__(self, host, user, pwd, insecure=False, read_only=False):
        if '://' not in host:
            host = 'https://' + host
        self.host = host
        self.user = user
        self.pwd = pwd
        self.insecure = insecure
        self.read_only = read_only


class XnatBase(abc.ABC):
    """Base class for an item in the XNAT data hierarchy"""

    def __init__(self, parent_cache, interface, label, read_only, xml_cleaner,
                 reporter):
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

    def fetch_interface(self):
        """Get the XNAT backend interface for this object"""
        return self.interface.fetch_interface()

    def user_visible_info(self):
        """String representation of this object that can be shown to user"""
        level = self.cache.cache_level
        return '  '*level + '--{}- label:{}'.format(self._name, self.label)  # pylint: disable=no-member

    def get_children(self) -> list:
        """Return XNAT child objects of this XNAT object"""
        children = []

        # Iterate through XnatItem classes that are child types of this class
        for child_class in self._child_types:  # pylint: disable=no-member
            children = children + self.get_children_of_type(child_class)
        return children

    def get_children_of_type(self, class_type) -> list:
        """
        Return child XnatItems of this item of a particular type
        """
        get_method = getattr(self.interface, class_type.interface_method)

        return [class_type(parent_cache=self.cache,
                           interface=item,
                           label=item.fetch_interface().label(),
                           read_only=self.read_only,
                           xml_cleaner=self.xml_cleaner,
                           reporter=self.reporter)
                for item in get_method()]


class XnatItem(XnatBase):
    """Base class for data-level item in the XNAT data hierarchy"""

    @abc.abstractmethod
    def duplicate(self, destination_parent, app_settings, dst_label=None,
                  dry_run=False):
        """
        Make a copy of this item on a different server, if it doesn't already
        exist, and return an XnatItem interface to the duplicate item.

        :destination_parent: parent XnatItem under which to make the duplicate
        :dst_label: label for destination object, or None to use source label
        :return: a new XnatItem corresponding to the duplicate item
        """

    def run_recursive(self, function, from_parent, reporter):
        """Run the function on this item and all its children"""
        next_output = function(self, from_parent)
        if isinstance(self, XnatExperiment):
            reporter.next_progress()
        if next_output.recurse:
            for child in self.get_children():
                child.run_recursive(function,
                                    next_output.to_children,
                                    reporter)

    def get_or_create_child(self, parent, label, create_params, local_file,
                            dry_run):
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
        if dry_run:

            print('DRY RUN: did not create {} {} with file {}'.
                  format(cls._name, label, local_file))  # pylint: disable=protected-access, no-member
        else:
            interface.create_on_server(local_file=local_file,
                                       create_params=create_params)

        return cls(parent_cache=parent.cache,
                   interface=interface,
                   label=label,
                   read_only=parent.read_only,
                   xml_cleaner=parent.xml_cleaner,
                   reporter=self.reporter)

    @abc.abstractmethod
    def export(self, app_settings) -> str:
        """Save this item to the cache"""


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

    def duplicate(self, destination_parent, app_settings, dst_label=None,
                  dry_run=False):
        src_xml_root = self.get_xml()

        # Make sure we make a copy, as we need to preserve the original
        cleaned_xml_root = self.get_xml()

        label = dst_label or self.label

        cleaned_xml_root = self.clean(
            xml_root=cleaned_xml_root,
            fix_scan_types=app_settings.fix_scan_types,
            destination_parent=destination_parent,
            label=label
        )

        local_file = self.cache.write_xml(
            cleaned_xml_root, self._xml_filename)  # pylint: disable=no-member

        output = self.get_or_create_child(
            parent=destination_parent,
            label=label,
            create_params=None,
            local_file=local_file,
            dry_run=dry_run)

        final_xml_root = output.get_xml()

        self.xml_cleaner.add_tag_remaps(src_xml_root=src_xml_root,
                                        dst_xml_root=final_xml_root,
                                        xnat_type=self._xml_id,  # pylint: disable=no-member
                                        )
        if local_file:
            os.remove(local_file)

        return output

    def clean(self, xml_root, fix_scan_types, destination_parent, label):  # pylint: disable=unused-argument
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
            xnat_type=self._xml_id,  # pylint: disable=no-member
            fix_scan_types=fix_scan_types)

    def export(self, app_settings):
        src_xml_root = self.get_xml()
        return self.cache.write_xml(src_xml_root, self._xml_filename)  # pylint: disable=no-member


class XnatFileContainerItem(XnatItem):
    """Base wrapper for resource items"""

    def duplicate(self, destination_parent, app_settings, dst_label=None,
                  dry_run=False):

        if app_settings.download_zips:
            folder_path = self.cache.make_output_path()
            local_file = self.interface.download_zip_file(folder_path)
        else:
            local_file = None

        label = dst_label or self.label
        copied_item = self.get_or_create_child(parent=destination_parent,
                                               label=label,
                                               create_params=None,
                                               local_file=local_file,
                                               dry_run=dry_run)
        if local_file:
            os.remove(local_file)

        return copied_item

    def export(self, app_settings):
        folder_path = self.cache.make_output_path()
        if not app_settings.download_zips:
            return folder_path

        return self.interface.download_zip_file(folder_path)


class XnatFile(XnatItem):
    """Base wrapper for file items"""

    _name = 'File'
    _xml_id = XnatType.file
    _cache_subdir_name = 'files'
    interface_method = 'files'
    _child_types = []

    def duplicate(self, destination_parent, app_settings, dst_label=None,
                  dry_run=False):
        if app_settings.download_zips:
            return None

        folder_path = self.cache.make_output_path()
        attributes = self.interface.file_attributes()
        local_file = self.interface.download_file(folder_path)
        label = dst_label or self.label
        copied_item = self.get_or_create_child(parent=destination_parent,
                                               label=label,
                                               create_params=attributes,
                                               local_file=local_file,
                                               dry_run=dry_run)

        if local_file:
            os.remove(local_file)

        return copied_item

    def export(self, app_settings):
        if app_settings.download_zips:
            return None

        folder_path = self.cache.make_output_path()
        return self.interface.download_file(folder_path)


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
    _child_types = [XnatResource, XnatInResource, XnatOutResource]


class XnatScan(XnatParentItem):
    """Wrapper for access to an XNAT scan"""

    _name = 'Scan'
    _xml_filename = 'metadata_scan.xml'
    _cache_subdir_name = 'scans'
    _xml_id = XnatType.scan
    interface_method = 'scans'
    _child_types = [XnatResource]


class XnatExperiment(XnatParentItem):
    """Wrapper for access to an XNAT experiment"""

    _name = 'Experiment'
    _xml_filename = 'metadata_session.xml'
    _cache_subdir_name = 'experiments'
    _xml_id = XnatType.experiment
    interface_method = 'experiments'
    _child_types = [XnatScan, XnatAssessor, XnatReconstruction, XnatResource]


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

    def clean(self, xml_root, fix_scan_types, destination_parent,
              label):
        disallowed = self.interface.get_disallowed_project_ids(
            server=destination_parent, label=label)
        cleaned_xml_root = self.xml_cleaner.make_project_names_unique(
            xml_root=xml_root,
            disallowed_ids=disallowed["secondary_ids"],
            disallowed_names=disallowed["names"]
        )

        return self.xml_cleaner.clean(
            xml_root=cleaned_xml_root,
            xnat_type=self._xml_id,  # pylint: disable=no-member
            fix_scan_types=fix_scan_types)


class XnatServer(XnatBase):
    """Access an XNAT server"""

    _name = 'Server'
    _cache_subdir_name = 'servers'
    _child_types = [XnatProject]

    def __init__(self,
                 factory,
                 params,
                 base_cache,
                 reporter
                 ):

        if params.insecure:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        interface = factory.create(params=params)

        label = params.host.replace('https://', '').replace('http://', '')
        self._projects = None
        super().__init__(parent_cache=base_cache,
                         interface=interface,
                         label=label,
                         read_only=params.read_only,
                         xml_cleaner=XmlCleaner(reporter=reporter),
                         reporter=reporter)

    def datatypes(self):
        """Return all the session datatypes in use on this server"""
        return self.interface.datatypes()

    def project_list(self):
        """Return array of project ids"""
        return self.interface.project_list()

    def project(self, label):
        """Return XnatProject for this project id"""
        return XnatProject(parent_cache=self.cache,
                           interface=self.interface.project(label),
                           label=label,
                           read_only=self.read_only,
                           xml_cleaner=self.xml_cleaner,
                           reporter=self.reporter)

    def logout(self):
        """Disconnect from this server"""
        self.interface.logout()

    def num_experiments(self, project):
        """Return number of experiments in this project"""
        return self.interface.num_experiments(project)
