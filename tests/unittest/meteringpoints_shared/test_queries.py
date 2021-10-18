from typing import List

import pytest
from itertools import product

from energytt_platform.models.common import Order
from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from energytt_platform.models.meteringpoints import MeteringPointType

from meteringpoints_shared.models import (
    DbMeteringPoint,
    DbMeteringPointDelegate, MeteringPointFilters, MeteringPointOrdering, MeteringPointOrderingKeys,
    DbMeteringPointAddress, DbMeteringPointTechnology,
)
from meteringpoints_shared.queries import MeteringPointQuery, MeteringPointAddressQuery, MeteringPointTechnologyQuery

TYPES = (MeteringPointType.consumption, MeteringPointType.production)
SECTORS = ('DK1', 'DK2')
COMBINATIONS = list(product(TYPES, SECTORS))


@pytest.fixture(scope='module')
def seed_meteringpoints() -> List[MeteringPoint]:
    """
    TODO

    :return:
    """

    mp_list = []

    for i, (type, sector) in enumerate(COMBINATIONS):
        mp_list.append(DbMeteringPoint(
            gsrn=f'gsrn{i}',
            type=type,
            sector=sector,
        ))

    return mp_list


@pytest.fixture(scope='function')
def seeded_session(
        session: db.Session,
        seed_meteringpoints: List[MeteringPoint],
        token_subject: str,
) -> db.Session:
    """
    TODO
    """
    session.begin()

    for meteringpoint in seed_meteringpoints:
        session.add(DbMeteringPoint(
            gsrn=meteringpoint.gsrn,
            type=meteringpoint.type,
            sector=meteringpoint.sector,
        ))

    session.commit()

    yield session


