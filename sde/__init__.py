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
from .sde import edit_json

# https://realpython.com/python-logging-source-code/#library-vs-application-logging-what-is-nullhandler
# when used as library, we default to opt-in approach, whereas library user have to enable logging
# from lastversion
logging.getLogger(__name__).addHandler(logging.NullHandler())

