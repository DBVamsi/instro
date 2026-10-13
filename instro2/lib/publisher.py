from typing import Protocol

from instro.lib.types import Command, Measurement


class Publisher(Protocol):
    def publish(self, data: Measurement | Command) -> None: ...

    def close(self) -> None: ...
