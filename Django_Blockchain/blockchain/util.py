import linecache
import sys


def print_exception(prefix=""):
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print(prefix + ' except({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
