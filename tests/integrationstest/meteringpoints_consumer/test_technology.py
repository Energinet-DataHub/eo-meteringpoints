import pytest
from typing import Optional
from flask.testing import FlaskClient

from origin.bus import messages as m
from origin.serialize import simple_serializer
from origin.models.delegates import MeteringPointDelegate
from origin.models.tech import \
    Technology, TechnologyType, TechnologyCodes
from origin.models.meteringpoints import \
    MeteringPoint, MeteringPointType

from meteringpoints_consumer.handlers import dispatcher
from meteringpoints_shared.db import db


TECHNOLOGY_1 = Technology(
    tech_code="100",
    fuel_code='200',
    type=TechnologyType.COAL,
)

TECHNOLOGY_2 = Technology(
    tech_code="300",
    fuel_code='400',
    type=TechnologyType.NUCLEAR,
)

METERINGPOINT_WITHOUT_TECHNOLOGY = MeteringPoint(
    gsrn='gsrn0',
    sector='DK1',
    type=MeteringPointType.PRODUCTION,
)

METERINGPOINT_WITH_TECHNOLOGY_1 = MeteringPoint(
    gsrn='gsrn1',
    sector='DK1',
    type=MeteringPointType.PRODUCTION,
    technology=TECHNOLOGY_1,
)

METERINGPOINT_WITH_TECHNOLOGY_2 = MeteringPoint(
    gsrn='gsrn2',
    sector='DK1',
    type=MeteringPointType.PRODUCTION,
    technology=TECHNOLOGY_2,
)

