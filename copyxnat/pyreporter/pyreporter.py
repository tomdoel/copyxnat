# coding=utf-8

"""Logging and user I/O"""


class PyReporter(object):
    """Class for custom reporting actions"""
    _WARN_PREFIX = 'WARNING'
    _INFO_PREFIX = 'INFO'
    _VERBOSE_PREFIX = 'VERBOSE INFO (verbose)'
    _SEPARATOR = ': '

    def __init__(self, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose
        self._handlers = [self._print_handler]
        self._iter_num = None
        self._max_iter = None
        self._message = None

    def info(self, message):
        """Status message to show to end user"""
        self._output(prefix=self._INFO_PREFIX, message=message)

    def message(self, message):
        """A message to the user"""
        self._output(prefix='', message=message)

    def warning(self, message):
        """Warning message to report to end user"""
        self._output(prefix=self._WARN_PREFIX, message=message)

    def log(self, message):
        """Message for logs but need not report to end user"""
        self._output(prefix=self._INFO_PREFIX, message=message)

    def verbose_log(self, message):
        """Message for logs only in verbose mode"""
        if self.verbose:
            self._output(prefix=self._VERBOSE_PREFIX, message=message)

    def _output(self, prefix, message):
        for handler in self._handlers:
            handler(prefix + self._SEPARATOR + message)

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
        """
        Display a progress bar
        """
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

        print(progress_text, end='\r', flush=True)

    def complete_progress(self):
        """
        Complete a progress bar
        """
        self._iter_num = self._max_iter
        self.next_progress()
        print()
        self._message = None

    @staticmethod
    def _print_handler(message):
        print(message)
