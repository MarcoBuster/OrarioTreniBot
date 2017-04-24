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

from datetime import datetime
from dateutil.parser import parse


def process_messages(bot, message, u):
    state = u.state().decode('utf-8')  # Redis returns strings in bytes, state must be converted in strings
    chat = message.chat
    api = viaggiatreno.API()

    if not message.text:
        return

    if state == "train_bynum":
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
            bot.api.call('sendMessage', {
                'chat_id': chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
                json.dumps(
                    {"inline_keyboard": [
                        [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                    ]}
                )
            })

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

    if state == "train_byiti":
        results = api.call('cercaStazione', message.text)
        if len(results) == 0:
            text = (
                "<b>🚅 Cerca treno</b> per itinerario"
                "\n❌ <b>Stazione di partenza non trovata</b>, riprovare o annullare?"
            )
            bot.api.call("sendMessage", {
                "chat_id": chat.id, "text": text, "parse_mode": "HTML", "reply_markup":
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🔄 Riprova", "callback_data": "train_byiti"}],
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })

        if len(results) == 1:
            u.setRedis('iti_station1', results[0]['id'])
            u.state('train_byiti_2')
            text = (
                "<b>🛤 Cerca treno</b> per itinerario"
                "\nInserisci ora la <b>stazione di arrivo</b>"
            )
            bot.api.call('sendMessage', {
                'chat_id': chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })

        if len(results) > 1:
            inline_keyboard = []
            for station in results:
                inline_keyboard.append([{"text": station['nomeLungo'], "callback_data": "station@" + station['id']}])
            inline_keyboard.append([{"text": "⬅️ Torna indietro", "callback_data": "home"}])

            text = (
                "<b>🛤 Cerca treno</b> per itinerario"
                "\nHo trovato {x} stazioni con quel nome, selezionane una:".format(x=len(results))
            )
            bot.api.call('sendMessage', {
                'chat_id': chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": inline_keyboard}
                    )
            })

    if state == "train_byiti_2":
        results = api.call('cercaStazione', message.text)
        if len(results) == 0:
            text = (
                "<b>🚅 Cerca treno</b> per itinerario"
                "\n❌ <b>Stazione di arrivo non trovata</b>, riprovare o annullare?"
            )
            bot.api.call("sendMessage", {
                "chat_id": chat.id, "text": text, "parse_mode": "HTML", "reply_markup":
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🔄 Riprova", "callback_data": "train_byiti"}],
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })

        if len(results) == 1:
            u.setRedis('iti_station2', results[0]['id'])
            u.state('train_byiti_3')
            text = (
                "<b>🛤 Cerca treno</b> per itinerario"
                "\nInserisci ora <b>la data</b> e/o <b>l'orario di partenza</b> desiderati "
                "(per esempio: <code>{a}</code>; <code>{b}</code>; <code>{c}</code>)"
                .format(a=datetime.now().strftime('%d/%m %H:%M'),
                        b=datetime.now().strftime("%H:%M %d/%m/%y"),
                        c=datetime.now().strftime("%H:%M"))
            )
            bot.api.call('sendMessage', {
                'chat_id': chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })

        if len(results) > 1:
            inline_keyboard = []
            for station in results:
                inline_keyboard.append([{"text": station['nomeLungo'], "callback_data": "station@" + station['id']}])
            inline_keyboard.append([{"text": "⬅️ Torna indietro", "callback_data": "home"}])

            text = (
                "<b>🛤 Cerca treno</b> per itinerario"
                "\nHo trovato {x} stazioni con quel nome, selezionane una:".format(x=len(results))
            )
            bot.api.call('sendMessage', {
                'chat_id': chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": inline_keyboard}
                    )
            })

    if state == "train_byiti_3":
        try:
            date = parse(message.text)
        except ValueError:
            text = (
                "<b>🛤 Cerca treno</b> per itinerario"
                "\nL'orario inserito <b>non è valido</b>."
                "\n<b>Esempi</b>: <code>{a}</code>; <code>{b}</code>; <code>{c}</code>"
                .format(a=datetime.now().strftime('%d/%m %H:%M'),
                        b=datetime.now().strftime("%H:%M %d/%m/%y"),
                        c=datetime.now().strftime("%H:%M"))
            )
            bot.api.call('sendMessage', {
                'chat_id': chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })
            return

        def minifyStation(__str):
            __str = __str[1:]
            x = 0
            for i in __str:
                if i != "0":
                    __str = __str[x:]
                    break
                x += 1
            return __str

        station_a = minifyStation(u.getRedis('iti_station1').decode('utf-8'))
        station_b = minifyStation(u.getRedis('iti_station2').decode('utf-8'))
        u.delRedis('iti_station1')
        u.delRedis('iti_station2')

        date = date.strftime('%Y-%m-%dT%H:%M:%S')

        raw = api.call('soluzioniViaggioNew', station_a, station_b, date)
        print(raw)
