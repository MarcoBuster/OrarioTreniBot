import API
import Callback
import Bot

import sqlite3
conn = sqlite3.connect('OrarioTreni.db')
c = conn.cursor()

def callback(bot, chains, update):
    API.db.creaTutto()
    message = update.callback_query.message
    chat = message.chat
    callback_q = str(update.callback_query.data)
    callback_id = update.callback_query.id

    if callback_q == "stazione":
        testo = ("<b>🔍Scrivi il nome della stazione che vuoi cercare</b>:")
        bot.api.call("editMessageText", {"chat_id":chat.id, "message_id": message.message_id, "text": testo, "parse_mode":"HTML", "reply_markup":\
                    '{"inline_keyboard":[[{"text":"❌Annulla","callback_data":"home"}]]}'})
        bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
            "text": "✍Scrivi il nome della stazione che vuoi cercare", "show_alert":False})
        API.db.updateState(chat.id, "stazione1", 0)

    if callback_q.find("$") > 0: #$ -> Azioni riguardanti le stazioni
        cb = callback_q.split("$")
        azione = cb[0]
        stazione = cb[1]
        if azione == "staz":
            state, completato, success, error = API.db.getState(chat.id)
            if state == "itinerario1":
                API.db.creaTutto()
                c.execute('''DELETE FROM itinerario WHERE userid=?''',(chat.id,))
                c.execute('''INSERT INTO itinerario VALUES(?,?,?,?)''',(chat.id, "None", "None", "None",))
                c.execute('''UPDATE itinerario SET stazione1=? WHERE userid=?''',(stazione, chat.id,))
                conn.commit()
                API.db.updateState(chat.id, "itinerario2", 1)
                testo = ("<b>🛤Cerca itinerario</b>"
                        "\n🚉Inserisci la <b>stazione di arrivo</b>")
                bot.api.call("editMessageText", {"chat_id": chat.id, "message_id":message.message_id, "text":testo,"parse_mode":"HTML",
                    "reply_markup":
                        '{"inline_keyboard":[[{"text":"❌Annulla","callback_data":"home"}]]}'})
                return

            if state == "itinerario2":
                API.db.creaTutto()
                c.execute('''UPDATE itinerario SET stazione2=? WHERE userid=?''',(stazione, chat.id,))
                conn.commit()
                API.db.updateState(chat.id, "itinerario3", 1)
                testo = ("<b>🛤Cerca itinerario</b>\nInserisci l'orario, in formato HH:MM."
                    "\nEsempio: <code>22:05</code>, <code>09:15</code>, <code>13:53</code>"
                    "\nSe vuoi cercare un itinerario per l'orario attuale, premi il pulsante 🕒Orario attuale")
                bot.api.call("editMessageText", {"chat_id": chat.id, "message_id":message.message_id, "text":testo,"parse_mode":"HTML",
                    "reply_markup":
                        '{"inline_keyboard":[[{"text":"🕒Orario attuale","callback_data":"orarioNow"}],[{"text":"❌Annulla","callback_data":"home"}]]}'})
                return

            callbackdata1 = "arv$"+stazione
            callbackdata2 = "part$"+stazione
            callbackdata3 = "pos$"+stazione
            testo = "<b>Informazioni della stazione di </b>"+stazione #TODO
            bot.api.call("editMessageText", {"chat_id": chat.id, "message_id":message.message_id, "text":testo,"parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"🔽Arrivi","callback_data":"'+callbackdata1+'"},{"text":"🔼Partenze","callback_data":"'+callbackdata2+'"}],'\
                    '[{"text":"📍Posizione","callback_data":"'+callbackdata3+'"}],[{"text":"🔙Torna indietro","callback_data":"home"}]]}'})

        if azione == "arv":
            data, success, error = API.orarioTreni.stazione.arrivi(stazione)
            testo = API.Messaggi.arriviStazione(data, stazione)
            callbackdata1 = "staz$"+stazione
            bot.api.call("editMessageText", {"chat_id": chat.id, "message_id":message.message_id, "text":testo,"parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"🔙Torna indietro","callback_data":"'+callbackdata1+'"}]]}'})
            bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
                "text": "Arrivi nella stazione di "+stazione, "show_alert":False})

        if azione == "part":
            data, success, error = API.orarioTreni.stazione.partenze(stazione)
            testo = API.Messaggi.partenzeStazione(data, stazione)
            callbackdata1 = "staz$"+stazione
            bot.api.call("editMessageText", {"chat_id": chat.id, "message_id":message.message_id, "text":testo,"parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"🔙Torna indietro","callback_data":"'+callbackdata1+'"}]]}'})
            bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
                "text": "Partenze nella stazione di "+stazione, "show_alert":False})

        if azione == "pos":
            data = API.orarioTreni.stazione.informazioni(stazione)
            lat = data['lat']
            lon = data['lon']
            chat.send_location(lat, lon)
            testo = "<b>Informazioni della stazione di </b>"+stazione
            callbackdata1 = "arv$"+stazione
            callbackdata2 = "part$"+stazione
#            bot.api.call("editMessageReplyMarkup", {"chat_id":chat.id, "message_id":message.message_id,"reply_markup":
#                '{"inline_keyboard":[[{"text":"Arrivi","callback_data":"'+callbackdata1+'"},{"text":"Partenze","callback_data":"'+callbackdata2+'"}],'
#                '[{"text":"🔙Torna indietro","callback_data":"home"}]]}'}) #TODO
            bot.api.call("editMessageReplyMarkup", {"chat_id":chat.id, "message_id":message.message_id,"reply_markup":
                '{"inline_keyboard":[[{"text":"🔙Torna indietro","callback_data":"home"}]]}'})
            bot.api.call("sendMessage", {"chat_id":chat.id, "text":testo, "parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"Arrivi","callback_data":"'+callbackdata1+'"},{"text":"Partenze","callback_data":"'+callbackdata2+'"}],'
                    '[{"text":"🔙Torna indietro","callback_data":"home"}]]}'})
