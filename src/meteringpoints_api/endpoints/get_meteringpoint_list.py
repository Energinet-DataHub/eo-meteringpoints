# Standard Library
from dataclasses import dataclass
from typing import List

# Third party
import requests

# First party
from meteringpoints_shared.config import (
    DATASYNC_BASE_URL,
)
from meteringpoints_shared.datasync_httpclient import (
    DataSyncHttpClient,
)
from origin.api import Context, Endpoint
from origin.models.meteringpoints import (
    MeteringPoint,
)

from origin.api.responses import BadRequest, InternalServerError

class GetMeteringPointList(Endpoint):
    """
    Look up metering points from the data sync domain.

    Given the users token, their tin can be requested
    and used to receive their metering point IDs.
    """

    @dataclass
    class Response:
        """TODO."""

        meteringpoints: List[MeteringPoint]

    def handle_request(
            self,
            context: Context,
    ) -> Response:
        """Handle HTTP request."""

        token = {"Authorization": f'Bearer: {context.internal_token_encoded}'}

        response = requests.get('http://eo-auth/user/info', headers=token)  # noqa: E501

        if response.status_code != 200:
            print("failed to get tin from auth service")

        user_info = response.json()

        if not user_info["tin"]:
            print("user_info['tin'] were none")

        http_client = DataSyncHttpClient(
            base_url=DATASYNC_BASE_URL,
            internal_token=context.internal_token_encoded,
        )

        meteringpoints: List[MeteringPoint] = []

        if user_info["tin"]:
            meteringpoints = http_client.get_meteringpoints_by_tin(user_info["tin"])  # noqa: E501
        elif user_info["ssn"]:
            # TODO: IMPLEMENT THIS
            print("httpClient.get_meteringpoints_by_ssn() not implemented")
            raise InternalServerError()
        else:
            raise BadRequest(
                body="User must have either a TIN or SSN"
            )



        return self.Response(
            meteringpoints=meteringpoints,  # noqa: E501
        )
