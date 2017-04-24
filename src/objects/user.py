# Copyright (c) 2016-2017 Marco Aceti <dev@marcoaceti.it>
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

r = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)


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
        r.hset(self.rhash, 'id', user.id)
        r.hset(self.rhash, 'username', user.username)
        r.hset(self.rhash, 'last_update', dt.now())
        if not self.state():
            r.hset(self.rhash, 'state', 'home')

        r.hset("users", user.id, True)

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