class TestMeteringPointQuery:
    @pytest.mark.parametrize('gsrn', ('gsrn0', 'gsrn1', 'gsrn2'))
    def test__has_gsrn__gsrn_exists__should_return_correct_meteringpoint(
            self,
            seeded_session: db.Session,
            gsrn: str,
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .has_gsrn(gsrn)

        # -- Assert ----------------------------------------------------------

        assert query.count() == 1
        assert query.one().gsrn == gsrn

    @pytest.mark.parametrize('gsrn', ('unknown_gsrn_1', None))
    def test__has_gsrn__gsrn_does_not_exists__should_return_no_meteringpoints(
            self,
            seeded_session: db.Session,
            gsrn: str,
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .has_gsrn(gsrn)

        # -- Assert ----------------------------------------------------------

        assert query.count() == 0

    @pytest.mark.parametrize('gsrn, expected_gsrn_returned', (
            (['gsrn0'], ['gsrn0']),
            (['gsrn0', 'gsrn1'], ['gsrn0', 'gsrn1']),
            (['unknown_gsrn_1'], []),
            (['unknown_gsrn_1', 'gsrn1'], ['gsrn1']),
            ([], []),
    ))
    def test__has_any_gsrn__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            gsrn: List[str],
            expected_gsrn_returned: List[str],
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .has_any_gsrn(gsrn)

        # -- Assert ----------------------------------------------------------

        assert query.count() == len(expected_gsrn_returned)
        assert all(mp.gsrn in expected_gsrn_returned for mp in query.all())

    @pytest.mark.parametrize('meteringpoint_type', (
            MeteringPointType.consumption,
            MeteringPointType.production,
    ))
    def test__is_type__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            meteringpoint_type: MeteringPointType,
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .is_type(meteringpoint_type)

        # -- Assert ----------------------------------------------------------

        assert query.count() > 0
        assert all(mp.type is meteringpoint_type for mp in query.all())

    @pytest.mark.parametrize('sector', (
            'DK1',
    ))
    def test__in_sector__sector_exists__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            sector: str,
    ):
        # -- Act - ------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .in_sector(sector)

        # -- Assert ----------------------------------------------------------

        assert query.count() == len([mp for mp in seed_meteringpoints if mp.sector == sector])
        assert all(mp.sector == sector for mp in query.all())

    @pytest.mark.parametrize('sector', (
            '',
            'unknown_sector',
    ))
    def test__in_sector__sector_does_not_exist__should_return_nothing(
            self,
            seeded_session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            sector: str,
    ):
        # -- Act - ------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .in_sector(sector)

        # -- Assert ----------------------------------------------------------

        assert query.count() == 0

    @pytest.mark.parametrize('sectors', (
            ['DK1'],
            ['DK1', 'DK2'],
            ['unknown_sector'],
            ['DK1', 'unknown_sector'],
            ['DK1', 'DK1'],
            [''],
            [],
    ))
    def test__in_any_sector__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            sectors: List[str],
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session) \
            .in_any_sector(sectors)

        # -- Assert ----------------------------------------------------------

        assert query.count() == len([mp for mp in seed_meteringpoints if mp.sector in sectors])
        assert all(meteringpoint.sector in sectors for meteringpoint in query.all())

    @pytest.mark.parametrize('gsrn_with_delegated_access', (
            ['gsrn1'],
            ['gsrn1', 'gsrn2'],
            [],
    ))
    def test__is_accessible_by__should_return_meteringpoints_with_delegated_access(
            self,
            seeded_session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            gsrn_with_delegated_access: List[str],
    ):
        # -- Arrange ---------------------------------------------------------

        subject = 'subject1'

        # -- Act -------------------------------------------------------------

        for gsrn in gsrn_with_delegated_access:
            seeded_session.add(DbMeteringPointDelegate(
                gsrn=gsrn,
                subject=subject,
            ))
        seeded_session.commit()

        query = MeteringPointQuery(seeded_session) \
            .is_accessible_by(subject)

        # -- Assert ----------------------------------------------------------

        assert query.count() == len(gsrn_with_delegated_access)
        assert all(mp.gsrn in gsrn_with_delegated_access for mp in query.all())

    @pytest.mark.parametrize('filters', (
            MeteringPointFilters(),
            MeteringPointFilters(gsrn=['gsrn1']),
            MeteringPointFilters(gsrn=['gsrn1', 'gsrn2']),
            MeteringPointFilters(type=MeteringPointType.production),
            MeteringPointFilters(type=MeteringPointType.consumption),
            MeteringPointFilters(sector=['DK1']),
            MeteringPointFilters(sector=['DK1', 'DK2']),
    ))
    def test__query_apply_filters__meteringpoints_match_filters__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            filters: MeteringPointFilters,
            seed_meteringpoints: List[MeteringPoint],
    ):

        # -- Act -------------------------------------------------------------

        results = MeteringPointQuery(seeded_session) \
            .apply_filters(filters) \
            .all()

        # -- Assert -------------------------------------------------------------

        assert len(results) > 0

        if filters.gsrn is not None:
            assert all(mp.gsrn in filters.gsrn for mp in results)

        if filters.type is not None:
            assert all(mp.type is filters.type for mp in results)

        if filters.sector is not None:
            assert all(mp.sector in filters.sector for mp in results)

    @pytest.mark.parametrize('filters', (
            MeteringPointFilters(gsrn=[]),
            MeteringPointFilters(gsrn=['UNKNOWN_GSRN']),
            MeteringPointFilters(sector=[]),
            MeteringPointFilters(sector=['UNKNOWN_SECTOR']),
    ))
    def test__query_apply_filters__meteringpoints_does_not_match_filters__should_return_no_meteringpoints(
            self,
            seeded_session: db.Session,
            filters: MeteringPointFilters,
            seed_meteringpoints: List[MeteringPoint],
    ):

        # -- Act -------------------------------------------------------------

        results = MeteringPointQuery(seeded_session) \
            .apply_filters(filters) \
            .all()

        # -- Assert -------------------------------------------------------------

        assert len(results) == 0

    @pytest.mark.parametrize('ordering', (
            MeteringPointOrdering(key=MeteringPointOrderingKeys.gsrn, order=Order.asc),
            MeteringPointOrdering(key=MeteringPointOrderingKeys.gsrn, order=Order.desc),
            MeteringPointOrdering(key=MeteringPointOrderingKeys.sector, order=Order.asc),
            MeteringPointOrdering(key=MeteringPointOrderingKeys.sector, order=Order.desc),
    ))
    def test__apply_ordering__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            ordering: MeteringPointOrdering,
            seed_meteringpoints: List[MeteringPoint],
    ):
        # -- Act -------------------------------------------------------------

        results = MeteringPointQuery(seeded_session) \
            .apply_ordering(ordering) \
            .all()

        # -- Assert ----------------------------------------------------------

        sort_descending = ordering.order == Order.desc

        if ordering.key is MeteringPointOrderingKeys.gsrn:
            f = lambda mp: mp.gsrn
        elif ordering.key is MeteringPointOrderingKeys.sector:
            f = lambda mp: mp.sector
        else:
            raise RuntimeError('Should not happen')

        assert len(results) == len(seed_meteringpoints)
        assert [mp.gsrn for mp in results] == \
               [mp.gsrn for mp in sorted(seed_meteringpoints,
                                         key=f, reverse=sort_descending)]


