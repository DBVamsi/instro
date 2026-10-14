"""Tests for CANInterface against python-can's in-process virtual bus (issue #641)."""

from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import can
import pytest

from instro.unstable.canbus import CANInterface
from instro.unstable.transports import CanConfig, CanTransport

DBC = Path(__file__).parent / "vehicle.dbc"


@pytest.fixture
def channel() -> str:
    """A virtual-bus channel name no other test shares."""
    return f"test-{uuid4()}"


@pytest.fixture
def peer(channel: str) -> Iterator[can.BusABC]:
    """The other node on the bus: sends frames to the interface and receives what it writes."""
    bus = can.Bus(interface="virtual", channel=channel)
    yield bus
    bus.shutdown()


def _interface(connection: str | CanTransport, **overrides: object) -> CANInterface:
    config = {"device": {"name": "vehicle_bus"}, "dbc": DBC, **overrides}
    if isinstance(connection, CanTransport):
        return CANInterface(config, connection=connection)
    return CANInterface(config, connection={"interface": "virtual", "channel": connection})


def test_interfaces_sharing_a_transport_keep_the_bus_open_until_the_last_closes(channel: str) -> None:
    transport = CanTransport(CanConfig(channel=channel, interface="virtual"))
    first, second = _interface(transport), _interface(transport)

    first.open()
    second.open()
    first.close()
    assert transport.is_open

    second.close()
    assert not transport.is_open
