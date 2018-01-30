import sys, traceback

from django.views.debug import ExceptionReporter

__all__ = ["get_html_traceback"]

def get_html_traceback(request=None):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    message = u'%s : %s' % ( exc_type, exc_value )
    reporter = ExceptionReporter(request, exc_type, exc_value, exc_traceback, is_email=False)
    html_message = reporter.get_traceback_html()
    return message, html_message