from datetime import datetime, timedelta, timezone
from typing import List
from flask.testing import FlaskClient


from energytt_platform.tokens import TokenEncoder

from energytt_platform.bus.messages.meteringpoints import MeteringPointAddressUpdate, MeteringPointRemoved, MeteringPointTechnologyUpdate

from energytt_platform.bus.messages.meteringpoints import MeteringPointUpdate
from energytt_platform.bus.messages.tech import TechnologyUpdate
from energytt_platform.bus.messages.delegates \
    import MeteringPointDelegateGranted

from energytt_platform.models.tech import Technology, TechnologyCodes, TechnologyType
from energytt_platform.models.common import Address, EnergyDirection
from energytt_platform.models.meteringpoints import MeteringPoint
from energytt_platform.models.delegates import MeteringPointDelegate
from energytt_platform.models.auth import InternalToken

from meteringpoints_consumer.handlers import dispatcher

from meteringpoints_shared.db import db


'''

    TEST_1 Single point added and fetched result matches
        TEST_1.1 metering_point.technology matches
        TEST_1.2 metering_point.address matches
        TEST_1.3 metering_point.sector matches
        TEST_1.4 metering_point.type matches
        TEST_1.5 metering_point.sector matches

    TEST_2 Single point added then updated and fetched result matches
        TEST_2.1 metering_point.technology matches
        TEST_2.2 metering_point.address matches
        TEST_2.3 metering_point.sector matches
        TEST_2.4 metering_point.type matches
        TEST_2.5 metering_point.sector matches

    TEST_3 Multiple points added and fetched result matches
        TEST_3.1 Fetched metering_point count matches inserted metering_point count
        TEST_3.2 Fetched metering_points matches inserted metering_point
        TEST_3.3 Received status code 200

    TEST_4 Create/Update/remove metering_point.address
        TEST_4.1 Insert metering_point.address
        TEST_4.2 Update metering_point address
        TEST_4.3 Remove metering_point address

    TEST_5 Create/Update/remove metering_point.technology
        TEST_5.1 Insert metering_point.technology
        TEST_5.2 Update metering_point.technology
        TEST_5.3 Remove metering_point.technology

    TEST_6 Remove metering_point 
        TEST_6.1 Remove metering_point using on_meteringpoint_removed handler

    ### /list requests
    - Test scope
        - using_correct_scope__point_fetched
        - using_incorrect_scope__no_point_fetched

    - Test filters parameter
        - Valid filters
            - filter_by_single_gsrn__single_point_fetched
            - filter_by_multiple_gsrn__muliple_points_fetched

            - filter_by_single_type__single_point_fetched
            - filter_by_multiple_types__multiple_points_fetched

            - filter_by_single_sector__single_point_fetched
            - filter_by_multiple_sectors__multiple_points_fetched

            - filter_by_gsrn_type__points_fetched
            - filter_by_gsrn_sector__points_fetched
            - filter_by_gsrn_type_sector__points_fetched

        - Invalid filters
            - filter_by_invalid_gsrn__expected_error
            - filter_by_invalid_sector__expected_error
            - filter_by_invalid_type__expected_error

    - Test offset parameter
        - valid_offset__points_fetched_with_offset
        - no_offset_provided__points_fetched
        - invalid_offset_type__error_expected
        - invalid_negative_offset__error_expected

    - Test limit parameter
        - valid_limit__points_limited
        - invalid_negative_limit__error_expected
        - invliad_limit_type__error_expected
        - no_limit_provided__default_limit_used

    - Test bearer token
        - no_token__expected_error
        - expired_token__expected_error
        - invalid_token__expected_error
        - invalid_scope__expected_error
        - unknown_subject__expected_error

        - using_matched_subject__points_fetched
        - using_no_matched_subject__no_points_fetched
        - using_partial_matched_subject__partial_points_fetched
        - using_subject_none__error_expected

'''


METERPING_POINT_TYPES = [
    EnergyDirection.consumption,
    EnergyDirection.production,
]

TECH_CODES = ['100', '200', '300', '400']
FUEL_CODES = ['101', '201', '301', '401']

TECHNOLOGY_TYPES = [
    TechnologyType.coal,
    TechnologyType.solar,
    TechnologyType.wind,
    TechnologyType.nuclear,
]


def get_dummy_technology(number: int) -> Technology:
    """
    Returns dummy technology
    """
    technology_types_count = len(TECHNOLOGY_TYPES)
    tech_codes_count = len(TECH_CODES)
    fuel_codes_count = len(FUEL_CODES)

    return Technology(
        type=TECHNOLOGY_TYPES[number % technology_types_count],
        tech_code=TECH_CODES[number % tech_codes_count],
        fuel_code=FUEL_CODES[number % fuel_codes_count],
    )


