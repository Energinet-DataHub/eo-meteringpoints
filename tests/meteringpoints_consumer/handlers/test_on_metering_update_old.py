from flask.testing import FlaskClient

from energytt_platform.tokens import TokenEncoder
from energytt_platform.bus.messages.meteringpoints import MeteringPointUpdate
from meteringpoints_consumer.handlers import dispatcher
from meteringpoints_shared.db import db

from typing import List
from flask.testing import FlaskClient


from energytt_platform.tokens import TokenEncoder


from energytt_platform.bus.messages.meteringpoints import MeteringPointUpdate
from energytt_platform.bus.messages.tech import TechnologyUpdate
from energytt_platform.bus.messages.delegates \
    import MeteringPointDelegateGranted

from energytt_platform.models.delegates import MeteringPointDelegate

from meteringpoints_consumer.handlers import dispatcher

from meteringpoints_shared.db import db

from .helpers import \
    get_all_technology_codes, \
    get_dummy_token, \
    get_dummy_meteringpoint, \
    get_dummy_meteringpoint_list


class TestMeteringPointUpdate:

    def test__meteringpoint_update__single_meteringpoint_added(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST#1 Single point added and fetched result matches
                TEST#1.1 meteringpoint.technology matches
                TEST#1.2 meteringpoint.address matches
                TEST#1.3 meteringpoint.sector matches
                TEST#1.4 meteringpoint.type matches
                TEST#1.5 meteringpoint.sector matches

            Addtionally tests the following:
                - Correct amount of meteringpoints returned
                - HTTP status code

        Steps:
            1. Create dummy meteringpoint
            2. Insert dummy point
            3. Fetch meteringpoint using /list
            4. Assert fetched meteringpoint equals the dummy meteringpoint
        """

        # -- Arrange ---------------------------------------------------------

        subject = 'foo'

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        mp = get_dummy_meteringpoint(
            number=1,
            include_address=True,
            include_technology=True,
        )

        # -- Act -------------------------------------------------------------

        # insert technology codes needed to read technology
        for technology in get_all_technology_codes():
            dispatcher(TechnologyUpdate(
                technology=technology
            ))

        # Insert single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=mp
        ))

        # Delegate access, needed to fetch it using api
        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=mp.gsrn,
            )
        ))

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [mp.gsrn],
                },
            },
            headers={
                'Authorization': f'Bearer: {token}'
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 1

        address = mp.address
        assert r.json['meteringpoints'] == [
            {
                'gsrn': mp.gsrn,
                'type': mp.type.value,
                'sector': mp.sector,
                'technology': {
                    'fuel_code': mp.technology.fuel_code,
                    'tech_code': mp.technology.tech_code,
                    'type': mp.technology.type.value,
                },
                'address': {
                    'street_code': address.street_code,
                    'street_name': address.street_name,
                    'building_number': address.building_number,
                    'floor_id': address.floor_id,
                    'room_id': address.room_id,
                    'post_code': address.post_code,
                    'city_name': address.city_name,
                    'city_sub_division_name': address.city_sub_division_name,
                    'municipality_code': address.municipality_code,
                    'location_description': address.location_description,
                }
            }
        ]

    def test__meteringpoint_update__single_meteringpoint_added_and_updated(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_2 Single point added then updated and fetched result matches
                TEST_2.1 meteringpoint.technology matches
                TEST_2.2 meteringpoint.address matches
                TEST_2.3 meteringpoint.sector matches
                TEST_2.4 meteringpoint.type matches
                TEST_2.5 meteringpoint.sector matches

            Addtionally tests the following:
                - Correct amount of meteringpoints returned
                - HTTP status code

        Steps:
            1. Create 1st dummy meteringpoint
            2. Create 2rd dummy meteringpoint with new values but same gsrn
            3. Insert 1st dummy point
            4. Insert/update 1st dummy meteringpoint with the 2rd meteringpoint
            5. Fetch meteringpoint using /list
            6. Assert fetched meteringpoint equals the 2rd dummy meteringpoint
        """

        # -- Arrange ---------------------------------------------------------

        subject = 'foo'

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        static_gsrn = 'GSRN1'

        mp_old = get_dummy_meteringpoint(
            1,
            use_gsrn=static_gsrn,  # Static GSRN needed to update again
            include_address=True,
            include_technology=True,
        )

        mp = get_dummy_meteringpoint(
            2,  # Get new variant with new properties
            use_gsrn=static_gsrn,  # Static GSRN needed to update again
            include_address=True,
            include_technology=True,
        )

        # insert technology codes needed to read technology
        for technology in get_all_technology_codes():
            dispatcher(TechnologyUpdate(
                technology=technology
            ))

        # -- Act -------------------------------------------------------------

        # Insert original single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=mp_old,
        ))

        # Update dummy metering point with updated version
        dispatcher(MeteringPointUpdate(
            meteringpoint=mp,
        ))

        # Delegate access, needed to fetch it using api
        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=mp_old.gsrn,
            )
        ))

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [mp_old.gsrn],
                },
            },
            headers={
                'Authorization': f'Bearer: {token}'
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 1

        address = mp.address
        assert r.json['meteringpoints'] == [
            {
                'gsrn': mp.gsrn,
                'type': mp.type.value,
                'sector': mp.sector,
                'technology': {
                    'fuel_code': mp.technology.fuel_code,
                    'tech_code': mp.technology.tech_code,
                    'type': mp.technology.type.value,
                },
                'address': {
                    'street_code': address.street_code,
                    'street_name': address.street_name,
                    'building_number': address.building_number,
                    'floor_id': address.floor_id,
                    'room_id': address.room_id,
                    'post_code': address.post_code,
                    'city_name': address.city_name,
                    'city_sub_division_name': address.city_sub_division_name,
                    'municipality_code': address.municipality_code,
                    'location_description': address.location_description,
                }
            }
        ]

    def test__meteringpoint_update__multiple_meteringpoints_added(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_3 Multiple points added and fetched result matches
                TEST_3.1 Fetched meteringpoint count matches inserted count
                TEST_3.2 Fetched meteringpoints matches inserted meteringpoint
                TEST_3.3 Received status code 200

            Addtionally tests the following:

        Steps:
            1. Create 10 dummy meteringpoints with different gsrn
            2. Insert dummy meteringpoints
            2. Delegate access for each gsrn
            3. Fetchs meteringpoints using /list
            4. Compare each dummy meteringpoint with fetched meteringpoint
        """

        # -- Arrange ---------------------------------------------------------

        subject = 'foo'

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        # Amount of meteringpoints to insert
        meteringpoint_count = 10

        # Create a list of dummy meteringpoints
        dummy_meteringpoint_list = get_dummy_meteringpoint_list(
            meteringpoint_count,
            include_address=True,
            include_technology=True,
        )

        dummy_meteringpoint_gsrn_list = [
            o.gsrn for o in dummy_meteringpoint_list]

        # insert technology codes needed to read technology
        for technology in get_all_technology_codes():
            dispatcher(TechnologyUpdate(
                technology=technology
            ))

        # -- Act -------------------------------------------------------------

        for dummy_meteringpoint in dummy_meteringpoint_list:
            # Insert metering point
            dispatcher(MeteringPointUpdate(
                meteringpoint=dummy_meteringpoint,
            ))

            # Delegate access, needed to fetch it using api
            dispatcher(MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=subject,
                    gsrn=dummy_meteringpoint.gsrn,
                )
            ))

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': dummy_meteringpoint_gsrn_list,
                },
            },
            headers={
                'Authorization': f'Bearer: {token}',
            }
        )

        # -- Assert ----------------------------------------------------------

        mp_count = len(r.json['meteringpoints'])
        dummy_mp_count = len(dummy_meteringpoint_gsrn_list)
        assert mp_count == dummy_mp_count

        # Loop each inserted dummy meteringpoint and check that
        # it exists in the fetched output
        for mp in dummy_meteringpoint_list:
            # Find fetched meteringpoint matching dummy mp
            fetched_mp = None
            for x in r.json['meteringpoints']:
                if x['gsrn'] == mp.gsrn:
                    fetched_mp = x

            if fetched_mp is None:
                assert False, 'One or more meteringpoints were not fetched'

            address = mp.address
            assert fetched_mp == {
                'gsrn': mp.gsrn,
                'type': mp.type.value,
                'sector': mp.sector,
                'technology': {
                    'fuel_code': mp.technology.fuel_code,
                    'tech_code': mp.technology.tech_code,
                    'type': mp.technology.type.value,
                },
                'address': {
                    'street_code': address.street_code,
                    'street_name': address.street_name,
                    'building_number': address.building_number,
                    'floor_id': address.floor_id,
                    'room_id': address.room_id,
                    'post_code': address.post_code,
                    'city_name': address.city_name,
                    'city_sub_division_name': address.city_sub_division_name,
                    'municipality_code': address.municipality_code,
                    'location_description': mp.address.location_description,
                }
            }
