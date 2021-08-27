"""
Runs a Message Bus consumer.
"""
from energytt_platform.bus import topics as t

from .bus import broker
from .handlers import dispatcher


broker.listen(
    topics=[t.METERINGPOINTS, t.TECHNOLOGIES],
    handler=dispatcher,
)