def get_dummy_address(number: int) -> Address:
    """
    Returns dummy address
    """
    return Address(
        street_code='street_code#'+str(number),
        street_name='street_name#'+str(number),
        building_number='building_number#'+str(number),
        floor_id='floor_id#'+str(number),
        room_id='room_id#'+str(number),
        post_code='post_code#'+str(number),
        city_name='city_name#'+str(number),
        city_sub_division_name='city_sub_division_name#'+str(number),
        municipality_code='municipality_code#'+str(number),
        location_description='location_description#'+str(number),
    )


def get_dummy_metering_point(
        number: int,
        use_gsrn: str = None,
        include_technology: bool = False,
        include_address: bool = False
) -> MeteringPoint:
    """
    Returns dummy metering_point
    """
    metering_point_type_count = len(METERPING_POINT_TYPES)

    technology = get_dummy_technology(number) if include_technology else None
    address = get_dummy_address(number) if include_address else None

    # If no gsrn is specififed generate one
    gsrn = use_gsrn
    if use_gsrn is None:
        gsrn = 'GSRN'+str(number)

    return MeteringPoint(
        gsrn=gsrn,
        sector='DK'+str(number),
        type=METERPING_POINT_TYPES[number % metering_point_type_count],
        technology=technology,
        address=address
    )


def get_dummy_metering_point_list(
    count: int,
    use_gsrn: str = None,
    include_technology: bool = False,
    include_address: bool = False
) -> List[MeteringPoint]:
    """
    Returns a list of dummy metering_points
    """
    metering_point_list = []
    for x in range(count):
        metering_point = get_dummy_metering_point(
            number=x,
            use_gsrn=use_gsrn,
            include_technology=include_technology,
            include_address=include_address,
        )
        metering_point_list.append(metering_point)

    return metering_point_list


def get_dummy_token(
    token_encoder: TokenEncoder,
    subject: str,
    actor: str = "foo",
    expired: bool = False,
    scopes: List[str] = []
):
    """
    Returns a dummy token
    """
    issued = datetime.now(timezone.utc)
    expires = datetime.now(timezone.utc) + timedelta(hours=5)

    if expired:
        expires = datetime.now(timezone.utc) - timedelta(hours=5)

    internal_token = InternalToken(
        issued=issued,
        expires=expires,
        actor=actor,
        subject=subject,
        scope=scopes,
    )

    return token_encoder.encode(internal_token)


def insert_metering_point(metering_point: MeteringPoint):
    dispatcher(MeteringPointUpdate(
        meteringpoint=metering_point
    ))


def insert_metering_points(metering_points: List[MeteringPoint]):
    for metering_point in metering_points:
        insert_metering_point(metering_point=metering_point)


def insert_all_technology_codes():

    for idx, (tech_code, fuel_code) in enumerate(zip(TECH_CODES, FUEL_CODES)):
        technology = Technology(
            tech_code=tech_code,
            fuel_code=fuel_code,
            type=TECHNOLOGY_TYPES[idx % len(TECHNOLOGY_TYPES)]
        )

        dispatcher(TechnologyUpdate(
            technology=technology
        ))


