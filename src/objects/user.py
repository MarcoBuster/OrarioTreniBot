# Copyright (c) 2016-2017 The OrarioTreniBot Authors (see AUTHORS)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime as dt

import redis

import config
from ..viaggiatreno.viaggiatreno import Utils

r = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password=config.REDIS_PASSWORD)


class User:
    """
    User base object
    """

    def __init__(self, user):
        """
        Create an user object
        :param user: Telegram's user object
        """
        self.id = user.id
        self.rhash = 'user:' + str(user.id)

        # Redis database
        if r.hget(self.rhash, 'id') != user.id:
            r.hset(self.rhash, 'id', user.id)
        if r.hget(self.rhash, 'username') != user.username:
            r.hset(self.rhash, 'username', user.username)
        r.hset(self.rhash, 'last_update', dt.now())
        if not self.state():
            r.hset(self.rhash, 'state', 'home')
        r.hset(self.rhash, "active", True)

    def state(self, new_state=None):
        """
        Get current user state or set a new user state
        :param new_state: new state for the user
        :return: state
        """
        if not new_state:
            return r.hget(self.rhash, 'state')

        r.hset(self.rhash, 'state', new_state)
        return True

    def setRedis(self, key, value):
        """
        Set a redis value
        :param key: redis key
        :param value: redis value
        :return: value
        """
        return r.hset(self.rhash, key, value)

    def getRedis(self, key):
        """
        Get a redis value
        :param key: redis key
        :return: value
        """
        return r.hget(self.rhash, key)

    def delRedis(self, key):
        """
        Delete a redis value
        :param key: redis key
        :return: None
        """
        return r.hdel(self.rhash, key)

    def increaseStat(self, stat):
        """
        Increase a stat value
        :param stat: which stat increase
        :return: redis response
        """
        response = r.hincrby(self.rhash, stat)
        return response

    def _getRecentElements(self, element_type, reverse=False):
        """
        Get recent elements
        :param element_type: element type
        :return: Recent elements in raw format
        """
        return sorted(r.smembers(self.rhash + ':recent:' + element_type), reverse=reverse)

    def removeRecentElement(self, element_type, index=0, reverse=False):
        """
        Remove a recent element
        :param element_type: element type
        :param index: index of redis result
        :param reverse: reverse elements order
        :return: None
        """
        names = self._getRecentElements(element_type, reverse=reverse)
        r.srem(self.rhash + ':recent:' + element_type, names[index])

    def addRecentElement(self, element_type, element_hash):
        """
        Add a recent searched element
        :param element_type: element type
        :param element_hash: element hash
        :return: None
        """
        names = self._getRecentElements(element_type)
        index = 0
        is_duplicate = False
        duplicate_check = None
        if element_type == "stations":
            duplicate_check = element_hash.split("@")[0]
        if element_type == "trains":
            duplicate_check = element_hash.split("@")[0]
        if element_type == "itineraries":
            duplicate_check = element_hash
        for name in names:
            if duplicate_check in name.decode('utf-8'):
                self.removeRecentElement(element_type, index)
                del (names[index])
                is_duplicate = True
                break
            index += 1

        if len(names) >= 5 and not is_duplicate:
            self.removeRecentElement(element_type, 0)

        names.reverse()
        r.sadd(self.rhash + ':recent:' + element_type,
               format((int(names[0].decode('utf-8').split("@")[0], 2) + 1) if names else 0, '016b') + "@" +
               element_hash)

    @staticmethod
    def formatRecentStationHash(station_name, station_id):
        return station_name + "@" + station_id

    @staticmethod
    def formatRecentItineraryHash(station_a, station_b):
        return station_a + "@" + station_b

    def formatRecentStationsKeyboard(self):
        """
        Format recents stations keyboard
        :return: list of lists of dict
        """
        names = sorted(self._getRecentElements('stations'), reverse=True)

        keyboard = []
        for name in names:
            station_name = name.decode('utf-8').split("@")[1]
            station_id = name.decode('utf-8').split("@")[2]
            keyboard.append([{"text": "🕒 {name}"
                            .format(name=station_name.title()),
                              "callback_data": "station@{station_id}"
                            .format(station_id=station_id)}])
        return keyboard

    def formatRecentTrainsKeyboard(self):
        """
        Format recent trains keyboard
        :return: list of lists of dict
        """
        names = sorted(self._getRecentElements('trains'), reverse=True)

        keyboard = []
        for name in names:
            train_name = name.decode('utf-8').split("@")[2]
            train_id = name.decode('utf-8').split("@")[1]
            keyboard.append([{"text": "🕒 {name}"
                            .format(name=train_name),
                              "callback_data": "train@{train_id}"
                            .format(train_id=train_id)}])
        return keyboard

    def formatRecentItinerariesKeyboard(self):
        """
        Format recent itineraries keyboard
        :return: list of lists of dicts
        """
        names = sorted(self._getRecentElements('itineraries'), reverse=True)

        utils = Utils()
        keyboard = []
        index = 0
        for name in names:
            station_a = name.decode('utf-8').split("@")[1]
            station_b = name.decode('utf-8').split("@")[2]
            if utils.station_from_ID(station_a) == 'UNKNOWN' or utils.station_from_ID(station_b) == 'UNKNOWN':
                self.removeRecentElement('itinerary', index=index, reverse=True)
                index += 1
                continue

            keyboard.append([{"text": "🕒 {station_a} ➡️ {station_b}"
                            .format(station_a=utils.station_from_ID(station_a).title(),
                                    station_b=utils.station_from_ID(station_b).title()),
                              "callback_data": "itinerary@{station_a}_{station_b}"
                            .format(station_a=station_a,
                                    station_b=station_b)}])
            index += 1
        return keyboard

    def isActive(self):
        return bool(r.hget(self.rhash, "active")) or False
