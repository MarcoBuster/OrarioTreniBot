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

import json
from datetime import datetime
from urllib.error import HTTPError

import botogram
from dateutil.parser import parse

from ..viaggiatreno import viaggiatreno, format


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

        elif len(results) == 1:
            u.increaseStat('stats_trains_bynum')

            raw = api.call('andamentoTreno', results[0][1], message.text)  # andamentoTreno; departure station; number
            text = format.formatTrain(raw)
            bot.api.call('sendMessage', {
                'chat_id': chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
                json.dumps(
                    {"inline_keyboard": [
                        [{"text": "🔄 Aggiorna le informazioni", "callback_data": "train@{d}_{n}@update"
                            .format(d=results[0][1],
                                    n=message.text)}],
                        [{"text": "🚉 Fermate", "callback_data": "train@{d}_{n}@stops"
                          .format(d=results[0][1],
                                  n=message.text)},
                         {"text": "📊 Grafico ritardo", "callback_data": "train@{d}_{n}@graph"
                          .format(d=results[0][1],
                                  n=message.text)}],
                        [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                    ]}
                )
            })
            u.state("home")

        elif len(results) > 1:
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

    elif state == "train_byiti":
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

        elif len(results) == 1:
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

        elif len(results) > 1:
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

    elif state == "train_byiti_2":
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

        elif len(results) == 1:
            u.setRedis('iti_station2', results[0]['id'])
            u.state('train_byiti_3')
            text = (
                "<b>🛤 Cerca treno</b> per itinerario"
                "\nInserisci ora <b>la data</b> e/o <b>l'orario di partenza</b> desiderati "
                "(per esempio: <code>{a}</code>; <code>{b}</code>"
                .format(a=datetime.now().strftime("%H:%M %d/%m/%y"),
                        b=datetime.now().strftime("%H:%M"))
            )
            bot.api.call('sendMessage', {
                'chat_id': chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🕒 Orario attuale", "callback_data": "train_byiti@now"}],
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })

        elif len(results) > 1:
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

    elif state == "train_byiti_3":
        try:
            date = parse(message.text, dayfirst=True)
        except ValueError:
            text = (
                "<b>🛤 Cerca treno</b> per itinerario"
                "\nL'orario inserito <b>non è valido</b>."
                "\n<b>Esempi</b>: <code>{a}</code>; <code>{b}</code>"
                .format(a=datetime.now().strftime("%H:%M %d/%m/%y"),
                        b=datetime.now().strftime("%H:%M"))
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

        u.increaseStat('stats_trains_byiti')

        date = date.strftime('%Y-%m-%dT%H:%M:%S')

        raw = api.call('soluzioniViaggioNew', station_a, station_b, date)
        text = format.formatItinerary(raw)
        bot.api.call('sendMessage', {
            'chat_id': chat.id, 'text': text,
            'parse_mode': 'HTML', 'disable_web_page_preview': True, 'reply_markup':
                json.dumps(
                    {"inline_keyboard": [
                        [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                    ]}
                )
        })
        u.state("home")

    elif state == "station":
        results = api.call('cercaStazione', message.text)
        if len(results) == 0:
            text = (
                "<b>🚉 Cerca stazione</b>"
                "\n❌ <b>Stazione non trovata</b>, riprovare o annullare?"
            )
            bot.api.call("sendMessage", {
                "chat_id": chat.id, "text": text, "parse_mode": "HTML", "reply_markup":
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🔄 Riprova", "callback_data": "station"}],
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })

        elif len(results) == 1:
            u.increaseStat('stats_stations')
            u.addRecentStation(results[0]['nomeLungo'], results[0]['id'])

            text = format.formatStation(results[0]['nomeLungo'], results[0]['id'])
            bot.api.call('sendMessage', {
                'chat_id': chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🔘 Mostra le informazioni da Wikipedia", "callback_data": "station@" + results[0]["id"] + "@wiki"}],
                            [{"text": "🚦 Arrivi", "callback_data": "station@" + results[0]["id"] + "@arrivals"},
                             {"text": "🚦 Partenze", "callback_data": "station@" + results[0]["id"] + "@departures"}],
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })
            u.state("home")

        elif len(results) > 1:
            inline_keyboard = []
            for station in results:
                inline_keyboard.append([{"text": station['nomeLungo'], "callback_data": "station@" + station['id']}])
            inline_keyboard.append([{"text": "⬅️ Torna indietro", "callback_data": "home"}])

            text = (
                "<b>🛤 Cerca stazione</b>"
                "\nHo trovato {x} stazioni con quel nome, selezionane una:".format(x=len(results))
            )
            bot.api.call('sendMessage', {
                'chat_id': chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": inline_keyboard}
                    )
            })
            u.state("home")

    elif state == "admin_newpost":
        chat.send("Ecco il tuo messaggio:")
        try:
            chat.send(message.text, syntax="HTML")
        except botogram.api.APIError:
            chat.send("Formattazione HTML errata, riprova.")
            return

        chat.send("Ora invia il JSON della tastiera inline o \"NO\" per inviare senza tastiera")
        u.setRedis("admin_newpost_text", message.text)
        u.state("admin_newpost_2")

    elif state == "admin_newpost_2":
        chat.send("Ecco il tuo messaggio:")
        try:
            bot.api.call('sendMessage', {
                'chat_id': chat.id, 'message_id': message.message_id,
                'text': u.getRedis('admin_newpost_text').decode('utf-8'), 'parse_mode': 'HTML',
                'reply_markup':
                    json.dumps({"inline_keyboard": json.loads(message.text)}) if message.text != "NO" else ""
            })
        except (botogram.api.APIError, json.decoder.JSONDecodeError):
            chat.send("Inline keyboard errata, riprova.")
            return

        bot.api.call('sendMessage', {
            'chat_id': chat.id, 'text': 'Invio?', 'reply_markup': json.dumps(
                {"inline_keyboard": [
                    [{"text": "📤 Sì", "callback_data": "admin@newpost@send"}],
                    [{"text": "❌ No", "callback_data": "admin"}]
                ]}
            )
        })
        u.setRedis("admin_newpost_keyboard", message.text if message.text != "NO" else "[]")
        u.state("home")
