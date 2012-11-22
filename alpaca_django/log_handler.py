import sys
import logging
import traceback

from alpaca_django.reporter import AlpacaDjangoReporter
from alpaca_django import settings

logger = logging.getLogger(__name__)

class AlpacaLogHandler(logging.Handler):

    def emit(self, record):
        try:
            reporter = AlpacaDjangoReporter(
                settings.get_alpaca_endpoint_url(),
                settings.get_alpaca_environment(),
                settings.get_alpaca_api_key(),
                ca_bundle=settings.get_alpaca_ca_bundle()
            )
            if hasattr(record, 'request'):
                request = record.request
            else:
                request = None
            reporter.report(log_record=record, request=request)
        except Exception:
            logger.error(
                "Error handling record in Alpaca logger: %s" % '\n'.join(
                    traceback.format_exception_only(*sys.exc_info()[:2])
                ).strip()
            )
