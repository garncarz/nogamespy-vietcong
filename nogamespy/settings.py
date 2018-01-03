DATABASE = 'postgresql://localhost/vietcong'

GAMESPY_KEY = 'bq98mE'

UDP_TIMEOUT = 4

MASTER_PORT = 28900

try:
    from .settings_local import *
except ImportError:
    pass
