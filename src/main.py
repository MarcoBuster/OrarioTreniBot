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

import botogram
import botogram.objects.base

import config
from .objects.callback import Callback
from .objects.inline import Inline
from .objects.user import User
from .updates import commands, callback, messages, deeplinking, inline


class CallbackQuery(botogram.objects.base.BaseObject):
    def __init__(self, update):
        super().__init__(update)

    required = {
        "id": str,
        "from": botogram.User,
        "data": str,
    }
    optional = {
        "inline_message_id": str,
        "message": botogram.Message,
    }
    replace_keys = {
        "from": "sender"
    }


class InlineQuery(botogram.objects.base.BaseObject):
    def __init__(self, update):
        super().__init__(update)

    required = {
        "id": str,
        "from": botogram.User,
        "query": str,
        "offset": str,
    }
    optional = {
        "location": botogram.Location,
    }
    replace_keys = {
        "from": "sender"
    }

botogram.Update.optional["callback_query"] = CallbackQuery
botogram.Update.optional["inline_query"] = InlineQuery

bot = botogram.create(config.BOT_TOKEN)


@bot.command("start")
def start(message, args):
    if args:
        deeplinking.process_deeplinking(bot, message, args)
        return

    commands.process_start_command(bot, message)


@bot.command("admin")
def admin(message):
    commands.process_admin_command(bot, message)


@bot.process_message
def process_messages(message):
    u = User(message.sender)
    messages.process_messages(bot, message, u)


def process_callback(__bot, __chains, update):
    del (__bot, __chains)  # Useless arguments from botogram
    cb = Callback(update)
    u = User(cb.sender)
    u.increaseStat('stats_callback_count')

    callback.process_callback(bot, update, u)

bot.register_update_processor("callback_query", process_callback)


def process_inline_query(__bot, __chains, update):
    del (__bot, __chains)  # Useless arguments from botogram
    iq = Inline(update)
    u = User(iq.sender)
    u.increaseStat('stats_inline_count')

    inline.process_inline_query(bot, update, u)

bot.register_update_processor("inline_query", process_inline_query)
