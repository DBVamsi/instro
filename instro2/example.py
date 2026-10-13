from instro2.drivers.fakedmm import FakeDMM
from instro2.drivers.fakepsu import FakePSU
from instro2.lib.psu import InstroPSU
from instro2.lib.voltmeter import InstroVoltmeter
from instro2.transports.faketransport import FakeTransport


def main():
    my_psu = FakePSU(FakeTransport("USB0"))
    my_dmm = FakeDMM(FakeTransport("USB1"))
    run_test(my_psu, my_dmm)

def run_test(psu: InstroPSU, vm: InstroVoltmeter):
    volt_setpoint = 12
    psu.set_psu_voltage_setpoint(channel=1, voltage = volt_setpoint)
    psu.set_psu_current_setpoint(channel=1, current = 1)
    voltage = vm.get_voltmeter_measured_voltage(channel=1)
    assert volt_setpoint==voltage
