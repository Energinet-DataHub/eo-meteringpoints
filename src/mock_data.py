import uuid
from datetime import datetime, timedelta

from energytt_platform.bus import messages as m, topics as t
from energytt_platform.models.common import Address
from energytt_platform.models.tech import \
    Technology, TechnologyCodes, TechnologyType
from energytt_platform.models.measurements import \
    Measurement, MeasurementType
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
    topic=t.MEASUREMENTS,
    msg=m.MeasurementUpdate(
        measurement=Measurement(
            id='1',
            gsrn='1',
            amount=100,
            begin=datetime.now(),
            end=datetime.now() + timedelta(hours=1),
        ),
    ),
)


broker.publish(
    topic=t.METERINGPOINTS,
    msg=m.MeteringPointUpdate(
        meteringpoint=MeteringPoint(
            gsrn='1',
            type=MeteringPointType.production,
            sector='DK1',
        ),
    ),
)

broker.publish(
    topic=t.METERINGPOINTS,
    msg=m.MeteringPointTechnologyUpdate(
        gsrn='1',
        codes=TechnologyCodes(
            tech_code='T010101',
            fuel_code='F01010101',
        ),
    ),
)

broker.publish(
    topic=t.METERINGPOINTS,
    msg=m.MeteringPointAddressUpdate(
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


broker.publish(
    topic=t.MEASUREMENTS,
    msg=m.MeasurementUpdate(
        measurement=Measurement(
            id='2',
            gsrn='1',
            amount=200,
            begin=datetime.now(),
            end=datetime.now() + timedelta(hours=1),
        ),
    ),
)


# -- MeteringPoint 2 (REVERSE ORDER OF EVENTS) -------------------------------


broker.publish(
    topic=t.METERINGPOINTS,
    msg=m.MeteringPointTechnologyUpdate(
        gsrn='2',
        codes=TechnologyCodes(
            tech_code='T020202',
            fuel_code='F02020202',
        ),
    ),
)


broker.publish(
    topic=t.METERINGPOINTS,
    msg=m.MeteringPointUpdate(
        meteringpoint=MeteringPoint(
            gsrn='2',
            type=MeteringPointType.consumption,
            sector='DK1',
        ),
    ),
)


begin = datetime(2021, 8, 18, 0, 0, 0)

for i in range(365 * 24):
    broker.publish(
        topic=t.MEASUREMENTS,
        msg=m.MeasurementUpdate(
            measurement=Measurement(
                id=str(3 + i),
                gsrn='2',
                amount=i * 10,
                begin=begin + timedelta(hours=i),
                end=begin + timedelta(hours=i) + timedelta(hours=1),
            ),
        ),
    )