class TestMeteringPointUpdate:

    def test__metering_point_update__single_metering_point_added(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST#1 Single point added and fetched result matches
                TEST#1.1 metering_point.technology matches
                TEST#1.2 metering_point.address matches
                TEST#1.3 metering_point.sector matches
                TEST#1.4 metering_point.type matches
                TEST#1.5 metering_point.sector matches

            Addtionally tests the following:
                - Correct amount of metering_points returned
                - HTTP status code

        Steps:
            1. Create dummy metering_point
            2. Insert dummy point
            3. Fetch metering_point using /list
            4. Assert fetched metering_point equals the dummy metering_point
        """

        # -- Arrange ---------------------------------------------------------

        subject = "foo"

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        dummy_metering_point = get_dummy_metering_point(
            1,
            include_address=True,
            include_technology=True,
        )

        # -- Act -------------------------------------------------------------

        # insert technology codes needed to read technology
        insert_all_technology_codes()

        # Insert single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=dummy_metering_point
        ))

        # Delegate access, needed to fetch it using api
        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=dummy_metering_point.gsrn,
            )
        ))

        response = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [dummy_metering_point.gsrn],
                },
            },
            headers={
                'Authorization': 'Bearer: ' + token
            }
        )

        response_json = response.get_json()

        # -- Assert ----------------------------------------------------------

        assert response.status_code == 200
        assert len(response_json['meteringpoints']) == 1

        mp = response_json['meteringpoints'][0]

        assert mp['type'] == dummy_metering_point.type.value
        assert mp['sector'] == dummy_metering_point.sector

        # Compare technology
        dummy_mp_technology = dummy_metering_point.technology
        mp_technology = mp['technology']

        assert mp_technology['fuel_code'] == dummy_mp_technology.fuel_code
        assert mp_technology['tech_code'] == dummy_mp_technology.tech_code
        assert mp_technology['type'] == dummy_mp_technology.type.value

        # Compare address
        dummy_mp_address = dummy_metering_point.address
        mp_address = mp['address']

        assert mp_address['street_code'] == dummy_mp_address.street_code
        assert mp_address['street_name'] == dummy_mp_address.street_name
        assert mp_address['building_number'] == dummy_mp_address.building_number
        assert mp_address['floor_id'] == dummy_mp_address.floor_id
        assert mp_address['room_id'] == dummy_mp_address.room_id
        assert mp_address['post_code'] == dummy_mp_address.post_code
        assert mp_address['city_name'] == dummy_mp_address.city_name
        assert mp_address['city_sub_division_name'] == dummy_mp_address.city_sub_division_name
        assert mp_address['municipality_code'] == dummy_mp_address.municipality_code
        assert mp_address['location_description'] == dummy_mp_address.location_description

    def test__metering_point_update__single_metering_point_added_and_updated(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_2 Single point added then updated and fetched result matches
                TEST_2.1 metering_point.technology matches
                TEST_2.2 metering_point.address matches
                TEST_2.3 metering_point.sector matches
                TEST_2.4 metering_point.type matches
                TEST_2.5 metering_point.sector matches

            Addtionally tests the following:
                - Correct amount of metering_points returned
                - HTTP status code

        Steps:
            1. Create 1st dummy metering_point
            2. Create 2rd dummy metering_point with new values but same gsrn
            3. Insert 1st dummy point
            4. Insert/update 1st dummy metering_point with the 2rd metering_point
            5. Fetch metering_point using /list
            6. Assert fetched metering_point equals the 2rd dummy metering_point
        """

        # -- Arrange ---------------------------------------------------------

        subject = "foo"

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        static_gsrn = 'GSRN1'

        dummy_metering_point = get_dummy_metering_point(
            1,
            use_gsrn=static_gsrn,  # Static GSRN needed to update again
            include_address=True,
            include_technology=True,
        )

        dummy_metering_point_update = get_dummy_metering_point(
            2,  # Get new variant with new properties
            use_gsrn=static_gsrn,  # Static GSRN needed to update again
            include_address=True,
            include_technology=True,
        )

        # insert technology codes needed to read technology
        insert_all_technology_codes()

        # -- Act -------------------------------------------------------------

        # Insert original single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=dummy_metering_point,
        ))

        # Update dummy metering point with updated version
        dispatcher(MeteringPointUpdate(
            meteringpoint=dummy_metering_point_update,
        ))

        # Delegate access, needed to fetch it using api
        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=dummy_metering_point.gsrn,
            )
        ))

        response = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [dummy_metering_point.gsrn],
                },
            },
            headers={
                'Authorization': 'Bearer: ' + token
            }
        )

        response_json = response.get_json()

        # -- Assert ----------------------------------------------------------

        assert response.status_code == 200
        assert len(response_json['meteringpoints']) == 1

        mp = response_json['meteringpoints'][0]

        assert mp['type'] == dummy_metering_point_update.type.value
        assert mp['sector'] == dummy_metering_point_update.sector

        # Compare technology
        dummy_mp_technology = dummy_metering_point_update.technology
        mp_technology = mp['technology']

        assert mp_technology['fuel_code'] == dummy_mp_technology.fuel_code
        assert mp_technology['tech_code'] == dummy_mp_technology.tech_code
        assert mp_technology['type'] == dummy_mp_technology.type.value

        # Compare address
        dummy_mp_address = dummy_metering_point_update.address
        mp_address = mp['address']

        assert mp_address['street_code'] == dummy_mp_address.street_code
        assert mp_address['street_name'] == dummy_mp_address.street_name
        assert mp_address['building_number'] == dummy_mp_address.building_number
        assert mp_address['floor_id'] == dummy_mp_address.floor_id
        assert mp_address['room_id'] == dummy_mp_address.room_id
        assert mp_address['post_code'] == dummy_mp_address.post_code
        assert mp_address['city_name'] == dummy_mp_address.city_name
        assert mp_address['city_sub_division_name'] == dummy_mp_address.city_sub_division_name
        assert mp_address['municipality_code'] == dummy_mp_address.municipality_code
        assert mp_address['location_description'] == dummy_mp_address.location_description

    def test__metering_point_update__multiple_metering_points_added(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_3 Multiple points added and fetched result matches
                TEST_3.1 Fetched metering_point count matches inserted metering_point count
                TEST_3.2 Fetched metering_points matches inserted metering_point
                TEST_3.3 Received status code 200

            Addtionally tests the following:

        Steps:
            1. Create 10 dummy metering_points with different gsrn
            2. Insert dummy metering_points
            2. Delegate access for each gsrn
            3. Fetchs metering_points using /list
            4. Compare each dummy metering_point with fetched metering_point
        """

        # -- Arrange ---------------------------------------------------------

        subject = "foo"

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        # Amount of metering_points to insert
        meteringpoint_count = 10

        # Create a list of dummy metering_points
        dummy_metering_point_list = get_dummy_metering_point_list(
            meteringpoint_count,
            include_address=True,
            include_technology=True,
        )

        dummy_metering_point_gsrn_list = [
            o.gsrn for o in dummy_metering_point_list]

        # insert technology codes needed to read technology
        insert_all_technology_codes()

        # -- Act -------------------------------------------------------------

        for dummy_metering_point in dummy_metering_point_list:
            # Insert metering point
            dispatcher(MeteringPointUpdate(
                meteringpoint=dummy_metering_point,
            ))

            # Delegate access, needed to fetch it using api
            dispatcher(MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=subject,
                    gsrn=dummy_metering_point.gsrn,
                )
            ))

        response = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': dummy_metering_point_gsrn_list,
                },
            },
            headers={
                'Authorization': 'Bearer: ' + token
            }
        )

        response_json = response.get_json()

        # # -- Assert ----------------------------------------------------------

        assert response.status_code == 200

        fetched_mp_list = response_json['meteringpoints']

        assert len(fetched_mp_list) == len(dummy_metering_point_gsrn_list)

        def find_metering_point_by_gsrn(metering_point_list, gsrn: str):
            """
            Finds a dummy meteringpoint by gsrn if it exists.
            Returns None if not found
            """
            for x in metering_point_list:
                if x['gsrn'] == gsrn:
                    return x
            return None

        # Loop each inserted dummy metering_point and check that
        # it exists in the fetched output
        for dummy_mp in dummy_metering_point_list:
            fetched_mp = find_metering_point_by_gsrn(
                metering_point_list=fetched_mp_list,
                gsrn=dummy_mp.gsrn,
            )

            if fetched_mp is None:
                assert False, 'One or more metering points were not fetched as expected'

            assert fetched_mp['type'] == dummy_mp.type.value
            assert fetched_mp['sector'] == dummy_mp.sector

            # Compare technology
            dummy_mp_technology = dummy_mp.technology
            mp_technology = fetched_mp['technology']

            assert mp_technology['fuel_code'] == dummy_mp_technology.fuel_code
            assert mp_technology['tech_code'] == dummy_mp_technology.tech_code
            assert mp_technology['type'] == dummy_mp_technology.type.value

            # Compare address
            dummy_mp_address = dummy_mp.address
            mp_address = fetched_mp['address']

            assert mp_address['street_code'] == dummy_mp_address.street_code
            assert mp_address['street_name'] == dummy_mp_address.street_name
            assert mp_address['building_number'] == dummy_mp_address.building_number
            assert mp_address['floor_id'] == dummy_mp_address.floor_id
            assert mp_address['room_id'] == dummy_mp_address.room_id
            assert mp_address['post_code'] == dummy_mp_address.post_code
            assert mp_address['city_name'] == dummy_mp_address.city_name
            assert mp_address['city_sub_division_name'] == dummy_mp_address.city_sub_division_name
            assert mp_address['municipality_code'] == dummy_mp_address.municipality_code
            assert mp_address['location_description'] == dummy_mp_address.location_description


class TestMeteringPointAddressUpdate:
    def test__meteringpoint_address_update__address_inserted_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_4 Create/Update/remove metering_point.address
                TEST_4.1 Insert metering_point.address

            Addtionally tests the following:
                - Correct amount of metering_points returned
                - HTTP status code

        Steps:
            1. Create dummy metering_point without address
            2. Insert dummy point
            3. Insert new address to metering_point
            3. Fetch metering_point using /list
            4. Assert fetched metering_point.address equals the dummy metering_point.address
        """

        # -- Arrange ---------------------------------------------------------

        subject = "foo"

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        dummy_metering_point = get_dummy_metering_point(
            1,
            include_address=False,
            include_technology=True,
        )

        dummy_mp_address = get_dummy_address(1)

        # -- Act -------------------------------------------------------------

        # insert technology codes needed to read technology
        insert_all_technology_codes()

        # Insert single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=dummy_metering_point,
        ))

        # Insert address to metering point
        dispatcher(MeteringPointAddressUpdate(
            gsrn=dummy_metering_point.gsrn,
            address=dummy_mp_address,
        ))

        # Delegate access, needed to fetch it using api
        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=dummy_metering_point.gsrn,
            )
        ))

        response = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [dummy_metering_point.gsrn],
                },
            },
            headers={
                'Authorization': 'Bearer: ' + token
            }
        )

        response_json = response.get_json()

        # -- Assert ----------------------------------------------------------

        assert response.status_code == 200
        assert len(response_json['meteringpoints']) == 1

        mp = response_json['meteringpoints'][0]

        assert mp['type'] == dummy_metering_point.type.value
        assert mp['sector'] == dummy_metering_point.sector

        # Compare technology
        dummy_mp_technology = dummy_metering_point.technology
        mp_technology = mp['technology']

        assert mp_technology['fuel_code'] == dummy_mp_technology.fuel_code
        assert mp_technology['tech_code'] == dummy_mp_technology.tech_code
        assert mp_technology['type'] == dummy_mp_technology.type.value

        # Compare address
        mp_address = mp['address']

        assert mp_address['street_code'] == dummy_mp_address.street_code
        assert mp_address['street_name'] == dummy_mp_address.street_name
        assert mp_address['building_number'] == dummy_mp_address.building_number
        assert mp_address['floor_id'] == dummy_mp_address.floor_id
        assert mp_address['room_id'] == dummy_mp_address.room_id
        assert mp_address['post_code'] == dummy_mp_address.post_code
        assert mp_address['city_name'] == dummy_mp_address.city_name
        assert mp_address['city_sub_division_name'] == dummy_mp_address.city_sub_division_name
        assert mp_address['municipality_code'] == dummy_mp_address.municipality_code
        assert mp_address['location_description'] == dummy_mp_address.location_description

    def test__meteringpoint_address_update__address_updates_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_4 Create/Update/remove metering_point.address
                TEST_4.2 Update metering_point address

            Addtionally tests the following:
                - Correct amount of metering_points returned
                - HTTP status code

        Steps:
            1. Create dummy metering_point with address
            2. Insert dummy point
            3. Update metering_point address
            3. Fetch metering_point using /list
            4. Assert fetched metering_point.address equals the dummy metering_point.address
        """

        # -- Arrange ---------------------------------------------------------

        subject = "foo"

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        dummy_metering_point = get_dummy_metering_point(
            1,
            include_address=False,
            include_technology=True,
        )

        dummy_mp_address_old = get_dummy_address(1)
        dummy_mp_address_new = get_dummy_address(2)
        dummy_metering_point.address = dummy_mp_address_old

        # -- Act -------------------------------------------------------------

        # insert technology codes needed to read technology
        insert_all_technology_codes()

        # Insert single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=dummy_metering_point,
        ))

        # Update metering point address to the new given address
        dispatcher(MeteringPointAddressUpdate(
            gsrn=dummy_metering_point.gsrn,
            address=dummy_mp_address_new,
        ))

        # Delegate access, needed to fetch it using api
        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=dummy_metering_point.gsrn,
            )
        ))

        response = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [dummy_metering_point.gsrn],
                },
            },
            headers={
                'Authorization': 'Bearer: ' + token
            }
        )

        response_json = response.get_json()

        # -- Assert ----------------------------------------------------------

        assert response.status_code == 200
        assert len(response_json['meteringpoints']) == 1

        mp = response_json['meteringpoints'][0]

        assert mp['type'] == dummy_metering_point.type.value
        assert mp['sector'] == dummy_metering_point.sector

        # Compare technology
        dummy_mp_technology = dummy_metering_point.technology
        mp_technology = mp['technology']

        assert mp_technology['fuel_code'] == dummy_mp_technology.fuel_code
        assert mp_technology['tech_code'] == dummy_mp_technology.tech_code
        assert mp_technology['type'] == dummy_mp_technology.type.value

        # Compare address
        mp_address = mp['address']

        assert mp_address['street_code'] == dummy_mp_address_new.street_code
        assert mp_address['street_name'] == dummy_mp_address_new.street_name
        assert mp_address['building_number'] == dummy_mp_address_new.building_number
        assert mp_address['floor_id'] == dummy_mp_address_new.floor_id
        assert mp_address['room_id'] == dummy_mp_address_new.room_id
        assert mp_address['post_code'] == dummy_mp_address_new.post_code
        assert mp_address['city_name'] == dummy_mp_address_new.city_name
        assert mp_address['city_sub_division_name'] == dummy_mp_address_new.city_sub_division_name
        assert mp_address['municipality_code'] == dummy_mp_address_new.municipality_code
        assert mp_address['location_description'] == dummy_mp_address_new.location_description

    def test__meteringpoint_address_update__address_removed_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_4 Create/Update/remove metering_point.address
                TEST_4.2 Remove metering_point address


            Addtionally tests the following:
                - HTTP status code

        Steps:
            1. Create dummy metering_point with address
            2. Insert dummy point
            3. Remove metering metering_point address
            3. Fetch metering_point using /list
            4. Assert fetched metering_point.address equals None
        """

        # -- Arrange ---------------------------------------------------------

        subject = "foo"

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        dummy_metering_point = get_dummy_metering_point(
            1,
            include_address=True,
            include_technology=True,
        )

        # -- Act -------------------------------------------------------------

        # insert technology codes needed to read technology
        insert_all_technology_codes()

        # Insert single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=dummy_metering_point,
        ))

        # delete metering point address
        dispatcher(MeteringPointAddressUpdate(
            gsrn=dummy_metering_point.gsrn,
            address=None,
        ))

        # Delegate access, needed to fetch it using api
        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=dummy_metering_point.gsrn,
            )
        ))

        response = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [dummy_metering_point.gsrn],
                },
            },
            headers={
                'Authorization': 'Bearer: ' + token
            }
        )

        response_json = response.get_json()

        # -- Assert ----------------------------------------------------------

        assert response.status_code == 200
        assert len(response_json['meteringpoints']) == 1

        mp = response_json['meteringpoints'][0]

        assert mp['type'] == dummy_metering_point.type.value
        assert mp['sector'] == dummy_metering_point.sector

        # Compare technology
        dummy_mp_technology = dummy_metering_point.technology
        mp_technology = mp['technology']

        assert mp_technology['fuel_code'] == dummy_mp_technology.fuel_code
        assert mp_technology['tech_code'] == dummy_mp_technology.tech_code
        assert mp_technology['type'] == dummy_mp_technology.type.value

        # Compare address
        assert mp['address'] is None


