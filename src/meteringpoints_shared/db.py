import sqlalchemy as sa

from energytt_platform.sql import SqlEngine
from energytt_platform.models.common import Address
from energytt_platform.models.technologies import Technology
from energytt_platform.models.meteringpoints import \
    MeteringPoint, MeteringPointType

from .config import SQL_URI, SQL_POOL_SIZE


db = SqlEngine(
    uri=SQL_URI,
    pool_size=SQL_POOL_SIZE,
)


db.registry.map_imperatively(Address, sa.Table(
    'addresses',
    db.registry.metadata,
    sa.Column('id', sa.String(50), primary_key=True),
    sa.Column('gsrn', sa.String(), nullable=True, index=True),
    sa.Column('street_code', sa.String(), nullable=True),
    sa.Column('street_name', sa.String(), nullable=True),
    sa.Column('building_number', sa.String(), nullable=True),
    sa.Column('floor_id', sa.String(), nullable=True),
    sa.Column('room_id', sa.String(), nullable=True),
    sa.Column('post_code', sa.String(), nullable=True),
    sa.Column('city_name', sa.String(), nullable=True),
    sa.Column('city_sub_division_name', sa.String(), nullable=True),
    sa.Column('municipality_code', sa.String(), nullable=True),
    sa.Column('location_description', sa.String(), nullable=True),
    sa.UniqueConstraint('gsrn', name='unique_gsrn'),
))


db.registry.map_imperatively(Technology, sa.Table(
    'technologies',
    db.registry.metadata,
    sa.Column('technology_code', sa.String(7), nullable=True),
    sa.Column('fuel_code', sa.String(9), nullable=True),
    sa.Column('label', sa.String(20), nullable=False),
    sa.PrimaryKeyConstraint('technology_code', 'fuel_code', name='tech_fuel_key'),
    sa.UniqueConstraint('technology_code', 'fuel_code', name='unique_tech_fuel_codes'),
))


db.registry.map_imperatively(MeteringPoint, sa.Table(
    'meteringpoints',
    db.registry.metadata,
    sa.Column('gsrn', sa.String(15), primary_key=True, nullable=False),
    sa.Column('sector', sa.String(20), nullable=False),
    sa.Column('type', sa.Enum(MeteringPointType), nullable=True),
    sa.Column('technology_code', sa.String(7), nullable=True),
    sa.Column('fuel_code', sa.String(9), nullable=True),
    sa.UniqueConstraint('gsrn', name='unique_gsrn'),
))
