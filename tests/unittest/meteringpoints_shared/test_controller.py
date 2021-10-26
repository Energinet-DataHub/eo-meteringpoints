import pytest
from typing import Union

from meteringpoints_shared.db import db

from energytt_platform.models.tech import Technology, TechnologyType, TechnologyCodes
from energytt_platform.models.meteringpoints import MeteringPointType
from energytt_platform.models.common import Address

from meteringpoints_shared.controller import controller
from meteringpoints_shared.models import DbMeteringPoint, DbTechnology, DbMeteringPointAddress, DbMeteringPointDelegate, \
    DbMeteringPointTechnology
from meteringpoints_shared.queries import MeteringPointQuery, MeteringPointAddressQuery, MeteringPointTechnologyQuery, \
    DelegateQuery, TechnologyQuery


# # ---- Seed Data -------------------------
#
# METERINGPOINT_1_WITHOUT_TECHNOLOGY = DbMeteringPoint(
#     gsrn='gsrn1',
#     type=MeteringPointType.consumption,
#     sector='DK1',
# )
#
# METERINGPOINT_2_WITH_TECHNOLOGY = DbMeteringPoint(
#     gsrn='gsrn2',
#     type=MeteringPointType.consumption,
#     sector='DK2',
# )
#
# METERINGPOINT_TECHNOLGY_2 = DbMeteringPointTechnology(
#     gsrn=METERINGPOINT_2_WITH_TECHNOLOGY.gsrn,
#     tech_code='100',
#     fuel_code='101',
# )
#
# METERINGPOINT_3_WITH_ADDRESS = DbMeteringPoint(
#     gsrn='gsrn3',
#     type=MeteringPointType.consumption,
#     sector='DK3',
# )
#
# METERINGPOINT_ADDRESS_3 = DbMeteringPointAddress(
#     gsrn=METERINGPOINT_3_WITH_ADDRESS.gsrn,
#     street_code='street_code_1',
#     street_name='street_name_1',
#     building_number='building_number_1',
#     floor_id='floor_id_1',
#     room_id='room_id_1',
#     post_code='post_code_1',
#     city_name='city_name_1',
#     city_sub_division_name='city_sub_division_name1',
#     municipality_code='municipality_code_1',
#     location_description='location_description_1',
# )
#
# METERINGPOINT_4_WITH_DELEGATE = DbMeteringPoint(
#     gsrn='gsrn4',
#     type=MeteringPointType.consumption,
#     sector='DK3',
# )
#
# METERINGPOINT_DELEGATE_4 = DbMeteringPointDelegate(
#     gsrn=METERINGPOINT_4_WITH_DELEGATE.gsrn,
#     subject='subject',
# )
#
# METERINGPOINT_5 = DbMeteringPoint(
#     gsrn='gsrn5',
#     type=MeteringPointType.consumption,
#     sector='DK3',
#
# )
#
# METERINGPOINT_TECHNOLGY_5 = DbMeteringPointTechnology(
#     gsrn=METERINGPOINT_5.gsrn,
#     tech_code='500',
#     fuel_code='501',
# )
#
# METERINGPOINT_ADDRESS_5 = DbMeteringPointAddress(
#     gsrn=METERINGPOINT_5.gsrn,
#     street_code='street_code_1',
#     street_name='street_name_1',
#     building_number='building_number_1',
#     floor_id='floor_id_1',
#     room_id='room_id_1',
#     post_code='post_code_1',
#     city_name='city_name_1',
#     city_sub_division_name='city_sub_division_name1',
#     municipality_code='municipality_code_1',
#     location_description='location_description_1',
# )
#
# METERINGPOINT_DELEGATE_5 = DbMeteringPointDelegate(
#     gsrn=METERINGPOINT_5.gsrn,
#     subject='subject5',
# )
#
# TECHNOLOGY_1 = DbTechnology(
#     type=TechnologyType.nuclear,
#     tech_code='001',
#     fuel_code='002',
# )
#
# TECHNOLOGY_2 = DbTechnology(
#     type=TechnologyType.solar,
#     tech_code='011',
#     fuel_code='012',
# )
#
# TECHNOLOGIES = [
#     TECHNOLOGY_1,
#     TECHNOLOGY_2,
# ]
#
# METERINGPOINTS = [
#     METERINGPOINT_1_WITHOUT_TECHNOLOGY,
#     METERINGPOINT_2_WITH_TECHNOLOGY,
#     METERINGPOINT_3_WITH_ADDRESS,
#     METERINGPOINT_4_WITH_DELEGATE,
#     METERINGPOINT_5,
# ]
#
# METERINGPOINT_TECHNOLOGIES = [
#     METERINGPOINT_TECHNOLGY_2,
#     METERINGPOINT_TECHNOLGY_5,
# ]
#
# ADDRESSES = [
#     METERINGPOINT_ADDRESS_3,
#     METERINGPOINT_ADDRESS_5,
# ]
#
# DELEGATES = [
#     METERINGPOINT_DELEGATE_4,
#     METERINGPOINT_DELEGATE_5,
# ]
#
#
# @pytest.fixture(scope='function')
# def seeded_session(
#         session: db.Session,
# ) -> db.Session:
#     for meteringpoint in METERINGPOINTS:
#         session.add(meteringpoint)
#
#     for meteringpoint_technology in METERINGPOINT_TECHNOLOGIES:
#         session.add(meteringpoint_technology)
#
#     for meteringpoint_address in ADDRESSES:
#         session.add(meteringpoint_address)
#
#     for meteringpoint_delegate in DELEGATES:
#         session.add(meteringpoint_delegate)
#
#     for technology in TECHNOLOGIES:
#         session.add(technology)
#
#     session.commit()
#     return session


