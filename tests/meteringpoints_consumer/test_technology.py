import pytest
from typing import List, Optional

from energytt_platform.models.tech import Technology, TechnologyType, TechnologyCodes
from energytt_platform.serialize import simple_serializer
from flask.testing import FlaskClient

from energytt_platform.bus import messages as m
from energytt_platform.models.meteringpoints import MeteringPoint, MeteringPointType
from energytt_platform.models.delegates import MeteringPointDelegate

from meteringpoints_consumer.handlers import dispatcher
from meteringpoints_shared.db import db

TECHNOLOGY_1 = Technology(
    tech_code="100",
    fuel_code='200',
    type=TechnologyType.coal,
)

TECHNOLOGY_2 = Technology(
    tech_code="300",
    fuel_code='400',
    type=TechnologyType.nuclear,
)

METERINGPOINT_WITHOUT_TECHNOLOGY = MeteringPoint(
    gsrn='gsrn0',
    sector='DK1',
    type=MeteringPointType.production,
)

METERINGPOINT_WITH_TECHNOLOGY_1 = MeteringPoint(
    gsrn='gsrn1',
    sector='DK1',
    type=MeteringPointType.production,
    technology=TECHNOLOGY_1,
)

METERINGPOINT_WITH_TECHNOLOGY_2 = MeteringPoint(
    gsrn='gsrn2',
    sector='DK1',
    type=MeteringPointType.production,
    technology=TECHNOLOGY_2,
)

METERINGPOINT_2_simple = simple_serializer.serialize(METERINGPOINT_WITH_TECHNOLOGY_1)

METERINGPOINTS = [
    METERINGPOINT_WITHOUT_TECHNOLOGY,
    METERINGPOINT_WITH_TECHNOLOGY_1,
    METERINGPOINT_WITH_TECHNOLOGY_2,
]

TECHNOLOGIES = [
    TECHNOLOGY_1,
    TECHNOLOGY_2
]


@pytest.fixture(scope='function')
def seed_meteringpoints(
        session: db.Session,
        token_subject: str
):
    """
    Insert dummy meteringpoints into the database
    """

    for meteringpoint in METERINGPOINTS:
        dispatcher(m.MeteringPointUpdate(
            meteringpoint=meteringpoint,
        ))

        dispatcher(m.MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=token_subject,
                gsrn=meteringpoint.gsrn,
            ),
        ))
    return session


class TestMeteringPointTechnologyUpdate:
    """
    TODO
    """

    @pytest.mark.parametrize('meteringpoint, updated_technology, expected_technology_result', (
            (METERINGPOINT_WITHOUT_TECHNOLOGY, TECHNOLOGY_1, TECHNOLOGY_1),
            (METERINGPOINT_WITH_TECHNOLOGY_1, TECHNOLOGY_2, TECHNOLOGY_2),
            (METERINGPOINT_WITH_TECHNOLOGY_1, TECHNOLOGY_1, TECHNOLOGY_1),
            (METERINGPOINT_WITH_TECHNOLOGY_1, None, None),
    ))
    def test__update_meteringpoint_technology__should_return_updated_meteringpoint_technology(
            self,
            seed_meteringpoints: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
            meteringpoint: MeteringPoint,
            updated_technology: Optional[Technology],
            expected_technology_result: Optional[Technology],
    ):
        """
        TODO
        """
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------
        for technology in TECHNOLOGIES:
            dispatcher(m.TechnologyUpdate(
                technology=technology,
            ))

        if updated_technology is None:
            dispatcher(m.MeteringPointTechnologyUpdate(
                gsrn=meteringpoint.gsrn,
                codes=updated_technology
            ))
        else:
            dispatcher(m.MeteringPointTechnologyUpdate(
                gsrn=meteringpoint.gsrn,
                codes=TechnologyCodes(
                    tech_code=updated_technology.tech_code,
                    fuel_code=updated_technology.fuel_code
                )
            ))

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [meteringpoint.gsrn],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

        # -- Assert ----------------------------------------------------------
        meteringpoint.technology = expected_technology_result

        expected_meteringpoint_simple = simple_serializer.serialize(meteringpoint)

        assert r.status_code == 200
        assert r.json == {
            'success': True,
            'total': 1,
            'meteringpoints': [expected_meteringpoint_simple],
        }


class TestTechnologyUpdate:
    """
    TODO
    """

    def test__add_technology__should_return_updated_meteringpoint_technology(
            self,
            seed_meteringpoints: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """
        TODO
        """
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        dispatcher(m.TechnologyUpdate(
            technology=TECHNOLOGY_1
        ))

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [METERINGPOINT_WITH_TECHNOLOGY_1.gsrn],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

        # -- Assert ----------------------------------------------------------

        expected_meteringpoint_simple = simple_serializer.serialize(METERINGPOINT_WITH_TECHNOLOGY_1)

        assert r.status_code == 200
        assert r.json == {
            'success': True,
            'total': 1,
            'meteringpoints': [expected_meteringpoint_simple],
        }


class TestTechnologyRemoved:
    """
    TODO
    """

    def test__remove_technology__should_return_meteringpoint_technology_equals_none(
            self,
            seed_meteringpoints: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """
        TODO
        """
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------
        dispatcher(m.TechnologyUpdate(
            technology=TECHNOLOGY_1
        ))

        dispatcher(m.TechnologyRemoved(
            codes=TechnologyCodes(
                tech_code=TECHNOLOGY_1.tech_code,
                fuel_code=TECHNOLOGY_1.fuel_code,
            )
        ))

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [METERINGPOINT_WITH_TECHNOLOGY_1.gsrn],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

    def test__remove_different_technology__should_return_meteringpoint_technology(
            self,
            seed_meteringpoints: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """
        Test that remove technology removes the correct technology.
        """
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------
        dispatcher(m.TechnologyUpdate(
            technology=TECHNOLOGY_1
        ))

        dispatcher(m.TechnologyUpdate(
            technology=TECHNOLOGY_2
        ))

        # Remove different technology
        dispatcher(m.TechnologyRemoved(
            codes=TechnologyCodes(
                tech_code=TECHNOLOGY_2.tech_code,
                fuel_code=TECHNOLOGY_2.fuel_code,
            )
        ))

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [METERINGPOINT_WITH_TECHNOLOGY_1.gsrn],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

        # -- Assert ----------------------------------------------------------

        expected_meteringpoint_simple = simple_serializer.serialize(METERINGPOINT_WITH_TECHNOLOGY_1)

        assert r.status_code == 200
        assert r.json == {
            'success': True,
            'total': 1,
            'meteringpoints': [expected_meteringpoint_simple],
        }
