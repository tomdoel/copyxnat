# coding=utf-8

"""Logging to terminal"""
from copyxnat.pyreporter.console import AnsiCodes


class ConsoleLogger:
    """Class for custom reporting actions"""
    _ERROR_PREFIX = '[ERROR]'
    _WARN_PREFIX = '[WARNING]'
    _INFO_PREFIX = '[INFO]'
    _VERBOSE_PREFIX = '[DEBUG INFO]'
    _SEPARATOR = ' '

    def __init__(self, console, verbose=False):
        self._console = console
        self.verbose = verbose

    def error(self, message):
        """Error message to report to end user"""
        self._output(prefix=self._ERROR_PREFIX, message=message,
                     color=AnsiCodes.RED)

    def warning(self, message):
        """Warning message to report to end user"""
        self._output(prefix=self._WARN_PREFIX, message=message,
                     color=AnsiCodes.YELLOW)

    def info(self, message):
        """Informational message which should be shown to the user"""
        self._output(prefix=self._INFO_PREFIX, message=message,
                     color=AnsiCodes.END)

    def output(self, message):
        """Print text to the console without a message prefix"""
        self._output(prefix=None, message=message,
                     color=AnsiCodes.END)

    def log(self, message):
        """Message which should always be written to the log but not shown
        to the end user unless debugging"""
        if self.verbose:
            self._output(prefix=self._INFO_PREFIX, message=message,
                         color=AnsiCodes.GREEN)

    def debug(self, message):
        """Message which can be ignored unless in verbose mode"""
        if self.verbose:
            self._output(prefix=self._VERBOSE_PREFIX, message=message,
                         color=AnsiCodes.GREEN)

    def _output(self, prefix, message, color=None):
        combined_prefix = prefix + self._SEPARATOR if prefix is not None \
            else ''
        self._console.text(combined_prefix + message, color)
