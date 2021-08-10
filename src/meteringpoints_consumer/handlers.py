from energytt_platform.bus import MessageDispatcher, messages as m
from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from meteringpoints_shared.queries import (
    MeteringPointQuery,
    MeteringPointDelegateQuery,
    AddressQuery,
    TechnologyQuery,
)


@db.atomic
def on_meteringpoint_added(
        msg: m.MeteringPointAdded,
        session: db.Session,
):
    """
    TODO
    """
    meteringpoint = MeteringPointQuery(session) \
        .has_gsrn(msg.meteringpoint.gsrn) \
        .one_or_none()

    if meteringpoint:
        meteringpoint.update(msg.meteringpoint)
    else:
        session.add(msg.meteringpoint)


@db.atomic
def on_meteringpoint_updated(
        msg: m.MeteringPointUpdated,
        session: db.Session,
):
    """
    TODO
    """
    meteringpoint = MeteringPointQuery(session) \
        .has_gsrn(msg.gsrn) \
        .one_or_none()

    if not meteringpoint:
        meteringpoint = MeteringPoint(gsrn=msg.gsrn)
        session.add(meteringpoint)

    if msg.basics:
        meteringpoint.update(msg.basics)
    if msg.technology:
        meteringpoint.update(msg.technology)
    if msg.address:
        meteringpoint.update(msg.address)


@db.atomic
def on_meteringpoint_removed(
        msg: m.MeteringPointRemoved,
        session: db.Session,
):
    """
    Delete all Measurements from this MeteringPoint.
    """
    MeteringPointQuery(session) \
        .has_gsrn(msg.gsrn) \
        .delete()

    MeteringPointDelegateQuery(session) \
        .has_gsrn(msg.gsrn) \
        .delete()


# -- Delegates ---------------------------------------------------------------


@db.atomic
def on_meteringpoint_delegate_granted(
        msg: m.MeteringPointDelegateGranted,
        session: db.Session,
):
    """
    TODO
    """
    exists = MeteringPointDelegateQuery(session) \
        .has_gsrn(msg.delegate.gsrn) \
        .has_subject(msg.delegate.subject) \
        .exists()

    if not exists:
        session.add(msg.delegate)


@db.atomic
def on_meteringpoint_delegate_revoked(
        msg: m.MeteringPointDelegateRevoked,
        session: db.Session,
):
    """
    TODO
    """
    MeteringPointDelegateQuery(session) \
        .has_gsrn(msg.delegate.gsrn) \
        .has_subject(msg.delegate.subject) \
        .delete()


# -- Technologies ------------------------------------------------------------


@db.atomic
def on_technology_update(
        msg: m.TechnologyUpdate,
        session: db.Session,
):
    """
    TODO
    """
    technology = TechnologyQuery(session) \
        .has_technology_code(msg.technology.tech_code) \
        .has_fuel_code(msg.technology.fuel_code) \
        .one_or_none()

    if technology:
        # Update type for existing Technology
        technology.type = msg.technology.type
    else:
        # Insert new Technology
        session.add(msg.technology)


@db.atomic
def on_technology_removed(
        msg: m.TechnologyRemoved,,
        session: db.Session,
):
    """
    TODO
    """
    TechnologyQuery(session) \
        .has_technology_code(msg.tech_code) \
        .has_fuel_code(msg.fuel_code) \
        .delete()


# -- Dispatcher --------------------------------------------------------------


dispatcher = MessageDispatcher({
    m.MeteringPointUpdated: on_meteringpoint_updated,
    m.MeteringPointRemoved: on_meteringpoint_removed,
    m.MeteringPointDelegateGranted: on_meteringpoint_delegate_granted,
    m.MeteringPointDelegateRevoked: on_meteringpoint_delegate_revoked,
    m.TechnologyUpdate: on_technology_update,
    m.TechnologyRemoved: on_technology_removed,
})
