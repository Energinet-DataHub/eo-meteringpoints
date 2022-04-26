"""Runs a Message Bus consumer."""

from origin.bus import topics as t

from meteringpoints_shared.bus import broker

from .handlers import dispatcher


broker.listen(
    topics=[t.AUTH, t.METERINGPOINTS, t.TECHNOLOGIES],
    handler=dispatcher,
)
