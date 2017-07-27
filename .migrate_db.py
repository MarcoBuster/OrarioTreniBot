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

import sqlite3

import redis

import config
from src.objects.user import User

conn = sqlite3.connect('OrarioTreni.db')  # Old Orario Treni file
c = conn.cursor()

r = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password=config.REDIS_PASSWORD)


class FakeUser:
    def __init__(self, user_id):
        self.id = user_id
        self.username = None


def reset_local_redis_database():
    keys = r.keys("user:*")
    for key in keys:
        r.delete(key)

    print("Local redis database resetted")


def migrate():
    rows = c.execute('SELECT * FROM stato')
    for row in rows:
        print(User(FakeUser(user_id=row[0])).id, "migrated")

if __name__ == "__main__":
    answer = input("Do you want to reset the local redis database? [Y/n] ")
    if answer.lower() in ["y", "yes"]:
        reset_local_redis_database()

    answer = input("Do you want to migrate the old sqlite3 database to the new redis database? [Y/n]")
    if answer.lower() in ["y", "yes"]:
        migrate()
