from typing import List
import pytest
from itertools import product
from flask.testing import FlaskClient

from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from energytt_platform.models.common import EnergyDirection

from meteringpoints_shared.models import DbMeteringPoint, DbMeteringPointDelegate
from ...helpers import \
    METERPING_POINT_TYPES, \
    insert_meteringpoint_and_delegate_access_to_subject, \
    make_dict_of_metering_point


SUBJECT = 'Subject1'
mp_types = METERPING_POINT_TYPES
mp_sectors = ('SECTOR_1', 'SECTOR_2')

combinations = product(
    mp_types, mp_sectors
)


@pytest.fixture(scope='module')
def seed_meteringpoints() -> List[MeteringPoint]:
    """
    TODO

    :return:
    """

    mp_list = []

    for i, (mp_type, mp_sector) in enumerate(combinations, start=1):
        mp_list.append(DbMeteringPoint(
            gsrn=f'GSRN#{i}',
            type=mp_type,
            sector=mp_sector,
        ))

    return mp_list


@pytest.fixture(scope='module')
def seeded_session(
        session: db.Session,
        seed_meteringpoints: List[MeteringPoint],
) -> db.Session:
    """
    TODO

    :param session:
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
            subject=SUBJECT,
        ))

    session.commit()

    yield session


class TestGetMeteringPointListFilters:

    def test__filter_by_single_gsrn__single_point_fetched(
        self,
        seed_session,
        client: FlaskClient,
        valid_token_encoded: str,
        seed_meteringpoints: List[MeteringPoint],
    ):
        # -- Arrange ---------------------------------------------------------

        mp_list = seed_session
        mp_gsrn_list = [o.gsrn for o in mp_list]

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [mp_gsrn_list[0]],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert len(r.json['meteringpoints']) == 1

        fetched_mp = r.json['meteringpoints'][0]
        assert fetched_mp == make_dict_of_metering_point(mp_list[0])

    def test__filter_by_multiple_gsrn__multiple_point_fetched(
        self,
        seed_session: db.Session,
        client: FlaskClient,
        valid_token_encoded: str,
        seed_meteringpoints: List[MeteringPoint],
    ):
        # -- Arrange ---------------------------------------------------------

        seed_meteringpoints = {m.gsrn: m for m in seed_meteringpoints}

        # mp_list = seed_session
        # mp_gsrn_list = [o.gsrn for o in mp_list]

        gsrn_list = [m.gsrn for m in seed_meteringpoints]
        gsrn_list.extend(('foo', 'bar'))

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            },
            json={
                'offset': 0,
                'limit': 100,
                'filters': {
                    'gsrn': gsrn_list,
                },
            },
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200

        for meteringpoint in r.json['meteringpoints']:
            expected = seed_meteringpoints[meteringpoint.gsrn]
            assert make_dict_of_metering_point(meteringpoint) == expected

        # # assert len(r.json['meteringpoints']) == len(mp_gsrn_list)
        #
        # # Validate that the inserted metering points is also fetched
        # for mp in mp_list:
        #     mp_dict = make_dict_of_metering_point(mp)
        #
        #     # Find fetched meteringpoint by gsrn
        #     needle = mp_dict['gsrn']
        #     haystack = r.json['meteringpoints']
        #
        #     filtered = filter(lambda obj: obj['gsrn'] == needle, haystack)
        #     fetched_mp = next(filtered, None)
        #
        #     if fetched_mp is None:
        #         assert False, 'One or more meteringpoints were not fetched'
        #
        #     assert fetched_mp == mp_dict

    def test__filter_by_meteringpoint_type__correct_meteringpoints_fetched(
        self,
        seed_session: List[MeteringPoint],
        client: FlaskClient,
        valid_token_encoded: str,
    ):
        # -- Arrange ---------------------------------------------------------

        mp_list = seed_session
        mp_type = EnergyDirection.consumption

        expected_mp_list = [o for o in mp_list if o.type == mp_type]

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 100,
                'filters': {
                    'type': mp_type.value,
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------
        assert len(r.json['meteringpoints']) == len(expected_mp_list)

        # Validate that the inserted metering points is also fetched
        for mp in expected_mp_list:
            mp_dict = make_dict_of_metering_point(mp)

            # Find fetched meteringpoint by gsrn
            needle = mp_dict['gsrn']
            haystack = r.json['meteringpoints']

            filtered = filter(lambda obj: obj['gsrn'] == needle, haystack)
            fetched_mp = next(filtered, None)

            if fetched_mp is None:
                assert False, 'One or more meteringpoints were not fetched'

            assert fetched_mp == mp_dict

    def test__filter_by_single_sector__correct_meteringpoints_fetched(
        self,
        seed_session: List[MeteringPoint],
        client: FlaskClient,
        valid_token_encoded: str,
    ):
        # -- Arrange ---------------------------------------------------------

        mp_list = seed_session
        sector = mp_sectors[0]

        expected_mp_list = [o for o in mp_list if o.sector == sector]

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 100,
                'filters': {
                    'sector': [sector],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == len(expected_mp_list)

        # Validate that the inserted metering points is also fetched
        for mp in expected_mp_list:
            mp_dict = make_dict_of_metering_point(mp)

            # Find fetched meteringpoint by gsrn
            needle = mp_dict['gsrn']
            haystack = r.json['meteringpoints']

            filtered = filter(lambda obj: obj['gsrn'] == needle, haystack)
            fetched_mp = next(filtered, None)

            if fetched_mp is None:
                assert False, 'One or more meteringpoints were not fetched'

            assert fetched_mp == mp_dict

    def test__filter_by_multiple_sectors__correct_meteringpoints_fetched(
        self,
        seed_session: List[MeteringPoint],
        client: FlaskClient,
        valid_token_encoded: str,
    ):
        # -- Arrange ---------------------------------------------------------

        mp_list = seed_session
        sector_list = [mp_sectors[0], mp_sectors[1]]

        expected_mp_list = [o for o in mp_list if o.sector in sector_list]

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 100,
                'filters': {
                    'sector': sector_list,
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------
        assert len(r.json['meteringpoints']) == len(expected_mp_list)

        # Validate that the inserted metering points is also fetched
        for mp in expected_mp_list:
            mp_dict = make_dict_of_metering_point(mp)

            # Find fetched meteringpoint by gsrn
            needle = mp_dict['gsrn']
            haystack = r.json['meteringpoints']

            filtered = filter(lambda obj: obj['gsrn'] == needle, haystack)
            fetched_mp = next(filtered, None)

            if fetched_mp is None:
                assert False, 'One or more meteringpoints were not fetched'

            assert fetched_mp == mp_dict

    def test__filter_by_invalid_gsrn__no_points_fetched(
        self,
        seed_session: List[MeteringPoint],
        client: FlaskClient,
        valid_token_encoded: str,
    ):
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [""],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert len(r.json['meteringpoints']) == 0
        assert r.json == {
            'meteringpoints': [],
            'success': True,
            'total': 0
        }

    @pytest.mark.parametrize("sector", ["", "invalid-sector"])
    def test__filter_by_empty_sector__no_points_fetched(
        self,
        seed_session: List[MeteringPoint],
        client: FlaskClient,
        valid_token_encoded: str,
        sector: str,
    ):
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'sector': [sector],
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------
        assert r.status_code == 200
        assert r.json == {
            'meteringpoints': [],
            'success': True,
            'total': 0
        }

    def test__filter_by_invalid_type__no_points_fetched(
        self,
        seed_session: List[MeteringPoint],
        client: FlaskClient,
        valid_token_encoded: str,
    ):
        # -- Arrange ---------------------------------------------------------

        # -- Act -------------------------------------------------------------

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'type': "invalid-type",
                },
            },
            headers={
                'Authorization': f'Bearer: {valid_token_encoded}',
            }
        )

        # -- Assert ----------------------------------------------------------
        assert r.status_code == 400
