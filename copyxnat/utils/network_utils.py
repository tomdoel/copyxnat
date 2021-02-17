# coding=utf-8
"""
Utilities
"""


def get_host(url):
    return url.replace('https://', '').replace('http://', '')
