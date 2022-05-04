from typing import List
from origin.serialize import simple_serializer
from origin.models.meteringpoints import MeteringPoint
import requests


class DataSyncHttpClient:
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

    def get_meteringpoints_by_tin(self, tin: str) -> List[MeteringPoint]:
        """Return meteringpoints with relations to given tin."""

        uri = f'{self.base_url}/MeteringPoint/GetByTin/{tin}'

        response = requests.get(uri, headers=self._getHeaders())

        if response.status_code == 404:
            raise DataSyncHttpClient.HttpError(
                status_code=response.status_code,
                message="User with tin not found."
            )
        elif response.status_code != 200:
            raise DataSyncHttpClient.HttpError(
                status_code=response.status_code,
                message="Failed to fetch meteringpoints by tin."
            )

        data = response.json()

        try:
            meteringpoints = simple_serializer.deserialize(
                data,
                List[MeteringPoint],
                True,
            )
        except:   # noqa: E722
            raise DataSyncHttpClient.DecodeError(
                "Failed to decode meteringpoints."
            )

        return meteringpoints

    def _getHeaders(self):
        headers = {
            "Authorization": f'Bearer: {self.internal_token}'
        }

        return headers
