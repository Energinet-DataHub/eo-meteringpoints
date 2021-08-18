from sqlalchemy import orm

from energytt_platform.sql import SqlQuery

from .models import (
    MeteringPointFilters,
    MeteringPointOrdering,
    DbMeteringPoint,
    DbMeteringPointTechnology,
    DbMeteringPointAddress,
    DbTechnology,
)


# -- MeteringPoints ----------------------------------------------------------


class MeteringPointQuery(SqlQuery):
    """
    Query DbMeteringPoint.
    """
    def _get_base_query(self) -> orm.Query:
        return self.session.query(DbMeteringPoint)

    def apply_filters(self, filters: MeteringPointFilters) -> 'MeteringPointQuery':
        return self

    def apply_ordering(self, ordering: MeteringPointOrdering) -> 'MeteringPointQuery':
        return self

    def has_gsrn(self, gsrn: str) -> 'MeteringPointQuery':
        return self.filter(DbMeteringPoint.gsrn == gsrn)

    def is_accessible_by(self, subject: str) -> 'MeteringPointQuery':
        return self


class MeteringPointAddressQuery(SqlQuery):
    """
    Query DbMeteringPointAddress.
    """
    def _get_base_query(self) -> orm.Query:
        return self.session.query(DbMeteringPointAddress)

    def has_gsrn(self, gsrn: str) -> 'MeteringPointAddressQuery':
        return self.filter(DbMeteringPointAddress.gsrn == gsrn)


class MeteringPointTechnologyQuery(SqlQuery):
    """
    Query DbMeteringPointTechnology.
    """
    def _get_base_query(self) -> orm.Query:
        return self.session.query(DbMeteringPointTechnology)

    def has_gsrn(self, gsrn: str) -> 'MeteringPointTechnologyQuery':
        return self.filter(DbMeteringPointTechnology.gsrn == gsrn)


class DelegateQuery(SqlQuery):
    """
    Query MeteringPointDelegate.
    """
    def _get_base_query(self) -> orm.Query:
        return self.session.query(DbMMeteringPointDelegate)

    def has_gsrn(self, gsrn: str) -> 'DelegateQuery':
        return self.filter(DbMMeteringPointDelegate.gsrn == gsrn)

    def has_subject(self, subject: str) -> 'DelegateQuery':
        return self.filter(DbMMeteringPointDelegate.subject == subject)


# class AddressQuery(SqlQuery):
#     """
#     Query MeteringPoints.
#     """
#     def _get_base_query(self) -> orm.Query:
#         return self.session.query(Address)
#
#     def has_technology_code(self, technology_code: str) -> 'AddressQuery':
#         return self.filter(Technology.technology_code == technology_code)
#
#     def has_gsrn(self, fuel_code: str) -> 'AddressQuery':
#         return self.filter(Technology.fuel_code == fuel_code)


# -- Technologies ------------------------------------------------------------


class TechnologyQuery(SqlQuery):
    """
    Query Technology.
    """
    def _get_base_query(self) -> orm.Query:
        return self.session.query(DbTechnology)

    def has_tech_code(self, tech_code: str) -> 'TechnologyQuery':
        return self.filter(DbTechnology.tech_code == tech_code)

    def has_fuel_code(self, fuel_code: str) -> 'TechnologyQuery':
        return self.filter(DbTechnology.fuel_code == fuel_code)
