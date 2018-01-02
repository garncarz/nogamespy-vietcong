DATABASE = 'postgresql://localhost/vietcong'

UDP_TIMEOUT = 4

MASTER_PORT = 28900

try:
    from .settings_local import *
except ImportError:
    pass
