# coding=utf-8

"""Logging to terminal"""


class TerminalLoggerCodes:
    """ANSI sequences for terminal output operations"""
    WARNING = '\33[93m'
    ERROR = '\33[91m'
    END = '\33[0m'
    CLEAR = '\33[K'


class ConsoleLogger:
    """Class for custom reporting actions"""
    _ERROR_PREFIX = 'ERROR'
    _WARN_PREFIX = 'WARNING'
    _INFO_PREFIX = 'INFO'
    _VERBOSE_PREFIX = 'DEBUG INFO'
    _SEPARATOR = ': '

    def __init__(self, console, verbose=False):
        self._console = console
        self.verbose = verbose

    def error(self, message):
        """Error message to report to end user"""
        self._output(prefix=self._ERROR_PREFIX, message=message,
                     colour=TerminalLoggerCodes.ERROR)

    def warning(self, message):
        """Warning message to report to end user"""
        self._output(prefix=self._WARN_PREFIX, message=message,
                     colour=TerminalLoggerCodes.WARNING)

    def info(self, message):
        """Informational message which should be shown to the user"""
        self._output(prefix=self._INFO_PREFIX, message=message)

    def output(self, message):
        """Print text to the console without a message prefix"""
        self._output(prefix=None, message=message)

    def log(self, message):
        """Message which should always be written to the log but not shown
        to the end user unless debugging"""
        if self.verbose:
            self._output(prefix=self._INFO_PREFIX, message=message)

    def debug(self, message):
        """Message which can be ignored unless in verbose mode"""
        if self.verbose:
            self._output(prefix=self._VERBOSE_PREFIX, message=message)

    def _output(self, prefix, message, colour=None):
        combined_prefix = prefix + self._SEPARATOR if prefix is not None \
            else ''
        if colour:
            start = colour
            end = TerminalLoggerCodes.END
        else:
            start = ''
            end = ''

        self._console.text(start + combined_prefix + message + end)
