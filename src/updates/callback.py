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
import os
from datetime import datetime, timedelta

import redis
from botogram.api import APIError

import config
from . import global_messages
from ..viaggiatreno import viaggiatreno, format
from ..viaggiatreno.dateutils import is_DST

r = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password=config.REDIS_PASSWORD)


def process_callback(bot, cb, u):
    if cb.isInline:
        return

    api = viaggiatreno.API()
    utils = viaggiatreno.Utils()

    if cb.query == "home":
        u.state("home")
        text = (
            "<b>Benvenuto in Orario Treni Bot!</b>"
            "\nCon questo bot potrai cercare 🚅 <b>treni</b>, 🚉 <b>stazioni</b> e 🚊 <b>itinerari</b> "
            "anche ☑️ <b>inline</b>!"
            "\nPremi uno dei <b>tasti qui sotto</b> per iniziare"
        )
        bot.api.call("editMessageText", {
            "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
            "parse_mode": "HTML", "reply_markup":
            json.dumps(
                {'inline_keyboard': [
                    [{"text": "🚅 Cerca treno", "callback_data": "train"},
                     {"text": "🚉 Cerca stazione", "callback_data": "station"}],
                    [{"text": "📰 News", "callback_data": "news"}],
                    [{"text": "ℹ️ Altre informazioni", "callback_data": "info"}]
                ]}
            )
        })
        cb.notify("🏡 Menù principale")

    elif cb.query == "info":
        text = (
            "<b>Informazioni sul bot</b>"
            "\n<i>Link utili</i>"
            "\n➖ <b>👤 Contatta lo sviluppatore</b> su Telegram per avere <b>assistenza gratuita</b> "
            "o per proporre <b>una nuova funzione</b>"
            "\n➖ Entra nel <b>📢 Canale ufficiale</b> per ricevere <b>news</b> e <b>aggiornamenti</b> "
            "in anteprima <b>sul bot</b>"
            "\n➖ <b>💰 Dona</b> <i>quello che vuoi</i> per tenere <b>il bot online</b> e per supportare "
            "<b>il lavoro dello sviluppatore</b>"
            "\n➖ Dai un'occhiata o contribuisci al <i>codice sorgente</i> su <b>🔘 GitHub</b>"
            "\n➖ Visualizza le <b>📈 Statistiche</b> di utilizzo del bot!"
        )
        bot.api.call("editMessageText", {
            "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
            "parse_mode": "HTML", "reply_markup":
            json.dumps(
                {'inline_keyboard': [
                    [{"text": "👤 Contatta lo sviluppatore", "url": "https://t.me/MarcoBuster"},
                     {"text": "📢 Canale ufficiale", "url": "https://t.me/OrarioTreni"}],
                    [{"text": "💰 Dona", "url": "https://paypal.me/marcoaceti"},
                     {"text": "🔘 GitHub", "url": "https://github.com/MarcoBuster/OrarioTreniBot/tree/rewrite"},
                     {"text": "📈 Statistiche", "callback_data": "stats"}],
                    [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                ]}
            )
        })
        cb.notify("ℹ️ Altre informazioni")

    elif cb.query == "stats":
        users = []
        for user in r.keys("user:*"):
            users.append(int(user[5:]))

        active_users = 0
        total_users = 0
        start_command = 0
        callbacks_count = 0
        trains_bynum = 0
        trains_byiti = 0
        stations = 0
        for user in users:
            user_hash = "user:" + str(user)
            active_users += 1 if bool(r.hget(user_hash, "active")) else 0
            total_users += 1

            start_command += int(r.hget(user_hash, 'stats_command_start')) \
                if r.hget(user_hash, 'stats_command_start') else 0
            callbacks_count += int(r.hget(user_hash, 'stats_callback_count')) \
                if r.hget(user_hash, 'stats_callback_count') else 0
            trains_bynum += int(r.hget(user_hash, 'stats_trains_bynum')) \
                if r.hget(user_hash, 'stats_trains_bynum') else 0
            trains_byiti += int(r.hget(user_hash, 'stats_trains_byiti')) \
                if r.hget(user_hash, 'stats_trains_byiti') else 0
            stations += int(r.hget(user_hash, 'stats_stations')) \
                if r.hget(user_hash, 'stats_stations') else 0

        personal_start_command = int(r.hget(u.rhash, 'stats_command_start')) \
            if r.hget(u.rhash, 'stats_command_start') else 0
        personal_callback_count = int(r.hget(u.rhash, 'stats_callback_count')) \
            if r.hget(u.rhash, 'stats_callback_count') else 0
        personal_trains_bynum = int(r.hget(u.rhash, 'stats_trains_bynum')) \
            if r.hget(u.rhash, 'stats_trains_bynum') else 0
        personal_trains_byiti = int(r.hget(u.rhash, 'stats_trains_byiti')) \
            if r.hget(u.rhash, 'stats_trains_byiti') else 0
        personal_stations = int(r.hget(u.rhash, 'stats_stations')) \
            if r.hget(u.rhash, 'stats_stations') else 0

        text = (
            "<b>Statistiche</b>"
            "\n<i>Le informazioni</i>"
            "\n➖➖ 👤 <i>Utenti</i>"
            "\n<b>Utenti attivi</b>: {au}"
            "\n<b>Utenti totali</b>: {tu}"
            "\n➖➖ 💬 <i>Comandi</i>"
            "\n<b>Comando /start</b>: {sc} <i>(tu {psc})</i>"
            "\n<b>Tastiere inline</b>: {cc} <i>(tu {pcc})</i>"
            "\n➖➖ 👁‍🗨 <i>Query</i>"
            "\n<b>Treni cercati</b> per numero: {tr_bynum} <i>(tu {ptr_bynum})</i>"
            "\n<b>Treni cercati</b> per itinerario: {tr_byiti} <i>(tu {ptr_byiti})</i>"
            "\n<b>Stazioni cercate</b> per nome: {st} <i>(tu {pst})</i>"
            .format(au=active_users, tu=total_users, sc=start_command, cc=callbacks_count,
                    psc=personal_start_command, pcc=personal_callback_count,
                    tr_bynum=trains_bynum, ptr_bynum=personal_trains_bynum,
                    tr_byiti=trains_byiti, ptr_byiti=personal_trains_byiti,
                    st=stations, pst=personal_stations)
        )
        bot.api.call("editMessageText", {
            "chat_id": cb.chat.id, "message_id": cb.message.message_id, "parse_mode": "HTML",
            "text": text, "reply_markup":
            json.dumps(
                {"inline_keyboard": [
                    [{"text": "⬅️ Torna indietro", "callback_data": "info"}]
                ]}
            )
        })
        cb.notify("📈 Statistiche")

    elif cb.query == "train":
        text = (
            "<b>🚅 Cerca treno</b>"
            "\n<b>Cerca</b> un <b>treno</b>, <b>visualizza</b> le <b>informazioni principali</b> e "
            "<b>molto altro</b>."
            "\n\nVuoi cercare il treno 1️⃣ <b>per numero di treno</b> o 🛤 <b>per itinerario</b>?"
        )
        bot.api.call("editMessageText", {
            "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
            "parse_mode": "HTML", "reply_markup":
            json.dumps(
                {"inline_keyboard": [
                    [{"text": "1️⃣ Numero", "callback_data": "train_bynum"},
                     {"text": "🛤 Itinerario", "callback_data": "train_byiti"}],
                    [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                ]}
            )
        })
        cb.notify("🚅 Cerca treno")

    elif cb.query == "train_bynum":
        u.state("train_bynum")
        text = (
            "<b>🚅 Cerca treno</b> per numero"
            "\nInserisci il <b>numero di treno</b> (senza nessuna sigla prima, per esempio <code>9650</code>)"
        )
        bot.api.call("editMessageText", {
            "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
            "parse_mode": "HTML", "reply_markup":
            json.dumps(
                {"inline_keyboard": [
                    [{"text": "🛤 Cerca invece per itinerario", "callback_data": "train_byiti"}],
                    [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                ]}
            )
        })
        cb.notify("1️⃣ Cerca treno per numero")

    elif cb.query == "train_byiti":
        u.state("train_byiti")
        text = (
            "<b>🛤 Cerca treno</b> per itinerario"
            "\nInserisci, come prima cosa, la <b>stazione di partenza</b>"
        )
        bot.api.call("editMessageText", {
            "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
            "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {"inline_keyboard": [
                        [{"text": "1️⃣ Cerca invece per numero", "callback_data": "train_bynum"}],
                        [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                    ]}
                )
        })
        cb.notify("🛤 Cerca treno per itinerario")

    elif cb.query == "station":
        u.state("station")
        text = (
            "<b>🚉 Cerca stazione</b>"
            "\nInserisci il <b>nome</b> della stazione che vuoi cercare"
        )
        bot.api.call("editMessageText", {
            "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
            "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {"inline_keyboard": [
                        [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                    ]}
                )
        })
        cb.notify("🚉 Cerca stazione")

    elif cb.query == "news":
        raw = api.call("news", 0, "it")
        text = format.formatNews(raw)
        bot.api.call("editMessageText", {
            "chat_id": cb.chat.id, "message_id": cb.message.message_id, "text": text,
            "parse_mode": "HTML", "reply_markup":
                json.dumps(
                    {"inline_keyboard": [
                        [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                    ]}
                )
        })
        cb.notify("📰 News")

    # TRAINS CALLBACK
    elif 'train@' in cb.query:
        arguments = cb.query.split('@')
        del(arguments[0])
        departure_station, train = arguments[0].split('_')[0:2]
        del(arguments[0])

        raw = api.call('andamentoTreno', departure_station, train)

        if not arguments:
            u.increaseStat('stats_trains_bynum')

            text = format.formatTrain(raw)
            bot.api.call('editMessageText', {
                'chat_id': cb.chat.id, 'message_id': cb.message.message_id, 'text': text,
                'parse_mode': 'HTML', 'reply_markup':
                json.dumps(
                    {"inline_keyboard": [
                        [{"text": "🔄 Aggiorna le informazioni", "callback_data": cb.query + "@update"}],
                        [{"text": "🚉 Fermate", "callback_data": cb.query + "@stops"},
                         {"text": "📊 Grafico ritardo", "callback_data": cb.query + "@graph"}],
                        [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                    ]}
                )
            })
            cb.notify("🚅 Treno {n} da {d} a {a}".format(n=train, d=raw['origine'], a=raw['destinazione']))
            return

        elif not arguments[0]:
            text = format.formatTrain(raw)
            bot.api.call('editMessageText', {
                'chat_id': cb.chat.id, 'message_id': cb.message.message_id, 'text': text,
                'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🔄 Aggiorna le informazioni", "callback_data": cb.query}],
                            [{"text": "🚉 Fermate", "callback_data": "@".join(cb.query.split("@")[:-1]) + "@stops"},
                             {"text": "📊 Grafico ritardo", "callback_data": cb.query + "@graph"}],
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })

        elif arguments[0] == "update":
            text = format.formatTrain(raw)

            try:
                bot.api.call('editMessageText', {
                    'chat_id': cb.chat.id, 'message_id': cb.message.message_id, 'text': text,
                    'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🔄 Aggiorna le informazioni", "callback_data": cb.query}],
                            [{"text": "🚉 Fermate", "callback_data": "@".join(cb.query.split("@")[:-1]) + "@stops"},
                             {"text": "📊 Grafico ritardo", "callback_data": cb.query + "@graph"}],
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
                })
                cb.notify("🔄 Informazioni per il treno {n} aggiornate".format(n=train))
            except APIError:  # Message is not modified
                cb.notify("❎ Informazioni invariate per il treno {n}".format(n=train), alert=True)
            return

        elif arguments[0] == "stops":
            inline_keyboard = format.getStopsInlineKeyboard(raw, cb.query)
            text = "<b>Lista fermate del treno {x}</b>".format(x=raw['compNumeroTreno'])
            bot.api.call('editMessageText', {
                'chat_id': cb.chat.id, 'message_id': cb.message.message_id, 'text': text,
                'parse_mode': 'HTML', 'reply_markup':
                json.dumps(
                    {"inline_keyboard": inline_keyboard}
                )
            })
            return

        elif arguments[0] == "stop":
            text = format.formatTrainStop(raw, int(arguments[1]))
            inline_keyboard = format.generateTrainStopInlineKeyboard(raw, int(arguments[1]))
            bot.api.call('editMessageText', {
                'chat_id': cb.chat.id, 'message_id': cb.message.message_id, 'text': text,
                'parse_mode': 'HTML', 'disable_web_page_preview': True, 'reply_markup':
                    json.dumps({"inline_keyboard": inline_keyboard})
            })
            return

        elif arguments[0] == "graph":
            filename = format.generateTrainGraph(raw)
            if not filename:
                cb.notify(
                    "❌ Impossibile generare il grafico del ritardo: troppe poche informazioni. Riprova più tardi",
                    alert=True
                )
                return

            cb.message.reply_with_photo(filename)
            os.remove(filename)
            return

    # STATIONS CALLBACK
    elif 'station@' in cb.query:
        arguments = cb.query.split('@')
        del(arguments[0])
        station = arguments[0]
        station_name = utils.station_from_ID(station)
        del(arguments[0])

        state = u.state().decode('utf-8')

        if state == "train_byiti":
            u.setRedis('iti_station1', station)
            u.state('train_byiti_2')
            text = (
                "<b>🛤 Cerca treno</b> per itinerario"
                "\nInserisci ora la <b>stazione di arrivo</b>"
            )
            bot.api.call('editMessageText', {
                'chat_id': cb.chat.id, 'message_id': cb.message.message_id,
                'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })
            cb.notify("🚉 Stazione di partenza selezionata: {s}".format(s=station_name))
            return

        elif state == "train_byiti_2":
            u.setRedis('iti_station2', station)
            u.state('train_byiti _3')
            text = (
                "<b>🛤 Cerca treno</b> per itinerario"
                "\nInserisci ora <b>la data</b> e/o <b>l'orario di partenza</b> desiderati "
                "(per esempio: <code>{a}</code>; <code>{b}</code>; <code>{c}</code>)"
                .format(a=datetime.now().strftime('%d/%m %H:%M'),
                        b=datetime.now().strftime("%H:%M %d/%m/%y"),
                        c=datetime.now().strftime("%H:%M"))
            )
            bot.api.call('editMessageText', {
                'chat_id': cb.chat.id, 'message_id': cb.message.message_id,
                'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🕒 Orario attuale", "callback_data": "train_byiti@now"}],
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })
            cb.notify("🚉 Stazione di arrivo selezionata: {s}".format(s=station_name))
            return

        elif not arguments:
            u.increaseStat('stats_stations')
            text = format.formatStation(station_name)
            bot.api.call('editMessageText', {
                'chat_id': cb.chat.id, 'message_id': cb.message.message_id,
                'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🔘 Mostra le informazioni da Wikipedia",
                              "callback_data": "station@" + station + "@wiki"}],
                            [{"text": "🚦 Arrivi", "callback_data": "station@" + station + "@arrivals"},
                             {"text": "🚦 Partenze", "callback_data": "station@" + station + "@departures"}],
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })
            cb.notify("ℹ️ Informazioni della stazione di {s}".format(s=station_name))
            return

        elif len(arguments) == 1 and arguments[0] == "wiki":
            text = format.formatStation(station_name, withWikiSummary=True)
            bot.api.call('editMessageText', {
                'chat_id': cb.chat.id, 'message_id': cb.message.message_id,
                'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🚦 Arrivi", "callback_data": "station@" + station + "@arrivals"},
                             {"text": "🚦 Partenze", "callback_data": "station@" + station + "@departures"}],
                            [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                        ]}
                    )
            })
            cb.notify("ℹ️ Informazioni della stazione di {s}".format(s=station_name))
            return

        elif len(arguments) == 1:
            date = (datetime.now() - (timedelta(hours=1) if is_DST() else 0)).strftime("%a %b %d %Y %H:%M:%S GMT+0100")
            raw = api.call('partenze' if arguments[0] == 'departures' else 'arrivi', station, date)
            text = format.formatDepartures(raw, station, format.ELEMENTS_FOR_PAGE) if arguments[0] == 'departures' \
                else format.formatArrivals(raw, station, format.ELEMENTS_FOR_PAGE)

            inline_keyboard = format.generateStationPagesInlineKeyboard([0, format.ELEMENTS_FOR_PAGE], format.getPagesCount(raw),
                                                                        station, arguments[0])
            bot.api.call('editMessageText', {
                'chat_id': cb.chat.id, 'message_id': cb.message.message_id,
                'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': True, 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": inline_keyboard}
                    )
            })
            cb.notify(
                "{a} della stazione di {s}".format(
                    a="🚦 Partenze" if arguments[0] == "departures" else "🚦 Arrivi ",
                    s=station_name)
            )

        elif len(arguments) == 2:
            date = (datetime.now() - (timedelta(hours=1) if is_DST() else 0)).strftime("%a %b %d %Y %H:%M:%S GMT+0100")
            raw = api.call('partenze' if arguments[0] == 'departures' else 'arrivi', station, date)
            text = format.formatDepartures(raw, station, int(arguments[1])) if arguments[0] == 'departures' \
                else format.formatArrivals(raw, station, int(arguments[1]))

            inline_keyboard = format.generateStationPagesInlineKeyboard([int(arguments[1]) - format.ELEMENTS_FOR_PAGE,
                                                                         int(arguments[1])], format.getPagesCount(raw),
                                                                        station, arguments[0])
            bot.api.call('editMessageText', {
                'chat_id': cb.chat.id, 'message_id': cb.message.message_id,
                'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': True, 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": inline_keyboard}
                    )
            })
            cb.notify(
                "{a} della stazione di {s} (pagina {x})".format(
                    a="🚦 Partenze" if arguments[0] == "departures" else "🚦 Arrivi ",
                    s=station_name,
                    x=int(arguments[1]) // format.ELEMENTS_FOR_PAGE)
            )

    # ITINERARY CALLBACK
    elif cb.query == "train_byiti@now":
        def minifyStation(__str):
            __str = __str[1:]
            x = 0
            for i in __str:
                if i != "0":
                    __str = __str[x:]
                    break
                x += 1
            return __str

        date = datetime.now()

        station_a = minifyStation(u.getRedis('iti_station1').decode('utf-8'))
        station_b = minifyStation(u.getRedis('iti_station2').decode('utf-8'))
        u.delRedis('iti_station1')
        u.delRedis('iti_station2')

        u.increaseStat('stats_trains_byiti')

        date = date.strftime('%Y-%m-%dT%H:%M:%S')

        raw = api.call('soluzioniViaggioNew', station_a, station_b, date)
        text = format.formatItinerary(raw)
        bot.api.call('editMessageText', {
            'chat_id': cb.chat.id, 'message_id': cb.message.message_id, 'text': text,
            'parse_mode': 'HTML', 'disable_web_page_preview': True, 'reply_markup':
                json.dumps(
                    {"inline_keyboard": [
                        [{"text": "⬅️ Torna indietro", "callback_data": "home"}]
                    ]}
                )
        })
        u.state("home")

    elif cb.query == "admin":
        if cb.sender.id not in config.ADMINS:
            return

        text = (
            "🔴 <b>Benvenuto nel pannello amministratore di Orario Treni</b>"
            "\nSeleziona un opzione:"
        )
        bot.api.call('editMessageText', {
            'chat_id': cb.chat.id, 'message_id': cb.message.message_id,
            'text': text, 'parse_mode': 'HTML', 'reply_markup':
                json.dumps(
                    {'inline_keyboard': [
                        [{"text": "➕🌐 Nuovo post globale", "callback_data": "admin@newpost"}]
                    ]}
                )
        })

    elif "admin@" in cb.query:
        if cb.sender.id not in config.ADMINS:
            return

        arguments = cb.query.split('@')
        del(arguments[0])

        if arguments[0] == "newpost" and len(arguments) == 1:
            text = (
                "➕🌐 <b>Nuovo post globale</b>"
                "\nInvia il testo <b>formattato in HTML</b> del <b>post globale</b>"
            )
            bot.api.call('editMessageText', {
                'chat_id': cb.chat.id, 'message_id': cb.message.message_id, 'text': text,
                'parse_mode': 'HTML', 'disable_web_page_preview': True, 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "⬅️ Annulla", "callback_data": "admin"}]
                        ]}
                    )
            })
            u.state("admin_newpost")
            return

        elif arguments[0] == "newpost" and arguments[1] == "send":
            text = u.getRedis("admin_newpost_text").decode('utf-8')
            inline_keyboard = json.loads(u.getRedis("admin_newpost_keyboard").decode('utf-8'))

            global_messages.post(
                text=text,
                reply_markup={"inline_keyboard": inline_keyboard},
                parse_mode="HTML",
                message=cb.message)