class TestMeteringPointAddressQuery:
    def test__has_gsrn__gsrn_exists__should_return_correct_meteringpointaddress(
            self,
            session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = 'gsrn1'

        session.add(DbMeteringPoint(
            gsrn=gsrn,
            type=MeteringPointType.consumption,
            sector='DK1',
        ))

        session.add(DbMeteringPointAddress(
            gsrn=gsrn,
            street_code='street_code_1',
            street_name='street_name_1',
            building_number='building_number_1',
            floor_id='floor_id_1',
            room_id='room_id_1',
            post_code='post_code_1',
            city_name='city_name_1',
            city_sub_division_name='city_sub_division_name1',
            municipality_code='municipality_code_1',
            location_description='location_description_1',
        ))

        session.commit()

        # -- Act -----------------------------------------------------------------

        result = MeteringPointAddressQuery(session) \
            .has_gsrn(gsrn) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 1
        assert result[0].gsrn == gsrn

    @pytest.mark.parametrize('gsrn', ('unknown_gsrn_1', None))
    def test__has_gsrn__gsrn_does_not_exists__should_not_return_any_meteringpointaddress(
            self,
            session: db.Session,
            gsrn: str,
    ):
        # -- Arrange -------------------------------------------------------------

        session.add(DbMeteringPoint(
            gsrn='gsrn1',
            type=MeteringPointType.consumption,
            sector='DK1',
        ))

        session.add(DbMeteringPointAddress(
            gsrn='gsrn1',
            street_code='street_code_1',
            street_name='street_name_1',
            building_number='building_number_1',
            floor_id='floor_id_1',
            room_id='room_id_1',
            post_code='post_code_1',
            city_name='city_name_1',
            city_sub_division_name='city_sub_division_name1',
            municipality_code='municipality_code_1',
            location_description='location_description_1',
        ))

        session.commit()

        # -- Act -----------------------------------------------------------------

        result = MeteringPointAddressQuery(session) \
            .has_gsrn(gsrn) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 0


class TestMeteringPointTechnologyQuery:
    def test__has_gsrn__gsrn_exists__should_return_correct_meteringpointtechnology(
            self,
            session: db.Session,
    ):
        # -- Arrange -------------------------------------------------------------

        gsrn = 'gsrn1'

        session.add(DbMeteringPoint(
            gsrn=gsrn,
            type=MeteringPointType.consumption,
            sector='DK1',
        ))

        session.add(DbMeteringPointTechnology(
            gsrn=gsrn,
            tech_code='100',
            fuel_code='102',
        ))

        session.commit()

        # -- Act -----------------------------------------------------------------

        result = MeteringPointTechnologyQuery(session) \
            .has_gsrn(gsrn) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 1
        assert result[0].gsrn == gsrn

    @pytest.mark.parametrize('gsrn', ('unknown_gsrn_1', None))
    def test__has_gsrn__gsrn_does_not_exists__should_not_return_any_meteringpointtechnology(
            self,
            session: db.Session,
            gsrn: str,
    ):
        # -- Arrange -------------------------------------------------------------

        session.add(DbMeteringPoint(
            gsrn='gsrn1',
            type=MeteringPointType.consumption,
            sector='DK1',
        ))

        session.add(DbMeteringPointTechnology(
            gsrn='gsrn1',
            tech_code='100',
            fuel_code='102',
        ))

        session.commit()

        # -- Act -----------------------------------------------------------------

        result = MeteringPointTechnologyQuery(session) \
            .has_gsrn(gsrn) \
            .all()

        # -- Assert --------------------------------------------------------------

        assert len(result) == 0
