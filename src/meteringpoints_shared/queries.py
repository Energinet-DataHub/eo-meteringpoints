from sqlalchemy import orm

from energytt_platform.sql import SqlQuery
from energytt_platform.models.tech import Technology
from energytt_platform.models.meteringpoints import \
    MeteringPoint, MeteringPointDelegate


class MeteringPointQuery(SqlQuery):
    """
    Query MeteringPoints.
    """
    def _get_base_query(self) -> orm.Query:
        return self.session.query(MeteringPoint)

    def has_gsrn(self, gsrn: str) -> 'MeteringPointQuery':
        return self.filter(MeteringPoint.gsrn == gsrn)

    def is_accessible_by(self, subject: str) -> 'MeteringPointQuery':
        return self


class DelegateQuery(SqlQuery):
    """
    Query MeteringPointDelegate.
    """
    def _get_base_query(self) -> orm.Query:
        return self.session.query(MeteringPointDelegate)

    def has_gsrn(self, gsrn: str) -> 'DelegateQuery':
        return self.filter(MeteringPointDelegate.gsrn == gsrn)

    def has_subject(self, subject: str) -> 'DelegateQuery':
        return self.filter(MeteringPointDelegate.subject == subject)


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


class TechnologyQuery(SqlQuery):
    """
    Query Technology.
    """
    def _get_base_query(self) -> orm.Query:
        return self.session.query(Technology)

    def has_tech_code(self, tech_code: str) -> 'TechnologyQuery':
        return self.filter(Technology.tech_code == tech_code)

    def has_fuel_code(self, fuel_code: str) -> 'TechnologyQuery':
        return self.filter(Technology.fuel_code == fuel_code)
