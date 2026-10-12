# instro-daq-dewesoftx

DewesoftX DAQ drivers for [`instro`](https://github.com/nominal-io/instro).

This package contributes `DewesoftX` under `instro.daq.drivers.dewesoftx`. The driver attaches over DCOM to a [DewesoftX](https://dewesoft.com) instance already running on the same PC, streams its live channels, and runs behind the `InstroDAQ` hardware abstraction alongside the other DAQ vendors.

## Installation

```bash
pip install 'instro[dewesoftx]'
```

DewesoftX exposes its DCOM interface only on Windows, so this package runs on Windows.

## Usage

Construct the driver, optionally with the name of the `.dxd` file to store to, then pass it to `InstroDAQ`:

```python
from instro.daq import InstroDAQ
from instro.daq.drivers.dewesoftx import DewesoftX

daq = InstroDAQ(name="myDAQ", driver=DewesoftX())
```

See the [DAQ guides](https://instro.nominal.io) for channel configuration, hardware timing, and publishing to Nominal Core.

## License

[Apache License 2.0](https://github.com/nominal-io/instro/blob/main/packages/instro-daq-dewesoftx/LICENSE).
