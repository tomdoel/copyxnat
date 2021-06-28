# coding=utf-8
"""
Execute rsync command
"""
import getpass
import subprocess

import six

from copyxnat.pyreporter.pyreporter import ProjectFailure
from copyxnat.utils.network_utils import get_host


class ProjectRsync:
    """Sync datafiles between XNAT servers"""

    def __init__(self, cache, src_params, dst_params, dry_run, reporter):
        self.reporter = reporter
        self.dry_run = dry_run
        self.src_user = self._get_user(src_params)
        self.dst_user = self._get_user(dst_params)
        self.src_host = get_host(src_params.host)
        self.dst_host = get_host(dst_params.host)
        self.cache = cache.sub_cache('cache', 'rsync')

    def rsync_project_data(self, src_project_path, dst_project_path, src_label):
        """Rsync data using calling server cache"""

        project_cache = self.cache.sub_cache('projects', src_label)
        project_cache.clear()
        cache_path = project_cache.make_output_path()

        src_string = self._server_string(
            user=self.src_user,
            host=self.src_host,
            project_path=src_project_path
        )
        dst_string = self._server_string(
            user=self.dst_user,
            host=self.dst_host,
            project_path=dst_project_path
        )
        self._rsync_files(src_string + '/', cache_path)
        self._rsync_files(cache_path + '/', dst_string)

    def _get_user(self, params):
        user = params.rsync_user
        if not user:
            user = getpass.getuser()
        if not user:
            self.reporter.error('No username specified for rsync')
            raise RuntimeError('No username specified for rsync')
        return user

    @staticmethod
    def _server_string(user, host, project_path):
        return "{}@{}:/{}".format(user, host, project_path).rstrip('/')

    def _rsync_files(self, src, dst):
        command_to_run = [
            "rsync",
            "-azP",
            "--ignore-existing",
            "--exclude=*.log",
            "--exclude=.*",
            "--exclude=*.json",
            "--stats",
            "--progress",
            src,
            dst
        ]

        string_command = " ".join(command_to_run)

        self.reporter.log('Running rsync command: {}'.format(string_command))
        if self.dry_run:
            self.reporter.info('DRY RUN: will not run {}'.
                               format(string_command))
        else:
            try:
                subprocess.check_output(command_to_run)
            except subprocess.CalledProcessError as exc:
                error_message = 'An error occurred running the rsync command ' \
                                '{}. The error was :{}'.format(string_command,
                                                               str(exc))
                self.reporter.error(error_message)
                six.raise_from(ProjectFailure(error_message), exc)
