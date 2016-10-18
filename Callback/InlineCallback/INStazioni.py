import API
import Callback
import Bot

import sqlite3
conn = sqlite3.connect('OrarioTreni.db')
c = conn.cursor()

def callback(bot, chains, update):
    API.db.creaTutto()
    callback_q = update.callback_query.data
    callback_id = update.callback_query.id
    inline_message_id = update.callback_query.inline_message_id

    if callback_q == "stazione":
        testo = ("<b>🔍Scrivi il nome della stazione che vuoi cercare</b>:")
        bot.api.call("editMessageText", {"inline_message_id": inline_message_id, "text": testo, "parse_mode":"HTML", "reply_markup":\
                    '{"inline_keyboard":[[{"text":"❌Annulla","callback_data":"home"}]]}'})
        bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
            "text": "✍Scrivi il nome della stazione che vuoi cercare", "show_alert":False})
        API.db.updateState(chat.id, "stazione1", 0)

    if callback_q.find("$") > 0: #$ -> Azioni riguardanti le stazioni
        cb = callback_q.split("$")
        azione = cb[0]
        stazione = cb[1]
        if azione == "staz":
            callbackdata1 = "arv$"+stazione
            callbackdata2 = "part$"+stazione
            callbackdata3 = "pos$"+stazione
            testo = "<b>Informazioni della stazione di </b>"+stazione #TODO
            bot.api.call("editMessageText", {"inline_message_id": inline_message_id, "text":testo,"parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"🔽Arrivi","callback_data":"'+callbackdata1+'"},{"text":"🔼Partenze","callback_data":"'+callbackdata2+'"}],'\
                    '[{"text":"🔙Vai al menù inline","callback_data":"home"}]]}'})

        if azione == "arv":
            data, success, error = API.orarioTreni.stazione.arrivi(stazione)
            testo = API.Messaggi.arriviStazione(data, stazione)
            callbackdata1 = "staz$"+stazione
            bot.api.call("editMessageText", {"inline_message_id": inline_message_id, "text":testo,"parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"🔙Torna indietro","callback_data":"'+callbackdata1+'"}]]}'})
            bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
                "text": "Arrivi nella stazione di "+stazione, "show_alert":False})

        if azione == "part":
            data, success, error = API.orarioTreni.stazione.partenze(stazione)
            testo = API.Messaggi.partenzeStazione(data, stazione)
            callbackdata1 = "staz$"+stazione
            bot.api.call("editMessageText", {"inline_message_id": inline_message_id, "text":testo,"parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"🔙Torna indietro","callback_data":"'+callbackdata1+'"}]]}'})
            bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
                "text": "Partenze nella stazione di "+stazione, "show_alert":False})
