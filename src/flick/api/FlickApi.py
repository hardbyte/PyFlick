"""
API Interface Module
"""
# !/usr/bin/env python
# encoding: utf-8

import json
import time
from calendar import timegm
import requests
from flick.authentication.FlickAuth import FlickAuth
from flick import util
from definitions import FLICK_PRICE_ENDPOINT, FLICK_DATA_STORE


class FlickApi(object):
    """ Flick Electric API Interface """

    def __init__(self, username, password, client_id, client_secret):
        AuthInstance = FlickAuth(username, password, client_id, client_secret)
        self.session = AuthInstance.getToken()
        self.getRawData()

    def __update(self, writeToFile=False):
        """ Pull Updates From Flick Servers"""

        print("getting the latest price")
        headers = {
            "Authorization": "Bearer %s" % self.session["id_token"]
        }
        req = requests.get(FLICK_PRICE_ENDPOINT, headers=headers)
        if req.status_code != 200:
            # If we don't get a success response, we raise an exception.
            raise Exception({
                "status": req.status_code,
                "message": req.text
            })
        # A 200 OK response will contain the JSON payload.
        # TODO: Create Exception Handler to catch failed json.load.
        response = json.loads(req.text)
        if writeToFile:
            util.saveJSONFile(FLICK_DATA_STORE, response)
        self.data = response
        return response

    def __priceExpired(self):
        """ Checks if spot price has expired """
        nowEpoch = int(time.time())
        nextEpoch = self.getNextUpdateTime(True)
        print("%d" % nextEpoch)
        print("%d" % nowEpoch)
        return nextEpoch < nowEpoch

    def __getUpdateTime(self, update, isEpoch):
        """ Gets the prev/next update time """
        if isEpoch:
            pattern = "%Y-%m-%dT%H:%M:%SZ"
            utc_time = time.strptime(update, pattern)
            epoch = timegm(utc_time)
            return epoch
        return update

    def getRawData(self, writeToFile=False):
        """ Public method to get pricing data """
        pricing = util.getJSONFile(FLICK_DATA_STORE)
        if not pricing:
            pricing = self.__update(writeToFile)
        self.data = pricing
        expired = self.__priceExpired()
        if expired is True:
            self.__update(True)
        return self.data

    def getPricePerKwh(self):
        """ Get's the pure price per kwh as a number"""
        return self.data["needle"]["price"]

    def getPriceBreakdown(self):
        """ Get the price, broken down into it's constituent parts"""
        charges = 0.0
        spotPrice = 0.0
        for item in self.data["needle"]["components"]:
            if item["charge_method"] == "kwh":
                charges += float(item["value"])
            elif item["charge_method"] == "spot_price":
                spotPrice = float(item["value"])

        response = {}
        response["charges"] = charges
        response["spotPrice"] = spotPrice
        return response

    def getLastUpdateTime(self, isEpoch=False):
        update = self.data["needle"]["start_at"]
        return self.__getUpdateTime(update, isEpoch)

    def getNextUpdateTime(self, isEpoch=False):
        update = self.data["needle"]["end_at"]
        return self.__getUpdateTime(update, isEpoch)
