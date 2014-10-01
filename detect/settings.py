__author__ = 'robdefeo'

import json
import os


def get_env_setting(env_variable_name, default):
    if env_variable_name in os.environ:
        return os.environ[env_variable_name]
    else:
        return default

MONGODB_HOST = get_env_setting("DETECT_MONGODB_HOST", "localhost")
MONGODB_PORT = int(get_env_setting("DETECT_MONGODB_PORT", 27017))
MONGODB_DB = get_env_setting("DETECT_MONGODB_DB", "detect")
MONGODB_USER = get_env_setting("DETECT_MONGODB_USER", "detect")
MONGODB_PASSWORD = get_env_setting("DETECT_MONGODB_PASSWORD", "jemboo")

PORT = int(get_env_setting("DETECT_PORT", 18999))
