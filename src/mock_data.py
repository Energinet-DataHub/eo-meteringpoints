from energytt_platform.bus import messages as m, topics as t
from energytt_platform.models.common import Address
from energytt_platform.models.tech import \
    Technology, TechnologyCodes, TechnologyType
from energytt_platform.models.meteringpoints import \
    MeteringPoint, MeteringPointType

from meteringpoints_consumer.bus import broker


# -- Technologies ------------------------------------------------------------


broker.publish(
    topic=t.TECHNOLOGIES,
    msg=m.TechnologyUpdate(
        technology=Technology(
            tech_code='T010101',
            fuel_code='F01010101',
            type=TechnologyType.solar,
        ),
    ),
)

broker.publish(
    topic=t.TECHNOLOGIES,
    msg=m.TechnologyUpdate(
        technology=Technology(
            tech_code='T020202',
            fuel_code='F02020202',
            type=TechnologyType.wind,
        ),
    ),
)

broker.publish(
    topic=t.TECHNOLOGIES,
    msg=m.TechnologyUpdate(
        technology=Technology(
            tech_code='T030303',
            fuel_code='F03030303',
            type=TechnologyType.coal,
        ),
    ),
)


# -- MeteringPoint 1 ---------------------------------------------------------


broker.publish(
    topic=t.METERINGPOINTS,
    msg=m.MeteringPointAdded(
        meteringpoint=MeteringPoint(
            gsrn='1',
            type=MeteringPointType.production,
            sector='DK1',
        ),
    ),
)

broker.publish(
    topic=t.METERINGPOINTS,
    msg=m.MeteringPointTechnologyUpdated(
        gsrn='1',
        codes=TechnologyCodes(
            tech_code='T010101',
            fuel_code='F01010101',
        ),
    ),
)

broker.publish(
    topic=t.METERINGPOINTS,
    msg=m.MeteringPointAddressUpdated(
        gsrn='1',
        address=Address(
            street_code='street_code',
            street_name='street_name',
            building_number='building_number',
            floor_id='floor_id',
            room_id='room_id',
            post_code='post_code',
            city_name='city_name',
            city_sub_division_name='city_sub_division_name',
            municipality_code='municipality_code',
            location_description='location_description',
        ),
    ),
)


# -- MeteringPoint 2 (REVERSE ORDER OF EVENTS) -------------------------------


broker.publish(
    topic=t.METERINGPOINTS,
    msg=m.MeteringPointTechnologyUpdated(
        gsrn='2',
        codes=TechnologyCodes(
            tech_code='T020202',
            fuel_code='F02020202',
        ),
    ),
)


broker.publish(
    topic=t.METERINGPOINTS,
    msg=m.MeteringPointAdded(
        meteringpoint=MeteringPoint(
            gsrn='2',
            type=MeteringPointType.consumption,
            sector='DK1',
        ),
    ),
)
