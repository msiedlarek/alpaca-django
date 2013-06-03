import sys


python_major_version = sys.version_info[0]


if python_major_version == 3:
    _string_types = (
        str,
    )
else:
    _string_types = (
        str,
        unicode,
    )


if python_major_version == 3:
    def _text(value, encoding='utf-8', errors='strict'):
        if isinstance(value, str):
            return value
        if isinstance(value, (bytearray, bytes)):
            return value.decode(encoding=encoding, errors=errors)
        return str(value)
else:
    def _text(value, encoding='utf-8', errors='strict'):  # flake8: noqa
        if isinstance(value, unicode):
            return value
        if isinstance(value, basestring):
            return value.decode(encoding=encoding, errors=errors)
        return unicode(value)


if python_major_version == 3:
    from queue import Queue
else:
    from Queue import Queue
