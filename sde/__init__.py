"""
sde
==========
License: BSD, see LICENSE for more details.
"""

__author__ = "Danila Vershinin"

import logging

from .__about__ import (
    __version__,
)

from .sde import main
# We intentially import for export here, so it is ok to silence DeepSource test
# skipcq: PY-W2000
from .sde import edit_file, normalize_val, read_file

# https://realpython.com/python-logging-source-code/#library-vs-application-logging-what-is-nullhandler
# when used as library, we default to opt-in approach, wherein a library user has to enable logging
# from within their application's code
# logging.getLogger(__name__).addHandler(logging.NullHandler())
# the exception handling is for supporting Python 2.6 (RHEL 6.x)

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

if __name__ == "__main__":
    main()
