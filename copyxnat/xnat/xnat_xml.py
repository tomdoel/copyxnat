# coding=utf-8

"""Remove and remap XML tags for xml transfer between XNAT servers"""


from xml.etree.cElementTree import register_namespace, XML


XNAT_NS = {
    'xnat': 'http://nrg.wustl.edu/xnat',
    'prov': 'http://www.nbirn.net/prov',
    'xdat': 'http://nrg.wustl.edu/xdat',
    'xs': 'http://www.w3.org/2001/XMLSchema',
    'proc': 'http://nrg.wustl.edu/proc',
    'fs': 'http://nrg.wustl.edu/fs',
    'icr': 'http://icr.ac.uk/icr'
}


def xml_from_string(xml_string):
    """Convert XML string to ElementTree with XNAT namespaces"""

    root = XML(xml_string)
    for prefix, namespace in XNAT_NS.items():
        register_namespace(prefix, namespace)
    return root
