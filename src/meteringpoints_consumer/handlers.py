from energytt_platform.bus import MessageDispatcher, messages as m

from meteringpoints_shared.db import db

from .controller import controller


# -- MeteringPoints ----------------------------------------------------------


@db.atomic()
def on_meteringpoint_added(
        msg: m.MeteringPointAdded,
        session: db.Session,
):
    """
    TODO
    """
    meteringpoint = controller.get_or_create_meteringpoint(
        session=session,
        gsrn=msg.meteringpoint.gsrn,
    )

    meteringpoint.type = msg.meteringpoint.type
    meteringpoint.sector = msg.meteringpoint.sector

    if msg.meteringpoint.address:
        controller.set_meteringpoint_address(msg.meteringpoint.address)
    if msg.meteringpoint.technology:
        controller.set_meteringpoint_technology(msg.meteringpoint.technology)


@db.atomic()
def on_meteringpoint_removed(
        msg: m.MeteringPointRemoved,
        session: db.Session,
):
    """
    TODO
    """
    controller.delete_meteringpoint(
        session=session,
        gsrn=msg.gsrn,
    )


# -- MeteringPoint Addresses -------------------------------------------------


@db.atomic()
def on_meteringpoint_address_updated(
        msg: m.MeteringPointAddressUpdated,
        session: db.Session,
):
    """
    TODO
    """
    if msg.address is None:
        controller.delete_meteringpoint_address(
            session=session,
            gsrn=msg.gsrn,
        )
    else:
        controller.set_meteringpoint_address(
            session=session,
            gsrn=msg.gsrn,
            address=msg.address,
        )


# -- MeteringPoint Technologies ----------------------------------------------


@db.atomic()
def on_meteringpoint_technology_updated(
        msg: m.MeteringPointTechnologyUpdated,
        session: db.Session,
):
    """
    TODO
    """
    if msg.codes is None:
        controller.delete_meteringpoint_technology(
            session=session,
            gsrn=msg.gsrn,
        )
    else:
        controller.set_meteringpoint_technology(
            session=session,
            gsrn=msg.gsrn,
            technology=msg.codes,
        )


# -- Technologies ------------------------------------------------------------


@db.atomic()
def on_technology_update(
        msg: m.TechnologyUpdate,
        session: db.Session,
):
    """
    TODO
    """
    technology = controller.get_or_create_technology(
        session=session,
        tech_code=msg.technology.tech_code,
        fuel_code=msg.technology.fuel_code,
    )

    technology.type = msg.technology.type


@db.atomic()
def on_technology_removed(
        msg: m.TechnologyRemoved,
        session: db.Session,
):
    """
    TODO
    """
    controller.delete_technology(
        session=session,
        tech_code=msg.codes.tech_code,
        fuel_code=msg.codes.fuel_code,
    )


# -- Dispatcher --------------------------------------------------------------


dispatcher = MessageDispatcher({
    m.MeteringPointAdded: on_meteringpoint_added,
    m.MeteringPointRemoved: on_meteringpoint_removed,
    m.MeteringPointAddressUpdated: on_meteringpoint_address_updated,
    m.MeteringPointTechnologyUpdated: on_meteringpoint_technology_updated,
    # m.MeteringPointDelegateGranted: on_meteringpoint_delegate_granted,
    # m.MeteringPointDelegateRevoked: on_meteringpoint_delegate_revoked,
    m.TechnologyUpdate: on_technology_update,
    m.TechnologyRemoved: on_technology_removed,
})
