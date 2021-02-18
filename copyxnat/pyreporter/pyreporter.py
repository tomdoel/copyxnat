# coding=utf-8

"""Logging and user I/O"""
from copyxnat.pyreporter.console import Console
from copyxnat.pyreporter.console_logger import ConsoleLogger
from copyxnat.pyreporter.file_logger import FileLogger
from copyxnat.pyreporter.progress import Progress


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
        self._console = Console()
        self._progress = Progress(self._console)
        self._handlers = [
            FileLogger(data_dir=data_dir, verbose=verbose),
            ConsoleLogger(self._console, verbose=verbose)
        ]

    def error(self, message):
        """Error message to report to end user"""
        for handler in self._handlers:
            handler.error(message)

    def warning(self, message):
        """Warning message to report to end user"""
        for handler in self._handlers:
            handler.warning(message)

    def info(self, message):
        """Informational message which should be shown to the user"""
        for handler in self._handlers:
            handler.info(message)

    def output(self, message):
        """Print text to the console without a message prefix"""
        for handler in self._handlers:
            handler.output(message)

    def log(self, message):
        """Message which should always be written to the log but not shown
        to the end user unless debugging"""
        for handler in self._handlers:
            handler.log(message)

    def debug(self, message):
        """Message which can be ignored unless in verbose mode"""
        for handler in self._handlers:
            handler.debug(message)

    def start_progress(self, message, max_iter):
        """Display a progress bar"""
        self._progress.start_progress(message=message, max_iter=max_iter)

    def next_progress(self):
        """Update existing progress bar to next step"""
        self._progress.next_progress()

    def complete_progress(self):
        """Complete progress bar"""
        self._progress.complete_progress()
