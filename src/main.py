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

import botogram
import botogram.objects.base

import config
from .objects.callback import Callback
from .objects.user import User
from .updates import callback, messages, deeplinking


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

botogram.Update.optional["callback_query"] = CallbackQuery

bot = botogram.create(config.BOT_TOKEN)


@bot.command("start")
def start(chat, message, args):
    if args:
        deeplinking.process_deeplinking(bot, message, args)
        return

    u = User(message.sender)
    u.state("home")
    u.increaseStat('stats_command_start')

    text = (
        "<b>Benvenuto in Orario Treni Bot!</b>"
        "\nCon questo bot potrai cercare 🚅 <b>treni</b>, 🚉 <b>stazioni</b> e 🚊 <b>itinerari</b> "
        "anche ☑️ <b>inline</b>!"
        "\nPremi uno dei <b>tasti qui sotto</b> per iniziare"
    )
    bot.api.call('sendMessage', {
        'chat_id': chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
        json.dumps(
            {'inline_keyboard': [
                [{"text": "🚅 Cerca treno", "callback_data": "train"},
                 {"text": "🚉 Cerca stazione", "callback_data": "station"}],
                [{"text": "📰 News", "callback_data": "news"}],
                [{"text": "ℹ️ Altre informazioni", "callback_data": "info"}]
            ]}
        )
    })


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
