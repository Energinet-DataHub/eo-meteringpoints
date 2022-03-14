from typing import List
from sqlalchemy import orm, asc, desc, and_

from origin.sql import SqlQuery
from origin.models.meteringpoints import MeteringPointType

from .models import (
    MeteringPointFilters,
    MeteringPointOrdering,
    MeteringPointOrderingKeys,
    DbMeteringPoint,
    DbMeteringPointTechnology,
    DbMeteringPointAddress,
    DbMeteringPointDelegate,
    DbTechnology,
)


# -- MeteringPoints ----------------------------------------------------------


class MeteringPointQuery(SqlQuery):
    """Query DbMeteringPoint."""

    def _get_base_query(self) -> orm.Query:
        return self.session.query(DbMeteringPoint)

    def apply_filters(
            self,
            filters: MeteringPointFilters,
    ) -> 'MeteringPointQuery':
        """Apply provided filters."""

        query = self

        if filters.gsrn is not None:
            query = query.has_any_gsrn(filters.gsrn)
        if filters.type is not None:
            query = query.is_type(filters.type)
        if filters.sector is not None:
            query = query.in_any_sector(filters.sector)

        return query

    def apply_ordering(
            self,
            ordering: MeteringPointOrdering,
    ) -> 'MeteringPointQuery':
        """Apply provided ordering."""

        fields = {
            MeteringPointOrderingKeys.GSRN: DbMeteringPoint.gsrn,
            MeteringPointOrderingKeys.TYPE: DbMeteringPoint.type,
            MeteringPointOrderingKeys.SECTOR: DbMeteringPoint.sector,
        }

        if ordering.asc:
            return self.query.order_by(asc(fields[ordering.key]))
        elif ordering.desc:
            return self.query.order_by(desc(fields[ordering.key]))
        else:
            raise RuntimeError('Should NOT have happened')

    def has_gsrn(self, gsrn: str) -> 'MeteringPointQuery':
        """
        TODO.

        Filters query; only include MeteringPoint with the
        provided gsrn.
        """
        return self.filter(DbMeteringPoint.gsrn == gsrn)

    def has_any_gsrn(self, gsrn: List[str]) -> 'MeteringPointQuery':
        """
        TODO.

        Filters query; only include MeteringPoints with any of
        the provided gsrn.
        """
        return self.filter(DbMeteringPoint.gsrn.in_(gsrn))

    def is_type(self, type: MeteringPointType) -> 'MeteringPointQuery':
        """
        TODO.

        Filters query; only include MeteringPoints with the
        provided type.
        """
        return self.filter(DbMeteringPoint.type == type)

    def in_sector(self, sector: str) -> 'MeteringPointQuery':
        """
        TODO.

        Filters query; only include MeteringPoints within the
        provided sector.
        """
        return self.filter(DbMeteringPoint.sector == sector)

    def in_any_sector(self, sector: List[str]) -> 'MeteringPointQuery':
        """
        TODO.

        Filters query; only include MeteringPoints within any of the
        provided sectors.
        """
        return self.filter(DbMeteringPoint.sector.in_(sector))

    def is_accessible_by(self, subject: str) -> 'MeteringPointQuery':
        """TODO."""

        return self.__class__(
            session=self.session,
            query=self.query.join(DbMeteringPointDelegate, and_(
                DbMeteringPointDelegate.gsrn == DbMeteringPoint.gsrn,
                DbMeteringPointDelegate.subject == subject,
            )),
        )


class MeteringPointAddressQuery(SqlQuery):
    """Query DbMeteringPointAddress."""

    def _get_base_query(self) -> orm.Query:
        """TODO."""

        return self.session.query(DbMeteringPointAddress)

    def has_gsrn(self, gsrn: str) -> 'MeteringPointAddressQuery':
        """TODO."""

        return self.filter(DbMeteringPointAddress.gsrn == gsrn)


class MeteringPointTechnologyQuery(SqlQuery):
    """Query DbMeteringPointTechnology."""

    def _get_base_query(self) -> orm.Query:
        """TODO."""

        return self.session.query(DbMeteringPointTechnology)

    def has_gsrn(self, gsrn: str) -> 'MeteringPointTechnologyQuery':
        """TODO."""

        return self.filter(DbMeteringPointTechnology.gsrn == gsrn)


class DelegateQuery(SqlQuery):
    """Query MeteringPointDelegate."""

    def _get_base_query(self) -> orm.Query:
        """TODO."""

        return self.session.query(DbMeteringPointDelegate)

    def has_gsrn(self, gsrn: str) -> 'DelegateQuery':
        """TODO."""

        return self.filter(DbMeteringPointDelegate.gsrn == gsrn)

    def has_subject(self, subject: str) -> 'DelegateQuery':
        """TODO."""

        return self.filter(DbMeteringPointDelegate.subject == subject)


# -- Technologies ------------------------------------------------------------


class TechnologyQuery(SqlQuery):
    """Query Technology."""

    def _get_base_query(self) -> orm.Query:
        """TODO."""

        return self.session.query(DbTechnology)

    def has_tech_code(self, tech_code: str) -> 'TechnologyQuery':
        """TODO."""

        return self.filter(DbTechnology.tech_code == tech_code)

    def has_fuel_code(self, fuel_code: str) -> 'TechnologyQuery':
        """TODO."""

        return self.filter(DbTechnology.fuel_code == fuel_code)
