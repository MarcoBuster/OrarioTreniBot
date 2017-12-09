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

    def _getRecentStations(self):
        """
        Get recent stations
        :return: Recent stations in raw format
        """
        return sorted(r.smembers(self.rhash + ':recent:stations'))

    def removeRecentStation(self, index=0):
        """
        Remove a recent station
        :param index: index of redis result
        :return: None
        """
        names = self._getRecentStations()
        r.srem(self.rhash + ':recent:stations', names[index])

    def addRecentStation(self, station_name, station_id):
        """
        Add a recent searched station
        :param station_name: Station name
        :param station_id: Station id
        :return: None
        """
        names = self._getRecentStations()
        index = 0
        is_duplicate = False
        for name in names:
            if station_id in name.decode('utf-8'):
                self.removeRecentStation(index)
                del(names[index])
                is_duplicate = True
                break
            index += 1

        if len(names) >= 5 and not is_duplicate:
            self.removeRecentStation(index=0)

        names.reverse()
        r.sadd(self.rhash + ':recent:stations',
               format((int(names[0].decode('utf-8').split("@")[0], 2) + 1) if names else 0, '016b') +
               '@' + station_name + '@' + station_id)

    def formatRecentStationsKeyboard(self):
        """
        Format recents stations keyboard
        :return: dict
        """
        names = sorted(self._getRecentStations(), reverse=True)

        keyboard = []
        for name in names:
            keyboard.append([{"text": "🕒 {name}"
                            .format(name=name.decode('utf-8').split("@")[1]),
                             "callback_data": "station@{station_id}"
                            .format(station_id=name.decode('utf-8').split("@")[2])}])
        return keyboard

    def isActive(self):
        return bool(r.hget(self.rhash, "active")) or False
