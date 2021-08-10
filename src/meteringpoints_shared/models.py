from enum import Enum
from typing import List, Optional
from dataclasses import dataclass, field

from energytt_platform.serialize import Serializable
from energytt_platform.models.common import DateTimeRange, ResultOrdering
from energytt_platform.models.meteringpoints import MeteringPoint, MeteringPointType
# from energytt_platform.models.measurements import MeasurementType


# @dataclass
# class MeasurementFilters(Serializable):
#     """
#     Filters for querying Measurements.
#     """
#     gsrn: Optional[List[str]] = field(default=None)
#     sector: Optional[List[str]] = field(default=None)
#     type: Optional[MeasurementType] = field(default=None)
#     begin: Optional[DateTimeRange] = field(default=None)
#
#
# class MeasurementOrderingKeys(Enum):
#     """
#     Keys to order Measurements by when querying.
#     """
#     gsrn = 'gsrn'
#     type = 'type'
#     begin = 'begin'
#     amount = 'amount'
#
#
# MeasurementOrdering = ResultOrdering[MeasurementOrderingKeys]


@dataclass
class DbMeteringPoint(MeteringPoint):
    subject: Optional[str] = field(default=None)
