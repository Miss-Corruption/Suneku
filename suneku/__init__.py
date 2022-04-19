"""
VNDB API Wrapper
~~~~~~~~~~~~~~~~~~~

A basic wrapper for the Discord API.

:copyright: (c) 2022 Miss Corruption
:license: MIT, see LICENSE for more details.

"""

__title__ = "Suneku"
__author__ = "Miss Corruption"
__license__ = "MIT"
__copyright__ = "Copyright 2022-present Miss Corruption"
__version__ = "0.0.1"

from typing import NamedTuple, Literal


from .client import *
from .errors import *
from suneku.ext.formatter import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(major=0, minor=0, micro=1, releaselevel="alpha", serial=0)
