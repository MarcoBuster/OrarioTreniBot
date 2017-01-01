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
    query = str(update.callback_query.data)
    callback_id = update.callback_query.id

    if "stop_tracciamento" in query:
        query = query.split("T")
        request_id = query[1]

        c.execute('SELECT * FROM tracciamento WHERE request_id=?', (request_id,))
        rows = c.fetchall()

        for res in rows:
            id_treno = str(res[2])

        c.execute('DELETE FROM tracciamento WHERE request_id=?', (request_id,))
        conn.commit()

        text = (
            "🚦 <b>Traccia treno</b> [BETA]"
            "\n<code>Tracciamento del treno {treno} interrotto</code>".format(treno=id_treno)
        )

        bot.api.call("editMessageText", {
            "chat_id": chat.id, "message_id": message.message_id, "text": text, "parse_mode": "HTML"
        })

        text = (
            "🚦 <b>Traccia treno</b> [BETA]"
            "\n<b>Tracciamento</b> del treno {treno} <b>interrotto</b>"
            "\nPuoi sempre <b>annullare</b> questa operazione".format(treno=id_treno)
        )

        bot.api.call("sendMessage", {
            "chat_id": chat.id, "text": text, "parse_mode": "HTML", "reply_markup":
                '{"inline_keyboard": [[{"text": "🚅 Traccia il treno '+id_treno+'", "callback_data": "traccia@'+id_treno+'"}]]}'
        })
