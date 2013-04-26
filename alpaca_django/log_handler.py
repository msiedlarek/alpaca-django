import sys
import logging
import traceback

from alpaca_django.reporter import AlpacaDjangoReporter
from alpaca_django import settings


logger = logging.getLogger(__name__)


class AlpacaLogHandler(logging.Handler):

    def emit(self, record):
        try:
            if hasattr(record, 'request'):
                request = record.request
            else:
                request = None
            self._reporter.report(log_record=record, request=request)
        except Exception:
            logger.error(
                "Error handling record in Alpaca logger: %s" % '\n'.join(
                    traceback.format_exception_only(*sys.exc_info()[:2])
                ).strip()
            )

    @property
    def _reporter(self):
        if not hasattr(self, '__reporter'):
            self.__reporter = AlpacaDjangoReporter(
                settings.get_alpaca_monitor_host(),
                settings.get_alpaca_monitor_port()
            )
        return self.__reporter
