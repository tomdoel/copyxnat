# coding=utf-8

"""Class for displaying a progress bar"""


class Progress:
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
