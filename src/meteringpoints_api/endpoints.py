from typing import List, Optional
from dataclasses import dataclass
import requests

from origin.api import Endpoint, Context
from origin.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from meteringpoints_shared.queries import MeteringPointQuery


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

        tin = 1
        response = requests.get(
            f'http://localhost:8080/MeteringPoint/GetByTin/{tin}')

        meteringpoint_list = response

        return self.Response(
            meteringpoints=meteringpoint_list,
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
