import json


def does_config_exist():
    """Checks if a config file exists"""

    try:
        with open("./config.json", "r") as f:
            return True
    except FileNotFoundError:
        return False


def create_default_config():
    """Creates an empty config file with default values"""

    # Don't overwrite existing config
    if does_config_exist():
        return

    default = {
        "net": {
            "ip": "192.168.1.151",
            "port": 21210
        },
        "radar": {
            "integrationIndex": 11,
            "scanStart": 26685,
            "scanEnd": 79419,
            "scanInterval": 0,
            "scanCount": 65535,
            "distanceCorrection": -2.0
        },
        "ui": {
            "units": "m"
        }
    }

    with open("./config.json", "w") as f:
        json.dump(default, f, indent=4)


def get_config_file():
    """Returns the config as a dict"""

    if not does_config_exist():
        create_default_config()

    with open("./config.json", "r") as f:
        try:
            results = json.load(f)
        except json.decoder.JSONDecodeError:
            # fatal error
            print("Error: config file is not valid JSON")
            exit(1)

        # TODO: validate config using validator lib

        return results


def write_config_file(config):
    """Writes the config to the config file"""

    with open("./config.json", "w") as f:
        json.dump(config, f, indent=4)


def get_config():
    """Returns the config as a dict"""

    return get_config_file()
