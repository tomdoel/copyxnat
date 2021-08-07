# coding=utf-8
"""
Utilities
"""


def get_host(url):
    """Strip the host prefix"""
    return url.replace('https://', '').replace('http://', '')
