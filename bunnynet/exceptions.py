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

    @staticmethod
    def generate_from_response(response: requests.Response, message: str = "") -> "BunnyHTTPException":
        """Generate an exception from the response to a call.

        :param response: The response to use to determine which exception type.
        :param message: Any message to add to the exception

        :returns: The best matching exception
        """
        # pylint: disable=too-many-return-statements
        match response.status_code:
            case 400:
                return BunnyHTTPBadRequestException(response, message)
            case 401:
                return BunnyHTTPUnauthorizedException(response, message)
            case 403:
                return BunnyHTTPForbiddenException(response, message)
            case 404:
                return BunnyHTTPNotFoundException(response, message)
            case 409:
                return BunnyHTTPConflictException(response, message)
            case 500:
                return BunnyHTTPInternalServerErrorException(response, message)

        return BunnyHTTPException(response, message)
        # pylint: enable=too-many-return-statements


class BunnyHTTPBadRequestException(BunnyHTTPException):
    """A 400 HTTP exception."""


class BunnyHTTPUnauthorizedException(BunnyHTTPException):
    """A 401 HTTP exception."""


class BunnyHTTPForbiddenException(BunnyHTTPException):
    """A 403 HTTP exception."""


class BunnyHTTPNotFoundException(BunnyHTTPException):
    """A 404 HTTP exception."""


class BunnyHTTPConflictException(BunnyHTTPException):
    """A 409 HTTP exception."""


class BunnyHTTPInternalServerErrorException(BunnyHTTPException):
    """A 500 HTTP exception."""
