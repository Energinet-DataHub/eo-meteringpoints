from typing import List, Optional
from dataclasses import dataclass
import requests
# from .fake_data import FakeMeteringPoint

from origin.api import Endpoint, Context
from origin.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from meteringpoints_shared.queries import MeteringPointQuery

# import uuid
import sys


class GetMeteringPointList(Endpoint):
    """Look up metering points from the data sync domain."""

    @dataclass
    class Response:
        """TODO."""

        meteringpoints: List[MeteringPoint]

    def handle_request(
            self,
    ) -> Response:
        """Handle HTTP request."""

        print("Prepare list")
        print("I am here!", file=sys.stderr)

        data_sync_url = 'http://eo-data-sync/MeteringPoint/GetByTin/2'
        token = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY3RvciI6IkpvaG4ifQ.jOJaJ-TwqnF9JtFanuD2k07F1AMGhTjZiVUDov_WSlA"}  # noqa: E501

        print("Data url: ", data_sync_url)

        response = requests.get(data_sync_url, headers=token)

        print("Will print response")
        print("Data response", response.json())

        

        return self.Response(
            meteringpoints=response.json(),
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
