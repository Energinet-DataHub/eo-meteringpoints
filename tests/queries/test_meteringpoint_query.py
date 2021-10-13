from typing import List, Dict

import pytest
from itertools import product

from energytt_platform.models.common import ResultOrdering, Order
from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from energytt_platform.models.meteringpoints import MeteringPointType

from meteringpoints_shared.models import (
    DbMeteringPoint,
    DbMeteringPointDelegate, MeteringPointFilters, MeteringPointOrdering, MeteringPointOrderingKeys,
)
from meteringpoints_shared.queries import MeteringPointQuery

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
def meteringpoint_dict(seed_meteringpoints: List[MeteringPoint]):
    return {o.gsrn: o for o in seed_meteringpoints}


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
    def test__query_has_gsrn__gsrn_exists__should_return_correct_meteringpoint(
            self,
            seeded_session: db.Session,
            gsrn: str,
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session).has_gsrn(gsrn)

        # -- Assert ----------------------------------------------------------

        assert query.count() == 1
        assert query.one().gsrn == gsrn

    @pytest.mark.parametrize('gsrn', ('unknown_gsrn_1', ''))
    def test__query_has_gsrn__gsrn_does_not_exists__should_return_correct_meteringpoint(
            self,
            seeded_session: db.Session,
            gsrn: str,
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session).has_gsrn(gsrn)

        # -- Assert ----------------------------------------------------------

        assert query.count() == 0
        assert query.one_or_none() is None

    @pytest.mark.parametrize('gsrn, expected_gsrn_returned', (
            (['gsrn0'], ['gsrn0']),
            (['gsrn0', 'gsrn1'], ['gsrn0', 'gsrn1']),
            (['unknown_gsrn_1'], []),
            (['unknown_gsrn_1', 'gsrn1'], ['gsrn1']),
            ([], []),
    ))
    def test__query_has_any_gsrn__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            gsrn: List[str],
            expected_gsrn_returned: List[str],
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session).has_any_gsrn(gsrn)

        # -- Assert ----------------------------------------------------------

        assert query.count() == len(expected_gsrn_returned)
        assert all(meteringpoint.gsrn in expected_gsrn_returned for meteringpoint in query.all())

    @pytest.mark.parametrize('meteringpoint_type', (
            MeteringPointType.consumption,
            MeteringPointType.production,
    ))
    def test__query_is_type__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            meteringpoint_type: MeteringPointType,
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session).is_type(meteringpoint_type)

        # -- Assert ----------------------------------------------------------
        assert query.count() > 0
        assert all(meteringpoint.type == meteringpoint_type for meteringpoint in query.all())

    @pytest.mark.parametrize('sector', (
            'DK1',
            'DK2',
            'unknown_sector',
    ))
    def test__query_in_sector__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            sector: str,
    ):
        # -- Act - ------------------------------------------------------------

        query = MeteringPointQuery(seeded_session).in_sector(sector)

        # -- Assert ----------------------------------------------------------

        assert query.count() == sum(o.sector is sector for o in seed_meteringpoints)
        assert all(meteringpoint.sector == sector for meteringpoint in query.all())

    @pytest.mark.parametrize('sectors', (
            ['DK1'],
            ['DK1', 'DK2'],
            ['unknown_sector'],
            ['DK1', 'unknown_sector'],
            ['DK1', 'DK1'],
            [''],
            [],
    ))
    def test__query_in_any_sector__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            seed_meteringpoints: List[MeteringPoint],
            sectors: List[str],
    ):
        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session).in_any_sector(sectors)

        # -- Assert ----------------------------------------------------------

        assert query.count() == sum(o.sector in sectors for o in seed_meteringpoints)
        assert all(meteringpoint.sector in sectors for meteringpoint in query.all())

    @pytest.mark.parametrize('gsrn_with_delegated_access', (
            ['gsrn1'],
            ['gsrn1', 'gsrn2'],
            [],
    ))
    def test__query_is_accessible_by__should_return_meteringpoints_with_delegated_access(
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
        query = MeteringPointQuery(seeded_session).is_accessible_by(subject)

        # -- Assert ----------------------------------------------------------

        assert query.count() == len(gsrn_with_delegated_access)
        assert all(meteringpoint.gsrn in gsrn_with_delegated_access for meteringpoint in query.all())

    @pytest.mark.parametrize('filters', (
            MeteringPointFilters(),
            MeteringPointFilters(gsrn=['gsrn1']),
            MeteringPointFilters(gsrn=['gsrn1', 'gsrn2']),
            MeteringPointFilters(gsrn=['unknown_gsrn']),
            MeteringPointFilters(gsrn=['unknown_gsrn', 'gsrn1']),
            MeteringPointFilters(type=MeteringPointType.production),
            MeteringPointFilters(type=MeteringPointType.consumption),
            MeteringPointFilters(sector=['DK1']),
            MeteringPointFilters(sector=['DK1', 'DK2']),
            MeteringPointFilters(sector=['unknown_sector']),
            MeteringPointFilters(sector=['unknown_sector', 'DK2']),
            MeteringPointFilters(
                gsrn=['gsrn1'],
                type=MeteringPointType.production,
            ),
            MeteringPointFilters(
                gsrn=['gsrn1'],
                type=MeteringPointType.production,
                sector=['DK1'],
            ),
    ))
    def test__query_apply_filters__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            filters: MeteringPointFilters,
            seed_meteringpoints: List[MeteringPoint],
    ):
        # -- Arrange ---------------------------------------------------------

        expected_meteringpoints = seed_meteringpoints

        if filters.gsrn is not None:
            expected_meteringpoints = [
                m for m in expected_meteringpoints
                if m.gsrn in filters.gsrn
            ]

        if filters.type is not None:
            expected_meteringpoints = [
                m for m in expected_meteringpoints
                if m.type == filters.type
            ]

        if filters.sector is not None:
            expected_meteringpoints = [
                m for m in expected_meteringpoints
                if m.sector in filters.sector
            ]

        expected_meteringpoints_gsrn = [m.gsrn for m in expected_meteringpoints]

        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session).apply_filters(filters)

        assert query.count() == len(expected_meteringpoints)
        assert all(meteringpoint.gsrn in expected_meteringpoints_gsrn for meteringpoint in query.all())

    @pytest.mark.parametrize('ordering', (
            MeteringPointOrdering(key=MeteringPointOrderingKeys.gsrn, order=Order.asc),
            MeteringPointOrdering(key=MeteringPointOrderingKeys.gsrn, order=Order.desc),
            MeteringPointOrdering(key=MeteringPointOrderingKeys.type, order=Order.asc),
            MeteringPointOrdering(key=MeteringPointOrderingKeys.type, order=Order.desc),
            MeteringPointOrdering(key=MeteringPointOrderingKeys.sector, order=Order.asc),
            MeteringPointOrdering(key=MeteringPointOrderingKeys.sector, order=Order.desc),
    ))
    def test__query_apply_ordering__should_return_correct_meteringpoints(
            self,
            seeded_session: db.Session,
            ordering: MeteringPointOrdering,
            seed_meteringpoints: List[MeteringPoint],
    ):
        # seed_meteringpoints[0].type.name
        # -- Arrange ---------------------------------------------------------
        expected_meteringpoints = []

        sort_descending = ordering.order == Order.desc

        if ordering.key == MeteringPointOrderingKeys.gsrn:
            expected_meteringpoints = sorted(seed_meteringpoints, key=lambda x: x.gsrn, reverse=sort_descending)
        elif ordering.key == MeteringPointOrderingKeys.type:
            expected_meteringpoints = sorted(
                seed_meteringpoints,
                key=lambda x: x.type.value,
                reverse=not sort_descending,  # Not pretty but it works
            )
        elif ordering.key == MeteringPointOrderingKeys.sector:
            expected_meteringpoints = sorted(seed_meteringpoints, key=lambda x: x.sector, reverse=sort_descending)

        expected_meteringpoints_gsrn = [m.gsrn for m in expected_meteringpoints]

        # -- Act -------------------------------------------------------------

        query = MeteringPointQuery(seeded_session).apply_ordering(ordering)

        # -- Assert ----------------------------------------------------------
        assert query.count() == len(expected_meteringpoints)

        returned_meteringpoints_gsrn = [m.gsrn for m in query.all()]
        assert returned_meteringpoints_gsrn == expected_meteringpoints_gsrn
