import re
import pprint

def get_lines_from_file(filename, lineno, context_lines, loader=None,
                         module_name=None):
    """
    Returns context_lines before and after lineno from file.
    Returns (pre_context_lineno, pre_context, context_line, post_context).
    """
    source = None
    if loader is not None and hasattr(loader, "get_source"):
        source = loader.get_source(module_name)
        if source is not None:
            source = source.splitlines()
    if source is None:
        try:
            with open(filename, 'rb') as fp:
                source = fp.readlines()
        except (OSError, IOError):
            pass
    if source is None:
        return None, [], None, []
    encoding = 'ascii'
    for line in source[:2]:
        # File coding may be specified. Match pattern from PEP-263
        # (http://www.python.org/dev/peps/pep-0263/)
        match = re.search(r'coding[:=]\s*([-\w.]+)', line)
        if match:
            encoding = match.group(1)
            break
    source = [unicode(sline, encoding, 'replace') for sline in source]
    lower_bound = max(0, lineno - context_lines)
    upper_bound = lineno + context_lines
    pre_context = [line.strip('\n') for line in source[lower_bound:lineno]]
    context_line = source[lineno].strip('\n')
    post_context = [line.strip('\n') for line in source[lineno + 1:upper_bound]]
    return lower_bound, pre_context, context_line, post_context

def serialize_stack(tb, exception_reporter_filter):
    frames = []
    while tb is not None:
        # Support for __traceback_hide__ which is used by a few libraries
        # to hide internal frames.
        if tb.tb_frame.f_locals.get('__traceback_hide__'):
            tb = tb.tb_next
            continue
        filename = tb.tb_frame.f_code.co_filename
        function = tb.tb_frame.f_code.co_name
        lineno = tb.tb_lineno - 1
        loader = tb.tb_frame.f_globals.get('__loader__')
        module_name = tb.tb_frame.f_globals.get('__name__') or ''
        pre_context_lineno, pre_context, context_line, post_context = \
            get_lines_from_file(filename, lineno, 7, loader, module_name)
        if pre_context_lineno is not None:
            frames.append(dict(
                filename=filename,
                line_number=lineno,
                function=function,
                pre_context=pre_context,
                context=context_line,
                post_context=post_context,
                variables=serialize_object_dict(
                    exception_reporter_filter \
                        .get_traceback_frame_variables(None, tb.tb_frame)
                )
            ))
        tb = tb.tb_next
    return frames

def serialize_object_dict(iterable_of_twotuples):
    result = dict()
    for key, value in iterable_of_twotuples:
        try:
            formatted_value = pprint.pformat(value)
        except Exception as exception:
            formatted_value = "Formatting error: %s" % str(exception)
        result[key] = formatted_value
    return result
