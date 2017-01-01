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

    if callback_q == "home":
        testo = "<b>Cosa vuoi fare?</b>"
        bot.api.call("editMessageText", {"chat_id": chat.id, "message_id":message.message_id, "text":testo,"parse_mode":"HTML",\
            "reply_markup":'{"inline_keyboard":[[{"text":"🚄Cerca treno",'\
            '"callback_data": "treno"},{"text":"🚉Cerca stazione","callback_data": "stazione"}],'\
            '[{"text":"🛤Cerca itinerario","callback_data":"itinerario"}],[{"text":"❓Aiuto","callback_data":"help"},'\
            '{"text":"🚧Altro","callback_data":"altro"},'\
            '{"text":"🌟Vota il bot","callback_data":"vota"}]]}'})
        bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
            "text": "🏠Sei tornato indietro", "show_alert":False})
        API.db.updateState(chat.id, "home", 1)

    if callback_q == "help":
        testo = ("<b>Aiuto</b>"
            "\nBenvenuto nel <b>nuovo Orario treni</b>"
            "\nQuesta <b>nuovissima</b> versione <b>abolisce completamente</b> i comandi testuali, come <b>/treno</b>, in favore delle <b>tastiere inline</b>."
            "\n\n<b>Cosa si può fare con questo bot?</b>"
            "\n• <b>Cercare treni</b>, visualizzare il loro <b>andamento</b> e le <b>fermate intermedie</b>"
            "\n• <b>Cercare stazioni</b>, con <b>partenze</b> e <b>arrivi</b> in due schermate distinte e la <b>posizione</b> precisa della stazione"
            "\n• <b>Cercare itinerari</b>, con la possibilità di specificare l\'<b>orario</b>"
            "\n• <b>Visualizzare curiose statistiche</b>, da condividere con gli amici"
            "\n• <b>Inline mode</b>, tutto questo è anche <b>inline</b> (tocca il pulsante sotto per altre informazioni)"
            "\n\nEssendo tutto molto <b>intuitivo</b>, basta utilizzare i <b>pulsanti inline</b>."
            "\nSe proprio non riesci a capire qualcosa o hai riscontrato qualche <b>problema</b>, contatta lo <b>sviluppatore</b> o utilizza il <b>comando /feedback</b>"
            "\n\n<b>Link utili:</b>"
            "\n<b>Creatore e sviluppatore</b>: 👉 @MarcoBuster"
            "\n<b>Gruppo del bot</b>: 👉 @MarcoBusterGroup"
            "\n<b>Canale con aggiornamenti e anteprime</b>: 👉 @OrarioTreni"
            "\n<b>Vota il bot</b>: 👉 <a href=\"telegram.me/storebot?start=OrarioTreniBot\">Storebot</a>"
            "\n<b>Codice sorgente</b>: <a href=\"www.github.com/MarcoBuster/OrarioTreniBot\">GitHub</a>")

        bot.api.call("editMessageText", {"chat_id":chat.id, "message_id": message.message_id, "text": testo, "parse_mode":"HTML", "reply_markup":\
                    '{"inline_keyboard":[[{"text":"🚀Inline mode", "callback_data":"inline"}], [{"text":"🔙Torna indietro","callback_data":"home"}]]}'})
        bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
            "text": "❓Aiuto", "show_alert":False})

    if callback_q == "inline":
        testo = (
                "<b>Inline mode</b>"
                "\n<i>Questo bot è anche inline. Questo significa che lo puoi usare in qualsiasi chat, indipendentemente che il bot ci sia</i>"
                "\n<b>Attenzione!</b> La modalità inline non funziona nei canali, a causa di una limitazione di Telegram"
                "\n\n<b>Cercare un treno inline</b>"
                "\nPer cercare un treno in modalità inline, devi scrivere, in <b>qualsiasi chat</b>:"
                "\n<code>@OrarioTreniBot numero-treno</code>"
                "\nApparirà una schermata sopra la tastiera, cliccandoci sopra il bot invierà nella chat le informazioni sul treno"
                "\n\n<b>Cercare una stazione inline</b>"
                "\nPer cercare una stazione in modalità inline, devi scrivere, in <b>qualsiasi chat</b>:"
                "\n<code>@OrarioTreniBot nome-stazione</code>"
                "\nSe la query di ricerca corrisponde <b>a più stazioni</b>, bisognerà scegliere una stazione tra l'elenco che apparirà. Questo può accadere scrivendo per esempio \"MILANO\""
                "\n\n<b>Cercare un itinerario inline</b>"
                "\nPer cercare un itinerario in modalità inline, devi scrivere, in <b>qualsiasi chat</b>:"
                "\n<code>@OrarioTreniBot stazionedipartenza - stazionediarrivo</code>"
                "\nEsempio: <code>@OrarioTreniBot MILANO CENTRALE - ROMA TERMINI</code>"
                )

        bot.api.call(
            "editMessageText",{
                "chat_id": chat.id, "message_id": message.message_id, "text": testo, "parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"🆗Torna all\'help", "callback_data":"help"}],[{"text":"🌐Prova ora!","switch_inline_query":" "}]]}'
            }
        )

    if callback_q == "vota":
        testo = ("*Grazie per il supporto!*"
            "\nVota il bot 5 stelle [cliccando qui](telegram.me/storebot?start=OrarioTreniBot)")
        bot.api.call("editMessageText", {"chat_id":chat.id, "message_id": message.message_id, "text": testo, "parse_mode":"Markdown", "reply_markup":\
                    '{"inline_keyboard":[[{"text":"🔙Torna indietro","callback_data":"home"}]]}'})
        bot.api.call("answerCallbackQuery", {"callback_query_id": callback_id,
            "text": "🌟Vota il bot per favore!", "show_alert":False})

    if callback_q == "altro":
        testo = "Visualizza le *statistiche* o vai al codice sorgente di *GitHub*"
        bot.api.call("editMessageText", {"chat_id":chat.id, "message_id": message.message_id, "text": testo, "parse_mode":"Markdown", "reply_markup":\
                    '{"inline_keyboard":[[{"text":"📊Statistiche","callback_data":"stats"}, {"text":"💻GitHub","url":"www.github.com/MarcoBuster/OrarioTreniBot"}],'\
                    '[{"text": "🚦 Treni in tracciamento", "callback_data": "lista_tracciamento"}],'
                    '[{"text":"🔙Torna indietro","callback_data":"home"}]]}'})

    if callback_q == "lista_tracciamento":
        c.execute('SELECT * FROM tracciamento WHERE userid=?', (chat.id,))
        rows = c.fetchall()

        text = "<b>Ecco la lista dei treni che sono in tracciamento in questa chat</b>"

        if not rows:
            text = text + "\n\n<i>Non stai tracciando nessun treno, per tracciarne uno, cerca un treno e premi su 🚦 Traccia treno</i>"

        for res in rows:
            request_id = str(res[0])
            user_id = res[1]
            id_treno = res[2]
            solo_oggi = res[3]
            stazione_ultimo_rilevamento = res[4]
            random_string = res[5]

            if solo_oggi == True:
                solo_oggi = "<i>stai tracciando questo treno solo per oggi</i>"
            else:
                solo_oggi = "<i>il tracciamento del treno continuerà fino a quando non sarà annullato</i>"

            text = text + "\n➡️ 🚅<b>Treno {treno}</b>, {solo_oggi}, #tr{random}".format(treno=id_treno, solo_oggi=solo_oggi, id=request_id, random=random_string)

        bot.api.call("editMessageText",
            {"chat_id":chat.id, "message_id": message.message_id, "text": text, "parse_mode": "HTML", "reply_markup":
                '{"inline_keyboard":[[{"text":"🔙Torna indietro","callback_data":"home"}]]}'})


    if callback_q == "stats":
        data, success, error = API.orarioTreni.cercaStatistiche()
        messaggio = API.Messaggi.statistiche(data)
        bot.api.call("editMessageText", {"chat_id":chat.id, "message_id": message.message_id, "text": messaggio, "parse_mode":"HTML", "reply_markup":\
                    '{"inline_keyboard":[[{"text":"🔙Torna indietro","callback_data":"home"}]]}'})
