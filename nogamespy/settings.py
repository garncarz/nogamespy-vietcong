DATABASE = 'postgresql://localhost/vietcong'

UDP_TIMEOUT = 4

try:
    from .settings_local import *
except ImportError:
    pass
