from instro2.lib.ammeter import InstroAmmeter
from instro2.lib.instrument import Instrument
from instro2.lib.ohmmeter import InstroOhmmeter
from instro2.lib.transport import MessageTransport
from instro2.lib.voltmeter import InstroVoltmeter


class FakeDMM(Instrument, InstroAmmeter, InstroVoltmeter, InstroOhmmeter):
    def __init__(self, transport: MessageTransport) -> None:
        super().__init__(name="FakeDMM", transport=transport)
        self.transport = transport

    def get_ammeter_measured_current(self, channel: int) -> float:
        return float(self.transport.query(f"MEAS:CURR? CH:{channel}"))

    def set_ammeter_range(self, channel: int, range: int) -> None:
        self.transport.write(f"SENS:CURR:RANGE {range} CH:{channel}")

    def get_voltmeter_measured_voltage(self, channel: int) -> float:
        return float(self.transport.query(f"MEAS:VOLT? CH:{channel}"))

    def set_voltmeter_range(self, channel: int, range: int) -> None:
        self.transport.write(f"SENS:VOLT:RANGE {range} CH:{channel}")

    def get_ohmmeter_measured_resistance(self, channel: int) -> float:
        return float(self.transport.query(f"MEAS:OHM? CH:{channel}"))

    def set_ohmmeter_range(self, channel: int, range: int) -> None:
        self.transport.write(f"SENS:OHM:RANGE {range} CH:{channel}")
