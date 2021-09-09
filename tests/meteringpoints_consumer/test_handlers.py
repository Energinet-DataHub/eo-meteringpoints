import pytest
from unittest.mock import patch

from energytt_platform.bus.messages.meteringpoints import MeteringPointUpdate
from energytt_platform.bus import messages as m
from meteringpoints_consumer.handlers import dispatcher

from energytt_platform.models.tech import Technology, TechnologyType
from energytt_platform.models.common import EnergyDirection
from energytt_platform.models.meteringpoints import MeteringPoint

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
    # Patch db method that returns session
    @patch('meteringpoints_shared.db.db.session_class')
    def test__metering_point_update__metering_point_added_to_db(self, make_session_func, session):

        # -- Arrange ---------------------------------------------------------

        make_session_func.return_value = session

        metering_point_update_msg = MeteringPointUpdate(
            meteringpoint=metering_point1
        )

        # -- Act -------------------------------------------------------------

        dispatcher(metering_point_update_msg)

        # -- Assert ----------------------------------------------------------

        query = MeteringPointQuery(session) \
            .has_gsrn(metering_point1.gsrn)
        result = query.one()

        assert result.sector == metering_point1.sector
        assert result.type == metering_point1.type
