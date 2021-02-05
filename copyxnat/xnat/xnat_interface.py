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
                 reporter, parent):
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
        self.label_map = {self._xml_id: label}  # pylint: disable=no-member
        if parent:
            for item_tag, item_label in parent.label_map.items():
                self.label_map[item_tag] = item_label

    def fetch_interface(self):
        """Get the XNAT backend interface for this object"""
        return self.interface.fetch_interface()

    def user_visible_info(self):
        """String representation of this object that can be shown to user"""
        level = self.cache.cache_level
        return '  '*level + '-({}) {}'.format(self._name, self.label)  # pylint: disable=no-member

    def get_children(self) -> list:
        """Return XNAT child objects of this XNAT object"""

        # Iterate through XnatItem classes that are child types of this class
        for child_class in self._child_types:  # pylint: disable=no-member

            # Call the defined PyXnatItem method to get the interfaces, and
            # wrap each in an XnatItem
            for item in getattr(self.interface, child_class.interface_method)():
                yield child_class(parent_cache=self.cache,
                                  interface=item,
                                  label=item.fetch_interface().label(),
                                  read_only=self.read_only,
                                  xml_cleaner=self.xml_cleaner,
                                  reporter=self.reporter,
                                  parent=self)


class XnatItem(XnatBase):
    """Base class for data-level item in the XNAT data hierarchy"""

    def copy(self, destination_parent, app_settings, dst_label=None,
             dry_run=False):
        """
        Make a copy of this item on a different server, if it doesn't already
        exist, and return an XnatItem interface to the duplicate item.

        :destination_parent: parent XnatItem under which to make the duplicate
        :app_settings: global settings
        :dst_label: label for destination object, or None to use source label
        :return: a new XnatItem corresponding to the duplicate item
        """
        duplicate = self.duplicate(destination_parent, app_settings, dst_label,
                                   dry_run)
        if duplicate:
            duplicate.post_create()
        return duplicate

    @abc.abstractmethod
    def duplicate(self, destination_parent, app_settings, dst_label, dry_run):
        """
        Make a copy of this item on a different server, if it doesn't already
        exist, and return an XnatItem interface to the duplicate item.

        :destination_parent: parent XnatItem under which to make the duplicate
        :dst_label: label for destination object, or None to use source label
        :return: a new XnatItem corresponding to the duplicate item
        """

    def post_create(self):
        """Post-processing after item creation"""

    def run_recursive(self, function, from_parent, reporter):
        """Run the function on this item and all its children"""
        next_output = function(self, from_parent)
        if isinstance(self, XnatProject):
            reporter.output('- Project {}'.format(self.label))
        if isinstance(self, XnatSubject):
            reporter.output('  - Subject {}'.format(self.label))
        if isinstance(self, XnatExperiment):
            reporter.next_progress()
        if next_output.recurse:
            for child in self.get_children():
                child.run_recursive(function,
                                    next_output.to_children,
                                    reporter)

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

        return cls(parent_cache=parent.cache,
                   interface=interface,
                   label=label,
                   read_only=parent.read_only,
                   xml_cleaner=parent.xml_cleaner,
                   reporter=self.reporter,
                   parent=parent)

    def create_on_server(self, create_params, local_file, dry_run):
        """Create this item on the XNAT server if it does not already exist"""
        if dry_run:
            print('DRY RUN: did not create {} {} with file {}'.
                  format(self._name, self.label, local_file))  # pylint: disable=protected-access, no-member
        else:
            self.interface.create_on_server(local_file=local_file,
                                            create_params=create_params,
                                            reporter=self.reporter)

    @abc.abstractmethod
    def export(self, app_settings) -> str:
        """Save this item to the cache"""

    def ohif_generate_session(self):
        """Trigger regeneration of OHIF session data"""

    def request(self, uri, method, warn_on_fail=True):
        """Execute a REST call on the server"""
        return self.parent.request(uri, method, warn_on_fail)

    def ohif_present(self):
        """Return True if the OHIF viewer plugin is installed"""
        return self.parent.ohif_present()

    def rebuild_catalog(self):
        """Send a catalog refresh request"""


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

        output = self.get_or_create_child(
            parent=destination_parent, label=label)

        local_file = self.cache.write_xml(
            cleaned_xml_root, self._xml_filename)  # pylint: disable=no-member

        output.create_on_server(create_params=None,
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
                                               label=label)
        copied_item.create_on_server(create_params=None,
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

        label = dst_label or self.label
        folder_path = self.cache.make_output_path()
        attributes = self.interface.file_attributes()
        copied_item = self.get_or_create_child(parent=destination_parent,
                                               label=label)
        if copied_item.interface.exists():
            self.reporter.verbose_log(
                'Skipping {}: item already exists on server'.format(label))
        else:
            local_file = self.interface.download_file(folder_path)
            copied_item.create_on_server(create_params=attributes,
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

    def post_create(self):
        self.ohif_generate_session()
        self.rebuild_catalog()

    def ohif_generate_session(self):
        if self.ohif_present():
            uri = 'xapi/viewer/projects/{}/experiments/{}'.format(
                self.label_map[XnatProject._xml_id],  # pylint: disable=protected-access
                self.interface.get_id())
            self.request(uri, 'POST', warn_on_fail=True)

    def rebuild_catalog(self):
        uri = 'data/services/refresh/catalog?' \
              'options=populateStats%2Cappend%2Cdelete%2Cchecksum&' \
              'resource=/archive/projects/{}/subjects/{}/experiments/{}'.format(
                self.label_map[XnatProject._xml_id],  # pylint: disable=protected-access
                self.label_map[XnatSubject._xml_id],  # pylint: disable=protected-access
                self.interface.get_id())
        self.request(uri, 'POST', warn_on_fail=True)


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
    _xml_id = XnatType.server

    def __init__(self,
                 factory,
                 params,
                 base_cache,
                 reporter
                 ):

        if params.insecure:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        interface = factory.create(params=params)

        self.ohif = None

        label = params.host.replace('https://', '').replace('http://', '')
        self._projects = None
        super().__init__(parent_cache=base_cache,
                         interface=interface,
                         label=label,
                         read_only=params.read_only,
                         xml_cleaner=XmlCleaner(reporter=reporter),
                         reporter=reporter,
                         parent=None)

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
                           reporter=self.reporter,
                           parent=self)

    def logout(self):
        """Disconnect from this server"""
        self.interface.logout()

    def num_experiments(self, project):
        """Return number of experiments in this project"""
        return self.interface.num_experiments(project)

    def request(self, uri, method, warn_on_fail=True):
        """Execute a REST call on the server"""
        return self.interface.request(uri=uri,
                                      method=method,
                                      reporter=self.reporter,
                                      warn_on_fail=warn_on_fail)

    def ohif_present(self):
        """Return True if the OHIF viewer plugin is installed"""

        if self.ohif is None:
            self.ohif = self.request(
                uri='xapi/plugins/ohifViewerPlugin',
                method='GET',
                warn_on_fail=False)
        return self.ohif
