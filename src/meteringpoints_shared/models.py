from enum import Enum
from typing import List, Optional
from dataclasses import dataclass, field

from energytt_platform.serialize import Serializable
from energytt_platform.models.common import DateTimeRange, ResultOrdering
from energytt_platform.models.meteringpoints import MeteringPoint, MeteringPointType
# from energytt_platform.models.measurements import MeasurementType


@dataclass
class MeteringPointFilters(Serializable):
    """
    Filters for querying MeteringPoints.
    """
    gsrn: Optional[List[str]] = field(default=None)
    type: Optional[MeteringPointType] = field(default=None)
    sector: Optional[List[str]] = field(default=None)


class MeteringPointOrderingKeys(Enum):
    """
    Keys to order MeteringPoints by when querying.
    """
    gsrn = 'gsrn'
    type = 'type'
    sector = 'sector'


MeteringPointOrdering = ResultOrdering[MeteringPointOrderingKeys]


@dataclass
class MeteringPointDelegate:
    gsrn: str
    subject: str
