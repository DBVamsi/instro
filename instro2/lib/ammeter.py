from typing import Protocol

from instro2.lib.instrument import commands, measures


class InstroAmmeter(Protocol):

    @measures("ammeter.ch{channel}.current")
    def get_ammeter_measured_current(self, channel: int) -> float:
        ...

    @commands("ammeter.ch{channel}.range.cmd", value="range")
    def set_ammeter_range(self, channel: int, range: int) -> None:
        ...
