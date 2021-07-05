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

    @staticmethod
    def optional_params(params):
        """Creates a new dictionary by making a shallow copy of an existing
        dictionary, but exclude entries from the final dictionary if their
        value is None"""
        optional_params = {}
        for key, value in params.items():
            if value is not None:
                optional_params[key] = value
        return optional_params
