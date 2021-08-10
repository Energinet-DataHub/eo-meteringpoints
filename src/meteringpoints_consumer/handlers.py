from energytt_platform.bus import MessageDispatcher, messages as m
from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from meteringpoints_shared.queries import \
    MeteringPointQuery, TechnologyQuery, AddressQuery


@db.atomic
def on_meteringpoint_added(msg: m.MeteringPointAdded, session: db.Session):
    """
    TODO
    """
    meteringpoint = MeteringPointQuery(session) \
        .has_gsrn(msg.meteringpoint.gsrn) \
        .one_or_none()

    if meteringpoint:
        # Update existing MeteringPoint
        if msg.meteringpoint.sector:
            meteringpoint.sector = msg.meteringpoint.sector
        if msg.meteringpoint.type:
            meteringpoint.type = msg.meteringpoint.type
        if msg.meteringpoint.technology_code:
            meteringpoint.technology_code = msg.meteringpoint.technology_code
        if msg.meteringpoint.fuel_code:
            meteringpoint.fuel_code = msg.meteringpoint.fuel_code
    else:
        # Insert new MeteringPoint
        session.add(msg.meteringpoint)


@db.atomic
def on_meteringpoint_updated(msg: m.MeteringPointUpdated, session: db.Session):
    """
    TODO
    """
    meteringpoint = MeteringPointQuery(session) \
        .has_gsrn(msg.meteringpoint.gsrn) \
        .one_or_none()

    if meteringpoint:
        # Update existing MeteringPoint
        if msg.meteringpoint.sector:
            meteringpoint.sector = msg.meteringpoint.sector
        if msg.meteringpoint.type:
            meteringpoint.type = msg.meteringpoint.type
        if msg.meteringpoint.technology_code:
            meteringpoint.technology_code = msg.meteringpoint.technology_code
        if msg.meteringpoint.fuel_code:
            meteringpoint.fuel_code = msg.meteringpoint.fuel_code
    else:
        # Insert new MeteringPoint
        session.add(msg.meteringpoint)


@db.atomic
def on_meteringpoint_removed(msg: m.MeteringPointRemoved, session: db.Session):
    """
    Delete all Measurements from this MeteringPoint.
    """
    MeteringPointQuery(session) \
        .has_gsrn(msg.gsrn) \
        .delete()


@db.atomic
def on_meteringpoint_meta_data_update(msg: m.MeteringPointMetaDataUpdate, session: db.Session):
    """
    TODO
    """
    meteringpoint = MeteringPointQuery(session) \
        .has_gsrn(msg.gsrn) \
        .one_or_none()

    if not meteringpoint:
        meteringpoint = MeteringPoint()

    if msg.technology:
        pass

    if msg.address:
        address = AddressQuery(session) \
            .has_gsrn(msg.gsrn) \
            .one_or_none()

        if address:
            # Update existing address
            pass
        else:
            # Insert new address
            pass


@db.atomic
def on_technology_update(msg: m.TechnologyUpdate, session: db.Session):
    """
    TODO
    """
    technology = TechnologyQuery(session) \
        .has_technology_code(msg.technology.technology_code) \
        .has_fuel_code(msg.technology.fuel_code) \
        .one_or_none()

    if technology:
        # Update label for existing Technology
        technology.label = msg.technology.label
    else:
        # Insert new Technology
        session.add(msg.technology)


dispatcher = MessageDispatcher({
    m.MeteringPointAdded: on_meteringpoint_added,
    m.MeteringPointUpdated: on_meteringpoint_added,
    m.MeteringPointRemoved: on_meteringpoint_removed,
    m.MeteringPointMetaDataUpdate: on_meteringpoint_meta_data_update,
    m.TechnologyUpdate: on_technology_update,
})
