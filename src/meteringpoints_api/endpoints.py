from typing import List, Optional
from dataclasses import dataclass
import requests

from origin.api import Endpoint, Context
from origin.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from meteringpoints_shared.queries import MeteringPointQuery


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

        user_info = response.json()

        data_sync_url = f'http://eo-data-sync/MeteringPoints/GetByTin/{user_info["tin"]}'  # noqa: E501

        response = requests.get(data_sync_url, headers=token)

        return self.Response(
            meteringpoints=[MeteringPoint(gsrn=mp['gsrn']) for mp in response.json()],  # noqa: E501
        )


class GetMeteringPointDetails(Endpoint):
    """Returns details about a single MeteringPoint."""

    @dataclass
    class Request:
        """TODO."""

        gsrn: str

    @dataclass
    class Response:
        """TODO."""

        success: bool
        meteringpoint: Optional[MeteringPoint]

    @db.session()
    def handle_request(
            self,
            request: Request,
            context: Context,
            session: db.Session,
    ) -> Response:
        """Handle HTTP request."""

        meteringpoint = MeteringPointQuery(session) \
            .is_accessible_by(context.token.subject) \
            .has_gsrn(request.gsrn) \
            .one_or_none()

        return self.Response(
            success=meteringpoint is not None,
            meteringpoint=meteringpoint,
        )
