DATABASE = 'postgresql://localhost/vietcong'

try:
    from .settings_local import *
except ImportError:
    pass
