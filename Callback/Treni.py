import API
import Callback
import Bot
import botogram

import sqlite3
conn = sqlite3.connect('OrarioTreni.db')
c = conn.cursor()

import os

def callback(bot, chains, update):
    API.db.creaTutto()
    message = update.callback_query.message
    chat = message.chat
    callback_q = str(update.callback_query.data)
    callback_id = update.callback_query.id

    if callback_q == "treno":
        testo = ("<b>🔍Scrivi il numero di treno che vuoi cercare</b>: ")
        bot.api.call("editMessageText", {"chat_id":chat.id, "message_id": message.message_id, "text": testo, "parse_mode":"HTML", "reply_markup":\
                    '{"inline_keyboard":[[{"text":"❌Annulla","callback_data":"home"}]]}'})
        bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
            "text": "✍Scrivi un numero di treno", "show_alert":False})

        API.db.updateState(chat.id, "treno1", 0)

    if callback_q.find("@") > 0: #@ -> Azioni riguardi i treni
        cb = callback_q.split("@")
        azione = cb[0]
        id_treno = cb[1]
        if azione == "agg":
            data, success, error = API.orarioTreni.cercaTreno(id_treno)
            testo = API.Messaggi.treno1(data)
            callbackdata1 = "list@"+id_treno
            callbackdata2 = "agg@"+id_treno
            try:
                bot.api.call("editMessageText", {"chat_id": chat.id, "message_id":message.message_id, "text":testo,"parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"🚉Lista fermate","callback_data":"'+callbackdata1+'"},'
                    '{"text":"🔄Aggiorna le informazioni","callback_data":"'+callbackdata2+'"}],'
                    '[{"text": "🚦Traccia il treno [BETA]", "callback_data": "traccia@'+id_treno+'"},'
                    '{"text": "📊Grafico ritardo", "callback_data": "grafico@'+id_treno+'"}],'
                    '[{"text":"🔙Torna indietro","callback_data":"home"}]]}'})
            except botogram.api.APIError:
                bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
                    "text": "❎Le informazioni sono state aggiornate, ma non sono cambiate!", "show_alert":True})
                return
            bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
                "text": "✅Informazioni aggiornate!", "show_alert":False})

        if azione == "list":
            data, success, error = API.orarioTreni.cercaTreno(id_treno)
            inline_keyboard = '['
            numeroFermata = 0
            for dict in data['fermate']:
                stazione = dict['stazione']
                callback_data = "ferm@"+id_treno+"%"+str(numeroFermata)
                inline_keyboard = inline_keyboard + '[{"text":"'+stazione+'","callback_data":"'+callback_data+'"}],'
                numeroFermata = numeroFermata + 1

            callbackdata = 'agg@'+id_treno
            inline_keyboard = inline_keyboard + '[{"text":"🔙Torna indietro","callback_data":"'+callbackdata+'"}]]'
            testo = "<b>Ecco la lista delle fermate del treno {}</b>".format(id_treno)
            bot.api.call("editMessageText", {"chat_id": chat.id, "message_id":message.message_id, "text":testo,"parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":'+inline_keyboard+'}'})

        if azione == "ferm":
            stringa = id_treno.split("%")
            id_treno = stringa[0]
            fermata = stringa[1]

            data, success, error = API.orarioTreni.cercaTreno(id_treno)
            testo = API.Messaggi.fermata(data, fermata)

            stazione = data['fermate'][int(fermata)]['stazione']

            fermata = int(fermata)

            n_fermate = 0
            for dict in data['fermate']:
                n_fermate = n_fermate + 1

            if fermata == n_fermate - 1:
                fermata_precedente = "ferm@"+id_treno+"%"+str(fermata - 1)
                nome_precedente = data['fermate'][fermata - 1]['stazione']
                bot.api.call("editMessageText", {"chat_id": chat.id, "message_id": message.message_id, "text":testo, "parse_mode":"HTML",
                    "reply_markup":
                        '{"inline_keyboard":[[{"text":"◀️'+nome_precedente+'", "callback_data": "'+fermata_precedente+'"}],'
                        '[{"text":"🔎Stazione di '+stazione+'", "callback_data":"staz$'+stazione+'"}],'+
                        '[{"text":"🔙Torna indietro", "callback_data":"list@'+id_treno+'"}]'
                                    ']}'
                })
                return

            if fermata == 0:
                fermata_successiva = "ferm@"+id_treno+"%"+str(fermata + 1)
                nome_successivo = data['fermate'][fermata + 1]['stazione']
                bot.api.call("editMessageText", {"chat_id": chat.id, "message_id": message.message_id, "text":testo, "parse_mode":"HTML",
                    "reply_markup":
                        '{"inline_keyboard":[[{"text":"▶️'+nome_successivo+'", "callback_data": "'+fermata_successiva+'"}],'
                        '[{"text":"🔎Stazione di '+stazione+'", "callback_data":"staz$'+stazione+'"}],'+
                        '[{"text":"🔙Torna indietro", "callback_data":"list@'+id_treno+'"}]'
                                    ']}'
                })
                return

            fermata_precedente = "ferm@"+id_treno+"%"+str(fermata - 1)
            fermata_successiva = "ferm@"+id_treno+"%"+str(fermata + 1)
            nome_precedente = data['fermate'][fermata - 1]['stazione']
            nome_successivo = data['fermate'][fermata + 1]['stazione']

            bot.api.call("editMessageText", {"chat_id": chat.id, "message_id": message.message_id, "text":testo, "parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"◀️'+nome_precedente+'", "callback_data": "'+fermata_precedente+'"}, {"text":"▶️'+nome_successivo+'", "callback_data":"'+fermata_successiva+'"}],'
                    '[{"text":"🔎Stazione di '+stazione+'", "callback_data":"staz$'+stazione+'"}],'+
                    '[{"text":"🔙Torna indietro", "callback_data":"list@'+id_treno+'"}]'
                                ']}'
            })

        if azione == "traccia":
            if "T" in id_treno:
                stringa = id_treno.split("T")
                id_treno = stringa[0]
                azione_2 = stringa[1]

                if azione_2 == "oggi":
                    solo_oggi = True
                    stringa_solo_oggi = "<b>Il treno verrà tracciato solo per oggi</b>"
                if azione_2 == "sempre":
                    solo_oggi = False
                    stringa_solo_oggi = "<b>Il treno verrà tracciato fino a interruzione</b>"

                result = API.db.tracciaTreno(message.chat.id, id_treno, solo_oggi)
                if type(result) == str:
                    bot.api.call("answerCallbackQuery", {
                        "callback_query_id": callback_id, "text": result, "show_alert": True
                    })
                    return

                text = (
                    "<b>🚦 Traccia treno</b>"
                    "\n🚅 Sto tracciando il <b>treno {treno}</b>"
                    "\n\n{solo_oggi}".format(solo_oggi=stringa_solo_oggi, treno=id_treno)
                )
                bot.api.call("editMessageText", {
                    "chat_id": chat.id, "message_id": message.message_id, "text": text, "parse_mode": "HTML", "reply_markup":
                        '{"inline_keyboard": [[{"text": "❌ Annulla il tracciamento", "callback_data": "stop_tracciamentoT'+str(result)+'"}]]}'
                })

                return

            text = (
                "<b>Traccia treno {treno}</b>"
                "\nVuoi tracciare questo treno <b>solo oggi</b> o ricevere notifiche <b>tutti i giorni?</b>".format(treno=id_treno)
            )
            bot.api.call("editMessageText", {
                "chat_id": chat.id, "message_id": message.message_id, "text": text, "parse_mode": "HTML", "reply_markup":
                    '{"inline_keyboard":'
                    '[[{"text": "📅 Traccia solo per oggi", "callback_data": "traccia@'+id_treno+'Toggi"}, {"text": "🗓 Traccia tutti i giorni", "callback_data": "traccia@'+id_treno+'Tsempre"}],'
                    '[{"text":"🔙Torna indietro", "callback_data": "agg@'+id_treno+'"}]]}'
            })

        if azione == "grafico":
            data, success, error = API.orarioTreni.cercaTreno(id_treno)
            bot.api.call("answerCallbackQuery", {
                "callback_query_id": callback_id, "text": "📊Sto generando il grafico, attendere..."
            })

            filename = API.Messaggi.grafico(data, id_treno)

            if filename == False:
                text = (
                    "❌<b>Impossibile generare il grafico</b>: troppi pochi dati"
                    "\n<i>Attendi che il treno fermi in qualche altra fermata e ritenta!</i>"
                )
                message.reply(text)
                return

            message.reply_with_photo(filename, caption="Grafico del treno "+id_treno+" generato con @OrarioTreniBot")
            os.remove(filename)
