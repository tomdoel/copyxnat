# coding=utf-8

"""Class for logging to a file"""

import logging
from datetime import datetime
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

        log_file = self._get_unique_filename(log_dir)

        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(logging.DEBUG if verbose else logging.INFO)

        handler = logging.FileHandler(log_file, mode='a')
        handler.setFormatter(
            logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        self._logger.addHandler(handler)

    @staticmethod
    def _get_unique_filename(log_dir):
        now_string = datetime.now().strftime('%d_%m_%Y_%H_%M_%S_')
        log_file = join(log_dir, 'copyxnat_{}.log'.format(now_string))
        suffix_index = 0
        while isfile(log_file):
            suffix_index += 1
            log_file = join(log_dir, 'copyxnat_{}_{}.log'.format(now_string,
                                                                suffix_index))
        return log_file
