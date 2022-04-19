"""Errors raised by Suneku"""
from typing import Any, Dict, NoReturn, Optional, Tuple, Type

__all__ = [
    "VNDBException",
    "LoginFailed",
    "InvalidClient"
]


class VNDBException(Exception):
    """Base exception for Suneku"""
    # TODO Actually write a base exception


class InvalidClient(VNDBException):
    """Client mismatches regex"""

    msg = "The client must be between 3-50 characters contain only ASCII alphanumeric characters, spaces, hyphens or " \
          "underscores. "


class LoginFailed(VNDBException):
    """Failed to log in"""

    msg = "The client failed to login"
