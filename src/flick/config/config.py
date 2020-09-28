"""
Configuration Module
"""

from definitions import CONFIG_PATH
from flick import util


class Config(object):
    """
    Class to handle configuration file
    """
    def __init__(self):
        pass

    def get(self):
        """
        Retrieve config from file
        """
        return util.getJSONFile(CONFIG_PATH)

    def save(self, config_object):
        """
        Save config to file
        """
        return util.saveJSONFile(CONFIG_PATH, config_object)
