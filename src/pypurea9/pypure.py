#! /usr/bin/env python3
# <hymnis@plazed.net> 2020

"""
Python API for Electrolux Pure A9 air purifier.

inspired by:
- https://github.com/rickardp/homey-electrolux-wellbeing/
- https://github.com/rene-d/netatmo/
"""

import sys
import time
import argparse
import json
import pprint
import requests
import pkg_resources
import logging


VERBOSITY = 0

_BASE_URL = "https://api.delta.electrolux.com/api/"
_CLIENT_VERSION = "1.8.16400"
_OS_PLATFORM = "iOS"

_LOGGER = logging.getLogger(__name__)


class Colors:
    """
    ANSI SGR codes
    https://en.wikipedia.org/wiki/ANSI_escape_code#graphics
    """

    Reset = "\033[0m"  # Reset / Normal
    Bold = "\033[1m"  # Bold or increased intensity
    Faint = "\033[2m"  # Faint (decreased intensity)
    Underline = "\033[4m"  # Underline: Single
    Blink = "\033[5m"  # Blink: Slow
    Inverse = "\033[7m"  # Image: Negative
    Black = "\033[0;30m"
    Red = "\033[0;31m"
    Green = "\033[0;32m"
    Yellow = "\033[0;33m"
    Blue = "\033[0;34m"
    Magenta = "\033[0;35m"
    Cyan = "\033[0;36m"
    LightGray = "\033[0;37m"
    DarkGray = "\033[1;30m"
    LightRed = "\033[1;31m"
    LightGreen = "\033[1;32m"
    LightYellow = "\033[1;33m"
    LightBlue = "\033[1;34m"
    LightMagenta = "\033[1;35m"
    LightCyan = "\033[1;36m"
    White = "\033[1;37m"


if not sys.stdout.isatty():
    for _ in dir(Colors):
        if not _.startswith("__"):
            setattr(Colors, _, "")


def trace(level, *args, pretty=False):
    """Print a colorized message when stdout is a terminal."""
    if level <= VERBOSITY:
        pretty = pprint.pformat if pretty else str
        color_codes = {
            -2: Colors.LightRed,
            -1: Colors.LightYellow,
            0: "",
            1: Colors.Green,
            2: Colors.Yellow,
            3: Colors.Red,
        }
        color = color_codes.get(level, "")
        sys.stdout.write(color)
        for i, arg in enumerate(args):
            if i != 0:
                sys.stdout.write(" ")
            sys.stdout.write(pretty(arg))
        sys.stdout.write(Colors.Reset)
        sys.stdout.write("\n")


def make_request(method, url, data, headers=None):
    """Wrapper for requests, with trace printing."""
    trace(1, ">>>> " + url)
    trace(2, data, pretty=True)
    start_time = time.time()
    response = requests.request(method, url, data=data, headers=headers)
    trace(
        1,
        "<<<< %d bytes in %.3f s"
        % (len(response.content), time.time() - start_time),
    )
    content = json.loads(response.content)
    trace(2, content, pretty=True)

    return content


