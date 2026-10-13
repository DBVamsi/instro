from typing import Protocol

from instro2.lib.instrument import commands, measures


class InstroPSU(Protocol):
    def connect(self):
        ...

    def disconnect(self):
        ...

    @measures("psu.ch{channel}.voltage")
    def get_psu_measured_voltage(self, channel: int) -> float:
        ...

    @measures("psu.ch{channel}.voltage.setpoint")
    def get_psu_voltage_setpoint(self, channel: int) -> float:
        ...

    @commands("psu.ch{channel}.voltage.cmd", value="voltage")
    def set_psu_voltage_setpoint(self, channel: int, voltage: float) -> None:
        ...

    @measures("psu.ch{channel}.current")
    def get_psu_measured_current(self, channel: int) -> float:
        ...

    @measures("psu.ch{channel}.current.setpoint")
    def get_psu_current_setpoint(self, channel: int) -> float:
        ...

    @commands("psu.ch{channel}.current.cmd", value="current")
    def set_psu_current_setpoint(self, channel: int, current: float) -> None:
        ...
