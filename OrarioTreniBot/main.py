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

from . import config
from .objects import user

import json

import botogram

bot = botogram.create(config.BOT_TOKEN)


@bot.command("start")
def start(chat, message):
    u = user.User(message.sender)
    u.state("home")

    text = (
        "<b>Benvenuto in Orario Treni Bot!</b>"
        "\nCon questo bot potrai cercare 🚅 <b>treni</b>, 🚉 <b>stazioni</b> e 🚊 <b>itinerari</b>"
        "anche ☑️ <b>inline</b>!"
        "\nPremi uno dei <b>tasti qui sotto</b> per iniziare"
    )
    bot.api.call('sendMessage', {
        'chat_id': chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
        json.dumps(
            {'inline_keyboard': [
                [{"text": "🚅 Cerca treno", "callback_data": "train"},
                 {"text": "🚉 Cerca stazione", "callback_data": "station"}],
                [{"text": "ℹ️ Altre informazioni", "callback_data": "info"}]
            ]}
        )
    })
