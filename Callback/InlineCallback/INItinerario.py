import API
import Callback
import Bot

import sqlite3
conn = sqlite3.connect('OrarioTreni.db')
c = conn.cursor()

import datetime

def callback(bot, chains, update):
    API.db.creaTutto()
    message = update.callback_query.message
    chat = message.chat
    callback_q = str(update.callback_query.data)
    callback_id = update.callback_query.id

    if callback_q == "itinerario":
        testo = ("<b>🛤Cerca itinerario</b>\n🚉Inserisci la <b>stazione di partenza</b>")
        bot.api.call("editMessageText", {"chat_id":chat.id, "message_id": message.message_id, "text": testo, "parse_mode":"HTML", "reply_markup":\
                    '{"inline_keyboard":[[{"text":"❌Annulla","callback_data":"home"}]]}'})
        bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
            "text": "✍Cerca itinerario", "show_alert":False})
        API.db.updateState(chat.id, "itinerario1", 0)

    if callback_q == "orarioNow":
        state, completato, success, error = API.db.getState(chat.id)
        if state != "itinerario3":
            return

        orario = datetime.datetime.now().strftime('%H:%M')

        c.execute('''UPDATE itinerario SET orario=? WHERE userid=?''',(orario, chat.id,))
        conn.commit()

        API.db.updateState(chat.id, "itinerario3", 2)

        c.execute('''SELECT * FROM itinerario WHERE userid=?''',(chat.id,))
        info = c.fetchall()
        for res in info:
            st1 = res[1]
            st2 = res[2]
            ora = res[3]
            chatid = res[0]
        conn.commit()
        data, success, error = API.orarioTreni.cercaItinerario(st1, st2, ora)
        testo, inline_keyboard = API.Messaggi.itinerario(data)
        bot.api.call("editMessageText", {"chat_id":chat.id, "message_id": message.message_id, "text":testo, "parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":'+inline_keyboard+'}'
                    })
