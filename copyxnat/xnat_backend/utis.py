# coding=utf-8

"""Utility functions"""


class Utils(object):
    """Utility functions"""

    @staticmethod
    def combine_dicts(dict_1, dict_2):
        """Creates a new dictionary which is the union of two dictionaries with
        a shallow copy of the elements"""
        combined = {}
        for key, value in (dict_1 or {}).items():
            combined[key] = value
        for key, value in (dict_2 or {}).items():
            combined[key] = value
        return combined
