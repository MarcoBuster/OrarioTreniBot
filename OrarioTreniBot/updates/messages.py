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

from ..viaggiatreno import viaggiatreno, format

import json
from urllib.error import HTTPError


def process_messages(bot, message, u):
    state = u.state().decode('utf-8')  # Redis returns strings in bytes, state must be converted in strings
    chat = message.chat

    if not message.text:
        return

    if state == "train_bynum":
        api = viaggiatreno.API()
        try:
            results = api.call('cercaNumeroTrenoTrenoAutocomplete', message.text)
        except HTTPError:
            results = []

        if len(results) == 0:
            u.state("home")
            text = (
                "<b>🚅 Cerca treno</b> per numero"
                "\n❌ <b>Nessun treno trovato</b>, riprovare o annullare?"
            )
            bot.api.call("sendMessage", {
                "chat_id": chat.id, "text": text, "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {"inline_keyboard": [
                        [{"text": "🔄 Riprova", "callback_data": "train_bynum"}],
                        [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                    ]}
                )
            })

        if len(results) == 1:
            raw = api.call('andamentoTreno', results[0][1], message.text)  # andamentoTreno; departure station; number
            text = format.formatTrain(raw)
            message.reply(text)

        if len(results) > 1:
            inline_keyboard = []
            for result in results:
                text = "🚉 {n} - Da {d}".format(n=message.text, d=result[0])
                inline_keyboard.append([{"text": text, "callback_data": "train@{d}_{n}".format(d=result[1],
                                                                                               n=message.text)}])
            text = (
                "<b>🚅 Cerca treno</b> per numero"
                "\n❗️ Il treno ha <b>{x} numerazioni</b>, seleziona quella desiderata:".format(x=len(results))
            )
            bot.api.call("sendMessage", {
                "chat_id": chat.id, "text": text, "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {"inline_keyboard": inline_keyboard}
                )
            })
