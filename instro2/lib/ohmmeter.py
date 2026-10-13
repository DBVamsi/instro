from typing import Protocol

from instro2.lib.instrument import commands, measures


class InstroOhmmeter(Protocol):

    @measures("ohmmeter.ch{channel}.resistance")
    def get_ohmmeter_measured_resistance(self, channel: int) -> float:
        ...

    @commands("ohmmeter.ch{channel}.range.cmd", value="range")
    def set_ohmmeter_range(self, channel: int, range: int) -> None:
        ...
