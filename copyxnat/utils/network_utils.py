# coding=utf-8
"""
Utilities
"""


def get_host(url):
    """Strinp the host prefix"""
    return url.replace('https://', '').replace('http://', '')
