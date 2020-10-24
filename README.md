# pypure

[![Build Status](https://travis-ci.org/hymnis/pypure.svg?branch=master)](https://travis-ci.org/hymnis/pypure)
[![Maintainability](https://api.codeclimate.com/v1/badges/99b6552ee2e6848806f0/maintainability)](https://codeclimate.com/github/hymnis/pypure/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/99b6552ee2e6848806f0/test_coverage)](https://codeclimate.com/github/hymnis/pypure/test_coverage)

Python 3 API for communicating with an Electrolux Pure appliances, through the cloud (yes, there's no local control is possible at this point).

There is currently no open API, but Electrolux have said that they are going to release one eventually.

## Installation

The fast and easy way:
```bash
pip3 install pypure
```

The not as fast way:
```bash
cd /path/to/repo
python3 setup.py install
```

## Requirements

- Python 3
- The [requests](http://docs.python-requests.org/) module.
- A Pure appliance/device that is properly setup in the Electrolux Wellbeing phone app.
- The client secret, username and password used in Electrolux Wellbeing phone app.

## Command-line usage

### Help

```bash
pypure -h
pypure <command> -h
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

from pypure import PyPure, PyPureError

# credentials as parameters
pure_client = PyPure('ankJaAjapsdvxu9xc9in2jkasdASda34wf', 'Myname', 'abc123')
devices = pure_client.get_devices()
print(pure_client.get_info(devices[0]))
print(pure_client.get_data(devices[0]))

try:
  # turn the unit off
  pure_client.set_state(devices[0], 'power', 'off')

  # turn the unit on and set to manual mode, with given speed setting
  pure_client.set_state(devices[0], 'power', 'on')
  pure_client.set_state(devices[0], 'preset_mode', 'manual')
  pure_client.set_state(devices[0], 'fan_mode', '6')

  # or with a single call (the state order is important)
  pure_client.set_state(devices[0], {
    'power': 'on,
    'preset_mode': 'manual',
    'fan_mode': '6'
  })
except PyPureError as err:
  print(f"Something went wrong! See here: {err}")
```

## Supported appliances/devices

- Electrolux Pure A9 (PA91-404GY) - _in testing_

## License and warranty

Written and release under the the Unlicense. There is no warranty.

This is **NOT** official software from Electrolux or in any way endorsed or supported by the company.

It was written for personal use and you may improve or adapt it however you want.
