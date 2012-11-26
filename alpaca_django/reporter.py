import sys
import datetime
import logging
import threading
import traceback
import hmac
import hashlib
import pprint

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import requests

from alpaca_django import settings, utils
from alpaca_django.exception_reporter_filter import SafeExceptionReporterFilter

logger = logging.getLogger(__name__)

class AlpacaReporter(object):

    def __init__(self, endpoint_url, environment, api_key, ca_bundle=None):
        self.endpoint_url = endpoint_url
        self.environment = environment
        self.api_key = api_key
        self.ca_bundle = ca_bundle

    def send(self, report):
        try:
            pickling_protocol = settings.get_alpaca_pickling_protocol()
            pickled_report = pickle.dumps(report, pickling_protocol)
            signature = hmac.new(
                self.api_key,
                pickled_report,
                hashlib.sha256
            ).hexdigest()
            if self.ca_bundle is None:
                verify = True
            else:
                verify = self.ca_bundle
            response = requests.post(
                self.endpoint_url,
                data=pickled_report,
                headers={
                    'Content-Type': 'application/x-pickle.python',
                    'X-Requested-With': 'AlpacaReporter',
                    'Alpaca-Environment': self.environment,
                    'Alpaca-Signature': signature,
                },
                timeout=settings.get_alpaca_connection_timeout(),
                verify=verify
            )
            if response.status_code != 200:
                raise RuntimeError(
                    "Alpaca responded with HTTP %d: %s" % (
                        response.status_code,
                        response.content.strip()
                    )
                )
        except:
            logger.error(
                "Error while sending report to Alpaca: %s" % '\n'.join(
                    traceback.format_exception_only(*sys.exc_info()[:2])
                ).strip()
            )

    def send_asynchronously(self, report):
        threading.Thread(
            target=self.send,
            args=(report,),
        ).start()

class AlpacaDjangoReporter(AlpacaReporter):

    def __init__(self, *args, **kwargs):
        super(AlpacaDjangoReporter, self).__init__(*args, **kwargs)
        self._exception_reporter_filter = SafeExceptionReporterFilter()

    def report(self, log_record=None, request=None):
        try:
            if not settings.is_alpaca_enabled():
                return
            if (log_record is not None
                    and hasattr(log_record, 'exc_info')
                    and log_record.exc_info != (None, None, None)):
                exc_info = log_record.exc_info
            else:
                exc_info = sys.exc_info()
            if exc_info is not None and exc_info != (None, None, None):
                message = (
                    ''.join(
                        traceback.format_exception_only(*exc_info[:2])
                    ).strip()
                )
                stack_trace = utils.serialize_stack(
                    exc_info[2],
                    self._exception_reporter_filter
                )
                most_important_frame = None
                for frame in reversed(stack_trace):
                    if (settings.get_alpaca_project_path_fragment() in
                            frame['filename']):
                        most_important_frame = frame
                        break
                if most_important_frame is None:
                    most_important_frame = stack_trace[-1]
                problem_hash = hashlib.md5(
                    ':'.join((
                        str(exc_info[0]),
                        most_important_frame['filename'],
                        most_important_frame['function'],
                        most_important_frame['context']
                    ))
                ).hexdigest()
            elif log_record is not None:
                try:
                    if isinstance(log_record.msg, basestring):
                        message = log_record.msg % log_record.args
                    else:
                        message = pprint.pformat(log_record.msg)
                except Exception as exception:
                    message = "Formatting error: %s" % str(exception)
                pre_context_lineno, pre_context, context_line, post_context = (
                    utils.get_lines_from_file(
                        log_record.pathname,
                        log_record.lineno - 1,
                        7,
                        None,
                        log_record.module
                    )
                )
                if pre_context_lineno is not None:
                    stack_trace = [dict(
                        filename=log_record.pathname,
                        line_number=log_record.lineno,
                        function=log_record.funcName,
                        pre_context=pre_context,
                        context=context_line,
                        post_context=post_context,
                        variables=dict()
                    )]
                else:
                    stack_trace = []
                problem_hash = hashlib.md5(
                    ':'.join((
                        log_record.pathname,
                        log_record.funcName,
                        context_line
                    ))
                ).hexdigest()
            else:
                raise RuntimeError(
                    "Neither log record nor exception information was supplied."
                )
            report = {
                'hash': problem_hash,
                'date': datetime.datetime.utcnow().isoformat() + 'Z',
                'message': message,
                'stack_trace': stack_trace,
                'environment_data': {},
            }
            if request is not None:
                post_parameters = (
                    self._exception_reporter_filter.get_post_parameters(request)
                )
                request_headers = (
                    utils.serialize_object_dict(request.META.iteritems())
                )
                report['environment_data'].update({
                    "General": {
                        "Full URI": request.build_absolute_uri(),
                    },
                    "GET Parameters": request.GET.dict(),
                    "POST Parameters": post_parameters.dict(),
                    "Cookies": request.COOKIES,
                    "Request Headers": request_headers,
                })
            self.send_asynchronously(report)
        except Exception:
            logger.error(
                "Error while preparing report for Alpaca: %s" % '\n'.join(
                    traceback.format_exception_only(*sys.exc_info()[:2])
                ).strip()
            )
