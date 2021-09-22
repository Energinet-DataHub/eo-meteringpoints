from flask.testing import FlaskClient

from energytt_platform.bus.messages.meteringpoints import MeteringPointAddressUpdate, MeteringPointUpdate

from meteringpoints_consumer.handlers import dispatcher

from meteringpoints_shared.db import db

from .helpers import \
    insert_meteringpoint_and_delegate_access_to_subject, \
    make_dict_of_metering_point, \
    insert_technology_from_meteringpoint, \
    get_dummy_meteringpoint, \
    get_dummy_meteringpoint_list, \
    get_dummy_address, \
    get_dummy_technology


class TestMeteringPointAddressUpdate:
    def test__meteringpoint_address_update__address_inserted_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """
        Test Case(s):
            TEST_4 Create/Update/remove meteringpoint.address
                TEST_4.1 Insert meteringpoint.address

            Addtionally tests the following:
                - Correct amount of meteringpoints returned
                - HTTP status code

        Steps:
            1. Create dummy meteringpoint without address
            2. Insert dummy point
            3. Insert new address to meteringpoint
            3. Fetch meteringpoint using /list
            4. Assert fetched address equals the dummy address
        """

        # -- Arrange ---------------------------------------------------------

        subject = 'bar'

        mp = get_dummy_meteringpoint(
            number=1,
            include_address=False,
            include_technology=True,
        )

        address = get_dummy_address(1)

        insert_technology_from_meteringpoint(
            meteringpoint=mp
        )

        # Insert single metering point
        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )
        
        mp.address = address

        expected_result = make_dict_of_metering_point(mp)

        # -- Act -------------------------------------------------------------
        
        # Insert address to metering point
        dispatcher(MeteringPointAddressUpdate(
            gsrn=mp.gsrn,
            address=address,
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
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 1

        assert r.json['meteringpoints'][0] == expected_result

    def test__meteringpoint_address_update__address_updates_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """
        Test Case(s):
            TEST_4 Create/Update/remove meteringpoint.address
                TEST_4.2 Update meteringpoint address

            Addtionally tests the following:
                - Correct amount of meteringpoints returned
                - HTTP status code

        Steps:
            1. Create dummy meteringpoint with address
            2. Insert dummy point
            3. Update meteringpoint address
            3. Fetch meteringpoint using /list
            4. Assert fetched mp.address equals the dummy mp.address
        """

        # -- Arrange ---------------------------------------------------------

        subject = 'bar'

        mp = get_dummy_meteringpoint(
            number=1,
            include_address=True,
            include_technology=True,
        )

        # Create new address with difference values from mp.address
        address = get_dummy_address(2)

        insert_technology_from_meteringpoint(
            meteringpoint=mp
        )

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

        # -- Act -------------------------------------------------------------

        # Update metering point address to the new given address
        dispatcher(MeteringPointAddressUpdate(
            gsrn=mp.gsrn,
            address=address,
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
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

        # -- Assert ----------------------------------------------------------
        mp.address = address
        expected_result = make_dict_of_metering_point(mp)

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 1

        assert r.json['meteringpoints'][0] == expected_result

    def test__meteringpoint_address_update__address_removed_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            valid_token_encoded: str,
    ):
        """
        Test Case(s):
            TEST_4 Create/Update/remove meteringpoint.address
                TEST_4.2 Remove meteringpoint address


            Addtionally tests the following:
                - HTTP status code

        Steps:
            1. Create dummy meteringpoint with address
            2. Insert dummy point
            3. Remove metering meteringpoint address
            3. Fetch meteringpoint using /list
            4. Assert fetched meteringpoint.address equals None
        """

        # -- Arrange ---------------------------------------------------------

        subject = 'bar'

        mp = get_dummy_meteringpoint(
            number=1,
            include_address=True,
            include_technology=True,
        )

        insert_technology_from_meteringpoint(
            meteringpoint=mp
        )

        insert_meteringpoint_and_delegate_access_to_subject(
            meteringpoint=mp,
            token_subject=subject,
        )

        # -- Act -------------------------------------------------------------

        # delete metering point address
        dispatcher(MeteringPointAddressUpdate(
            gsrn=mp.gsrn,
            address=None,
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
                'Authorization': f'Bearer: {valid_token_encoded}'
            }
        )

        # -- Assert ----------------------------------------------------------
        mp.address = None
        expected_result = make_dict_of_metering_point(mp)
        assert r.status_code == 200
        assert r.json['meteringpoints'][0] == expected_result
