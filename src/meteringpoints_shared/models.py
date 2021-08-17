import sqlalchemy as sa
from sqlalchemy.orm import relationship

from energytt_platform.models.tech import TechnologyType
from energytt_platform.models.meteringpoints import MeteringPointType

from .db import db


# -- MeteringPoints ----------------------------------------------------------


class DbMeteringPoint(db.ModelBase):
    """
    SQL representation of a MeteringPoint.
    """
    __tablename__ = 'meteringpoint'
    __table_args__ = (
        sa.PrimaryKeyConstraint('gsrn'),
        sa.UniqueConstraint('gsrn'),
    )

    gsrn = sa.Column(sa.String(), index=True, nullable=False)
    sector = sa.Column(sa.String(), index=True, nullable=False)
    type = sa.Column(sa.Enum(MeteringPointType), index=True, nullable=False)

    # -- Relationships -------------------------------------------------------

    technology = relationship(
        'DbTechnology',
        primaryjoin='foreign(DbMeteringPoint.gsrn) == DbMeteringPointTechnology.gsrn',
        secondary='meteringpoint_technology',
        secondaryjoin=(
            'and_('
            'foreign(DbMeteringPointTechnology.tech_code) == DbTechnology.tech_code,'
            'foreign(DbMeteringPointTechnology.fuel_code) == DbTechnology.fuel_code'
            ')'
        ),
        uselist=False,
        viewonly=True,
        lazy='joined',
    )

    address = relationship(
        'DbMeteringPointAddress',
        primaryjoin='foreign(DbMeteringPoint.gsrn) == DbMeteringPointAddress.gsrn',
        uselist=False,
        viewonly=True,
        lazy='joined',
    )


class DbMeteringPointAddress(db.ModelBase):
    """
    SQL representation of a (physical) address of a MeteringPoint.
    """
    __tablename__ = 'meteringpoint_address'
    __table_args__ = (
        sa.PrimaryKeyConstraint('gsrn'),
        sa.UniqueConstraint('gsrn'),
    )

    gsrn = sa.Column(sa.String(), index=True, nullable=False)
    street_code = sa.Column(sa.String())
    street_name = sa.Column(sa.String())
    building_number = sa.Column(sa.String())
    floor_id = sa.Column(sa.String())
    room_id = sa.Column(sa.String())
    post_code = sa.Column(sa.String())
    city_name = sa.Column(sa.String())
    city_sub_division_name = sa.Column(sa.String())
    municipality_code = sa.Column(sa.String())
    location_description = sa.Column(sa.String())


class DbMeteringPointTechnology(db.ModelBase):
    """
    SQL representation of a technology of a MeteringPoint.
    """
    __tablename__ = 'meteringpoint_technology'
    __table_args__ = (
        sa.PrimaryKeyConstraint('gsrn'),
        sa.UniqueConstraint('gsrn'),
    )

    gsrn = sa.Column(sa.String(), index=True, nullable=False)
    tech_code = sa.Column(sa.String())
    fuel_code = sa.Column(sa.String())


# -- Technologies ------------------------------------------------------------


class DbTechnology(db.ModelBase):
    """
    SQL representation of a Technology.
    """
    __tablename__ = 'technology'
    __table_args__ = (
        sa.PrimaryKeyConstraint('tech_code', 'fuel_code'),
        sa.UniqueConstraint('tech_code', 'fuel_code'),
    )

    fuel_code = sa.Column(sa.String())
    tech_code = sa.Column(sa.String())
    type = sa.Column(sa.Enum(TechnologyType))
