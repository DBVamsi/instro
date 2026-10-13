from instro2.lib.instrument import Instrument
from instro2.lib.psu import InstroPSU
from instro2.lib.transport import MessageTransport


class FakePSU(Instrument, InstroPSU):
    def __init__(self, transport: MessageTransport) -> None:
        super().__init__(name="FakePSU", transport=transport)
        self.transport = transport

    def get_psu_measured_voltage(self, channel: int) -> float:
        return float(self.transport.query(f"MEAS:VOLT? CH:{channel}"))

    def get_psu_voltage_setpoint(self, channel: int) -> float:
        return float(self.transport.query(f"VOLT? CH:{channel}"))

    def set_psu_voltage_setpoint(self, channel: int, voltage: float) -> None:
        self.transport.write(f"VOLT {voltage} CH:{channel}")

    def get_psu_measured_current(self, channel: int) -> float:
        return float(self.transport.query(f"MEAS:CURR? CH:{channel}"))

    def get_psu_current_setpoint(self, channel: int) -> float:
        return float(self.transport.query(f"CURR? CH:{channel}"))

    def set_psu_current_setpoint(self, channel: int, current: float) -> None:
        self.transport.write(f"CURR {current} CH:{channel}")
