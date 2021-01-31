# coding=utf-8

"""Remove and remap XML tags for xml transfer between XNAT servers"""


from xml.etree.cElementTree import register_namespace, XML


class XmlCleaner:
    """Remove and remap XML tags for xml transfer between XNAT servers"""

    ICR_SUBJECT_ID_TAG = '{http://icr.ac.uk/icr}subjectID'
    XNAT_IMAGE_SESSION_ID = '{http://nrg.wustl.edu/xnat}image_session_ID'
    XNAT_SUBJECT_ID = '{http://nrg.wustl.edu/xnat}subject_ID'
    XNAT_OUT_TAG = '{http://nrg.wustl.edu/xnat}out'
    XNAT_EXPERIMENTS_TAG = '{http://nrg.wustl.edu/xnat}experiments'
    XNAT_SCANS_TAG = '{http://nrg.wustl.edu/xnat}scans'
    XNAT_RESOURCES_TAG = '{http://nrg.wustl.edu/xnat}resources'
    XNAT_ASSESSORS_TAG = '{http://nrg.wustl.edu/xnat}assessors'
    XNAT_PREARCHIVE_PATH_TAG = '{http://nrg.wustl.edu/xnat}prearchivePath'
    XNAT_SHARING_TAG = '{http://nrg.wustl.edu/xnat}sharing'
    XNAT_FILE_TAG = '{http://nrg.wustl.edu/xnat}file'
    XNAT_MODALITY_TAG = '{http://nrg.wustl.edu/xnat}modality'
    XNAT_PROJECT_NAME_TAG = '{http://nrg.wustl.edu/xnat}name'

    ATTR_SECONDARY_PROJECT_ID = 'secondary_ID'

    XNAT_IMAGE_SCAN_DATA_TAG = '{http://nrg.wustl.edu/xnat}imageScanData'
    XNAT_MR_SCAN = 'xnat:MRScan'
    XNAT_CT_SCAN = 'xnat:CTScan'
    XNAT_OTHER_SCAN = 'xnat:OtherDicomScan'

    XNAT_PROJECT_ID_ATTR = 'XNAT_PROJECT_ID_ATTR'
    XNAT_SUBJECT_ID_ATTR = 'XNAT_SUBJECT_ID_ATTR'
    XNAT_SESSION_ID_ATTR = 'XNAT_SESSION_ID_ATTR'
    XNAT_SCAN_ID_ATTR = 'XNAT_SCAN_ID_ATTR'
    XNAT_ASSESSOR_LABEL_ATTR = 'XNAT_ASSESSOR_LABEL_ATTR'
    XNAT_ASSESSOR_PROJECT_ATTR = 'XNAT_ASSESSOR_PROJECT_ATTR'

    TAGS_TO_REMAP = {
        ICR_SUBJECT_ID_TAG: XNAT_SUBJECT_ID_ATTR,
        XNAT_SUBJECT_ID: XNAT_SUBJECT_ID_ATTR,
        XNAT_IMAGE_SESSION_ID: XNAT_SESSION_ID_ATTR
    }

    TAGS_TO_DELETE = {
        XNAT_OUT_TAG,
        XNAT_EXPERIMENTS_TAG,
        XNAT_SCANS_TAG,
        XNAT_RESOURCES_TAG,
        XNAT_ASSESSORS_TAG,
        XNAT_PREARCHIVE_PATH_TAG,
        XNAT_SHARING_TAG,
        XNAT_FILE_TAG
    }

    MODALITY_TO_SCAN = {
        'MR': '{http://nrg.wustl.edu/xnat}MRScan',
        'CT': '{http://nrg.wustl.edu/xnat}CTScan',
        'US': '{http://nrg.wustl.edu/xnat}USScan',
        'PT': '{http://nrg.wustl.edu/xnat}PETScan'
    }

    NAMESPACES = {
        'xnat': 'http://nrg.wustl.edu/xnat',
        'prov': 'http://www.nbirn.net/prov',
        'xdat': 'http://nrg.wustl.edu/xdat',
        'xs': 'http://www.w3.org/2001/XMLSchema',
        'proc': 'http://nrg.wustl.edu/proc',
        'fs': 'http://nrg.wustl.edu/fs',
        'icr': 'http://icr.ac.uk/icr'
    }

    def __init__(self, reporter):
        self._reporter = reporter
        self.tag_values = {}

    @staticmethod
    def xml_from_string(xml_string):
        """Convert XML string to ElementTree with XNAT namespaces"""

        root = XML(xml_string)
        for prefix, namespace in XmlCleaner.NAMESPACES.items():
            register_namespace(prefix, namespace)
        return root

    def make_project_names_unique(self, xml_root, disallowed_names,
                                  disallowed_ids):
        """
        Update project XML tags and attributes to ensure unique values

        @param xml_root: ElementTree root of the XML to remap
        @param disallowed_names: names already in use by other projects
        @param disallowed_ids: secondary IDs already in use by other projects
        """

        # Get current values of secondary ID and name
        secondary_id = xml_root.attrib[self.ATTR_SECONDARY_PROJECT_ID]
        name = xml_root.find(self.XNAT_PROJECT_NAME_TAG, self.NAMESPACES).text

        # Find new values that are not already present on the server, by adding
        # a " copy x" to the name and ID string. We keep the index x the
        # same for both to avoid confusion
        new_id = secondary_id
        new_name = name
        index = 0
        while new_id in disallowed_ids or new_name in disallowed_names:
            index += 1
            new_id = secondary_id + ' copy {}'.format(index)
            new_name = name + ' copy {}'.format(index)

        # Update the XML values
        xml_root.attrib[self.ATTR_SECONDARY_PROJECT_ID] = new_id
        for child in xml_root.findall(self.XNAT_PROJECT_NAME_TAG,
                                      self.NAMESPACES):
            child.text = new_name
        return xml_root

    def clean(self, xml_root, attr_to_tag_map, fix_scan_types):
        """
        Remove or XML remap tags that change between XNAT servers

        @param xml_root: ElementTree root of the XML to remap
        @param attr_to_tag_map: dict of attribute names in the root element to
        @param xnat_type: Enumeration describing the type of XNAT item
        @param fix_scan_types: set to True to correct ambiguous scan types
        @return:
        """
        # Delete all attributes that change on dest server
        for attr in attr_to_tag_map:
            if attr in xml_root.attrib:
                del xml_root.attrib[attr]

        if fix_scan_types:
            if xml_root.tag == self.XNAT_IMAGE_SCAN_DATA_TAG:
                new_tag = self.XNAT_OTHER_SCAN
                modalities = [mod.text for mod in
                              xml_root.findall(self.XNAT_MODALITY_TAG,
                                               self.NAMESPACES)]
                if len(modalities) == 1:
                    new_tag = self.MODALITY_TO_SCAN.get(modalities[0],
                                                        self.XNAT_OTHER_SCAN)
                self._reporter.warning('Modifying scan type {} to {}'.format(
                    self.XNAT_IMAGE_SCAN_DATA_TAG, new_tag))
                xml_root.tag = new_tag

        # Remove tags to delete
        for tag in self.TAGS_TO_DELETE:
            for child in xml_root.findall(tag, self.NAMESPACES):
                xml_root.remove(child)

        # Remap all tags that change on dest server
        # for tag, values in self.tag_values.items():
        for tag, tag_id in self.TAGS_TO_REMAP.items():
            for child in xml_root.findall(tag, self.NAMESPACES):
                tag_remap_dict = self.tag_values[tag_id]
                src_value = child.text
                if src_value not in tag_remap_dict:
                    raise ValueError('Tag {}: no new value for {} found'.format(
                                                                   tag,
                                                                   src_value))

                dst_value = tag_remap_dict[src_value]
                child.text = dst_value

        return xml_root

    def add_tag_remaps(self, src_xml_root, dst_xml_root, attr_to_tag_map):
        """
        Update the remapping dictionary to add add before and after values
        for the tags in the map
        @param src_xml_root:
        @param dst_xml_root:
        @param attr_to_tag_map:
        """
        for attr, global_attr_name in attr_to_tag_map.items():
            if attr in src_xml_root.attrib:
                attr_dict = self.tag_values.get(global_attr_name, {})
                src_value = src_xml_root.attrib[attr]
                dst_value = dst_xml_root.attrib[attr]
                attr_dict[src_value] = dst_value
                self.tag_values[global_attr_name] = attr_dict
