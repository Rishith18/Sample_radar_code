# Library Documentation

A simple guide on internal library usage.

## Table of Contents

- [Introduction](#introduction)
  - [mrmapi](#mrmapi)
  - [commanager](#commanager)
- [Example Usage](#example-usage)
- [Properties](#properties)
- [Methods](#methods)
  - [`send_sync`](#send_sync)
  - [`get_data`](#get_data)
  - [`init_radar`](#init_radar)
  - [`exec_scan`](#exec_scan)
  - [`sleep_radar`](#sleep_radar)
  - [`wake_radar`](#wake_radar)

## Introduction

### mrmapi

The core of this project is the `src/lib/mrmapi` module. It contains functions to translate from and to the binary data used by the MRM API. In addition, it also contains utility functions to easily select the correct function given a name (e.g. `MRM_SET_CONFIG_REQUEST`) or ID (e.g. `0x1001`).

Specific documentation for the `mrmapi` module can be best found within the source code itself. [Link Here](../src//lib/mrmapi.py)

Documentation on the effects of every parameter are defined in the device Data Sheet and official MRM API Specification.

- [Data Sheet](https://fccid.io/NUF-P440-A/User-Manual/User-Manual-2878444.pdf)
- [API Specification](https://tdsr-uwb.com/wp-content/uploads/2021/03/320-0298G-MRM-API-Specification.pdf)

### commanager

Built on top of `mrmapi` is the `src/lib/commanager` module, which seeks to largely abstract away the specific details of the MRM API. It provides a simple interface for sending synchronous messages, as well as a refined interface for data collection. This module will be the focus of the rest of this documentation.

## Example Usage

```python
from lib.commanager import commanager

cmm = commanager()

# set radar config
config = cmm.init_radar(baseIntegrationIndex=11, persistFlag=1, scanStart=0, scanEnd=10000)

# start the scan
data = cmm.exec_scan(scanCount=100, scanInterval=0)

# turn off the radar
cmm.sleep_radar()
```

## Properties

- `mode` [`str`] - The current mode of the radar. Can be either `sync` or `async`. Defaults to `sync`.
  > Note: This property is not meant to be modified manually. It is used internally to ensure that the radar is in the correct mode before sending a message.
- `shutdown_mode` [`bool`] - Whether or not the radar is in the process of shutting down. Defaults to `False`. Used in GUI mode
- `databuffer` [`dequeue`] - A queue of all complete scans recieved from the radar.
- `partialbuffer` [`dequeue`] - A queue of all partial scans recieved from the radar.

## Methods

### `send_sync`

Sends a synchronous message to the radar and returns the response.

#### Parameters

- `msgtype` [`int or str`] - The message type to send. Can be either the message ID (e.g. `0x1001`) or the message name (e.g. `MRM_SET_CONFIG_REQUEST`).
- `noreply` [`bool`] - Whether or not to expect a reply from the radar. If `True`, the function will return an empty dict instead of the response.
- `**kwargs` [`dict`] - The parameters to send with the message. These should be the same as defined for the specified message type in the `mrmapi` module [Link Here](../src/lib/mrmapi.py).

#### Returns

- `response` [`dict`] - The response from the radar. If `noreply` is `True`, this will be an empty dict. The contents of the response will be the same as defined for the specified message type in the `mrmapi` module [Link Here](../src/lib/mrmapi.py).

#### Example

```python
from lib.commanager import commanager
cmm = commanager()
config = cmm.send_sync("MRM_GET_CONFIG_REQUEST", False)
cmm.send_sync(0x1003, False, scanCount=100, scanInterval=0)
```

### `get_data`

Fetches and processes a single data packet from the radar. All data recieved is store in `self.databuffer` and `self.partialbuffer`

#### Parameters

- `num_scans` [`int`] - The limit on the number of scans. Defaults to 10^8. This is used to determine whether this function needs to run again.

#### Returns

- `cont` [`bool`] - Whether or not the function should be called again. If `True`, the function should be called again. If `False`, the function has finished processing all data.

#### Example

```python
from lib.commanager import commanager
cmm = commanager()
cmm.get_data()
```

#### Behavior

This function is meant to be be used in a loop as part of an active monitoring system. As such, it may seem to wish to stop execution for non-obvious reasons. For clarity, a definitive list of stop conditions are listed below.

- (Internal) Async mode is disabled. This is triggered as a safeguard on execution order. To enable async mode manually **(NOT RECOMMENDED!)**, set `self.mode` to `async`.
- Socket Timeout. This is set to 2 seconds by default. This can be triggered when the connection is lost during a data transfer, or a data transfer is completed.
- The number of saved scans in `self.databuffer` and `self.partialbuffer` exceeds `num_scans`. This is unlikely to happen unless `num_scans` was modified, or the radar was configured to send data at a very high rate.

For use in GUI mode, this function will also set `self.shutdown_mode` to `True` if any of the following packets are recieved.

- `MRM_SET_SLEEPMODE_CONFIRM`
- `MRM_CONTROL_CONFIRM`

### `init_radar`

Initializes the radar with the specified configuration.

#### Parameters

- `**kwargs` [`dict`] - The parameters to send with the message. These should be the same as `MRM_SET_CONFIG_REQUEST` in the `mrmapi` module [Link Here](../src/lib/mrmapi.py).

#### Returns

- `config` [`dict`] - The configuration set by the radar. The contents of the response will be the same as `MRM_GET_CONFIG_CONFIRM` in the `mrmapi` module [Link Here](../src/lib/mrmapi.py).

> Note: Due to the way the radar operates, some fields (especially `scanStart` and `scanEnd`) may not be modified. This may be due to an incorrect `scanResolution` value.

> Note: `scanStart` and `scanEnd` values often differ than those set. This is due to hardware limitations of the radar. Consult the Data Sheet for more information.

#### Example

```python
from lib.commanager import commanager
cmm = commanager()
config = cmm.init_radar(baseIntegrationIndex=11, persistFlag=1, scanStart=0, scanEnd=10000)
```

### `exec_scan`

Executes a single scan with the specified configuration.

#### Parameters

- `scan_count` [`int`] - The number of scans to execute.
- `scan_interval` [`int`] - The time between scans in microseconds.

> Note: These are the values passed to `MRM_CONTROL_CONFIRM`

#### Returns

- `scandata` [`deque[dict]`] - The data recieved from the radar.

dict format:

```json
{
  "timestamp": 0,
  "data": [0, 0, 0, 0]
}
```

#### Example

```python
from lib.commanager import commanager
cmm = commanager()
cmm.init_radar(baseIntegrationIndex=11, persistFlag=1, scanStart=0, scanEnd=10000)
data = cmm.exec_scan(scanCount=100, scanInterval=0)
```

#### Behavior

This function _must_ be run after `init_radar` has been called. Failure to do so will cause undefined behavior. Data returned by this function is sorted by timestamp, and is padded to a common length in cases where missing packets were encountered.

### `sleep_radar`

Turns off the radar.

#### Parameters

None

#### Returns

None

#### Example

```python
from lib.commanager import commanager
cmm = commanager()
cmm.sleep_radar()
```

### Behavior

This function put the radar into `IDLE` mode.

### `wake_radar`

Turns on the radar. Halts until the radar is ready to accept commands.

#### Parameters

None

#### Returns

None

#### Example

```python
from lib.commanager import commanager
cmm = commanager()
cmm.wake_radar()
```

### Behavior

This function put the radar into `ACTIVE` mode.
