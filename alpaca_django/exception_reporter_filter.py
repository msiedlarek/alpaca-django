from django.views.debug import SafeExceptionReporterFilter

from alpaca_django.compat import _text


class ForcedSafeExceptionReporterFilter(SafeExceptionReporterFilter):

    def is_active(self, request):
        return True

    def get_traceback_frame_variables(self, *args, **kwargs):
        variables = super(
            ForcedSafeExceptionReporterFilter,
            self
        ).get_traceback_frame_variables(*args, **kwargs)
        return [
            (
                key,
                (
                    value
                    if (
                        not key.lower().startswith('password')
                        and not key.lower().startswith('passwd')
                    ) else
                    _text('*****')
                )
            ) for key, value in variables
        ]


exception_reporter_filter = ForcedSafeExceptionReporterFilter()
