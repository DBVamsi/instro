# CAN

CANInterface is a config-driven CAN client. One JSON file names the adapter and a DBC file;
the DBC describes every message and signal (bit layout, scaling, units), so you read and
write signals by name instead of packing bytes.

```{warning}
CANInterface is new and is currently available only in the Unstable package.
```

```python
from instro.unstable.canbus import CANInterface

bus = CANInterface("bench_can.json", autostart=True)
bus.read("BMS_Status.pack_voltage")            # latest received value, in volts
bus.write("Motor_Command.torque_request", 5.0) # sends the whole Motor_Command frame
bus.close()
```

## Sample Config

```{literalinclude} ../../../packages/instro-unstable/instro/unstable/canbus/examples/bench_can.json
:language: json
```

## JSON Config Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `version` | int | `1` | Config format version |
| `protocol` | string | `"can"` | Must be `"can"` |
| `device` | object | *required* | {py:class}`~instro.lib.types.DeviceInfo`; `name` is the channel prefix |
| `connection` | object | `null` | The CAN adapter; see [Connection](#connection) |
| `timing` | object | `null` | `{"poll_interval": <seconds>}`; required for `autostart=True` |
| `dbc` | string | *required* | Path to the DBC file, relative to the JSON file |
| `rx_messages` | list | every DBC message | DBC message names to receive |
| `tx_messages` | list | `[]` | DBC message names this interface may send |

Message names are checked against the DBC when the config loads, so a typo fails before the bus is opened.

### Connection

Connection can be provided in the config or passed to the constructor, which takes precedence:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `interface` | string | *required* | python-can interface: `"gs_usb"`, `"slcan"`, `"socketcan"`, ... |
| `channel` | string or int | *required* | Adapter channel, e.g. `0` for gs_usb or `"COM4"` for slcan |
| `bitrate` | int | `500000` | Bus bitrate in bit/s |
| `bus_kwargs` | object | `{}` | Extra keyword arguments for `can.Bus` |

To put several interfaces on one adapter, pass the same
{py:class}`~instro.unstable.transports.can.CanTransport` to each; the bus stays open until the last one closes:

```python
from instro.unstable.transports import CanConfig, CanTransport

transport = CanTransport(CanConfig(channel=0, interface="gs_usb"))
bms = CANInterface("bms.json", connection=transport)
inverter = CANInterface("inverter.json", connection=transport)
```

## Reading

CAN devices broadcast, so `read("Message.signal")` requests nothing from the bus. It returns the
value from the newest frame received since `open()`, and raises if none has arrived yet.
Samples are timestamped with the host's receive time: adapter timestamps (gs_usb, for one) are
device counters, not wall-clock time.

The background daemon runs `poll()`, which publishes one Measurement per message that received a
new frame since the last poll, with a channel per signal: `vehicle_bus.BMS_Status.pack_voltage`.
A message that goes quiet stops publishing. Only the newest frame per message is kept between
polls, so set `poll_interval` shorter than a message's cycle time to publish every frame.

## Writing

`write("Message.signal", value)` takes the value in the DBC's units and sends the whole frame.
The message's other signals keep the last value written to them (their DBC initial value until
then), so writing one signal never resets its neighbours. Values outside the signal's DBC range
raise `cantools.database.EncodeError` and nothing is sent. Each write publishes a Command on
`<channel>.cmd`, e.g. `vehicle_bus.Motor_Command.torque_request.cmd`.

`send_frame(arbitration_id, data, is_extended_id=...)` sends a raw frame, bypassing the DBC.

Not yet supported: CAN FD, and writing multiplexed messages (reading them works).

## API Reference

```{eval-rst}
.. autosummary::
   :toctree: generated
   :nosignatures:

   ~instro.unstable.canbus.CANInterface
   ~instro.unstable.canbus.CANConfig
   ~instro.unstable.canbus.CANConnectionInfo
```
