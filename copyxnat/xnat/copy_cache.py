# coding=utf-8

"""Abstraction of disk cache used to store XNAT files"""

import os
from os.path import expanduser
from xml.etree import cElementTree


class CacheBox(object):
    """Controls caches on disk"""
    def __init__(self, root_path=None):
        self.root_path = root_path or os.path.join(expanduser("~"), 'copyxnat')

    def new_cache(self, cache_type):
        """Create a new cache within the main cache"""
        return CopyCache(cache_type=cache_type,
                         root_path=self.root_path,
                         name='current')


class CopyCache(object):
    """Abstraction of disk cache used to store XNAT files"""

    def __init__(self, cache_type, root_path, name=None,
                 parent_rel_path='', read_only=False,
                 cache_level=0,
                 base_name=None):
        self._read_only = read_only
        self.root_path = root_path
        if name is None:
            name_i = 1
            name = str(name_i)
            rel_path = os.path.join(parent_rel_path, cache_type, name)
            full_path = os.path.join(self.root_path, rel_path)
            while os.path.exists(full_path):
                name_i += 1
                name = str(name_i)
                rel_path = os.path.join(parent_rel_path, cache_type, name)
                full_path = os.path.join(self.root_path, rel_path)
        else:
            rel_path = os.path.join(parent_rel_path, cache_type, name)

        self.rel_path = rel_path
        self.cache_level = cache_level
        if base_name:
            self.full_name = base_name + "/" + name
        else:
            self.full_name = name

    def sub_cache(self, cache_type, name):
        """
        Create a child cache representing some level of the XNAT hierarchy
        @param cache_type: The type of XNAT item
        @param name: label for this cache
        @return:a new :class:`CopyCache` for this XNAT level
        """
        return CopyCache(cache_type=cache_type,
                         name=name,
                         root_path=self.root_path,
                         parent_rel_path=self.rel_path,
                         read_only=self._read_only,
                         cache_level=self.cache_level + 1,
                         base_name=self.full_name)

    def write_xml(self, xml_root, filename):
        """Write XML to a file in this cache"""
        full_path = self.make_output_path()
        full_xml_path = os.path.join(full_path, filename)
        if not self._read_only:
            cElementTree.ElementTree(xml_root).write(full_xml_path)
        return full_xml_path

    def make_output_path(self):
        """Write to file to this cache"""
        full_path = self.full_path()
        if self._read_only:
            print('Not making directory {} due to read-only mode'.
                  format(full_path))
        else:
            if not os.path.exists(full_path):
                os.makedirs(full_path)
        return full_path

    def full_path(self):
        """Return absolute path to this cache"""
        return os.path.join(self.root_path, self.rel_path)
