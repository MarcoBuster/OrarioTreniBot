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

from ..objects.callback import Callback
from .. import config

import json

import redis

r = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)


def process_callback(bot, update, u):
    cb = Callback(update)

    if cb.query == "home":
        u.state("home")
        text = (
            "<b>Benvenuto in Orario Treni Bot!</b>"
            "\nCon questo bot potrai cercare 🚅 <b>treni</b>, 🚉 <b>stazioni</b> e 🚊 <b>itinerari</b>"
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
                    [{"text": "ℹ️ Altre informazioni", "callback_data": "info"}]
                ]}
            )
        })

    if cb.query == "info":
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

    if cb.query == "stats":
        users = r.hgetall('users')

        active_users = 0
        total_users = 0
        start_command = 0
        callbacks_count = 0
        for user in users:
            active_users += 1 if users[user] else 0
            total_users += 1

            user = int(user)

            start_command += int(r.hget('user:' + str(user), 'stats_command_start')) \
                if r.hget('user:' + str(user), 'stats_command_start') else 0
            callbacks_count += int(r.hget('user:' + str(user), 'stats_callback_count')) \
                if r.hget('user:' + str(user), 'stats_callback_count') else 0

        personal_start_command = int(r.hget(u.rhash, 'stats_command_start'))
        personal_callback_count = int(r.hget(u.rhash, 'stats_callback_count'))

        text = (
            "<b>Statistiche</b>"
            "\n➖➖ 👤 <i>Utenti</i>"
            "\n<b>Utenti attivi</b>: {au}"
            "\n<b>Utenti totali</b>: {tu}"
            "\n➖➖ 💬 <i>Comandi</i>"
            "\n<b>Comando /start</b>: {sc} <i>(tu {psc})</i>"
            "\n<b>Pulsanti inline</b>: {cc} <i>(tu {pcc})</i>"
            .format(au=active_users, tu=total_users, sc=start_command, cc=callbacks_count,
                    psc=personal_start_command, pcc=personal_callback_count)
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

    if cb.query == "train":
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

    if cb.query == "train_bynum":
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
