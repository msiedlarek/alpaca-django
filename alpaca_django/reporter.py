import sys
import datetime
import logging
import traceback
import hashlib
import pprint
import threading

import msgpack
import zmq

from alpaca_django import settings, utils
from alpaca_django.compat import _text, _string_types
from alpaca_django.exception_reporter_filter import SafeExceptionReporterFilter


logger = logging.getLogger(__name__)


class AlpacaReporter(object):

    _subscription_confirmation_timeout = 5000 # milliseconds
    _message_encoding = 'utf-8'
    _threadlocal = threading.local()

    class ConnectionError(Exception):
        pass

    def __init__(self, monitor_host, monitor_port):
        self._monitor_address = 'tcp://{host}:{port}'.format(
            host=monitor_host,
            port=monitor_port
        )
        if not hasattr(self._threadlocal, 'sockets'):
            self._threadlocal.sockets = {}

    def send(self, report):
        try:
            environment = _text(settings.get_alpaca_environment()).encode(
                'utf-8'
            ) + bytes(bytearray([0]))
            report = msgpack.packb(report, encoding=self._message_encoding)
            self._get_socket().send_multipart((environment, report))
        except:
            logger.error(
                "Error while sending report to Alpaca: %s" % '\n'.join(
                    traceback.format_exception_only(*sys.exc_info()[:2])
                ).strip()
            )

    def _get_context(self):
        return zmq.Context.instance()

    def _get_socket(self):
        if not self._monitor_address in self._threadlocal.sockets:
            # Using XPUB socket to receive subscription messages.
            socket = self._get_context().socket(zmq.XPUB)
            logger.info(
                "Connecting to Alpaca monitor at {address}...".format(
                    address=self._monitor_address
                )
            )
            socket.connect(self._monitor_address)
            # Wait for a subscription message, preventing the slow joiner
            # syndrome.
            event = socket.poll(
                timeout=self._subscription_confirmation_timeout
            )
            if event == 0:
                raise self.ConnectionError(
                    "Timeout while waiting for a subscription message."
                )
            logger.info(
                "Connected to Alpaca monitor at {address}.".format(
                    address=self._monitor_address
                )
            )
            self._threadlocal.sockets[self._monitor_address] = socket
        return self._threadlocal.sockets[self._monitor_address]


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
                    _text('').join(
                        map(
                            _text,
                            traceback.format_exception_only(*exc_info[:2])
                        )
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
                    _text(':').join((
                        _text(exc_info[0]),
                        _text(most_important_frame['filename']),
                        _text(most_important_frame['function']),
                        _text(most_important_frame['context']),
                    )).encode(encoding='utf-8', errors='replace')
                ).hexdigest()
            elif log_record is not None:
                try:
                    if isinstance(log_record.msg, _string_types):
                        message = log_record.msg % log_record.args
                    else:
                        message = pprint.pformat(log_record.msg)
                except Exception as exception:
                    message = _text("Formatting error: {}").format(exception)
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
                    _text(':').join((
                        _text(log_record.pathname),
                        _text(log_record.funcName),
                        _text(context_line)
                    ))
                ).hexdigest()
            else:
                raise RuntimeError(
                    "Neither log record nor exception information was"
                    " supplied."
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
                    self._exception_reporter_filter.get_post_parameters(
                        request
                    )
                )
                request_headers = (
                    utils.serialize_object_dict(request.META.items())
                )
                report['environment_data'].update({
                    _text("General"): {
                        _text("Full URI"): request.build_absolute_uri(),
                    },
                    _text("GET Parameters"): request.GET.dict(),
                    _text("POST Parameters"): post_parameters.dict(),
                    _text("Cookies"): request.COOKIES,
                    _text("Request Headers"): request_headers,
                })
            self.send(report)
        except Exception:
            logger.error(
                "Error while preparing report for Alpaca: %s" % '\n'.join(
                    traceback.format_exception_only(*sys.exc_info()[:2])
                ).strip()
            )
