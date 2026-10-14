"""Config-driven CAN client (``CANInterface``). Signals are described by a DBC file and carried on `CanTransport`."""

from __future__ import annotations

import dataclasses
import threading
import time
from pathlib import Path
from typing import cast

import can
from cantools.database.can import Message

from instro.lib import Instrument, Measurement
from instro.lib.instrument import publish_measurement
from instro.lib.publishers import Publisher
from instro.unstable.transports.can import CanSubscription, CanTransport

from .types import CANConfig, CANConnectionInfo


@dataclasses.dataclass(frozen=True)
class _ReceivedFrame:
    """The newest frame seen for one message.

    Stamped with host receive time because adapter timestamps are not wall clock
    (gs_usb reports a device microsecond counter, or 0).
    """

    data: bytes
    received_at: int  # ns since the Unix epoch


class CANInterface(Instrument):
    """Config-driven CAN client. Reads and writes DBC signals by ``"Message.signal"`` name."""

    def __init__(
        self,
        config: CANConfig | dict | Path | str,
        connection: CanTransport | dict | None = None,
        name: str | None = None,
        publishers: list[Publisher] | None = None,
        **kwargs,
    ) -> None:
        """Initialize a CANInterface.

        Args:
            config: A ``CANConfig``, a dict (validated via Pydantic), or a path to a JSON config.
            connection: Overrides ``config.connection``. Pass a ``CanTransport`` to share one
                adapter between several interfaces, or a dict of ``CANConnectionInfo`` fields
                to build a private one. Required if the config has no ``connection`` section.
            name: Channel-name prefix; falls back to ``config.device.name``.
            publishers: Publishers that receive emitted Measurement/Command data.
            **kwargs: Default tags applied to every emitted Measurement/Command.

        Raises:
            ValueError: No connection in the arguments or the config.

        Example:
            >>> bus = CANInterface("bench_can.json")  # doctest: +SKIP
            >>> bus.open()  # doctest: +SKIP
            >>> bus.close()  # doctest: +SKIP
        """
        if isinstance(config, CANConfig):
            self._config = config
        elif isinstance(config, dict):
            self._config = CANConfig.model_validate(config)
        else:
            self._config = CANConfig.from_json(config)

        super().__init__(name=name or self._config.device.name, publishers=publishers, **kwargs)

        self._transport = _resolve_connection(connection, self._config)
        self._subscription: CanSubscription | None = None

        self._rx_messages_by_name = {m.name: m for m in self._config.rx_dbc_messages}
        self._rx_messages_by_frame_id = {(m.frame_id, m.is_extended_frame): m for m in self._config.rx_dbc_messages}

        # The background daemon and the caller both drain, so received-frame state is locked.
        self._lock = threading.Lock()
        self._latest_frames: dict[str, _ReceivedFrame] = {}

    # ============ Connection Management ============

    def open(self) -> None:
        """Take a hold on the transport (opening the bus if this is the first holder) and start receiving."""
        if self._subscription is not None:
            return
        self._transport.open(self)
        with self._lock:
            self._latest_frames.clear()
            self._subscription = self._transport.subscribe(self._is_rx_frame)

    def close(self) -> None:
        """Stop the daemon and release this interface's hold; the bus closes when its last holder leaves."""
        super().close()
        if self._subscription is None:
            return
        self._transport.unsubscribe(self._subscription)
        self._subscription = None
        self._transport.close(self)

    @property
    def is_open(self) -> bool:
        """Whether this interface is open."""
        return self._subscription is not None

    # ============ Reading ============

    @publish_measurement
    def read(self, signal: str, **kwargs) -> Measurement:
        """Return the latest received value of ``signal``, named ``"Message.signal"``.

        CAN devices broadcast, so nothing is requested from the bus: the value comes from
        the newest frame received since ``open()``, timestamped when it was received.

        Args:
            signal: ``"Message.signal"``, e.g. ``"BMS_Status.pack_voltage"``.
            **kwargs: Extra tags for this Measurement.

        Returns:
            Measurement: One sample on channel ``"<name>.<Message>.<signal>"``, in the DBC's units.

        Raises:
            KeyError: The message is not in ``rx_messages``, or has no such signal.
            RuntimeError: Not open, or no frame for the message has been received yet.
        """
        message, signal_name = _find_signal(signal, self._rx_messages_by_name, "rx_messages")
        with self._lock:
            self._drain_locked()
            frame = self._latest_frames.get(message.name)
        if frame is None:
            raise RuntimeError(f"No '{message.name}' frame received since open().")

        values = _decode(message, frame.data)
        if signal_name not in values:
            raise RuntimeError(f"'{signal}' is not in the latest '{message.name}' frame (multiplexed out).")
        return Measurement(
            channel_data={f"{self.name}.{signal}": [values[signal_name]]},
            timestamps=[frame.received_at],
            tags={**self.default_tags, **kwargs},
        )

    # ============ Internal Helpers ============

    def _is_rx_frame(self, frame: can.Message) -> bool:
        return (frame.arbitration_id, frame.is_extended_id) in self._rx_messages_by_frame_id

    def _drain_locked(self) -> None:
        """Move pending frames off the bus, keeping the newest frame of each message. Caller holds ``self._lock``."""
        if self._subscription is None:
            raise RuntimeError("CANInterface is not open. Call open() first.")
        received_at = time.time_ns()
        for frame in self._subscription.drain():
            message = self._rx_messages_by_frame_id[(frame.arbitration_id, frame.is_extended_id)]
            self._latest_frames[message.name] = _ReceivedFrame(bytes(frame.data), received_at)


def _decode(message: Message, data: bytes) -> dict[str, float]:
    """Decode a frame to physical signal values (scaling applied)."""
    # decode_choices=False keeps value-table signals numeric, and DBC messages are never containers,
    # so the result is always a flat name -> number mapping.
    return cast(dict[str, float], message.decode(data, decode_choices=False))


def _find_signal(signal: str, messages: dict[str, Message], config_field: str) -> tuple[Message, str]:
    """Split ``"Message.signal"`` and check both halves against ``messages``, one of the configured lists."""
    message_name, _, signal_name = signal.partition(".")
    message = messages.get(message_name)
    if message is None:
        raise KeyError(f"'{message_name}' is not in {config_field}: {sorted(messages)}")
    signal_names = [s.name for s in message.signals]
    if signal_name not in signal_names:
        raise KeyError(f"'{message_name}' has no signal '{signal_name}': {signal_names}")
    return message, signal_name


def _resolve_connection(connection: CanTransport | dict | None, config: CANConfig) -> CanTransport:
    """Pick the transport: a shared one passed in, one built from a dict, or one built from the config."""
    match connection:
        case CanTransport():
            return connection
        case dict():
            return CANConnectionInfo.model_validate(connection).build()
        case None if config.connection is not None:
            return config.connection.build()
        case _:
            raise ValueError(
                "No connection configuration provided. Either include a 'connection' section "
                "in the config or pass a 'connection' argument to CANInterface()."
            )
