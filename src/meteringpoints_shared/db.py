import sqlalchemy as sa

from energytt_platform.sql import SqlEngine
from energytt_platform.models.common import Address
from energytt_platform.models.technologies import Technology
from energytt_platform.models.meteringpoints import \
    MeteringPoint, MeteringPointType, MeteringPointDelegate

from .config import SQL_URI, SQL_POOL_SIZE


db = SqlEngine(
    uri=SQL_URI,
    pool_size=SQL_POOL_SIZE,
)


# db.registry.map_imperatively(Address, sa.Table(
#     'addresses',
#     db.registry.metadata,
#     sa.Column('id', sa.String(), primary_key=True),
#     sa.Column('gsrn', sa.String(), nullable=True, index=True),
#     sa.Column('street_code', sa.String(), nullable=True),
#     sa.Column('street_name', sa.String(), nullable=True),
#     sa.Column('building_number', sa.String(), nullable=True),
#     sa.Column('floor_id', sa.String(), nullable=True),
#     sa.Column('room_id', sa.String(), nullable=True),
#     sa.Column('post_code', sa.String(), nullable=True),
#     sa.Column('city_name', sa.String(), nullable=True),
#     sa.Column('city_sub_division_name', sa.String(), nullable=True),
#     sa.Column('municipality_code', sa.String(), nullable=True),
#     sa.Column('location_description', sa.String(), nullable=True),
#     sa.UniqueConstraint('gsrn', name='unique_gsrn'),
# ))


db.registry.map_imperatively(Technology, sa.Table(
    'technologies',
    db.registry.metadata,
    sa.Column('technology_code', sa.String(), nullable=False),
    sa.Column('fuel_code', sa.String(), nullable=False),
    sa.Column('label', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('technology_code', 'fuel_code', name='tech_fuel_key'),
    sa.UniqueConstraint('technology_code', 'fuel_code', name='unique_tech_fuel_codes'),
))


db.registry.map_imperatively(MeteringPoint, sa.Table(
    'meteringpoints',
    db.registry.metadata,

    # MeteringPoint
    sa.Column('gsrn', sa.String(), primary_key=True, nullable=False),
    sa.Column('sector', sa.String()),
    sa.Column('type', sa.Enum(MeteringPointType)),

    # TechnologyCodes
    sa.Column('technology_code', sa.String()),
    sa.Column('fuel_code', sa.String()),

    # Address
    sa.Column('street_code', sa.String()),
    sa.Column('street_name', sa.String()),
    sa.Column('building_number', sa.String()),
    sa.Column('floor_id', sa.String()),
    sa.Column('room_id', sa.String()),
    sa.Column('post_code', sa.String()),
    sa.Column('city_name', sa.String()),
    sa.Column('city_sub_division_name', sa.String()),
    sa.Column('municipality_code', sa.String()),
    sa.Column('location_description', sa.String()),

    # Table constraints
    sa.UniqueConstraint('gsrn', name='unique_gsrn'),
))


db.registry.map_imperatively(MeteringPointDelegate, sa.Table(
    'delegates',
    db.registry.metadata,
    sa.Column('gsrn', sa.String(), nullable=False),
    sa.Column('subject', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('gsrn', 'subject'),
    sa.UniqueConstraint('gsrn', 'subject'),
))
