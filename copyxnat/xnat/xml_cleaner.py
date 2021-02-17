# coding=utf-8

"""Remove and remap XML tags for xml transfer between XNAT servers"""


from enum import Enum
from xml.etree.cElementTree import register_namespace, XML


class XnatType(Enum):
    """Describe the type of XNAT item so cleaning can be performed"""

    server = 'server'
    project = 'project'
    subject = 'subject'
    experiment = 'experiment'
    scan = 'scan'
    assessor = 'assessor'
    reconstruction = 'reconstruction'
    resource = 'resource'
    in_resource = 'in_resource'
    out_resource = 'out_resource'
    file = 'file'


class XmlCleaner:
    """Remove and remap XML tags for xml transfer between XNAT servers"""

    XNAT_MODALITY_TAG = '{http://nrg.wustl.edu/xnat}modality'
    XNAT_PROJECT_NAME_TAG = '{http://nrg.wustl.edu/xnat}name'

    ATTR_SECONDARY_PROJECT_ID = 'secondary_ID'

    XNAT_IMAGE_SCAN_DATA_TAG = '{http://nrg.wustl.edu/xnat}imageScanData'
    XNAT_OTHER_SCAN = 'xnat:OtherDicomScan'

    XNAT_FILE_TAG = '{http://nrg.wustl.edu/xnat}file'

    TAGS_TO_REMAP = {
        '{http://icr.ac.uk/icr}subjectID': XnatType.subject,
        '{http://nrg.wustl.edu/xnat}subject_ID': XnatType.subject,
        '{http://nrg.wustl.edu/xnat}image_session_ID': XnatType.experiment,
        '{http://nrg.wustl.edu/xnat}imageSession_ID': XnatType.experiment,
        '{http://nrg.wustl.edu/xnat}session_id': XnatType.experiment,
        '{http://nrg.wustl.edu/xnat}scanID': XnatType.scan,
        '{http://nrg.wustl.edu/xnat}imageScan_ID': XnatType.scan
    }

    ATTRS_TO_DELETE = {
        'ID',
        'project'
    }

    TAGS_TO_DELETE = {
        '{http://nrg.wustl.edu/xnat}out',
        '{http://nrg.wustl.edu/xnat}experiments',
        '{http://nrg.wustl.edu/xnat}scans',
        '{http://nrg.wustl.edu/xnat}resources',
        '{http://nrg.wustl.edu/xnat}assessors',
        '{http://nrg.wustl.edu/xnat}prearchivePath',
        '{http://nrg.wustl.edu/xnat}sharing'
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
        self.id_maps = {}

    @staticmethod
    def xml_from_string(xml_string):
        """Convert XML string to ElementTree with XNAT namespaces"""

        root = XML(xml_string)
        for prefix, namespace in XmlCleaner.NAMESPACES.items():
            register_namespace(prefix, namespace)
        return root

    def make_project_names_unique(self, xml_root, disallowed_ids):
        """
        Update project XML tags and attributes to ensure unique values

        @param xml_root: ElementTree root of the XML to remap
        @param disallowed_ids: names and secondary IDs in use by other projects
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
        while new_id in disallowed_ids or new_name in disallowed_ids:
            index += 1
            new_id = secondary_id + ' copy {}'.format(index)
            new_name = name + ' copy {}'.format(index)

        # Update the XML values
        xml_root.attrib[self.ATTR_SECONDARY_PROJECT_ID] = new_id
        for child in xml_root.findall(self.XNAT_PROJECT_NAME_TAG,
                                      self.NAMESPACES):
            child.text = new_name
        return xml_root

    # pylint: disable=too-many-branches
    def clean(self, xml_root, fix_scan_types, src_path, dst_path,
              remove_files=True):
        """
        Remove or XML remap tags that change between XNAT servers

        @param xml_root: ElementTree root of the XML to remap
        @param src_path: Archive path on source server
        @param dst_path: Archive path on destination server
        @param fix_scan_types: set to True to correct ambiguous scan types
        @param remove_files: set to True to remove file tags. Only set to False
        if the files and file catalogs are already in place on the destination
        server at the correct locations
        @return:
        """

        # Delete all attributes that change on dest server
        for attr in self.ATTRS_TO_DELETE:
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

        for tag, xnat_id_type in self.TAGS_TO_REMAP.items():
            for child in xml_root.findall(tag, self.NAMESPACES):
                tag_remap_dict = self.id_maps[xnat_id_type]
                src_value = child.text
                if src_value not in tag_remap_dict:
                    raise ValueError('Tag {}: no new value for {} found'.format(
                                                                   tag,
                                                                   src_value))

                dst_value = tag_remap_dict[src_value]
                child.text = dst_value

        # File tags should be removed (if uploading files) or their paths
        # rewritten (if files are already present in the correct locations)
        for child in xml_root.findall(self.XNAT_FILE_TAG, self.NAMESPACES):
            if remove_files:
                xml_root.remove(child)
            else:
                self._rewrite_uris(child, src_path, dst_path)

        return xml_root

    def _rewrite_uris(self, child, src_path, dst_path):
        if 'URI' in child.attrib:
            current = child.attrib['URI']
            if src_path not in current:
                raise RuntimeError('Unexpected server file path')
            self._reporter.log('Replacing path {}->{}'.format(src_path,
                                                              dst_path))
            new = current.replace('{}/'.format(src_path),
                                  '{}/'.format(dst_path), 1)
            child.attrib['URI'] = new

    def add_tag_remaps(self, xnat_type, id_src, id_dst):
        """
        Update the remapping dictionary to add add before and after ID values
        for the tags in the map
        @param xnat_type: Enumeration describing the type of XNAT item which the
        ID describes
        @param id_src: ID on the source server
        @param id_dst: ID on the destination server
        """

        id_map = self.id_maps.get(xnat_type, {})
        id_map[id_src] = id_dst
        self.id_maps[xnat_type] = id_map
