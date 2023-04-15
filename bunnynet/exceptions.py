"""Exceptions."""

import requests


class BunnyException(Exception):
    """Base class for exceptions."""


class BunnyHTTPException(BunnyException):
    """A HTTP exception."""

    response: requests.Response

    def __init__(self, response: requests.Response, message: str = "") -> None:
        super().__init__(message)
        self.response = response
