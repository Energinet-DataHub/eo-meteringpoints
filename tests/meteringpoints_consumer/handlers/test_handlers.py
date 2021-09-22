from datetime import datetime, timedelta, timezone
from typing import List
from flask.testing import FlaskClient


from energytt_platform.tokens import TokenEncoder

from energytt_platform.bus.messages.meteringpoints import \
    MeteringPointAddressUpdate, MeteringPointTechnologyUpdate

from energytt_platform.bus.messages.meteringpoints import MeteringPointUpdate
from energytt_platform.bus.messages.tech import TechnologyUpdate
from energytt_platform.bus.messages.delegates \
    import MeteringPointDelegateGranted

from energytt_platform.models.tech import \
    Technology, TechnologyCodes, TechnologyType
from energytt_platform.models.common import Address, EnergyDirection
from energytt_platform.models.meteringpoints import MeteringPoint
from energytt_platform.models.delegates import MeteringPointDelegate
from energytt_platform.models.auth import InternalToken

from meteringpoints_consumer.handlers import dispatcher

from meteringpoints_shared.db import db


'''

    TEST_1 Single point added and fetched result matches
        TEST_1.1 meteringpoint.technology matches
        TEST_1.2 meteringpoint.address matches
        TEST_1.3 meteringpoint.sector matches
        TEST_1.4 meteringpoint.type matches
        TEST_1.5 meteringpoint.sector matches

    TEST_2 Single point added then updated and fetched result matches
        TEST_2.1 meteringpoint.technology matches
        TEST_2.2 meteringpoint.address matches
        TEST_2.3 meteringpoint.sector matches
        TEST_2.4 meteringpoint.type matches
        TEST_2.5 meteringpoint.sector matches

    TEST_3 Multiple points added and fetched result matches
        TEST_3.1 Fetched meteringpoint count matches inserted count
        TEST_3.2 Fetched meteringpoints matches inserted meteringpoint
        TEST_3.3 Received status code 200

    TEST_4 Create/Update/remove meteringpoint.address
        TEST_4.1 Insert meteringpoint.address
        TEST_4.2 Update meteringpoint address
        TEST_4.3 Remove meteringpoint address

    TEST_5 Create/Update/remove meteringpoint.technology
        TEST_5.1 Insert meteringpoint.technology
        TEST_5.2 Update meteringpoint.technology
        TEST_5.3 Remove meteringpoint.technology

    TEST_6 Remove meteringpoint
        TEST_6.1 Remove meteringpoint using on_meteringpoint_removed handler

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


def get_dummy_meteringpoint(
        number: int,
        use_gsrn: str = None,
        include_technology: bool = False,
        include_address: bool = False
) -> MeteringPoint:
    """
    Returns dummy meteringpoint
    """
    meteringpoint_type_count = len(METERPING_POINT_TYPES)

    technology = get_dummy_technology(number) if include_technology else None
    address = get_dummy_address(number) if include_address else None

    # If no gsrn is specififed generate one
    gsrn = use_gsrn
    if use_gsrn is None:
        gsrn = 'GSRN'+str(number)

    return MeteringPoint(
        gsrn=gsrn,
        sector='DK'+str(number),
        type=METERPING_POINT_TYPES[number % meteringpoint_type_count],
        technology=technology,
        address=address
    )


def get_dummy_meteringpoint_list(
    count: int,
    use_gsrn: str = None,
    include_technology: bool = False,
    include_address: bool = False
) -> List[MeteringPoint]:
    """
    Returns a list of dummy meteringpoints
    """
    meteringpoint_list = []
    for x in range(count):
        meteringpoint = get_dummy_meteringpoint(
            number=x,
            use_gsrn=use_gsrn,
            include_technology=include_technology,
            include_address=include_address,
        )
        meteringpoint_list.append(meteringpoint)

    return meteringpoint_list


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


def get_all_technology_codes():
    for idx, (tech_code, fuel_code) in enumerate(zip(TECH_CODES, FUEL_CODES)):
        yield Technology(
            tech_code=tech_code,
            fuel_code=fuel_code,
            type=TECHNOLOGY_TYPES[idx % len(TECHNOLOGY_TYPES)]
        )


class TestMeteringPointAddressUpdate:
    def test__meteringpoint_address_update__address_inserted_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
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
            include_address=False,
            include_technology=True,
        )

        address = get_dummy_address(1)

        # -- Act -------------------------------------------------------------

        # insert technology codes needed to read technology
        for technology in get_all_technology_codes():
            dispatcher(TechnologyUpdate(
                technology=technology
            ))

        # Insert single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=mp,
        ))

        # Insert address to metering point
        dispatcher(MeteringPointAddressUpdate(
            gsrn=mp.gsrn,
            address=address,
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
                'Authorization': f'Bearer: {token}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 1

        # Compare address
        assert r.json['meteringpoints'][0]['address'] == {
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

    def test__meteringpoint_address_update__address_updates_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
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

        address = get_dummy_address(2)

        # -- Act -------------------------------------------------------------

        # insert technology codes needed to read technology
        for technology in get_all_technology_codes():
            dispatcher(TechnologyUpdate(
                technology=technology
            ))

        # Insert single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=mp,
        ))

        # Update metering point address to the new given address
        dispatcher(MeteringPointAddressUpdate(
            gsrn=mp.gsrn,
            address=address,
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
                'Authorization': f'Bearer: {token}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 1

        # Compare address
        assert r.json['meteringpoints'][0]['address'] == {
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

    def test__meteringpoint_address_update__address_removed_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
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
            meteringpoint=mp,
        ))

        # delete metering point address
        dispatcher(MeteringPointAddressUpdate(
            gsrn=mp.gsrn,
            address=None,
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
                'Authorization': f'Bearer: {token}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert r.json['meteringpoints'][0]['address'] is None


class TestMeteringPointTechnologyUpdate:
    def test__meteringpoint_technology_update__technology_inserted_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_5 Create/Update/remove meteringpoint.technology
                TEST_5.1 Insert meteringpoint.technology

            Addtionally tests the following:
                - Correct amount of meteringpoints returned
                - HTTP status code

        Steps:
            1. Create dummy meteringpoint without technology
            2. Insert dummy point
            3. Insert new technology to meteringpoint
            3. Fetch meteringpoint using /list
            4. Assert fetched technology equals the dummy technology
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

        meteringpoint = get_dummy_meteringpoint(
            number=1,
            include_address=True,
            include_technology=False,
        )

        technology = get_dummy_technology(1)

        # -- Act -------------------------------------------------------------

        # insert technology codes needed to read technology
        for technology in get_all_technology_codes():
            dispatcher(TechnologyUpdate(
                technology=technology
            ))

        # Insert single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=meteringpoint,
        ))

        # Insert technology to metering point
        dispatcher(MeteringPointTechnologyUpdate(
            gsrn=meteringpoint.gsrn,
            codes=TechnologyCodes(
                tech_code=technology.tech_code,
                fuel_code=technology.fuel_code
            )
        ))

        # Delegate access, needed to fetch it using api
        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=meteringpoint.gsrn,
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
                'Authorization': f'Bearer: {token}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert r.json['meteringpoints'][0]['technology'] == {
            'fuel_code': technology.fuel_code,
            'tech_code': technology.tech_code,
            'type': technology.type.value,
        }

    def test__meteringpoint_technology_update__technology_updated_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_5 Create/Update/remove meteringpoint.technology
                TEST_5.2 Update meteringpoint.technology

            Addtionally tests the following:
                - Correct amount of meteringpoints returned
                - HTTP status code

        Steps:
            1. Create dummy meteringpoint with technology
            2. Insert dummy point
            3. Create new technology
            4. Ypdate meteringpoint technology with new technology
            5. Fetch meteringpoint using /list
            6. Assert fetched technology equals the new dummy technology
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

        technology = get_dummy_technology(2)

        # -- Act -------------------------------------------------------------

        # insert technology codes needed to read technology
        for technology in get_all_technology_codes():
            dispatcher(TechnologyUpdate(
                technology=technology
            ))

        # Insert single metering point
        dispatcher(MeteringPointUpdate(
            meteringpoint=mp,
        ))

        # Update metering point technology
        dispatcher(MeteringPointTechnologyUpdate(
            gsrn=mp.gsrn,
            codes=TechnologyCodes(
                tech_code=technology.tech_code,
                fuel_code=technology.fuel_code
            ),
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
                'Authorization': f'Bearer: {token}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert r.json['meteringpoints'][0]['technology'] == {
            'fuel_code': technology.fuel_code,
            'tech_code': technology.tech_code,
            'type': technology.type.value,
        }

    def test__meteringpoint_technology_update__technology_removed_correctly(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        Test Case(s):
            TEST_5 Create/Update/remove meteringpoint.technology
                TEST_5.3 Remove meteringpoint.technology

            Addtionally tests the following:
                - Correct amount of meteringpoints returned
                - HTTP status code

        Steps:
            1. Create dummy meteringpoint with technology
            2. Insert dummy point
            3. Remove meteringpoint technology
            5. Fetch meteringpoint using /list
            6. Assert fetched meteringpoint.technology equals None
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
            meteringpoint=mp,
        ))

        # Remove meteringpoint.technology by setting it to None
        dispatcher(MeteringPointTechnologyUpdate(
            gsrn=mp.gsrn,
            codes=None,
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
                'Authorization': f'Bearer: {token}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert r.json['meteringpoints'][0]['technology'] is None


class TestMeteringPointRemoved:
    def test__meteringpoint_removed__meteringpoint_removed(
        self,
        session: db.Session,
        client: FlaskClient,
        token_encoder: TokenEncoder,
    ):
        """
        TEST_6 Remove meteringpoint
            TEST_6.1 Remove meteringpoint using meteringpoint_removed handler

        Addtionally tests the following:
            -

        Steps:
            1. Create 2 dummy meteringpoints
            2. Insert dummy meteringpoints
            3. Delegate access for each gsrn
            4. Remove meteringpoint
            3. Fetchs meteringpoint using /list
            4. Check that correct meteringpoint has been removed
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

        mp_1 = get_dummy_meteringpoint(
            number=1,
            include_address=True,
            include_technology=True,
        )

        mp_2 = get_dummy_meteringpoint(
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

        # Insert both meteringpoint
        dispatcher(MeteringPointUpdate(
            meteringpoint=mp_1,
        ))

        dispatcher(MeteringPointUpdate(
            meteringpoint=mp_2,
        ))

        # Remove meteringpoint.technology by setting it to None
        dispatcher(MeteringPointTechnologyUpdate(
            gsrn=mp_1.gsrn,
            codes=None,
        ))

        # Delegate access, needed to fetch it using api
        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=mp_1.gsrn,
            )
        ))

        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=mp_2.gsrn,
            )
        ))

        r = client.post(
            path='/list',
            json={
                'offset': 0,
                'limit': 10,
                'filters': {
                    'gsrn': [mp_1.gsrn, mp_2.gsrn],
                },
            },
            headers={
                'Authorization': f'Bearer: {token}',
            }
        )

        # -- Assert ----------------------------------------------------------

        assert r.status_code == 200
        assert len(r.json['meteringpoints']) == 1

        assert r.json['meteringpoints'][0]['gsrn'] == mp_2.gsrn
