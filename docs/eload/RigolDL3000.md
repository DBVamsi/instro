---
orphan: true
card: Rigol DL3000
image: RigolDL3000.png
myst:
  html_meta:
    description: "A driver for InstroELoad"
---

# RigolDL3000

{.lead}
A driver for [`InstroELoad`](/eload.md)

![Rigol DL3000](RigolDL3000.png){.driver-image}

The {py:obj}`RigolDL3000 <instro.eload.drivers.rigol_dl3000.RigolDL3000>` provides a driver that can be used to instantiate an [InstroELoad](/eload.md).

## Creating an [`InstroELoad`](/eload.md) with {py:obj}`RigolDL3000 <instro.eload.drivers.rigol_dl3000.RigolDL3000>`

```python
from instro.eload.drivers import RigolDL3000
from instro.eload import InstroELoad

eload = InstroELoad(
    name="myELoad",
    driver=RigolDL3000(visa_resource="USB0::0x1AB1::0x0E11::DL3A000001::INSTR"),
)
```

Parameters and methods specific to {py:obj}`RigolDL3000 <instro.eload.drivers.rigol_dl3000.RigolDL3000>` can be found in the [SDK](/sdk/index.md).