class TestDatabaseControllerMeteringPoints:
    """
    Tests methods regarding MeteringPoints.
    """

    def test__get_or_create_meteringpoint__meteringpoint_already_exists__should_return(
            self,
            session: db.Session,
    ):

        # -- Arrange ---------------------------------------------------------

        session.begin()
        session.add(DbMeteringPoint(gsrn='gsrn123'))
        session.commit()

        # -- Act -------------------------------------------------------------

        session.begin()

        meteringpoint = controller.get_or_create_meteringpoint(
            session=session,
            gsrn='gsrn123',
        )

        session.commit()

        # -- Assert ----------------------------------------------------------

        assert meteringpoint.gsrn == 'gsrn123'

    def test__get_or_create_meteringpoint__meteringpoint_does_not_exists__should_create_and_return_meteringpoint(
            self,
            session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        session.begin()

        meteringpoint = controller.get_or_create_meteringpoint(
            session=session,
            gsrn='gsrn321',
        )

        session.commit()

        # -- Assert ----------------------------------------------------------

        # Check database for new meteringpoint
        db_meteringpoint = MeteringPointQuery(session) \
            .has_gsrn('gsrn321') \
            .one()

        assert meteringpoint.gsrn == 'gsrn321'
        assert db_meteringpoint.gsrn == 'gsrn321'

    def test__delete_meteringpoint__should_delete_meteringpoint_and_associated_data(
            self,
            session: db.Session,
    ):

        # -- Arrange -------------------------------------------------------------

        session.begin()

        session.add(DbMeteringPoint(gsrn='gsrn1'))
        session.add(DbMeteringPointAddress(gsrn='gsrn1'))
        session.add(DbMeteringPointTechnology(gsrn='gsrn1'))
        session.add(DbMeteringPointDelegate(gsrn='gsrn1', subject='subject'))

        session.add(DbMeteringPoint(gsrn='gsrn2'))
        session.add(DbMeteringPointAddress(gsrn='gsrn2'))
        session.add(DbMeteringPointTechnology(gsrn='gsrn2'))
        session.add(DbMeteringPointDelegate(gsrn='gsrn2', subject='subject'))

        session.commit()

        # -- Act -----------------------------------------------------------------

        session.begin()

        controller.delete_meteringpoint(
            session=session,
            gsrn='gsrn1',
        )

        session.commit()

        # -- Assert --------------------------------------------------------------

        # Assert 'gsrn1' and all of its associated data has been deleted

        assert not MeteringPointQuery(session) \
            .has_gsrn('gsrn1') \
            .exists()

        assert not MeteringPointAddressQuery(session) \
            .has_gsrn('gsrn1') \
            .exists()

        assert not MeteringPointTechnologyQuery(session) \
            .has_gsrn('gsrn1') \
            .exists()

        assert not DelegateQuery(session) \
            .has_gsrn('gsrn1') \
            .exists()

        # Assert 'gsrn2' and all of its associated data still exists

        assert MeteringPointQuery(session) \
            .has_gsrn('gsrn2') \
            .exists()

        assert MeteringPointAddressQuery(session) \
            .has_gsrn('gsrn2') \
            .exists()

        assert MeteringPointTechnologyQuery(session) \
            .has_gsrn('gsrn2') \
            .exists()

        assert DelegateQuery(session) \
            .has_gsrn('gsrn2') \
            .exists()


class TestDatabaseControllerMeteringPointAddress:
    """
    Tests methods regarding MeteringPointAddresses.
    """

    @pytest.mark.parametrize('new_address', (
        Address(
            street_code='new_street_code1',
            street_name='new_street_name1',
            building_number='new_building_number1',
            floor_id='new_floor_id1',
            room_id='new_room_id1',
            post_code='new_post_code1',
            city_name='new_city_name1',
            city_sub_division_name='new_city_sub_division_nam1',
            municipality_code='new_municipality_code1',
            location_description='new_location_description1',
        ),
        DbMeteringPointAddress(
            street_code='new_street_code2',
            street_name='new_street_name2',
            building_number='new_building_number2',
            floor_id='new_floor_id2',
            room_id='new_room_id2',
            post_code='new_post_code2',
            city_name='new_city_name2',
            city_sub_division_name='new_city_sub_division_nam2',
            municipality_code='new_municipality_code2',
            location_description='new_location_description2',
        ),
    ))
    def test__set_meteringpoint_address__address_already_exists__should_update_meteringpoint_address(
            self,
            session: db.Session,
            new_address: Union[Address, DbMeteringPointAddress],
    ):

        # -- Arrange ---------------------------------------------------------

        session.begin()
        session.add(DbMeteringPointAddress(gsrn='gsrn1'))
        session.add(DbMeteringPointAddress(gsrn='gsrn2'))
        session.commit()

        # -- Act -------------------------------------------------------------

        controller.set_meteringpoint_address(
            session=session,
            gsrn='gsrn1',
            address=new_address,
        )

        # -- Assert --------------------------------------------------------------

        address = MeteringPointAddressQuery(session) \
            .has_gsrn('gsrn1') \
            .one()

        assert address.gsrn == 'gsrn1'
        assert address.street_code == new_address.street_code
        assert address.street_name == new_address.street_name
        assert address.building_number == new_address.building_number
        assert address.floor_id == new_address.floor_id
        assert address.room_id == new_address.room_id
        assert address.post_code == new_address.post_code
        assert address.city_name == new_address.city_name
        assert address.city_sub_division_name == new_address.city_sub_division_name
        assert address.municipality_code == new_address.municipality_code
        assert address.location_description == new_address.location_description

        # Address for gsrn2 should be untouched

        gsrn2_address = MeteringPointAddressQuery(session) \
            .has_gsrn('gsrn2') \
            .one()

        assert gsrn2_address.gsrn == 'gsrn2'
        assert gsrn2_address.street_code is None
        assert gsrn2_address.street_name is None
        assert gsrn2_address.building_number is None
        assert gsrn2_address.floor_id is None
        assert gsrn2_address.room_id is None
        assert gsrn2_address.post_code is None
        assert gsrn2_address.city_name is None
        assert gsrn2_address.city_sub_division_name is None
        assert gsrn2_address.municipality_code is None
        assert gsrn2_address.location_description is None

    @pytest.mark.parametrize('new_address', (
        Address(
            street_code='new_street_code1',
            street_name='new_street_name1',
            building_number='new_building_number1',
            floor_id='new_floor_id1',
            room_id='new_room_id1',
            post_code='new_post_code1',
            city_name='new_city_name1',
            city_sub_division_name='new_city_sub_division_nam1',
            municipality_code='new_municipality_code1',
            location_description='new_location_description1',
        ),
        DbMeteringPointAddress(
            street_code='new_street_code2',
            street_name='new_street_name2',
            building_number='new_building_number2',
            floor_id='new_floor_id2',
            room_id='new_room_id2',
            post_code='new_post_code2',
            city_name='new_city_name2',
            city_sub_division_name='new_city_sub_division_nam2',
            municipality_code='new_municipality_code2',
            location_description='new_location_description2',
        ),
    ))
    def test__set_meteringpoint_address__address_does_not_exists__should_create_meteringpoint_address(
            self,
            session: db.Session,
            new_address: Union[Address, DbMeteringPointAddress],
    ):

        # -- Act -------------------------------------------------------------

        controller.set_meteringpoint_address(
            session=session,
            gsrn='gsrn1',
            address=new_address,
        )

        # -- Assert ----------------------------------------------------------

        address = MeteringPointAddressQuery(session) \
            .has_gsrn('gsrn1') \
            .one()

        assert address.gsrn == 'gsrn1'
        assert address.street_code == new_address.street_code
        assert address.street_name == new_address.street_name
        assert address.building_number == new_address.building_number
        assert address.floor_id == new_address.floor_id
        assert address.room_id == new_address.room_id
        assert address.post_code == new_address.post_code
        assert address.city_name == new_address.city_name
        assert address.city_sub_division_name == new_address.city_sub_division_name
        assert address.municipality_code == new_address.municipality_code
        assert address.location_description == new_address.location_description

    def test__delete_meteringpoint_address__address_exists__should_delete_correct(
            self,
            session: db.Session,
    ):

        # -- Arrange ---------------------------------------------------------

        session.begin()
        session.add(DbMeteringPointAddress(gsrn='gsrn1'))
        session.add(DbMeteringPointAddress(gsrn='gsrn2'))
        session.commit()

        # -- Act -------------------------------------------------------------

        session.begin()

        controller.delete_meteringpoint_address(
            session=session,
            gsrn='gsrn1',
        )

        session.commit()

        # -- Assert ----------------------------------------------------------

        assert not MeteringPointAddressQuery(session) \
            .has_gsrn('gsrn1') \
            .exists()

        assert MeteringPointAddressQuery(session) \
            .has_gsrn('gsrn2') \
            .exists()


class TestDatabaseControllerMeteringPointDelegate:
    """
    Tests methods regarding MeteringPointDelegates.
    """

    def test__grant_meteringpoint_delegate__delegate_already_exists__should_not_do_anything(
            self,
            session: db.Session,
    ):

        # -- Arrange ---------------------------------------------------------

        session.begin()
        session.add(DbMeteringPointDelegate(gsrn='gsrn1', subject='subject1'))
        session.commit()

        # -- Act -------------------------------------------------------------

        session.begin()

        controller.grant_meteringpoint_delegate(
            session=session,
            gsrn='gsrn1',
            subject='subject1',
        )

        session.commit()

        # -- Assert ----------------------------------------------------------

        delegate = DelegateQuery(session) \
            .one()

        assert delegate.gsrn == 'gsrn1'
        assert delegate.subject == 'subject1'

    def test__grant_meteringpoint_delegate__delegate_does_not_exists__should_create_delegate(
            self,
            session: db.Session,
    ):

        # -- Act -------------------------------------------------------------

        session.begin()

        controller.grant_meteringpoint_delegate(
            session=session,
            gsrn='gsrn1',
            subject='subject1',
        )

        session.commit()

        # -- Assert ----------------------------------------------------------

        delegate = DelegateQuery(session) \
            .one()

        assert delegate.gsrn == 'gsrn1'
        assert delegate.subject == 'subject1'

    # -- revoke_meteringpoint_delegate() -------------------------------------

    def test__revoke_meteringpoint_delegate__should_delete_delegate(
            self,
            session: db.Session,
    ):

        # -- Arrange ---------------------------------------------------------

        session.begin()
        session.add(DbMeteringPointDelegate(gsrn='gsrn1', subject='subject1'))
        session.add(DbMeteringPointDelegate(gsrn='gsrn1', subject='subject2'))
        session.add(DbMeteringPointDelegate(gsrn='gsrn2', subject='subject1'))
        session.add(DbMeteringPointDelegate(gsrn='gsrn2', subject='subject2'))
        session.commit()

        # -- Act -------------------------------------------------------------

        session.begin()

        controller.revoke_meteringpoint_delegate(
            session=session,
            gsrn='gsrn1',
            subject='subject1',
        )

        session.commit()

        # -- Assert ----------------------------------------------------------

        assert not DelegateQuery(session) \
            .has_gsrn('gsrn1') \
            .has_subject('subject1') \
            .exists()

        assert DelegateQuery(session) \
            .has_gsrn('gsrn1') \
            .has_subject('subject2') \
            .exists()

        assert DelegateQuery(session) \
            .has_gsrn('gsrn2') \
            .has_subject('subject1') \
            .exists()

        assert DelegateQuery(session) \
            .has_gsrn('gsrn2') \
            .has_subject('subject2') \
            .exists()


class TestDatabaseControllerMeteringPointTechnology:
    """
    Tests methods regarding MeteringPointTechnologies.
    """

    @pytest.mark.parametrize('new_technology', (
        Technology(
            tech_code='T010101',
            fuel_code='F01010101',
            type=TechnologyType.solar,  # Irrelevant
        ),
        TechnologyCodes(
            tech_code='T010101',
            fuel_code='F01010101',
        ),
        DbTechnology(
            tech_code='T010101',
            fuel_code='F01010101',
            type=TechnologyType.solar,  # Irrelevant
        ),
        DbMeteringPointTechnology(
            gsrn='',  # Irrelevant
            tech_code='T010101',
            fuel_code='F01010101',
        ),
    ))
    def test__set_meteringpoint_technology__technology_already_exists__should_update_meteringpoint_technology(
            self,
            session: db.Session,
            new_technology: Union[
                Technology,
                TechnologyCodes,
                DbTechnology,
                DbMeteringPointTechnology,
            ],
    ):

        # -- Arrange ---------------------------------------------------------

        session.begin()
        session.add(DbMeteringPointTechnology(gsrn='gsrn1'))
        session.add(DbMeteringPointTechnology(gsrn='gsrn2'))
        session.commit()

        # -- Act -------------------------------------------------------------

        session.begin()

        controller.set_meteringpoint_technology(
            session=session,
            gsrn='gsrn1',
            technology=new_technology,
        )
        session.commit()

        # -- Assert ----------------------------------------------------------

        technology = MeteringPointTechnologyQuery(session) \
            .has_gsrn('gsrn1') \
            .one()

        assert technology.gsrn == 'gsrn1'
        assert technology.tech_code == new_technology.tech_code
        assert technology.fuel_code == new_technology.fuel_code

        # Technology for gsrn2 should be untouched

        gsrn2_technology = MeteringPointTechnologyQuery(session) \
            .has_gsrn('gsrn2') \
            .one()

        assert gsrn2_technology.gsrn == 'gsrn2'
        assert gsrn2_technology.tech_code is None
        assert gsrn2_technology.fuel_code is None

    @pytest.mark.parametrize('new_technology', (
        Technology(
            tech_code='T010101',
            fuel_code='F01010101',
            type=TechnologyType.solar,  # Irrelevant
        ),
        TechnologyCodes(
            tech_code='T010101',
            fuel_code='F01010101',
        ),
        DbTechnology(
            tech_code='T010101',
            fuel_code='F01010101',
            type=TechnologyType.solar,  # Irrelevant
        ),
        DbMeteringPointTechnology(
            gsrn='',  # Irrelevant
            tech_code='T010101',
            fuel_code='F01010101',
        ),
    ))
    def test__set_meteringpoint_technology__technology_does_not_exists__should_create_meteringpoint_technology(  # noqa: E501
            self,
            session: db.Session,
            new_technology: Union[
                Technology,
                TechnologyCodes,
                DbTechnology,
                DbMeteringPointTechnology,
            ],
    ):

        # -- Act -------------------------------------------------------------

        session.begin()

        controller.set_meteringpoint_technology(
            session=session,
            gsrn='gsrn1',
            technology=new_technology,
        )

        session.commit()

        # -- Assert ----------------------------------------------------------

        technology = MeteringPointTechnologyQuery(session) \
            .has_gsrn('gsrn1') \
            .one()

        assert technology.gsrn == 'gsrn1'
        assert technology.tech_code == new_technology.tech_code
        assert technology.fuel_code == new_technology.fuel_code

    def test__delete_meteringpoint_technology__technology_exists__should_delete_correct(
            self,
            session: db.Session,
    ):

        # -- Arrange ---------------------------------------------------------

        session.begin()
        session.add(DbMeteringPointTechnology(gsrn='gsrn1'))
        session.add(DbMeteringPointTechnology(gsrn='gsrn2'))
        session.commit()

        # -- Act -------------------------------------------------------------

        session.begin()

        controller.delete_meteringpoint_technology(
            session=session,
            gsrn='gsrn1',
        )

        session.commit()

        # -- Assert ----------------------------------------------------------

        assert not MeteringPointTechnologyQuery(session) \
            .has_gsrn('gsrn1') \
            .exists()

        assert MeteringPointTechnologyQuery(session) \
            .has_gsrn('gsrn2') \
            .exists()


class TestDatabaseControllerTechnology:
    """
    Tests methods regarding Technologies.
    """

    def test__get_or_create_technology__technology_already_exists__should_return_existing_technology(
            self,
            session: db.Session,
    ):

        # -- Arrange ---------------------------------------------------------

        session.begin()
        session.add(DbTechnology(
            tech_code='T010101',
            fuel_code='F01010101',
        ))
        session.commit()

        # -- Act -----------------------------------------------------------------

        technology = controller.get_or_create_technology(
            session=session,
            tech_code='T010101',
            fuel_code='F01010101',
        )

        # -- Assert --------------------------------------------------------------

        assert technology.tech_code == 'T010101'
        assert technology.fuel_code == 'F01010101'

    def test__get_or_create_technology__technology_does_not_exists__should_create_and_return_technology(
            self,
            session: db.Session,
    ):

        # -- Act -----------------------------------------------------------------

        technology = controller.get_or_create_technology(
            session=session,
            tech_code='T010101',
            fuel_code='F01010101',
        )

        # -- Assert --------------------------------------------------------------

        db_technology = TechnologyQuery(session) \
            .has_tech_code('T010101') \
            .has_fuel_code('F01010101') \
            .one()

        assert technology.tech_code == 'T010101'
        assert technology.fuel_code == 'F01010101'

        assert db_technology.tech_code == 'T010101'
        assert db_technology.fuel_code == 'F01010101'

    # -- delete_technology() ------------------------------------------------------

    def test__delete_technology__should_delete_technology(
            self,
            session: db.Session,
    ):

        # -- Arrange -------------------------------------------------------------

        session.begin()
        session.add(DbTechnology(tech_code='T010101', fuel_code='F01010101'))
        session.add(DbTechnology(tech_code='T020202', fuel_code='F02020202'))
        session.commit()

        # -- Act -----------------------------------------------------------------

        session.begin()

        controller.delete_technology(
            session=session,
            tech_code='T010101',
            fuel_code='F01010101',
        )

        session.commit()

        # -- Assert --------------------------------------------------------------

        assert not TechnologyQuery(session) \
            .has_tech_code('T010101') \
            .has_fuel_code('F01010101') \
            .exists()

        assert TechnologyQuery(session) \
            .has_tech_code('T020202') \
            .has_fuel_code('F02020202') \
            .exists()
