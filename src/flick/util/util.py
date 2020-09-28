""" Utility Class"""
#!/usr/bin/env python
#encoding: utf-8

import json
import os


def saveJSONFile(filepath, data):
    """ Saves JSON Data to File"""
    with open(filepath, 'w') as outfile:
        try:
            json.dump(data, outfile, indent=2)
        except ValueError as e:
            return False
        return True


def getJSONFile(filepath):
    """ Get Data from cached file """
    if not os.path.exists(filepath):
        return False
    with open(filepath) as stream:
        try:
            data = json.load(stream)
        except ValueError as e:
            return False
        return data
