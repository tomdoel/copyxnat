# coding=utf-8

"""Logging and user I/O"""
import logging
from os import makedirs
from os.path import join, exists


class PyReporterCodes:
    """ANSI sequences for terminal output operations"""
    WARNING = '\33[93m'
    ERROR = '\33[91m'
    END = '\33[0m'
    CLEAR = '\33[K'


class PyReporterError(RuntimeError):
    """Non-recoverable error"""


class ProjectFailure(PyReporterError):
    """An error which is non-recoverable for a project but which allows other
    project processing to continue"""


class PyProgress:
    """Class for displaying a progress bar"""

    def __init__(self):
        self._iter_num = None
        self._max_iter = None
        self._message = None
        self._last_progress_text = None

    def start_progress(self, message, max_iter):
        """
        Display a progress bar
        @param message: message to display in the progress bar
        @param max_iter: total number of iterations
        """
        self._max_iter = max_iter
        self._iter_num = 0
        self._message = message
        self.next_progress()

    def next_progress(self):
        """Update existing progress bar to next step"""
        if self._iter_num is not None and self._max_iter is not None:
            width = 50
            num_bars = int(width*self._iter_num//self._max_iter) if \
                self._max_iter >= 1 else width
            bar_str = '█'*num_bars + '-'*(width - num_bars)
            progress_text = '\r{} |{}| {:3d}/{} done'.format(self._message,
                                                             bar_str,
                                                             self._iter_num,
                                                             self._max_iter
                                                             )
            self._iter_num = self._iter_num + 1
        else:
            progress_text = self._message

        print('\r' + progress_text, end='', flush=True)
        self._print_progress(progress_text)

    def complete_progress(self):
        """Complete progress bar"""
        self._iter_num = self._max_iter
        self.next_progress()
        print()
        self._message = None
        self._last_progress_text = None

    def reprint_progress(self):
        """Re-print progress after text output"""
        if self._last_progress_text:
            print(self._last_progress_text, end='\r', flush=True)

    def _print_progress(self, progress_text):
        self._last_progress_text = progress_text
        self.reprint_progress()


class PyReporter:
    """Class for custom reporting actions"""
    _ERROR_PREFIX = 'ERROR'
    _WARN_PREFIX = 'WARNING'
    _INFO_PREFIX = 'INFO'
    _VERBOSE_PREFIX = 'VERBOSE INFO (verbose)'
    _SEPARATOR = ': '

    def __init__(self, data_dir, verbose=False):
        self.verbose = verbose
        self._handlers = [self._print_handler]
        self._setup_logging(data_dir=data_dir, verbose=verbose)
        self._progress = PyProgress()

    def error(self, message):
        """Error message to report to end user"""
        logging.error(message)
        self._output(prefix=self._ERROR_PREFIX, message=message,
                     colour=PyReporterCodes.ERROR)

    def warning(self, message):
        """Warning message to report to end user"""
        logging.warning(message)
        self._output(prefix=self._WARN_PREFIX, message=message,
                     colour=PyReporterCodes.WARNING)

    def info(self, message):
        """Informational message which should be shown to the user"""
        logging.info(message)
        self._output(prefix=self._INFO_PREFIX, message=message)

    def output(self, message):
        """Print text to the console without a message prefix"""
        logging.info(message)
        self._output(prefix=None, message=message)

    def log(self, message):
        """Message which should always be written to the log but not shown
        to the end user unless debugging"""
        logging.info(message)
        if self.verbose:
            self._output(prefix=self._INFO_PREFIX, message=message)

    def debug(self, message):
        """Message which can be ignored unless in verbose mode
        """
        logging.debug(message)
        if self.verbose:
            self._output(prefix=self._VERBOSE_PREFIX, message=message)

    def start_progress(self, message, max_iter):
        """Display a progress bar

        @param message: message to display in the progress bar
        @param max_iter: total number of iterations
        """
        self._progress.start_progress(message=message, max_iter=max_iter)

    def next_progress(self):
        """Update existing progress bar to next step"""

        self._progress.next_progress()

    def complete_progress(self):
        """Complete progress bar"""
        self._progress.complete_progress()

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

    def _output(self, prefix, message, colour=None):
        combined_prefix = prefix + self._SEPARATOR if prefix is not None \
            else ''
        if colour:
            colour_prefix = colour
            colour_suffix = PyReporterCodes.END
        else:
            colour_prefix = ''
            colour_suffix = ''

        self._print_handler(colour_prefix + combined_prefix + message +
                            colour_suffix)

    def _print_handler(self, message):
        print(message + PyReporterCodes.CLEAR)
        self._progress.reprint_progress()
