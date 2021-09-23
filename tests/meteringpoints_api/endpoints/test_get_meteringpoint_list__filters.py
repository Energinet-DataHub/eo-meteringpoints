from typing import List
import pytest
from itertools import product
from flask.testing import FlaskClient

from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from meteringpoints_consumer.handlers import dispatcher


from ...helpers import \
    METERPING_POINT_TYPES, \
    get_dummy_address, \
    get_dummy_meteringpoint_list, \
    get_dummy_technology, \
    get_dummy_token, \
    insert_meteringpoint_and_delegate_access_to_subject, \
    insert_technology_from_meteringpoint, \
    make_dict_of_metering_point, \
    get_dummy_meteringpoint


mp_types = METERPING_POINT_TYPES
mp_sectors = ('SECTOR_1', 'SECTOR_2')

combinations = product(
    mp_types, mp_sectors
)


class TestGetMeteringPointListFilters:
    @pytest.fixture(scope='function')
    def seed_session(self, session: db.Session) -> List[MeteringPoint]:
        mp_list = []

        for i, (mp_type, mp_sector) in \
                enumerate(combinations, start=1):
            gsrn = f'GSRN#{i}'
            mp = MeteringPoint(
                gsrn=gsrn,
                type=mp_type,
                sector=mp_sector,
                technology=None,
                address=None,
            )

            insert_meteringpoint_and_delegate_access_to_subject(
                meteringpoint=mp,
                token_subject='bar',
            )
            mp_list.append(mp)

        return mp_list

    def test__filter_by_single_gsrn__single_point_fetched(
        self,
        seed_session,
        client: FlaskClient,
        valid_token_encoded: str,
    ):
        # -- Arrange ---------------------------------------------------------

        mp_gsrn_list = [o.gsrn for o in seed_session]

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
