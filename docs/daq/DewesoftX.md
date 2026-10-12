---
orphan: true
card: DewesoftX
image: DewesoftX.png
myst:
  html_meta:
    description: "A driver for InstroDAQ"
---

# DewesoftX

{.lead}
A driver for [`InstroDAQ`](/daq.md)

![DewesoftX](DewesoftX.png){.driver-image}

:::{note}
This driver is Windows only and ships in the `instro-daq-dewesoftx` package. Install it with the `dewesoftx` extra: `pip install "instro[dewesoftx]"`.
:::

The {py:obj}`DewesoftX <instro.daq.drivers.dewesoftx.dewesoftx.DewesoftX>` driver provides a driver that can be used to instantiate an [InstroDAQ](/daq.md). It attaches over DCOM to a DewesoftX instance already running on the same PC and exposes its live channels.

## Creating an [`InstroDAQ`](/daq.md) with {py:obj}`DewesoftX <instro.daq.drivers.dewesoftx.dewesoftx.DewesoftX>`

```python
from instro.daq import InstroDAQ
from instro.daq.drivers.dewesoftx import DewesoftX

# attaches to the DewesoftX instance running on this Windows PC
daq = InstroDAQ(name="dewesoftDAQ", driver=DewesoftX())
```

Pass `dxd_name` to control the `.dxd` file `start()` stores to; the default names it after the run time.

Parameters and methods specific to {py:obj}`DewesoftX <instro.daq.drivers.dewesoftx.dewesoftx.DewesoftX>` can be found in the [SDK](/sdk/index.md).
