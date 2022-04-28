from typing import List, Optional
from dataclasses import dataclass
from types import SimpleNamespace
import requests
import sys
import json

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
            context: Context,
    ) -> Response:
        """Handle HTTP request."""

        print("Prepare list")
        print("I am here!", file=sys.stderr)

        data_sync_url = 'http://eo-data-sync/MeteringPoint/GetByTin/2'
        token = {"Authorization": context.headers['Authorization']}  # noqa: E501

        print("Data url: ", data_sync_url)

        response = requests.get(data_sync_url, headers=token)

        print("Will print response")
        print("Data response", response.json())

        print("context", context)
        print("context.token", context.token)
        print("headers", context.headers)

        print("internal_token_encoded", context.internal_token_encoded)
        print("token_encoder", context.token_encoder)

        try:
            internal_token = context.token_encoder.decode(
                context.internal_token_encoded)
            print("internal_token", internal_token.is_valid)    

        except context.token_encoder.DecodeError as e:
            print("e",e)


        return self.Response(
            meteringpoints=json.dumps(json.loads(response.json, object_hook=lambda d: SimpleNamespace(**d)))
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