METERINGPOINT_2_simple = simple_serializer.serialize(METERINGPOINT_WITH_TECHNOLOGY_1)  # noqa: E501

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
    """Insert dummy meteringpoints into the database."""

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
    """TODO."""

    @pytest.mark.parametrize('meteringpoint, updated_technology', (
        (METERINGPOINT_WITHOUT_TECHNOLOGY, TECHNOLOGY_1),
        (METERINGPOINT_WITH_TECHNOLOGY_1, TECHNOLOGY_2),
        (METERINGPOINT_WITH_TECHNOLOGY_1, TECHNOLOGY_1),
    ))
    def test__update_meteringpoint_technology__should_return_updated_meteringpoint_technology(  # noqa: E501
            self,
            seed_meteringpoints: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
            meteringpoint: MeteringPoint,
            updated_technology: Optional[Technology],
    ):
        """TODO."""

        # -- Act -------------------------------------------------------------

        for technology in TECHNOLOGIES:
            dispatcher(m.TechnologyUpdate(
                technology=technology,
            ))

        if updated_technology is None:
            dispatcher(m.MeteringPointTechnologyUpdate(
                gsrn=meteringpoint.gsrn,
                codes=None,
            ))
        else:
            dispatcher(m.MeteringPointTechnologyUpdate(
                gsrn=meteringpoint.gsrn,
                codes=TechnologyCodes(
                    tech_code=updated_technology.tech_code,
                    fuel_code=updated_technology.fuel_code,
                ),
            ))

        res = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
            json={
                'filters': {
                    'gsrn': [meteringpoint.gsrn],
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        expected_meteringpoint_simple = \
            simple_serializer.serialize(meteringpoint)
        expected_meteringpoint_simple['technology'] = \
            simple_serializer.serialize(updated_technology)

        assert res.status_code == 200
        assert res.json == {
            'meteringpoints': [expected_meteringpoint_simple],
        }

    def test__update_meteringpoint_technology_to_none__should_return_meteringpoint_technology(  # noqa: E501
            self,
            seed_meteringpoints: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """TODO."""

        # -- Act -------------------------------------------------------------

        for technology in TECHNOLOGIES:
            dispatcher(m.TechnologyUpdate(
                technology=technology,
            ))

        dispatcher(m.MeteringPointTechnologyUpdate(
            gsrn=METERINGPOINT_WITH_TECHNOLOGY_1.gsrn,
            codes=None,
        ))

        res = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
            json={
                'filters': {
                    'gsrn': [METERINGPOINT_WITH_TECHNOLOGY_1.gsrn],
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        expected_meteringpoint_simple = \
            simple_serializer.serialize(METERINGPOINT_WITH_TECHNOLOGY_1)
        expected_meteringpoint_simple['technology'] = None

        assert res.status_code == 200
        assert res.json == {
            'meteringpoints': [expected_meteringpoint_simple],
        }

    def test__add_two_meteringpoints_update_one__should_update_only_update_correct_meteringpoint_technology(  # noqa: E501
            self,
            seed_meteringpoints: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """TODO."""
        # -- Act -------------------------------------------------------------

        for technology in TECHNOLOGIES:
            dispatcher(m.TechnologyUpdate(
                technology=technology,
            ))

        dispatcher(m.MeteringPointTechnologyUpdate(
            gsrn=METERINGPOINT_WITHOUT_TECHNOLOGY.gsrn,
            codes=TechnologyCodes(
                tech_code=TECHNOLOGY_1.tech_code,
                fuel_code=TECHNOLOGY_1.fuel_code,
            ),
        ))

        res = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
        )

        # -- Assert ----------------------------------------------------------

        assert res.status_code == 200

        # Make dictionary from fetched meteringpoint
        result_dict = {
            mp['gsrn']: mp['technology']
            for mp in res.json['meteringpoints']
        }

        # Updated meteringpoint expected to be updated
        assert result_dict[METERINGPOINT_WITHOUT_TECHNOLOGY.gsrn] == \
               simple_serializer.serialize(TECHNOLOGY_1)

        # Expected to stay the same
        assert result_dict[METERINGPOINT_WITH_TECHNOLOGY_1.gsrn] == \
               simple_serializer.serialize(TECHNOLOGY_1)

        # Expected to stay the same
        assert result_dict[METERINGPOINT_WITH_TECHNOLOGY_2.gsrn] == \
               simple_serializer.serialize(TECHNOLOGY_2)


class TestTechnologyUpdate:
    """TODO."""

    def test__add_technology__should_return_updated_meteringpoint_technology(
            self,
            seed_meteringpoints: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """TODO."""
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        dispatcher(m.TechnologyUpdate(
            technology=TECHNOLOGY_1
        ))

        res = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
            json={
                'filters': {
                    'gsrn': [METERINGPOINT_WITH_TECHNOLOGY_1.gsrn],
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        expected_meteringpoint_simple = \
            simple_serializer.serialize(METERINGPOINT_WITH_TECHNOLOGY_1)

        assert res.status_code == 200
        assert res.json == {
            'meteringpoints': [expected_meteringpoint_simple],
        }

    def test__do_not_add_technology__meteringpoint_technology_is_none(
            self,
            seed_meteringpoints: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """TODO."""
        # -- Act -------------------------------------------------------------

        res = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
            json={
                'filters': {
                    'gsrn': [METERINGPOINT_WITH_TECHNOLOGY_1.gsrn],
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        expected_meteringpoint_simple = \
            simple_serializer.serialize(METERINGPOINT_WITH_TECHNOLOGY_1)
        expected_meteringpoint_simple['technology'] = None

        assert res.status_code == 200
        assert res.json == {
            'meteringpoints': [expected_meteringpoint_simple],
        }


class TestTechnologyRemoved:
    """TODO."""

    def test__remove_technology__should_return_meteringpoint_technology_equals_none(  # noqa: E501
            self,
            seed_meteringpoints: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """TODO."""
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

        res = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
            json={
                'filters': {
                    'gsrn': [METERINGPOINT_WITH_TECHNOLOGY_1.gsrn],
                },
            },
        )

        assert res.status_code == 200

        expected_meteringpoint_simple = \
            simple_serializer.serialize(METERINGPOINT_WITH_TECHNOLOGY_1)
        expected_meteringpoint_simple['technology'] = None

        assert res.json == {
            'meteringpoints': [expected_meteringpoint_simple],
        }

    def test__remove_different_technology__should_return_meteringpoint_technology(  # noqa: E501
            self,
            seed_meteringpoints: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """Test that remove technology removes the correct technology."""

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

        res = client.post(
            path='/list',
            json={
                'filters': {
                    'gsrn': [METERINGPOINT_WITH_TECHNOLOGY_1.gsrn],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

        # -- Assert ----------------------------------------------------------

        expected_meteringpoint_simple = \
            simple_serializer.serialize(METERINGPOINT_WITH_TECHNOLOGY_1)

        assert res.status_code == 200
        assert res.json == {
            'meteringpoints': [expected_meteringpoint_simple],
        }
