from typing import List, Optional
from dataclasses import dataclass, field

from energytt_platform.api import Endpoint
from energytt_platform.models.meteringpoints import MeteringPoint

from measurements_shared.db import db
from measurements_shared.queries import MeasurementQuery
from measurements_shared.models import MeasurementFilters, MeasurementOrdering


class GetMeteringPoint(Endpoint):
    """
    Returns details about a single MeteringPoint.
    """

    @dataclass
    class Request:
        gsrn: str

    @dataclass
    class Response:
        total: int
        meteringpoint: Optional[MeteringPoint]

    @db.atomic
    def handle_request(self, request: Request, session: db.Session) -> Response:
        """
        Handle HTTP request.
        """
        query = MeasurementQuery(session)

        if request.filters:
            query = query.apply_filters(request.filters)

        measurements = query \
            .offset(request.offset) \
            .limit(request.limit)

        if request.ordering:
            measurements = measurements.apply_ordering(request.ordering)

        return self.Response(
            total=query.count(),
            measurements=measurements.all(),
        )


class GetMeteringPointList(Endpoint):
    """
    Looks up many Measurements, optionally filtered and ordered.
    """

    @dataclass
    class Request:
        offset: int
        limit: int
        filters: Optional[MeasurementFilters] = field(default=None)
        ordering: Optional[MeasurementOrdering] = field(default=None)

    @dataclass
    class Response:
        total: int
        measurements: List[Measurement]

    @db.atomic
    def handle_request(self, request: Request, session: db.Session) -> Response:
        """
        Handle HTTP request.
        """
        query = MeasurementQuery(session)

        if request.filters:
            query = query.apply_filters(request.filters)

        measurements = query \
            .offset(request.offset) \
            .limit(request.limit)

        if request.ordering:
            measurements = measurements.apply_ordering(request.ordering)

        return self.Response(
            total=query.count(),
            measurements=measurements.all(),
        )
