# Standard Library
from dataclasses import dataclass
from typing import Dict, List, TypeVar

# Third party
import requests
from requests import Response

# First party
from origin.serialize import simple_serializer


class GenericHttpClient:
    """
    A httpclient for communicating with the data-sync service.

    Each HttpClient should use the internal_token provided by the
    individual user.

    :param base_url: base url of the datasync class.
        :type base_url: str
        :param internal_token: The bearer internal_token used
               for authentication.
        :type internal_token: str
    """

    class HttpError(Exception):
        """Raised when http requests fails."""

        def __init__(self, status_code: int, message: str) -> None:
            self.message = message
            self.status_code = status_code

            super().__init__(self.message)

    class DecodeError(Exception):
        """Raised when http requests fails."""

        pass

    def __init__(self, base_url: str, internal_token: str):
        self.base_url = base_url
        self.internal_token = internal_token

    T = TypeVar('T')

    def _decode_response(self, data: any, schema: T) -> T:
        """
        Decodes/Deserialize a response returns object of type schema.

        Attempts to deserialize data and returns object of given schema.
        If invalid data provided, a DecodeError is raised.

        :param data: Data to be decoded
        :type data: any
        :param schema: The schema to be decoded into. Expects a dataclass.
        :type schema: T
        :raises GenericHttpClient.DecodeError: Raised when failing to decode
        :return: Object of type schema.
        :rtype: T
        """
        try:
            decoded = simple_serializer.deserialize(
                data,
                schema,
                True,
            )
        except:   # noqa: E722
            raise GenericHttpClient.DecodeError(
                "Failed to decode response body."
            )

        return decoded

    def _decode_list_response(self, response: any, schema: T) -> List[T]:
        """
        Decodes a list response, and return new object of type "schema".

        Takes a response with with a .json() which returns list of objects,
        and decodes the data and return new object of type "schema".
        This is used due to a limitation of the used serializer serpyco,
        which takes a dataclass as type "schema". This means that
        schema can't take argument "List[str]" since List can't be a dataclass.

        :param response: The response to decode
        :type response: requests Response
        :param schema: Type to decode response into, must be a dataclass.
        :type schema: T
        :return: The decoded/deseriales output
        :rtype: List[T]
        """
        @dataclass
        class ExpectedResponse:
            """Expected result from http request."""

            result: List[schema]

        decoded = self._decode_response(
            data={
                "result": response.json()
            },
            schema=ExpectedResponse
        )

        return decoded.result

    def _raiseHttpErrorIf(self, response: Response, code: int, message: str):
        """
        Raise HttpError if response.status_code == code.

        Raise HttpError when the response.status_code equals code argument,
        with the message as HttpError Message.

        :param response: the requests response
        :type response: Response
        :param code: http_status code to trigger error
        :type code: int
        :param message: Message to display in error
        :type message: str
        :raises GenericHttpClient.HttpError: Error to be raised
        """
        if response.status_code == code:
            raise GenericHttpClient.HttpError(
                status_code=response.status_code,
                message=message
            )

    def _raiseHttpErrorIfNot(self, response: Response, code: int, message: str):
        """
        Raise HttpError if response.status_code != code.

        Raise HttpError when the response.status_code does not equal
        code argument,with the message as HttpError Message.

        :param response: the requests response
        :type response: Response
        :param code: http_status code to not trigger error
        :type code: int
        :param message: Message to display in error
        :type message: str
        :raises GenericHttpClient.HttpError: Error to be raised
        """
        if response.status_code != code:
            raise GenericHttpClient.HttpError(
                status_code=response.status_code,
                message=message
            )

    def _getHeaders(self) -> Dict[str, str]:
        """
        Create headers used for authorization.

        :return: headers used for HttpRequests
        :rtype: Dict[str, str]
        """
        headers = {
            "Authorization": f'Bearer: {self.internal_token}'
        }

        return headers
