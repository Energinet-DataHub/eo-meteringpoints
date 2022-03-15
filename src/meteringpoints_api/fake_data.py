from dataclasses import dataclass
from typing import List

from origin.serialize import Serializable
import uuid
from origin.api import Endpoint


@dataclass
class MeteringPoint(Serializable):
    """Class to store the parameters for the metering point."""

    gsrn: str


class FakeGetMeteringPointList(Endpoint):
    """Look up many Measurements, optionally filtered and ordered."""

    @dataclass
    class Response:
        """TODO."""

        meteringpoints: List[MeteringPoint]

    def handle_request(
            self,
    ) -> Response:
        """Handle HTTP request."""

        fake_meteringpoint_list = [
            MeteringPoint(gsrn=str(uuid.uuid1())[:18]),
            MeteringPoint(gsrn=str(uuid.uuid1())[:18]),
            MeteringPoint(gsrn=str(uuid.uuid1())[:18]),
        ]

        return self.Response(
            meteringpoints=fake_meteringpoint_list,
        )
