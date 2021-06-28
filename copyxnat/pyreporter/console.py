# coding=utf-8

"""Output text to the console"""
import sys

import six


class AnsiCodes:
    """ANSI sequences for console output operations"""
    YELLOW = '\33[93m'
    RED = '\33[91m'
    GREEN = '\33[92m'
    CYAN = '\33[96m'
    END = '\33[0m'
    CLEAR = '\33[K'


class Console:
    """Output text to the console"""

    def __init__(self):
        self._last_sticky_text = None

    def sticky_text(self, text):
        """Print sticky text, which will stay as final output line even if
        other text is printed"""
        self._last_sticky_text = text
        self._reprint_sticky()

    def end_sticky(self):
        """Clear sticky text, but keep previous sticky text in console"""
        if self._last_sticky_text:
            six.print_()
        self._last_sticky_text = None

    def text(self, message, color=None):
        """Output text without interfering with sticky text"""
        if color:
            text = color + message + AnsiCodes.END
        else:
            text = message
        six.print_('\r' + text + AnsiCodes.CLEAR)
        self._reprint_sticky()

    def _reprint_sticky(self):
        """Re-print sticky text"""
        if self._last_sticky_text:
            text = AnsiCodes.CYAN + self._last_sticky_text + AnsiCodes.END
            six.print_('\r' + text, end='')
            sys.stdout.flush()
