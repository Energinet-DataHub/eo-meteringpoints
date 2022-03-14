import pytest
from typing import Dict, Any
from flask.testing import FlaskClient

from origin.bus import messages as m
from origin.serialize import simple_serializer
from origin.models.common import Address
from origin.models.delegates import MeteringPointDelegate
from origin.models.tech import Technology, TechnologyType
from origin.models.meteringpoints import \
    MeteringPointType, MeteringPoint

from meteringpoints_consumer.handlers import dispatcher
from meteringpoints_shared.db import db


# -- Test data ---------------------------------------------------------------


TECHNOLOGY = Technology(
    tech_code='T010101',
    fuel_code='F01010101',
    type=TechnologyType.SOLAR,
)

ADDRESS = Address(
    street_code='street_code#',
    street_name='street_name#',
    building_number='building_number#',
    floor_id='floor_id#',
    room_id='room_id#',
    post_code='post_code#',
    city_name='city_name#',
    city_sub_division_name='city_sub_division_name#',
    municipality_code='municipality_code#',
    location_description='location_description#',
)

GSRN = 'gsrn1'

METERINGPOINT = MeteringPoint(
    gsrn=GSRN,
    sector='DK1',
    type=MeteringPointType.PRODUCTION,
)

METERINGPOINT_WITH_TECHNOLOGY = MeteringPoint(
    gsrn=GSRN,
    sector='DK2',
    type=MeteringPointType.CONSUMPTION,
    technology=TECHNOLOGY,
)

METERINGPOINT_WITH_ADDRESS = MeteringPoint(
    gsrn=GSRN,
    sector='DK3',
    type=MeteringPointType.CONSUMPTION,
    address=ADDRESS,
)

METERINGPOINT_WITH_TECHNOLOGY_AND_ADDRESS = MeteringPoint(
    gsrn=GSRN,
    sector='DK4',
    type=MeteringPointType.CONSUMPTION,
    technology=TECHNOLOGY,
    address=ADDRESS,
)

# Representation of MeteringPoints using simple Python data-types:

METERINGPOINT_SIMPLE = simple_serializer.serialize(METERINGPOINT)

METERINGPOINT_WITH_TECHNOLOGY_SIMPLE = \
    simple_serializer.serialize(METERINGPOINT_WITH_TECHNOLOGY)

METERINGPOINT_WITH_ADDRESS_SIMPLE = \
    simple_serializer.serialize(METERINGPOINT_WITH_ADDRESS)

METERINGPOINT_WITH_TECHNOLOGY_AND_ADDRESS_SIMPLE = \
    simple_serializer.serialize(METERINGPOINT_WITH_TECHNOLOGY_AND_ADDRESS)


# -- Tests -------------------------------------------------------------------


class TestOnMeteringPointUpdate:
    """
    Test of MeteringPoint.

    Testing inserting of MeteringPoint (via message bus) and then invoking
    the API returns expected results.
    """

    @pytest.mark.parametrize('meteringpoint, meteringpoint_expected', (
        (
            METERINGPOINT,
            METERINGPOINT_SIMPLE,
        ),
        (
            METERINGPOINT_WITH_TECHNOLOGY,
            METERINGPOINT_WITH_TECHNOLOGY_SIMPLE,
        ),
        (
            METERINGPOINT_WITH_ADDRESS,
            METERINGPOINT_WITH_ADDRESS_SIMPLE,
        ),
        (
            METERINGPOINT_WITH_TECHNOLOGY_AND_ADDRESS,
            METERINGPOINT_WITH_TECHNOLOGY_AND_ADDRESS_SIMPLE,
        ),
    ))
    def test__add_a_meteringpoint_and_delegate_access__should_return_meteringpoint_correctly(  # noqa: E501
            self,
            meteringpoint: MeteringPoint,
            meteringpoint_expected: Dict[str, Any],
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
            token_subject: str,
    ):
        """TODO."""

        # -- Act -------------------------------------------------------------

        dispatcher(m.MeteringPointUpdate(
            meteringpoint=meteringpoint,
        ))

        dispatcher(m.MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=token_subject,
                gsrn=meteringpoint.gsrn,
            ),
        ))

        if meteringpoint.technology:
            dispatcher(m.TechnologyUpdate(
                technology=meteringpoint.technology,
            ))

        res = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
            json={
                'filters': {
                    'gsrn': [METERINGPOINT.gsrn],
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        assert res.status_code == 200
        assert res.json == {
            'meteringpoints': [meteringpoint_expected],
        }

    def test__add_a_meteringpoint_then_update_it__should_return_updated_meteringpoint(  # noqa: E501
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
            token_subject: str,
    ):
        """TODO."""

        # -- Arrange ---------------------------------------------------------

        dispatcher(m.MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=token_subject,
                gsrn=METERINGPOINT.gsrn,
            ),
        ))

        dispatcher(m.TechnologyUpdate(
            technology=METERINGPOINT_WITH_TECHNOLOGY_AND_ADDRESS.technology,
        ))

        # MeteringPoint without Address and Technology
        dispatcher(m.MeteringPointUpdate(
            meteringpoint=METERINGPOINT,
        ))

        # MeteringPoint with Address and Technology
        dispatcher(m.MeteringPointUpdate(
            meteringpoint=METERINGPOINT_WITH_TECHNOLOGY_AND_ADDRESS,
        ))

        # -- Act -------------------------------------------------------------

        res = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
            json={
                'filters': {
                    'gsrn': [GSRN],
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        assert res.status_code == 200
        assert res.json == {
            'meteringpoints': [METERINGPOINT_WITH_TECHNOLOGY_AND_ADDRESS_SIMPLE],  # noqa: E501
        }

    def test__add_many_meteringpoints_and_delegate_access__should_return_meteringpoints_correctly(  # noqa: E501
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
            token_subject: str,
    ):
        """TODO."""

        all_gsrn = ['gsrn1', 'gsrn2', 'gsrn3']

        # -- Act -------------------------------------------------------------

        for gsrn in all_gsrn:
            dispatcher(m.MeteringPointUpdate(
                meteringpoint=MeteringPoint(gsrn=gsrn),
            ))

            dispatcher(m.MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=token_subject,
                    gsrn=gsrn,
                ),
            ))

        res = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}'
            },
        )

        # -- Assert ----------------------------------------------------------

        assert res.status_code == 200
        assert all(mp['gsrn'] in all_gsrn for mp in res.json['meteringpoints'])
