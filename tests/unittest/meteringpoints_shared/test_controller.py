import pytest

from meteringpoints_shared.db import db

from energytt_platform.models.tech import Technology, TechnologyType
from energytt_platform.models.meteringpoints import MeteringPoint, MeteringPointType
from energytt_platform.models.common import Address

from meteringpoints_shared.controller import controller
from meteringpoints_shared.models import DbMeteringPoint, DbTechnology
from meteringpoints_shared.queries import MeteringPointQuery

TECHNOLGY_1 = DbTechnology(
    type=TechnologyType.nuclear,
    tech_code='100',
    fuel_code='101',
)

METERINGPOINT_WITHOUT_TECHNOLOGY = DbMeteringPoint(
    gsrn='gsrn1',
    type=MeteringPointType.consumption,
    sector='DK1',
    technology=None,
    address=None,
)

METERINGPOINT_WITH_TECHNOLOGY = DbMeteringPoint(
    gsrn='gsrn2',
    type=MeteringPointType.consumption,
    sector='DK2',
    technology=TECHNOLGY_1,
    address=None,
)

METERINGPOINT_WITH_ADDRESS = DbMeteringPoint(
    gsrn='gsrn3',
    type=MeteringPointType.consumption,
    sector='DK3',
    technology=None,
    address=Address(
        street_code='street_code_1',
        street_name='street_name_1',
        building_number='building_number_1',
        floor_id='floor_id_1',
        room_id='room_id_1',
        post_code='post_code_1',
        city_name='city_name_1',
        city_sub_division_name='city_sub_division_name1',
        municipality_code='municipality_code_1',
        location_description='location_description_1',
    ),
)

METERINGPOINTS = [
    METERINGPOINT_WITHOUT_TECHNOLOGY,
    METERINGPOINT_WITH_TECHNOLOGY,
    METERINGPOINT_WITH_ADDRESS,
]

TECHNOLOGIES = [
    TECHNOLGY_1
]


@pytest.fixture(scope='function')
def seeded_session(
        session: db.Session,
) -> db.Session:
    for meteringpoint in METERINGPOINTS:
        session.add(meteringpoint)

    for technology in TECHNOLOGIES:
        session.add(technology)

    session.commit()
    return session


class TestDatabaseController:
    # FIXME: Test does not work if run all at once

    @pytest.mark.parametrize('meteringpoint', (
            METERINGPOINT_WITHOUT_TECHNOLOGY,
            METERINGPOINT_WITH_TECHNOLOGY,
            METERINGPOINT_WITH_ADDRESS,
    ))
    def test__get_or_create_meteringpoint__meteringpoint_does_exists__should_return_meteringpoint(
            self,
            seeded_session: db.Session,
            meteringpoint: DbMeteringPoint,
    ):
        # -- Act -----------------------------------------------------------------

        fetched_meteringpoint = controller.get_or_create_meteringpoint(
            session=seeded_session,
            gsrn=meteringpoint.gsrn
        )

        # -- Assert --------------------------------------------------------------

        assert fetched_meteringpoint == meteringpoint

    def test__get_or_create_meteringpoint__meteringpoint_does_not_exists__should_create_and_return_meteringpoint(
            self,
            seeded_session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------
        gsrn = 'gsrn100'

        # -- Act -----------------------------------------------------------------

        meteringpoint = controller.get_or_create_meteringpoint(
            session=seeded_session,
            gsrn=gsrn,
        )

        # Check database for new meteringpoint
        db_meteringpoint = MeteringPointQuery(seeded_session) \
            .has_gsrn(gsrn) \
            .one_or_none()

        # -- Assert --------------------------------------------------------------

        assert meteringpoint.gsrn == gsrn
        assert db_meteringpoint.gsrn == gsrn




