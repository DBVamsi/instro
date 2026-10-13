from typing import Protocol

from instro2.lib.instrument import commands, measures


class InstroVoltmeter(Protocol):

    @measures("voltmeter.ch{channel}.voltage")
    def get_voltmeter_measured_voltage(self, channel: int) -> float:
        ...

    @commands("voltmeter.ch{channel}.range.cmd", value="range")
    def set_voltmeter_range(self, channel: int, range: int) -> None:
        ...
