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

import json
import time

import botogram
import progressbar
import redis

import config

r = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password=config.REDIS_PASSWORD)
bot = botogram.create(config.BOT_TOKEN)


def post(text, parse_mode="HTML", reply_markup=None, disable_web_page_preview=True, message=None):
    users = []
    for user in r.keys("user:*"):
        users.append(int(user[5:]))

    print("Sending global message...")
    print("> Text", text, sep=": ")
    print("> Reply Markup", reply_markup, sep=": ")
    print("> Parse mode", parse_mode, sep=": ")
    print("> Disable web page preview", disable_web_page_preview, sep=": ")

    bar = progressbar.ProgressBar()
    for user in bar(users):
        if message:
            message.edit(
                "<b>Sending global message...</b>"
                "\n<b>{value}/{max_value}</b> ({percentage}%)"
                .format(value=bar.value, max_value=bar.max_value, percentage=round(bar.percentage, 1))
            )
            time.sleep(0.1)

        user_hash = "user:" + str(user)
        try:
            bot.chat(user)
        except botogram.APIError:
            r.hset(user_hash, "active", False)
            continue

        try:
            if r.hget(user_hash, "active").decode("utf-8") == "False":
                continue

            bot.api.call("sendMessage", {
                "chat_id": user, "text": text, "parse_mode": parse_mode,
                "disable_web_page_preview": disable_web_page_preview,
                "reply_markup": json.dumps(reply_markup) if reply_markup else ""
            })

        except botogram.APIError:
            r.hset(user_hash, "active", False)

        finally:
            time.sleep(0.5)

    if message:
        message.edit(
            "<b>Sending global message...</b>"
            "\n<b>{value}/{max_value}</b> ({percentage}%)"
            .format(value=bar.value, max_value=bar.max_value, percentage=round(bar.percentage, 1))
        )
        time.sleep(0.1)
