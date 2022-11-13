from datetime import datetime


def get_current_year():
    return datetime.now().year


def is_read_method(method):
    return method in ('GET', 'HEAD', 'OPTIONS')
