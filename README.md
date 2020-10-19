# pypurea9

[![Build Status](https://travis-ci.org/hymnis/pypurea9.svg?branch=master)](https://travis-ci.org/hymnis/pypurea9)
[![pyi](https://img.shields.io/pypi/v/pypurea9.svg)](https://pypi.python.org/pypi/pypurea9)
[![pyi](https://img.shields.io/pypi/pyversions/pypurea9.svg)](https://pypi.python.org/pypi/pypurea9)

Python 3 API for communicating with an Electrolux Pure A9 air purifier, through the cloud (yes, no local control is possible at this point).

There is currently no open API, but Electrolux have said that they are going to release one eventually.

## Installation

The fast and easy way:
```bash
pip3 install pypurea9
```

The not as fast way:
```bash
cd /path/to/repo
python3 setup.py install
```

## Requirements

- Python 3
- The [requests](http://docs.python-requests.org/) module.
- A Pure A9 device that is properly setup in the Electrolux Wellbeing phone app.
- The client secret, username and password used in Electrolux Wellbeing phone app.

## Command-line usage

### Help

```bash
purea9 -h
purea9 <command> -h
```

### Commands

- get_devices
- get_info
- get_data
- set_state
- test

## Usage as a Python module

```python
#! /usr/bin/env python3

from pypurea9 import PureA9, PureA9Error

# credentials as parameters
purea9_client = PureA9('ankJaAjapsdvxu9xc9in2jkasdASda34wf', 'Myname', 'abc123')
devices = purea9_client.get_devices()
print(purea9_client.get_info(devices[0]))
print(purea9_client.get_data(devices[0]))

try:
  # turn the unit off
  purea9_client.set_state(devices[0], 'power', 'off')

  # turn the unit on and set to manual mode, with given speed setting
  purea9_client.set_state(devices[0], 'power', 'on')
  purea9_client.set_state(devices[0], 'preset_mode', 'manual')
  purea9_client.set_state(devices[0], 'fan_mode', '6')

  # or with a single call (the state order is important)
  purea9_client.set_state(devices[0], {
    'power': 'on,
    'preset_mode': 'manual',
    'fan_mode': '6'
  })
except PureA9Error as err:
  print(f"Something went wrong! See here: {err}")
```

## License and warranty

Written and release under the the Unlicense. There is no warranty.

This is **NOT** official software from Electrolux or in any way endorsed or supported by the company.

It was written for personal use and you may improve or adapt it however you want.
