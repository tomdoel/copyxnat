# coding=utf-8
"""
Utilities
"""


class UserError(Exception):
    """Exception that is within the user's control"""

    def __init__(self, user_friendly_message, cause=None):
        self.user_friendly_message = user_friendly_message
        self.cause = cause
        super(UserError, self).__init__(user_friendly_message)


def message_from_exception(exc):
    """Return exception name and content as a string"""

    text = '{e.__class__.__module__}.{e.__class__.__name__}: {e}'.format(e=exc)
    if isinstance(exc, UserError) and exc.cause:
        return text + ' caused by: ' + message_from_exception(exc.cause)
    else:
        return text

    return '{e.__class__.__module__}.{e.__class__.__name__}: {e}'.format(e=exc)
