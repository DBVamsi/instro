"""Config-driven CAN client (``CANInterface``). Signals are described by a DBC file and carried on `CanTransport`."""

from __future__ import annotations

from pathlib import Path

import can

from instro.lib import Instrument
from instro.lib.publishers import Publisher
from instro.unstable.transports.can import CanSubscription, CanTransport

from .types import CANConfig, CANConnectionInfo


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
        self._rx_frame_ids = {(m.frame_id, m.is_extended_frame) for m in self._config.rx_dbc_messages}
        self._subscription: CanSubscription | None = None

    # ============ Connection Management ============

    def open(self) -> None:
        """Take a hold on the transport (opening the bus if this is the first holder) and start receiving."""
        if self._subscription is not None:
            return
        self._transport.open(self)
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

    # ============ Internal Helpers ============

    def _is_rx_frame(self, frame: can.Message) -> bool:
        return (frame.arbitration_id, frame.is_extended_id) in self._rx_frame_ids


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
