# coding=utf-8

"""Class for logging to a file"""

import logging
from logging.handlers import RotatingFileHandler
from os import makedirs
from os.path import join, exists, isfile


class FileLogger:
    """Class for logging to a file"""

    def __init__(self, data_dir, verbose):
        self.name = 'copyxnat'
        self._setup_logging(data_dir=data_dir, verbose=verbose)

    def error(self, message):
        """Error message"""
        self._logger.error(message)

    def warning(self, message):
        """Warning message"""
        self._logger.warning(message)

    def info(self, message):
        """Informational message"""
        self._logger.info(message)

    def output(self, message):
        """Information that on screen would be shown without message prefix"""
        self._logger.info(message)

    def log(self, message):
        """Message which should always be written to the log but not shown
        to the end user unless debugging"""
        self._logger.info(message)

    def debug(self, message):
        """Message which can be ignored unless in verbose mode"""
        self._logger.debug(message)

    def _setup_logging(self, data_dir, verbose):
        log_dir = join(data_dir, 'logs')
        if not exists(log_dir):
            makedirs(log_dir)
        log_file = join(log_dir, 'copyxnat.log')
        log_file_exists = isfile(log_file)

        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(logging.DEBUG if verbose else logging.INFO)

        handler = RotatingFileHandler(log_file, mode='a', backupCount=20,
                                      delay=True)
        handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        self._logger.addHandler(handler)

        if log_file_exists:
            handler.doRollover()
