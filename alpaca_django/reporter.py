import sys
import datetime
import logging
import traceback
import hashlib
import pprint
import threading
import contextlib

import msgpack
import zmq

from alpaca_django import settings, utils
from alpaca_django.compat import _text, _string_types, Queue
from alpaca_django.exception_reporter_filter import SafeExceptionReporterFilter


logger = logging.getLogger(__name__)


class AlpacaReporter(object):

    _subscription_confirmation_timeout = 5000 # milliseconds
    _waiting_for_free_socket_timeout = 5 # seconds
    _message_encoding = 'utf-8'

    _socket_pools = {}
    _socket_pools_lock = threading.Lock()

    class ConnectionError(Exception):
        pass

    def __init__(self, monitor_host, monitor_port):
        self._monitor_address = 'tcp://{host}:{port}'.format(
            host=monitor_host,
            port=monitor_port
        )

    def send(self, report):
        try:
            environment = _text(settings.get_alpaca_environment()).encode(
                'utf-8'
            ) + bytes(bytearray([0]))
            report = msgpack.packb(report, encoding=self._message_encoding)
            with self._socket_for(self._monitor_address) as socket:
                socket.send_multipart((environment, report))
        except:
            logger.error(
                "Error while sending report to Alpaca: %s" % '\n'.join(
                    traceback.format_exception_only(*sys.exc_info()[:2])
                ).strip()
            )

    @classmethod
    @contextlib.contextmanager
    def _socket_for(cls, address):
        if address not in cls._socket_pools:
            with cls._socket_pools_lock:
                cls._socket_pools[address] = Queue()
                logger.info(
                    "Opening {connections} connections to Alpaca monitor at"
                    " {address}...".format(
                        connections=settings.get_alpaca_connection_pool_size(),
                        address=address
                    )
                )
                for i in range(settings.get_alpaca_connection_pool_size()):
                    cls._socket_pools[address].put(
                        cls._create_socket(address)
                    )
        socket = cls._socket_pools[address].get(
            True,
            cls._waiting_for_free_socket_timeout
        )
        yield socket
        cls._socket_pools[address].put(socket)

    @classmethod
    def _get_context(cls):
        return zmq.Context.instance()

    @classmethod
    def _create_socket(cls, address):
        # Using XPUB socket to receive subscription messages.
        socket = cls._get_context().socket(zmq.XPUB)
        socket.connect(address)
        # Wait for a subscription message, preventing the slow joiner
        # syndrome.
        event = socket.poll(
            timeout=cls._subscription_confirmation_timeout
        )
        if event == 0:
            raise cls.ConnectionError(
                "Timeout while waiting for a subscription message."
            )
        return socket


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
                        _text("Command line arguments"): ' '.join(sys.argv),
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
