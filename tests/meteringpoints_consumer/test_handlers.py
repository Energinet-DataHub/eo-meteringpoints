import datetime

import pytest
from energytt_platform.models.auth import InternalToken
from energytt_platform.tokens import TokenEncoder
from flask.testing import FlaskClient
from unittest.mock import patch

from energytt_platform.bus.messages.meteringpoints import MeteringPointUpdate
from energytt_platform.bus import messages as m
from meteringpoints_consumer.handlers import dispatcher

from energytt_platform.models.tech import Technology, TechnologyType
from energytt_platform.models.common import EnergyDirection
from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from meteringpoints_shared.models import DbMeteringPoint, DbTechnology
from meteringpoints_shared.queries import MeteringPointQuery


technology = Technology(
    type=TechnologyType.coal,
    tech_code='123',
    fuel_code='456',
)


metering_point1 = MeteringPoint(
    gsrn='GSRN1',
    sector='DK1',
    type=EnergyDirection.consumption,
)


class TestMeteringPointUpdate:

    def test__metering_point_update__metering_point_added_to_db(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        TODO Describe test...
        """

        # -- Arrange ---------------------------------------------------------

        token = token_encoder.encode(InternalToken(
            issued=datetime.datetime.now(),
        ))

        # -- Act -------------------------------------------------------------

        dispatcher(MeteringPointUpdate(
            meteringpoint=metering_point1
        ))

        dispatcher(MeteringPointUpdate(
            meteringpoint=metering_point1
        ))

        response = client.post('/list', json={
            'offset': 0,
            'limit': 10,
        })

        response_json = response.get_json()

        # -- Assert ----------------------------------------------------------

        assert len(response_json['meteringpoints']) == 10

        # query = MeteringPointQuery(session) \
        #     .has_gsrn(metering_point1.gsrn)
        # result = query.one()
        #
        # assert result.sector == metering_point1.sector
        # assert result.type == metering_point1.type
