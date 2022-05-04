from typing import List, Optional
from dataclasses import dataclass
import requests

from origin.api import Endpoint, Context
from origin.models.meteringpoints import MeteringPoint
from origin.api.responses import InternalServerError
from meteringpoints_shared.config import DATASYNC_BASE_URL
from meteringpoints_shared.datasync_httpclient import DataSyncHttpClient

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

        if response.status_code != 200:
            print("failed to get tin from auth service")

        if not user_info["tin"]:
            print("user_info['tin'] were none")

        user_info = response.json()

        # data_sync_url = f'http://eo-data-sync/MeteringPoint/GetByTin/{user_info["tin"]}'  # noqa: E501

        # response = requests.get(data_sync_url, headers=token)

        http_client = DataSyncHttpClient(
            base_url=DATASYNC_BASE_URL,
            internal_token=context.internal_token_encoded,
        )

        if user_info["tin"]:
            meteringpoints = http_client.get_meteringpoints_by_tin(user_info["tin"])  # noqa: E501
        elif user_info["ssn"]:
            # IMPLEMENT THIS
            print("httpClient.get_meteringpoints_by_ssn() not implemented")
            return self.Response(success=False)
        else:
            return self.Response(success=False)

        return self.Response(
            meteringpoints=meteringpoints,  # noqa: E501
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


class CreateMeteringPointRelations(Endpoint):
    """Returns details about a single MeteringPoint."""

    @dataclass
    class Request:
        """TODO."""

        tin: Optional[str]
        ssn: Optional[str]

    @dataclass
    class Response:
        """TODO."""

        success: bool

    @db.session()
    def handle_request(
            self,
            request: Request,
            context: Context,
            session: db.Session,
    ) -> Response:
        """Handle HTTP request."""

        http_client = DataSyncHttpClient(
            base_url=DATASYNC_BASE_URL,
            internal_token=context.internal_token_encoded,
        )

        if request.tin:
            meteringpoints = http_client.get_meteringpoints_by_tin(request.tin)
        elif request.ssn:
            # IMPLEMENT THIS
            print("httpClient.get_meteringpoints_by_ssn() not implemented")
            pass
        else:
            return self.Response(success=False)

        meteringpoint_ids = [MeteringPoint(gsrn=mp) for mp in meteringpoints]

        print(meteringpoint_ids)

        return self.Response(
            success=meteringpoint_ids is not None,
        )
