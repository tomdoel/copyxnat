# coding=utf-8

"""Encapsulates parameters used to access an XNAT server"""


class XnatServerParams:
    """Encapsulates parameters used to access an XNAT server"""

    def __init__(self, host, user, pwd, rsync_user=None, insecure=False):
        if '://' not in host:
            host = 'https://' + host
        self.host = host
        self.user = user
        self.pwd = pwd
        self.rsync_user = rsync_user
        self.insecure = insecure
