# Standard Library
from dataclasses import dataclass
from typing import List, TypeVar

# Third party
import requests
from requests import Response

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
        if response.status_code == code:
            raise GenericHttpClient.HttpError(
                status_code=response.status_code,
                message=message
            )


    def _raiseHttpErrorIfNot(self, response: Response, code: int, message: str):
        if response.status_code != code:
            raise GenericHttpClient.HttpError(
                status_code=response.status_code,
                message=message
            )

    def _getHeaders(self):
        headers = {
            "Authorization": f'Bearer: {self.internal_token}'
        }

        return headers
