import botogram

import API
import Callback
import Bot

import sqlite3
conn = sqlite3.connect('OrarioTreni.db')
c = conn.cursor()

def callback(bot, chains, update):
    callback_q = str(update.callback_query.data)
    callback_id = update.callback_query.id
    inline_message_id = update.callback_query.inline_message_id

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
                bot.api.call("editMessageText", {"inline_message_id": inline_message_id, "text":testo,"parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"🚉Lista fermate","callback_data":"'+callbackdata1+'"},'
                    '{"text":"🔄Aggiorna le informazioni","callback_data":"'+callbackdata2+'"}],'
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
            bot.api.call("editMessageText", {"inline_message_id": inline_message_id, "text":testo,"parse_mode":"HTML",
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
                bot.api.call("editMessageText", {"inline_message_id": inline_message_id, "text":testo, "parse_mode":"HTML",
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
                bot.api.call("editMessageText", {"inline_message_id": inline_message_id, "text":testo, "parse_mode":"HTML",
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

            bot.api.call("editMessageText", {"inline_message_id": inline_message_id, "text":testo, "parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"◀️'+nome_precedente+'", "callback_data": "'+fermata_precedente+'"}, {"text":"▶️'+nome_successivo+'", "callback_data":"'+fermata_successiva+'"}],'
                    '[{"text":"🔎Stazione di '+stazione+'", "callback_data":"staz$'+stazione+'"}],'+
                    '[{"text":"🔙Torna indietro", "callback_data":"list@'+id_treno+'"}]'
                                ']}'
            })
