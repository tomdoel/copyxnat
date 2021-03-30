# coding=utf-8

"""Remove and remap XML tags for xml transfer between XNAT servers"""
from collections import OrderedDict

import xmltodict

from copyxnat.config.app_settings import TransferMode
from copyxnat.xnat.xnat_interface import XnatProject, XnatType
from copyxnat.xnat.xnat_xml import XNAT_NS


class XmlCleaner:
    """Remove and remap XML tags for xml transfer between XNAT servers"""

    XNAT_MODALITY_TAG = '{http://nrg.wustl.edu/xnat}modality'
    XNAT_PROJECT_NAME_TAG = '{http://nrg.wustl.edu/xnat}name'

    ATTR_SECONDARY_PROJECT_ID = 'secondary_ID'

    XNAT_IMAGE_SCAN_DATA_TAG = '{http://nrg.wustl.edu/xnat}imageScanData'
    XNAT_OTHER_SCAN = 'xnat:OtherDicomScan'

    XNAT_FILE_TAG = '{http://nrg.wustl.edu/xnat}file'

    TAGS_TO_REMAP = {
        '{http://icr.ac.uk/icr}subjectID': XnatType.SUBJECT,
        '{http://nrg.wustl.edu/xnat}subject_ID': XnatType.SUBJECT,
        '{http://nrg.wustl.edu/xnat}image_session_ID': XnatType.EXPERIMENT,
        '{http://nrg.wustl.edu/xnat}imageSession_ID': XnatType.EXPERIMENT,
        '{http://nrg.wustl.edu/xnat}session_id': XnatType.EXPERIMENT,
        '{http://nrg.wustl.edu/xnat}scanID': XnatType.SCAN,
        '{http://nrg.wustl.edu/xnat}imageScan_ID': XnatType.SCAN
    }

    IDS_TO_MAP = {
        XnatType.PROJECT: XnatType.PROJECT,
        XnatType.SUBJECT: XnatType.SUBJECT,
        XnatType.EXPERIMENT: XnatType.EXPERIMENT,
        XnatType.ASSESSOR: XnatType.EXPERIMENT,
        XnatType.RECONSTRUCTION: XnatType.RECONSTRUCTION,
        XnatType.SCAN: XnatType.SCAN
    }

    ATTRS_TO_DELETE = {
        'ID',
        'project'
    }

    TAGS_TO_DELETE = {
        '{http://nrg.wustl.edu/xnat}in',
        '{http://nrg.wustl.edu/xnat}out',
        '{http://nrg.wustl.edu/xnat}experiments',
        '{http://nrg.wustl.edu/xnat}scans',
        '{http://nrg.wustl.edu/xnat}resources',
        '{http://nrg.wustl.edu/xnat}assessors',
        '{http://nrg.wustl.edu/xnat}reconstructions',
        '{http://nrg.wustl.edu/xnat}prearchivePath',
        '{http://nrg.wustl.edu/xnat}sharing'
    }

    MODALITY_TO_SCAN = {
        'MR': '{http://nrg.wustl.edu/xnat}MRScan',
        'CT': '{http://nrg.wustl.edu/xnat}CTScan',
        'US': '{http://nrg.wustl.edu/xnat}USScan',
        'PT': '{http://nrg.wustl.edu/xnat}PETScan'
    }

    def __init__(self, app_settings, reporter):
        self._app_settings = app_settings
        self._reporter = reporter
        self.id_maps = {}

    def make_project_names_unique(self, xml_root, disallowed_ids):
        """
        Update project XML tags and attributes to ensure unique values

        @param xml_root: ElementTree root of the XML to remap
        @param disallowed_ids: names and secondary IDs in use by other projects
        """

        # Get current values of secondary ID and name
        secondary_id = xml_root.attrib[self.ATTR_SECONDARY_PROJECT_ID]
        name = xml_root.find(self.XNAT_PROJECT_NAME_TAG, XNAT_NS).text

        # Find new values that are not already present on the server, by adding
        # a " copy x" to the name and ID string. We keep the index x the
        # same for both to avoid confusion
        new_id = secondary_id
        new_name = name
        index = 0
        while new_id in disallowed_ids or new_name in disallowed_ids:
            index += 1
            new_id = secondary_id + ' copy {}'.format(index)
            new_name = name + ' copy {}'.format(index)

        # Update the XML values
        xml_root.attrib[self.ATTR_SECONDARY_PROJECT_ID] = new_id
        for child in xml_root.findall(self.XNAT_PROJECT_NAME_TAG, XNAT_NS):
            child.text = new_name
        return xml_root

    # pylint: disable=too-many-branches
    def clean_xml(self, xml_root, src_item, dst_item):
        """
        Remove or XML remap tags that change between XNAT servers

        @param xml_root: ElementTree root of the XML to remap
        @param src_item: XNAT item on source server
        @param dst_item: XNAT item on destination server
        @return:
        """

        remove_file_tags = self._app_settings.transfer_mode not in [
                            TransferMode.RSYNC, TransferMode.META]

        if isinstance(src_item, XnatProject):
            # Note: we do not try to remap files specified at the project level
            remove_file_tags = True

            # Special logic required for Project items, as none of the project
            # labels can match those used in any other project on the server, so
            # we ensure they have unique values.
            disallowed = dst_item.parent.get_disallowed_project_ids(
                label=dst_item.label)
            xml_root = self.make_project_names_unique(
                xml_root=xml_root,
                disallowed_ids=disallowed
            )

        # Delete all attributes that change on dest server
        for attr in self.ATTRS_TO_DELETE:
            if attr in xml_root.attrib:
                del xml_root.attrib[attr]

        if self._app_settings.fix_scan_types:
            if xml_root.tag == self.XNAT_IMAGE_SCAN_DATA_TAG:
                new_tag = self.XNAT_OTHER_SCAN
                modalities = [mod.text for mod in
                              xml_root.findall(self.XNAT_MODALITY_TAG, XNAT_NS)]
                if len(modalities) == 1:
                    new_tag = self.MODALITY_TO_SCAN.get(modalities[0],
                                                        self.XNAT_OTHER_SCAN)
                self._reporter.warning('Modifying scan type {} to {}'.format(
                    self.XNAT_IMAGE_SCAN_DATA_TAG, new_tag))
                xml_root.tag = new_tag

        # Remove tags to delete
        for tag in self.TAGS_TO_DELETE:
            for child in xml_root.findall(tag, XNAT_NS):
                xml_root.remove(child)

        for tag, xnat_id_type in self.TAGS_TO_REMAP.items():
            for child in xml_root.findall(tag, XNAT_NS):
                tag_remap_dict = self._get_map_for_type(xnat_id_type)
                src_value = child.text
                if src_value not in tag_remap_dict:
                    raise ValueError('Tag {}: no new value for {} found'.format(
                                                                   tag,
                                                                   src_value))

                dst_value = tag_remap_dict[src_value]
                child.text = dst_value

        # File tags should be removed (if uploading files) or their paths
        # rewritten (if files are already present in the correct locations)
        for child in xml_root.findall(self.XNAT_FILE_TAG, XNAT_NS):
            if remove_file_tags:
                xml_root.remove(child)
            else:
                self._rewrite_uris(child, src_item, dst_item)

        return xml_root

    def _rewrite_uris(self, child, src_item, dst_item):
        if 'URI' in child.attrib:
            current = child.attrib['URI']
            src_path = src_item.project_server_path()
            dst_path = dst_item.project_server_path()

            if src_path not in current:
                raise RuntimeError('Unexpected server file path')
            self._reporter.log('Replacing path {}->{}'.format(src_path,
                                                              dst_path))
            new = current.replace('{}/'.format(src_path),
                                  '{}/'.format(dst_path), 1)
            child.attrib['URI'] = new

    def xml_compare(self, src_string, dst_string, src_item, dst_item):
        """Report comparison of XML strings"""
        src_d = xmltodict.parse(src_string, process_namespaces=True)
        dst_d = xmltodict.parse(dst_string, process_namespaces=True)
        self._compare_dicts(src_d, dst_d, src_item, dst_item)

    def _compare_dicts(self, src, dst, src_item, dst_item, nesting=0):
        both = set(src.keys()).intersection(dst.keys())
        only_src = set(src.keys()).difference(dst.keys())
        only_dst = set(dst.keys()).difference(src.keys())

        for key in only_src:
            src_value = src[key]
            if self._skip_compare(key=key):
                self._reporter.debug(
                    "Skipping comparison of {} {}->{}".format(
                        key, src_value, '(not present)'))
            else:
                if isinstance(src_value, dict):
                    item = 'Element'
                else:
                    item = 'Attribute'
                text = ' - {} {} missing from dst: {}->{} (location: {})'.\
                    format(item, key, src_value, '(not present)',
                           src_item.full_name_label())
                self._reporter.output(text)

        for key in only_dst:
            dst_value = dst[key]
            if self._skip_compare(key=key):
                self._reporter.debug(
                    "Skipping comparison of {} {}->{}".format(
                        key, '(not present)', dst_value))
            else:
                if isinstance(dst_value, dict):
                    item = 'Element'
                else:
                    item = 'Attribute'
                text = ' - {} {} added to dst: {}->{} (location: {})'.format(
                    item, key, '(not present)', dst_value,
                    dst_item.full_name_label())
                self._reporter.output(text)

        for key in both:
            src_value = src[key]
            dst_value = dst[key]

            if self._skip_compare(key=key):
                self._reporter.debug(
                    "Skipping comparison of {} {}->{}".format(
                        key, src_value, dst_value))
            else:
                if isinstance(src_value, dict) and isinstance(dst_value, dict):
                    self._compare_dicts(
                        src=src_value,
                        dst=dst_value,
                        src_item=src_item,
                        dst_item=dst_item,
                        nesting=nesting+1)
                elif isinstance(src_value, (list, dict)) and \
                        isinstance(dst_value, (list, dict)):
                    next_src = self._nest_dicts(src_value)
                    next_dst = self._nest_dicts(dst_value)
                    self._compare_dicts(
                        src=next_src,
                        dst=next_dst,
                        src_item=src_item,
                        dst_item=dst_item,
                        nesting=nesting+1)
                else:
                    if self._compare_values(
                            key=key,
                            src_value=src_value,
                            dst_value=dst_value,
                            src_item=src_item,
                            dst_item=dst_item,
                            nesting=nesting):
                        text = ' - Attribute {} matches: {}->{} (location: {}' \
                               ')'.format(key, src_value, dst_value,
                                          src_item.full_name_label())
                        self._reporter.debug(text)
                    else:
                        text = ' - Attribute {} differs: {}->{} (location: {}' \
                               ')'.format(key, src_value, dst_value,
                                          src_item.full_name_label())
                        self._reporter.output(text)

    @staticmethod
    def _skip_compare(key):
        if key == '@http://www.w3.org/2001/XMLSchema-instance:schemaLocation':
            return True
        if key == '@URI':
            return True
        if key.startswith('@xmlns'):
            return True
        return False

    def _compare_values(self, key, src_value, dst_value, src_item, dst_item,
                        nesting):

        if key == '@ID':
            # The ID in the root element maps to the XNAT level
            if nesting <= 2:
                xnat_id_type = src_item.xnat_type
                if xnat_id_type in self.IDS_TO_MAP:
                    tag_remap_dict = self._get_map_for_type(xnat_id_type)
                    if src_value in tag_remap_dict:
                        self._reporter.debug("Compare: remapping {} {}->{}".
                                             format(key, src_value, dst_value))
                        src_value = tag_remap_dict[src_value]
            else:
                # IDs in other elements could map to experiments, scans etc.
                tag_remap_dict = self._get_map_for_type(XnatType.EXPERIMENT)
                if src_value in tag_remap_dict:
                    self._reporter.debug("Compare: remapping {} {}->{}".
                                         format(key, src_value, dst_value))
                    src_value = tag_remap_dict[src_value]

        if key == '@project':
            project_remap_dict = self._get_map_for_type(XnatType.PROJECT)
            if src_value in project_remap_dict:
                self._reporter.debug("Compare: remapping {} {}->{}".
                                     format(key, src_value, dst_value))
                src_value = project_remap_dict[src_value]

        if key == '@http://www.w3.org/2001/XMLSchema-instance:schemaLocation':
            src_host = src_item.get_server().host
            dst_host = dst_item.get_server().host
            src_value = src_value.replace(src_host, dst_host)
            self._reporter.debug("Compare: remapping {} {}->{}".
                                 format(key, src_value, dst_value))

        key_converted = self._convert_key_ns(key)

        if key_converted in self.TAGS_TO_REMAP:
            map_id = self.TAGS_TO_REMAP[key_converted]
            tag_remap_dict = self.id_maps[map_id]
            if src_value in tag_remap_dict:
                self._reporter.debug("Compare: remapping {} {}->{}".
                                     format(key_converted, src_value,
                                            dst_value))
                src_value = tag_remap_dict[src_value]

        if key == '@URI':
            src_path = src_item.project_server_path()
            dst_path = dst_item.project_server_path()
            src_value = src_value.replace(src_path, dst_path, 1)
            self._reporter.debug("Compare: remapping {} {}->{}".
                                 format(key, src_value, dst_value))

        return src_value == dst_value

    @staticmethod
    def _nest_dicts(list_or_dict):
        if isinstance(list_or_dict, dict):
            return {XmlCleaner._choose_key(list_or_dict): list_or_dict}
        if isinstance(list_or_dict, list):
            return XmlCleaner._list_to_dict(list_or_dict)
        raise RuntimeError

    @staticmethod
    def _list_to_dict(list_to_convert):
        dict_out = {}
        for item in list_to_convert:
            if isinstance(item, OrderedDict):
                key = XmlCleaner._choose_key(item)
                dict_out[key] = item
            else:
                raise RuntimeError('Unable to compare the XML data because the'
                                   'structure was unexpected.')
        return dict_out

    @staticmethod
    def _choose_key(item):
        if '@label' in item:
            return item['@label']
        if '@ID' in item:
            return item['@ID']
        if '@name' in item:
            return item['@name']
        raise RuntimeError('Unable to compare the XML data because the'
                           'dictionary did not contain a standard key.')

    def add_tag_remaps(self, src_item, dst_item):
        """
        Update the remapping dictionary to add add before and after ID values
        for the tags in the map
        @param src_item: item on the source server
        @param dst_item: item on the destination server
        ID describes
        """

        xnat_type = src_item.xnat_type
        if src_item and dst_item and xnat_type in self.IDS_TO_MAP:
            id_src = src_item.get_id()
            id_dst = dst_item.get_id()
            id_map = self._get_map_for_type(xnat_type)
            id_map[id_src] = id_dst

    @staticmethod
    def _convert_key_ns(key):
        for _, namespaces in XNAT_NS.items():
            old_ns = "{}:".format(namespaces)
            new_ns = "{{{}}}".format(namespaces)
            if old_ns in key:
                key = key.replace(old_ns, new_ns, 1)
        return key

    def _get_map_for_type(self, xnat_type):
        # Find the correct dictionary
        map_id = self.IDS_TO_MAP[xnat_type]

        # Create empty dictionary if one does not exist
        if map_id not in self.id_maps:
            self.id_maps[map_id] = {}

        # Return reference to dictionary
        return self.id_maps[map_id]