def process_inline_callback(bot, cb, u):
    if not cb.isInline:
        return

    api = viaggiatreno.API()
    utils = viaggiatreno.Utils()

    if 'train@' in cb.query:
        arguments = cb.query.split('@')
        del(arguments[0])
        departure_station, train = arguments[0].split('_')[0:2]
        del(arguments[0])

        raw = api.call('andamentoTreno', departure_station, train)

        if not arguments:
            u.increaseStat('stats_trains_bynum')

            text = format.formatTrain(raw)
            bot.api.call('editMessageText', {
                'inline_message_id': cb.inline_message_id, 'text': text,
                'parse_mode': 'HTML', 'reply_markup':
                json.dumps(
                    {"inline_keyboard": [
                        [{"text": "🔄 Aggiorna le informazioni", "callback_data": cb.query + "@update"}],
                        [{"text": "🚉 Fermate", "callback_data": cb.query + "@stops"}]
                    ]}
                )
            })
            cb.notify("🚅 Treno {n} da {d} a {a}".format(n=train, d=raw['origine'], a=raw['destinazione']))
            return

        elif not arguments[0]:
            text = format.formatTrain(raw)
            bot.api.call('editMessageText', {
                'inline_message_id': cb.inline_message_id, 'text': text,
                'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🔄 Aggiorna le informazioni", "callback_data": cb.query}],
                            [{"text": "🚉 Fermate", "callback_data": "@".join(cb.query.split("@")[:-1]) + "@stops"}]
                        ]}
                    )
            })

        elif arguments[0] == "update":
            text = format.formatTrain(raw)

            try:
                bot.api.call('editMessageText', {
                    'inline_message_id': cb.inline_message_id, 'text': text,
                    'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🔄 Aggiorna le informazioni", "callback_data": cb.query}],
                            [{"text": "🚉 Fermate", "callback_data": "@".join(cb.query.split("@")[:-1]) + "@stops"}]
                        ]}
                    )
                })
                cb.notify("🔄 Informazioni per il treno {n} aggiornate".format(n=train))
            except APIError:  # Message is not modified
                cb.notify("❎ Informazioni invariate per il treno {n}".format(n=train), alert=True)
            return

        elif arguments[0] == "stops":
            inline_keyboard = format.getStopsInlineKeyboard(raw, cb.query)
            text = "<b>Lista fermate del treno {x}</b>".format(x=raw['compNumeroTreno'])
            bot.api.call('editMessageText', {
                'inline_message_id': cb.inline_message_id, 'text': text,
                'parse_mode': 'HTML', 'reply_markup':
                json.dumps(
                    {"inline_keyboard": inline_keyboard}
                )
            })
            return

        elif arguments[0] == "stop":
            text = format.formatTrainStop(raw, int(arguments[1]))
            inline_keyboard = format.generateTrainStopInlineKeyboard(raw, int(arguments[1]))
            bot.api.call('editMessageText', {
                'inline_message_id': cb.inline_message_id, 'text': text,
                'parse_mode': 'HTML', 'disable_web_page_preview': True, 'reply_markup':
                    json.dumps({"inline_keyboard": inline_keyboard})
            })
            return

    # STATIONS CALLBACK
    elif 'station@' in cb.query:
        arguments = cb.query.split('@')
        del(arguments[0])
        station = arguments[0]
        station_name = utils.station_from_ID(station)
        del(arguments[0])

        if not arguments:
            u.increaseStat('stats_stations')
            text = format.formatStation(station_name)
            bot.api.call('editMessageText', {
                'inline_message_id': cb.inline_message_id,
                'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🔘 Mostra le informazioni da Wikipedia",
                              "callback_data": "station@" + station + "@wiki"}],
                            [{"text": "🚦 Arrivi", "callback_data": "station@" + station + "@arrivals"},
                             {"text": "🚦 Partenze", "callback_data": "station@" + station + "@departures"}],
                        ]}
                    )
            })
            cb.notify("ℹ️ Informazioni della stazione di {s}".format(s=station_name))
            return

        elif len(arguments) == 1 and arguments[0] == "wiki":
            text = format.formatStation(station_name, withWikiSummary=True)
            bot.api.call('editMessageText', {
                'inline_message_id': cb.inline_message_id,
                'text': text, 'parse_mode': 'HTML', 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": [
                            [{"text": "🚦 Arrivi", "callback_data": "station@" + station + "@arrivals"},
                             {"text": "🚦 Partenze", "callback_data": "station@" + station + "@departures"}],
                        ]}
                    )
            })
            cb.notify("ℹ️ Informazioni della stazione di {s}".format(s=station_name))
            return

        elif len(arguments) == 1:
            date = (datetime.now() - (timedelta(hours=1) if is_DST() else 0)).strftime("%a %b %d %Y %H:%M:%S GMT+0100")
            raw = api.call('partenze' if arguments[0] == 'departures' else 'arrivi', station, date)
            text = format.formatDepartures(raw, station, format.ELEMENTS_FOR_PAGE) if arguments[0] == 'departures' \
                else format.formatArrivals(raw, station, format.ELEMENTS_FOR_PAGE)

            inline_keyboard = format.generateStationPagesInlineKeyboard([0, format.ELEMENTS_FOR_PAGE], format.getPagesCount(raw),
                                                                        station, arguments[0])
            bot.api.call('editMessageText', {
                'inline_message_id': cb.inline_message_id,
                'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': True, 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": inline_keyboard}
                    )
            })
            cb.notify(
                "{a} della stazione di {s}".format(
                    a="🚦 Partenze" if arguments[0] == "departures" else "🚦 Arrivi ",
                    s=station_name)
            )

        elif len(arguments) == 2:
            date = (datetime.now() - (timedelta(hours=1) if is_DST() else 0)).strftime("%a %b %d %Y %H:%M:%S GMT+0100")
            raw = api.call('partenze' if arguments[0] == 'departures' else 'arrivi', station, date)
            text = format.formatDepartures(raw, station, int(arguments[1])) if arguments[0] == 'departures' \
                else format.formatArrivals(raw, station, int(arguments[1]))

            inline_keyboard = format.generateStationPagesInlineKeyboard([int(arguments[1]) - format.ELEMENTS_FOR_PAGE,
                                                                         int(arguments[1])], format.getPagesCount(raw),
                                                                        station, arguments[0])
            bot.api.call('editMessageText', {
                'inline_message_id': cb.inline_message_id,
                'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': True, 'reply_markup':
                    json.dumps(
                        {"inline_keyboard": inline_keyboard}
                    )
            })
            cb.notify(
                "{a} della stazione di {s} (pagina {x})".format(
                    a="🚦 Partenze" if arguments[0] == "departures" else "🚦 Arrivi ",
                    s=station_name,
                    x=int(arguments[1]) // format.ELEMENTS_FOR_PAGE)
            )

    else:
        cb.notify("501 - Not Implemented", alert=True)