class ElectroluxDeltaApi:
    """Class to interface with the Electrolux Delta API."""

    _auth_state = {
        "clientSecret": None,
        "clientToken": None,
        "mmsToken": None,
        "userToken": None,
        "username": None,
        "password": None,
    }

    def __init__(self, client_secret, username, password):
        self._auth_state["clientSecret"] = client_secret
        self._auth_state["username"] = username
        self._auth_state["password"] = password

    def check_for_update(self):
        payload = {"Version": _CLIENT_VERSION, "Platform": _OS_PLATFORM}

        try:
            # response = requests.post(
            #     f"{_BASE_URL}updates/Wellbeing",
            #     data=json.dumps(payload),
            #     headers={"Content-Type": "application/json"}
            # )
            # response_json = response.json()
            response_json = make_request(
                "POST",
                f"{_BASE_URL}updates/Wellbeing",
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )

            if not response_json["forceUpdate"]:
                _LOGGER.error("Invalid response from update server")

            if response_json["forceUpdate"]:
                _LOGGER.info("Back-end API needs to be updated")

            return response_json
        except ConnectionError as err:
            _LOGGER.error("Connection error! %s" % err)
            return False

    def refresh_client_token(self):
        self.check_for_update()
        payload = {"ClientSecret": self._auth_state["clientSecret"]}

        try:
            response = requests.post(
                f"{_BASE_URL}Clients/Wellbeing",
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )
            response_json = response.json()
            trace(2, response_json, pretty=True)  # DEBUG

            if "accessToken" not in response_json:
                raise PureA9Error(
                    "Error refreshing client token! "
                    + response_json["codeDescription"]
                )

            self._auth_state["clientToken"] = response_json["accessToken"]
        except ConnectionError as err:
            _LOGGER.error("Connection error! %s" % err)

    def refresh_user_token(self):
        self.refresh_client_token()
        payload = {
            "userName": self._auth_state["username"],
            "password": self._auth_state["password"],
        }

        try:
            response = requests.post(
                f"{_BASE_URL}Users/Login",
                data=json.dumps(payload),
                headers={
                    "Content-Type": "application/json",
                    "Authorization":
                        f"Bearer {self._auth_state['clientToken']}",
                },
            )
            response_json = response.json()
            if not response_json["accessToken"]:
                raise PureA9Error("Login error: %s" % response.reason)

            self._auth_state["userToken"] = response_json["accessToken"]
        except ConnectionError as err:
            _LOGGER.error("Connection error! %s" % err)

    def fetch_api(self, suffix, options=None):
        if not options:
            options = {"method": None, "headers": None, "data": None}
        if not options["method"]:
            options["method"] = "POST"
        if not options["headers"]:
            options["headers"] = {}

        for i in range(3):
            if self._auth_state["userToken"]:
                options["headers"][
                    "Authorization"
                ] = f"Bearer {self._auth_state['userToken']}"

            response = requests.request(
                method=options["method"],
                url=f"{_BASE_URL}{suffix}",
                headers=options["headers"],
                data=options["data"],
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code >= 400 and response.status_code < 500:
                _LOGGER.error("Error: %s" % response.status_code)
                self.refresh_user_token()
            else:
                raise PureA9Error(
                    "Internal server error: %s" % response.status_code
                )
        raise PureA9Error("Internal error. Too many authentication attempts")


class PyPure(ElectroluxDeltaApi):
    """Class to interface with a Pure appliance."""

    def __init__(self, client_secret=None, username=None, password=None):
        """Initialize a device."""
        super().__init__(client_secret, username, password)
        self._initialized = True

    def set_token(self, token):
        self._auth_state["userToken"] = token

    def set_credentials(self, username, password):
        self._auth_state["username"] = username
        self._auth_state["password"] = password

    def verify_credentials(self):
        self.refresh_user_token()

    def get_appliances(self):
        return self.fetch_api("Domains/Appliances")

    def get_appliance(self, pnc_id):
        return self.fetch_api(f"Appliances/{pnc_id}")

    def send_device_command(self, id, command):
        return self.fetch_api(
            f"Appliances/{id}/Commands",
            {
                "method": "PUT",
                "data": json.dumps(command),
                "headers": {"Content-Type": "application/json"},
            },
        )


class PyPureError(Exception):
    """Class for error handling."""

    def __init__(self, message):
        self.message = message


def get_devices(args):
    """Get all configured devices/appliances."""
    api = PyPureargs.client_secret, args.username, args.password)
    devices = api.get_appliances()

    if sys.stdout.isatty():
        pprint(devices)
    else:
        return devices

    exit(0 if devices else 1)


def get_info(args):
    pass


def get_data(args):
    pass


def set_state(args):
    pass


def self_test(args):
    """Check if connection to API works."""
    api = PyPure)
    ok = api.check_for_update()

    if sys.stdout.isatty():
        if ok:
            print("pypure : API OK")
        else:
            print("pypure : API ERROR")

    exit(0 if ok else 1)


def main():
    """Main CLI function."""
    global VERBOSITY

    parser = argparse.ArgumentParser(
        description="pypure Python3 library",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--version", help="show version", action="store_true")
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase VERBOSITY level",
        action="count",
        default=VERBOSITY,
    )
    parser.add_argument(
        "-c", "--client_secret", help="your client secret", required=True
    )
    parser.add_argument(
        "-u", "--username", help="your username", required=True
    )
    parser.add_argument(
        "-p", "--password", help="your password", required=True
    )

    subparsers = parser.add_subparsers(help="sub-commands", dest="action")

    # action "get_devices"
    sp = subparsers.add_parser(
        "get_devices", help="list all devices"
    ).set_defaults(func=get_devices)

    # action "get_info"
    sp = subparsers.add_parser("get_info", help="list device information")
    sp.add_argument(
        "-d", "--device", help="the device to target", required=True
    )
    sp.set_defaults(func=get_info)

    # action "get_data"
    sp = subparsers.add_parser("get_data", help="list device sensor data")
    sp.add_argument(
        "-d", "--device", help="the device to target", required=True
    )
    sp.set_defaults(func=get_data)

    # action "set_state"
    sp = subparsers.add_parser("set_state", help="set desired device state")
    sp.add_argument(
        "-d", "--device", help="the device to target", required=True
    )
    sp.add_argument("-s", "--state", help="the state to change", required=True)
    sp.add_argument(
        "-a", "--argument", help="the new state value", required=True
    )
    sp.set_defaults(func=set_state)

    # action "test"
    subparsers.add_parser("test", help="test the API connection").set_defaults(
        func=self_test
    )

    args = parser.parse_args()

    if args.version:
        print(pkg_resources.require("pypure")[0])
        exit(0)

    # set the verbose level as a global variable
    VERBOSITY = args.verbose

    trace(1, str(args))

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
