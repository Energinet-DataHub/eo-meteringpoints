from sqlalchemy import orm

from energytt_platform.sql import SqlQuery
from energytt_platform.models.common import Address
from energytt_platform.models.technologies import Technology
from energytt_platform.models.meteringpoints import \
    MeteringPoint, MeteringPointDelegate


class MeteringPointQuery(SqlQuery):
    """
    Query MeteringPoints.
    """
    # def __init__(self, session: orm.Session, q: orm.Query = None):
    #     """
    #     :param session:
    #     :param q:
    #     """
    #     if q is None:
    #         q = session.query(MeteringPoint)
    #     super(MeteringPointQuery, self).__init__(session, q)

    def _get_base_query(self) -> orm.Query:
        return self.session.query(MeteringPoint)

    def has_gsrn(self, gsrn: str) -> 'MeteringPointQuery':
        return self.filter(MeteringPoint.gsrn == gsrn)

    def is_accessible_by(self, subject: str) -> 'MeteringPointQuery':
        return self

    # def apply_filters(self, filters: MeasurementFilters) -> 'MeasurementQuery':
    #     """
    #     TODO
    #     """
    #     q = self
    #
    #     if filters.gsrn is not None:
    #         q = q.has_any_gsrn(filters.gsrn)
    #     if filters.sector is not None:
    #         q = q.in_any_sector(filters.sector)
    #     if filters.type is not None:
    #         q = q.is_type(filters.type)
    #     if filters.begin is not None:
    #         q = q.begins_within(filters.begin)
    #
    #     return q
    #
    # def apply_ordering(self, ordering: MeasurementOrdering) -> 'MeasurementQuery':
    #     return self
    #
    # def has_id(self, id: str) -> 'MeasurementQuery':
    #     return self.filter(Measurement.id == id)
    #
    # def has_gsrn(self, gsrn: str) -> 'MeasurementQuery':
    #     return self
    #
    # def has_any_gsrn(self, gsrn: List[str]) -> 'MeasurementQuery':
    #     return self
    #
    # def in_any_sector(self, sector: List[str]) -> 'MeasurementQuery':
    #     return self
    #
    # def is_type(self, type: MeasurementType) -> 'MeasurementQuery':
    #     return self.filter(Measurement.type == type)
    #
    # def begins_at(self, begin: datetime) -> 'MeasurementQuery':
    #     return self.filter(Measurement.begin == begin)
    #
    # def begins_within(self, begin_range: DateTimeRange) -> 'MeasurementQuery':
    #     return self


class MeteringPointDelegateQuery(SqlQuery):
    """
    Query MeteringPoints.
    """
    # def __init__(self, session: orm.Session, q: orm.Query = None):
    #     """
    #     :param session:
    #     :param q:
    #     """
    #     if q is None:
    #         q = session.query(MeteringPointDelegate)
    #     super(MeteringPointDelegateQuery, self).__init__(session, q)

    def _get_base_query(self) -> orm.Query:
        return self.session.query(MeteringPointDelegate)

    def has_gsrn(self, gsrn: str) -> 'MeteringPointDelegateQuery':
        return self.filter(MeteringPointDelegate.gsrn == gsrn)

    def has_subject(self, subject: str) -> 'MeteringPointDelegateQuery':
        return self.filter(MeteringPointDelegate.subject == subject)


class AddressQuery(SqlQuery):
    """
    Query MeteringPoints.
    """
    # def __init__(self, session: orm.Session, q: orm.Query = None):
    #     """
    #     :param session:
    #     :param q:
    #     """
    #     if q is None:
    #         q = session.query(Address)
    #     super(AddressQuery, self).__init__(session, q)

    def _get_base_query(self) -> orm.Query:
        return self.session.query(Address)

    def has_technology_code(self, technology_code: str) -> 'AddressQuery':
        return self.filter(Technology.technology_code == technology_code)

    def has_gsrn(self, fuel_code: str) -> 'AddressQuery':
        return self.filter(Technology.fuel_code == fuel_code)


class TechnologyQuery(SqlQuery):
    """
    Query MeteringPoints.
    """
    # def __init__(self, session: orm.Session, q: orm.Query = None):
    #     """
    #     :param session:
    #     :param q:
    #     """
    #     if q is None:
    #         q = session.query(Technology)
    #     super(TechnologyQuery, self).__init__(session, q)

    def _get_base_query(self) -> orm.Query:
        return self.session.query(Technology)

    def has_technology_code(self, technology_code: str) -> 'TechnologyQuery':
        return self.filter(Technology.technology_code == technology_code)

    def has_fuel_code(self, fuel_code: str) -> 'TechnologyQuery':
        return self.filter(Technology.fuel_code == fuel_code)
