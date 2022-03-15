import pytest
from typing import List, Any
from itertools import product
from flask.testing import FlaskClient

from origin.models.meteringpoints import MeteringPointType


from meteringpoints_shared.db import db
from meteringpoints_shared.models import (
    DbMeteringPoint,
    DbMeteringPointDelegate,
)
from src.meteringpoints_api.fake_data import FakeMeteringPoint

TYPES = (MeteringPointType.CONSUMPTION, MeteringPointType.PRODUCTION)
SECTORS = ('DK1', 'DK2')
COMBINATIONS = list(product(TYPES, SECTORS))


@pytest.fixture(scope='module')
def seed_meteringpoints() -> List[FakeMeteringPoint]:
    """
    TODO.

    :return:
    """

    mp_list = []

    for idx in enumerate(COMBINATIONS):
        mp_list.append(DbMeteringPoint(
            gsrn=f'gsrn{idx}',
        ))

    return mp_list


@pytest.fixture(scope='function')
def seeded_session(
        session: db.Session,
        seed_meteringpoints: List[FakeMeteringPoint],
        token_subject: str,
) -> db.Session:
    """
    TODO.

    :param session:
    :param seed_meteringpoints:
    :param token_subject:
    :return:
    """
    session.begin()

    for meteringpoint in seed_meteringpoints:
        session.add(DbMeteringPoint(
            gsrn=meteringpoint.gsrn,
            type=meteringpoint.type,
            sector=meteringpoint.sector,
        ))

        session.add(DbMeteringPointDelegate(
            gsrn=meteringpoint.gsrn,
            subject=token_subject,
        ))

    session.commit()

    yield session


class TestGetMeteringPointList:
    """TODO."""

    # -- Filter by GSRN ------------------------------------------------------

    @pytest.mark.parametrize('gsrn', [
        ['gsrn1', 'gsrn2', 'gsrn3'],
    ])
    def test__filter_by_known_gsrn__should_return_correct_meteringpoints(
        self,
        gsrn: List[str],
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):
        """TODO."""

        # -- Act -------------------------------------------------------------

        res = client.get(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'filters': {
                    'gsrn': gsrn,
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        # Assert response JSON
        assert res.status_code == 200

        # Assert number of returned MeteringPoints
        assert len(res.json['meteringpoints']) == len(gsrn)


    @pytest.mark.parametrize('gsrn', [
        ['Foo'],
    ])
    def test__filter_by_unknown_gsrn__should_return_no_meteringpoints(
        self,
        gsrn: List[str],
        client: FlaskClient,
        valid_token_encoded: str,
        seeded_session: db.Session,
    ):
        """TODO."""

        # -- Act -------------------------------------------------------------

        res = client.get(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'filters': {
                    'gsrn': gsrn,
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        assert res.status_code == 200
        assert res.json != {
            'meteringpoints': [],
        }
