# coding=utf-8

"""Logging and user I/O"""
from copyxnat.pyreporter.file_logger import FileLogger
from copyxnat.pyreporter.progress import Progress


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
        self._progress = Progress()
        self._file_logger = FileLogger(data_dir=data_dir, verbose=verbose)

    def error(self, message):
        """Error message to report to end user"""
        self._file_logger.error(message)
        self._output(prefix=self._ERROR_PREFIX, message=message,
                     colour=PyReporterCodes.ERROR)

    def warning(self, message):
        """Warning message to report to end user"""
        self._file_logger.warning(message)
        self._output(prefix=self._WARN_PREFIX, message=message,
                     colour=PyReporterCodes.WARNING)

    def info(self, message):
        """Informational message which should be shown to the user"""
        self._file_logger.info(message)
        self._output(prefix=self._INFO_PREFIX, message=message)

    def output(self, message):
        """Print text to the console without a message prefix"""
        self._file_logger.output(message)
        self._output(prefix=None, message=message)

    def log(self, message):
        """Message which should always be written to the log but not shown
        to the end user unless debugging"""
        self._file_logger.log(message)
        if self.verbose:
            self._output(prefix=self._INFO_PREFIX, message=message)

    def debug(self, message):
        """Message which can be ignored unless in verbose mode"""
        self._file_logger.debug(message)
        if self.verbose:
            self._output(prefix=self._VERBOSE_PREFIX, message=message)

    def start_progress(self, message, max_iter):
        """Display a progress bar"""
        self._progress.start_progress(message=message, max_iter=max_iter)

    def next_progress(self):
        """Update existing progress bar to next step"""
        self._progress.next_progress()

    def complete_progress(self):
        """Complete progress bar"""
        self._progress.complete_progress()

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
