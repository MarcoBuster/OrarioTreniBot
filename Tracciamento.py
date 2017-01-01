import API
import Bot
from CONFIG import TOKEN
from Callback import *
from Inlinemode import *

import time

import sqlite3
conn = sqlite3.connect('OrarioTreni.db')
c = conn.cursor()
API.db.creaTutto()

import botogram
bot = botogram.create(TOKEN)

import logging
logger = logging.getLogger("tracciamento")

format = "%(asctime)s [%(levelname)s]: %(message)s"
level = logging.DEBUG
logging.basicConfig(format=format, level=level)

def tracciamento():
    c.execute('''SELECT * FROM tracciamento''')
    rows = c.fetchall()
    if not rows:
        logging.debug("Nessun treno da tracciare")
        return

    for res in rows:
        request_id = str(res[0])
        user_id = res[1]
        id_treno = res[2]
        solo_oggi = res[3]
        stazione_ultimo_rilevamento = res[4]
        random_string = res[5]

        data, success, error = API.orarioTreni.cercaTreno(str(id_treno))

        if data == None:
            continue

        stazione_attuale = data['stazioneUltimoRilevamento']
        if stazione_attuale == "--":
            stazione_attuale = data['origine']

        logging.info("Processando la richiesta numero {} del treno {} da {}".format(request_id, id_treno, user_id))

        if stazione_ultimo_rilevamento == data['destinazione'] and stazione_ultimo_rilevamento == data['stazioneUltimoRilevamento']:
            continue

        if stazione_ultimo_rilevamento == data['destinazione'] and stazione_attuale == data['origine']:
            c.execute('''UPDATE tracciamento SET stazione_ultimo_rilevamento=? WHERE request_id=?''', (stazione_attuale, request_id,))
            conn.commit()
            continue

        if stazione_attuale != stazione_ultimo_rilevamento:
            logging.info("Richiesta numero {}, il treno ha cambiato stazione da {} a {}".format(id_treno, stazione_ultimo_rilevamento, stazione_attuale))
            c.execute('''UPDATE tracciamento SET stazione_ultimo_rilevamento=? WHERE request_id=?''', (stazione_attuale, request_id,))
            text = (
                "🚦<b>Traccia treno</b> [BETA]"
                "\n🚅<b>Il treno {treno} ha cambiato stazione!</b>"
                "\n🚉{precedente} ➡️ 🚉<b>{successiva}</b>"
                "\n🕒<b>Ritardo</b>: {ritardo}m".format(treno=id_treno, precedente=stazione_ultimo_rilevamento, successiva=stazione_attuale, ritardo=data['ritardo'])
            )

            if stazione_attuale in str(data['fermate']):
                numero_fermata = -1
                for dict in data['fermate']:
                    numero_fermata = numero_fermata + 1
                    if stazione_attuale == dict['stazione']:
                        break

                try:
                    fermata = API.Messaggi.fermata(data, numero_fermata)
                    text = text + "\n\n" + fermata
                except Exception as e:
                    logger.error("Errore nella formattazione della fermata: {}".format(e))
                    text = text + "\n\n" + "<i>Errore sconosciuto. Contattare lo sviluppatore.</i> {}".format(e)

                text = text + "\n➡️Clicca qui per seguire tutto il tracciamento: #tracciamento{N}".format(N=random_string)

            else:
                text = text + "\n\n" + "<i>Il treno non ferma in questa fermata</i>"
                text = text + "\n\n➡️Clicca qui per seguire tutto il tracciamento: #tracciamento{N}".format(N=random_string)

            bot.api.call("sendMessage", {
                "chat_id": user_id, "text": text, "parse_mode": "HTML", "reply_markup":
                    '{"inline_keyboard": [[{"text": "❌ Disattiva le notifiche", "callback_data": "stop_tracciamentoT'+request_id+'"}]]}'
            })

        if stazione_attuale == data['destinazione']:
            if solo_oggi == True:
                c.execute('DELETE FROM tracciamento WHERE request_id=?', (request_id,))
                logging.info("Utente {} tracciamento cancellato {}".format(user_id, request_id))
                conn.commit()

                text = (
                    "🚦<b>Traccia treno</b> [BETA]"
                    "\n<b>Il treno {treno} è arrivato a destinazione con un ritardo di {ritardo} minuti!</b>"
                    "\n<i>Ho interrotto il tracciamento</i>".format(treno=id_treno, ritardo=data['ritardo'])
                )
                bot.api.call("sendMessage", {
                    "chat_id": user_id, "text": text, "parse_mode": "HTML"
                })

            if solo_oggi == False:
                c.execute('''UPDATE tracciamento SET stazione_ultimo_rilevamento=? WHERE request_id=?''', (data['destinazione'], request_id,))
                text = (
                    "🚦<b>Traccia treno</b> [BETA]"
                    "\n<b>Il treno {treno} è arrivato a destinazione</b> con un ritardo di <b>{ritardo} minuti</b>"
                    "\n<i>Domani riceverai ancora notifiche sul treno</i>".format(treno=id_treno, ritardo=data['ritardo'])
                )
                bot.api.call("sendMessage", {
                    "chat_id": user_id, "text": text, "parse_mode": "HTML", "reply_markup":
                        '{"inline_keyboard": [[{"text": "❌ Disattiva le notifiche", "callback_data": "stop_tracciamentoT'+request_id+'"}]]}'
                })


        conn.commit()

while True:
    try:
        tracciamento()
    except Exception as e:
        logging.exception(e)
    time.sleep(5)
