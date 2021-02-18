# coding=utf-8

"""Class for logging to a file"""

import logging
from os import makedirs
from os.path import join, exists


class FileLogger:
    """Class for logging to a file"""

    def __init__(self, data_dir, verbose):
        self._setup_logging(data_dir=data_dir, verbose=verbose)

    @staticmethod
    def error(message):
        """Error message"""
        logging.error(message)

    @staticmethod
    def warning(message):
        """Warning message"""
        logging.warning(message)

    @staticmethod
    def info(message):
        """Informational message"""
        logging.info(message)

    @staticmethod
    def output(message):
        """Information that on screen would be shown without message prefix"""
        logging.info(message)

    @staticmethod
    def log(message):
        """Message which should always be written to the log but not shown
        to the end user unless debugging"""
        logging.info(message)

    @staticmethod
    def debug(message):
        """Message which can be ignored unless in verbose mode"""
        logging.debug(message)

    @staticmethod
    def _setup_logging(data_dir, verbose):
        log_dir = join(data_dir, 'logs')
        if not exists(log_dir):
            makedirs(log_dir)
        log_file = join(log_dir, 'copyxnat.log')

        level = logging.DEBUG if verbose else logging.INFO

        # PyCharm inspection: https://youtrack.jetbrains.com/issue/PY-39762
        # noinspection PyArgumentList
        logging.basicConfig(
            filename=log_file,
            encoding='utf-8',
            format='%(asctime)s %(message)s',
            level=level
        )