class TestMeteringPointTechnologyUpdate:
    def test__meteringpoint_technology_update__technology_inserted_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_5 Create/Update/remove metering_point.technology
                TEST_5.1 Insert metering_point.technology

            Addtionally tests the following:
                - Correct amount of metering_points returned
                - HTTP status code

        Steps:
            1. Create dummy metering_point without technology
            2. Insert dummy point
            3. Insert new technology to metering_point
            3. Fetch metering_point using /list
            4. Assert fetched metering_point.technology equals the dummy metering_point.technology
        """

        # -- Arrange ---------------------------------------------------------

        subject = "foo"

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        dummy_metering_point = get_dummy_metering_point(
            1,
            include_address=True,
            include_technology=False,
        )

        dummy_mp_technology = get_dummy_technology(1)

        technology_code = TechnologyCodes(
            tech_code=dummy_mp_technology.tech_code,
            fuel_code=dummy_mp_technology.fuel_code
        )

        # -- Act -------------------------------------------------------------

        # insert technology codes needed to read technology
        insert_all_technology_codes()

        # Insert single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=dummy_metering_point,
        ))

        # Insert technology to metering point
        dispatcher(MeteringPointTechnologyUpdate(
            gsrn=dummy_metering_point.gsrn,
            codes=technology_code,
        ))

        # Delegate access, needed to fetch it using api
        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=dummy_metering_point.gsrn,
            )
        ))

        response = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [dummy_metering_point.gsrn],
                },
            },
            headers={
                'Authorization': 'Bearer: ' + token
            }
        )

        response_json = response.get_json()

        # -- Assert ----------------------------------------------------------

        assert response.status_code == 200
        assert len(response_json['meteringpoints']) == 1

        mp = response_json['meteringpoints'][0]

        assert mp['type'] == dummy_metering_point.type.value
        assert mp['sector'] == dummy_metering_point.sector

        # Compare technology
        mp_technology = mp['technology']

        assert mp_technology['fuel_code'] == dummy_mp_technology.fuel_code
        assert mp_technology['tech_code'] == dummy_mp_technology.tech_code
        assert mp_technology['type'] == dummy_mp_technology.type.value

        # Compare address
        mp_address = mp['address']
        dummy_mp_address = dummy_metering_point.address

        assert mp_address['street_code'] == dummy_mp_address.street_code
        assert mp_address['street_name'] == dummy_mp_address.street_name
        assert mp_address['building_number'] == dummy_mp_address.building_number
        assert mp_address['floor_id'] == dummy_mp_address.floor_id
        assert mp_address['room_id'] == dummy_mp_address.room_id
        assert mp_address['post_code'] == dummy_mp_address.post_code
        assert mp_address['city_name'] == dummy_mp_address.city_name
        assert mp_address['city_sub_division_name'] == dummy_mp_address.city_sub_division_name
        assert mp_address['municipality_code'] == dummy_mp_address.municipality_code
        assert mp_address['location_description'] == dummy_mp_address.location_description

    def test__meteringpoint_technology_update__technology_updated_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_5 Create/Update/remove metering_point.technology
                TEST_5.2 Update metering_point.technology

            Addtionally tests the following:
                - Correct amount of metering_points returned
                - HTTP status code

        Steps:
            1. Create dummy metering_point with technology
            2. Insert dummy point
            3. Create new technology
            4. Ypdate metering_point technology with new technology
            5. Fetch metering_point using /list
            6. Assert fetched metering_point.technology equals the new dummy technology
        """

        # -- Arrange ---------------------------------------------------------

        subject = "foo"

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        dummy_metering_point = get_dummy_metering_point(
            1,
            include_address=True,
            include_technology=False,
        )

        dummy_mp_technology_old = get_dummy_technology(1)
        dummy_mp_technology_new = get_dummy_technology(1)

        # Make sure inserted metering_point contains old technology
        dummy_metering_point.technology = dummy_mp_technology_old

        # -- Act -------------------------------------------------------------

        # insert technology codes needed to read technology
        insert_all_technology_codes()

        # Insert single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=dummy_metering_point,
        ))

        # Update metering point technology
        dispatcher(MeteringPointTechnologyUpdate(
            gsrn=dummy_metering_point.gsrn,
            codes=TechnologyCodes(
                tech_code=dummy_mp_technology_new.tech_code,
                fuel_code=dummy_mp_technology_new.fuel_code
            ),
        ))

        # Delegate access, needed to fetch it using api
        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=dummy_metering_point.gsrn,
            )
        ))

        response = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [dummy_metering_point.gsrn],
                },
            },
            headers={
                'Authorization': 'Bearer: ' + token
            }
        )

        response_json = response.get_json()

        # -- Assert ----------------------------------------------------------

        assert response.status_code == 200
        assert len(response_json['meteringpoints']) == 1

        mp = response_json['meteringpoints'][0]

        assert mp['type'] == dummy_metering_point.type.value
        assert mp['sector'] == dummy_metering_point.sector

        # Compare technology equals the new technology and not the old
        mp_technology = mp['technology']

        assert mp_technology['fuel_code'] == dummy_mp_technology_new.fuel_code
        assert mp_technology['tech_code'] == dummy_mp_technology_new.tech_code
        assert mp_technology['type'] == dummy_mp_technology_new.type.value

        # Compare address
        mp_address = mp['address']
        dummy_mp_address = dummy_metering_point.address

        assert mp_address['street_code'] == dummy_mp_address.street_code
        assert mp_address['street_name'] == dummy_mp_address.street_name
        assert mp_address['building_number'] == dummy_mp_address.building_number
        assert mp_address['floor_id'] == dummy_mp_address.floor_id
        assert mp_address['room_id'] == dummy_mp_address.room_id
        assert mp_address['post_code'] == dummy_mp_address.post_code
        assert mp_address['city_name'] == dummy_mp_address.city_name
        assert mp_address['city_sub_division_name'] == dummy_mp_address.city_sub_division_name
        assert mp_address['municipality_code'] == dummy_mp_address.municipality_code
        assert mp_address['location_description'] == dummy_mp_address.location_description

    def test__meteringpoint_technology_update__technology_removed_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_5 Create/Update/remove metering_point.technology
                TEST_5.3 Remove metering_point.technology

            Addtionally tests the following:
                - Correct amount of metering_points returned
                - HTTP status code

        Steps:
            1. Create dummy metering_point with technology
            2. Insert dummy point
            3. Remove metering_point technology
            5. Fetch metering_point using /list
            6. Assert fetched metering_point.technology equals None
        """

        # -- Arrange ---------------------------------------------------------

        subject = "foo"

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        dummy_metering_point = get_dummy_metering_point(
            1,
            include_address=True,
            include_technology=True,
        )

        # -- Act -------------------------------------------------------------

        # insert technology codes needed to read technology
        insert_all_technology_codes()

        # Insert single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=dummy_metering_point,
        ))

        # Remove metering_point.technology by setting it to None
        dispatcher(MeteringPointTechnologyUpdate(
            gsrn=dummy_metering_point.gsrn,
            codes=None,
        ))

        # Delegate access, needed to fetch it using api
        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=dummy_metering_point.gsrn,
            )
        ))

        response = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [dummy_metering_point.gsrn],
                },
            },
            headers={
                'Authorization': 'Bearer: ' + token
            }
        )

        response_json = response.get_json()

        # -- Assert ----------------------------------------------------------

        assert response.status_code == 200
        assert len(response_json['meteringpoints']) == 1

        mp = response_json['meteringpoints'][0]

        assert mp['type'] == dummy_metering_point.type.value
        assert mp['sector'] == dummy_metering_point.sector

        # Compare technology - None => Deleted
        assert mp['technology'] is None

        # Compare address
        mp_address = mp['address']
        dummy_mp_address = dummy_metering_point.address

        assert mp_address['street_code'] == dummy_mp_address.street_code
        assert mp_address['street_name'] == dummy_mp_address.street_name
        assert mp_address['building_number'] == dummy_mp_address.building_number
        assert mp_address['floor_id'] == dummy_mp_address.floor_id
        assert mp_address['room_id'] == dummy_mp_address.room_id
        assert mp_address['post_code'] == dummy_mp_address.post_code
        assert mp_address['city_name'] == dummy_mp_address.city_name
        assert mp_address['city_sub_division_name'] == dummy_mp_address.city_sub_division_name
        assert mp_address['municipality_code'] == dummy_mp_address.municipality_code
        assert mp_address['location_description'] == dummy_mp_address.location_description


class TestMeteringPointRemoved:
    def test__metering_point_removed__metering_point_removed(
        self,
        session: db.Session,
        client: FlaskClient,
        token_encoder: TokenEncoder,
    ):
        """
        TEST_6 Remove metering_point 
            TEST_6.1 Remove metering_point using on_meteringpoint_removed handler

        Addtionally tests the following:
            -

        Steps:
            1. Create multiple dummy metering_points with different gsrn
            2. Insert dummy metering_points
            3. Delegate access for each gsrn
            4. Remove 1 metering_point
            3. Fetchs metering_points using /list
            4. Check that the correct metering_point has been removed
        """

        # -- Arrange ---------------------------------------------------------

        subject = "foo"

        token = get_dummy_token(
            token_encoder=token_encoder,
            subject=subject,
            scopes=[
                'meteringpoints.read',
            ],
        )

        # Amount of metering_points to insert
        meteringpoint_count = 5

        # Create a list of dummy metering_points
        dummy_metering_point_list = get_dummy_metering_point_list(
            meteringpoint_count,
            include_address=True,
            include_technology=True,
        )

        # Get list of metering_point's gsrn
        dummy_metering_point_gsrn_list = [
            o.gsrn for o in dummy_metering_point_list]

        # metering_point to be removed
        gsrn_to_be_remove = dummy_metering_point_gsrn_list[0]

        # insert technology codes needed to read technology
        insert_all_technology_codes()

        # -- Act -------------------------------------------------------------

        for dummy_metering_point in dummy_metering_point_list:
            # Insert metering point
            dispatcher(MeteringPointUpdate(
                meteringpoint=dummy_metering_point,
            ))

            # Delegate access, needed to fetch it using api
            dispatcher(MeteringPointDelegateGranted(
                delegate=MeteringPointDelegate(
                    subject=subject,
                    gsrn=dummy_metering_point.gsrn,
                )
            ))

        dispatcher(MeteringPointRemoved(
            gsrn=gsrn_to_be_remove,
        ))

        response = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 20,
                'filters': {
                    'gsrn': dummy_metering_point_gsrn_list,
                },
            },
            headers={
                'Authorization': 'Bearer: ' + token
            }
        )

        response_json = response.get_json()

        # -- Assert ----------------------------------------------------------

        assert response.status_code == 200

        fetched_mp_list = response_json['meteringpoints']

        expected_metering_point_count = len(dummy_metering_point_gsrn_list) - 1
        assert len(fetched_mp_list) == expected_metering_point_count

        def find_metering_point_by_gsrn(metering_point_list, gsrn: str):
            """
            Finds a dummy meteringpoint by gsrn if it exists.
            Returns None if not found
            """
            for x in metering_point_list:
                if x['gsrn'] == gsrn:
                    return x
            return None

        # Loop each inserted dummy metering_point and check that
        # it exists in the fetched output
        for dummy_mp in dummy_metering_point_list:
            fetched_mp = find_metering_point_by_gsrn(
                metering_point_list=fetched_mp_list,
                gsrn=dummy_mp.gsrn,
            )

            if dummy_mp.gsrn == gsrn_to_be_remove:
                # Check if removed metering_point is actually removed
                assert fetched_mp is None
                continue
            elif fetched_mp is None:
                assert False, 'One or more metering points(excl. deleted mp) were not fetched as expected'

            assert fetched_mp['type'] == dummy_mp.type.value
            assert fetched_mp['sector'] == dummy_mp.sector

            # Compare technology
            dummy_mp_technology = dummy_mp.technology
            mp_technology = fetched_mp['technology']

            assert mp_technology['fuel_code'] == dummy_mp_technology.fuel_code
            assert mp_technology['tech_code'] == dummy_mp_technology.tech_code
            assert mp_technology['type'] == dummy_mp_technology.type.value

            # Compare address
            dummy_mp_address = dummy_mp.address
            mp_address = fetched_mp['address']

            assert mp_address['street_code'] == dummy_mp_address.street_code
            assert mp_address['street_name'] == dummy_mp_address.street_name
            assert mp_address['building_number'] == dummy_mp_address.building_number
            assert mp_address['floor_id'] == dummy_mp_address.floor_id
            assert mp_address['room_id'] == dummy_mp_address.room_id
            assert mp_address['post_code'] == dummy_mp_address.post_code
            assert mp_address['city_name'] == dummy_mp_address.city_name
            assert mp_address['city_sub_division_name'] == dummy_mp_address.city_sub_division_name
            assert mp_address['municipality_code'] == dummy_mp_address.municipality_code
            assert mp_address['location_description'] == dummy_mp_address.location_description
