import time
from datetime import datetime
import datetime

import urllib.request

import API
from Callback import Callback
from Inlinemode import Inline
from Callback.InlineCallback import INCallback

import botogram.objects.base
class CallbackQuery(botogram.objects.base.BaseObject):
    required = {
        "id": str,
        "from": botogram.User,
        "data": str,
    }
    optional = {
        "inline_message_id": str,
        "message": botogram.Message,
    }
    replace_keys = {
        "from": "sender"
    }
botogram.Update.optional["callback_query"] = CallbackQuery

class InlineQuery(botogram.objects.base.BaseObject):
    required = {
        "id": str,
        "from": botogram.User,
        "query": str,
    }
    optional = {
        "location": botogram.Location,
        "offest": str,
    }
    replace_keys = {
        "from": "sender"
    }
botogram.Update.optional["inline_query"] = InlineQuery

import botogram
bot = botogram.create("TOKEN")
bot.lang = "it"

import sqlite3
conn = sqlite3.connect('OrarioTreni.db')
c = conn.cursor()

try:
    c.execute('''CREATE TABLE stato(userid INTEGER, stato STRING, completato INTEGER)''')
except sqlite3.OperationalError: #table already exists
    pass

try:
    c.execute('''CREATE TABLE bannati(userid INTEGER)''')
except sqlite3.OperationalError: #table already exists
    pass

try:
    c.execute('''CREATE TABLE itinerario(userid INTEGER, stazione1 STRING, stazione2 STRING, orario STRING)''')
except sqlite3.OperationalError: #table already exists
    pass

conn.commit()

def process_callback(bot, chains, update):
    if update.callback_query.message == None:
        INCallback.process(bot, chains, update)
        return

    Callback.process(bot, chains, update)
bot.register_update_processor("callback_query", process_callback)

def process_inline(bot, chains, update):
    Inline.process(bot, chains, update)
bot.register_update_processor("inline_query", process_inline)

@bot.command("start")
def start(chat, message, args):

    if len(args) == 1:
        if args[0] == "inline":

            testo = (
                    "<b>Inline tutorial</b>"
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
                "sendMessage",{
                    "chat_id": chat.id, "text": testo, "parse_mode":"HTML",
                    "reply_markup":
                        '{"inline_keyboard":[[{"text":"🆗Torna all\'help", "callback_data":"help"}],[{"text":"🌐Prova ora!","switch_inline_query":" "}]]}'
                }
            )
            return

    API.db.creaTutto()
    success, error = API.db.updateState(chat.id, "home", 1)
    testo = ("<b>Benvenuto in @OrarioTreniBot!</b>"
            "\nCosa vuoi fare?")

    bot.api.call("sendMessage", {"chat_id": chat.id, "text":testo,"parse_mode":"HTML",\
        "reply_markup":'{"inline_keyboard":[[{"text":"🚄Cerca treno",'\
        '"callback_data": "treno"},{"text":"🚉Cerca stazione","callback_data": "stazione"}],'\
        '[{"text":"🛤Cerca itinerario","callback_data":"itinerario"}],[{"text":"❓Aiuto","callback_data":"help"},'
        '{"text":"🚧Altro","callback_data":"altro"},'\
        '{"text":"🌟Vota il bot","callback_data":"vota"}]]}'})

@bot.command("post")
def post(chat, message, args):
    """Post a message to all users"""
    if message.sender.id != 26170256: #Only admin command
        message.reply("This command it's only for the admin of the bot")
        return

    c.execute('''SELECT * FROM stato''')
    users_list = c.fetchall()

    message = " ".join(message.text.split(" ", 1)[1:])

    for res in users_list:
        try:
            bot.chat(res[0]).send(message)
            chat.send("Post sent to "+str(res[0]))
        except botogram.api.ChatUnavailableError:
            c.execute('DELETE FROM stato WHERE userid={}'.format(res[0]))
            chat.send("The user "+str(res[0])+" has blocked your bot, so I removed him from the database")
            conn.commit()
        except Exception as e:
            chat.send("*Unknow error :(*\n"+str(e))

    chat.send("<b>Done!</b>\nThe message has been delivered to all users") #Yeah
    conn.commit()

@bot.command("viewusers")
def viewusers(chat, message, args):
    """View the list and the count of users"""
    if message.sender.id != 26170256: #Only admin command
        message.reply("This command it's only for the admin of the bot")
        return

    c.execute('''SELECT * FROM stato''')
    users_list = c.fetchall()
    c.execute('''SELECT COUNT(*) AS count FROM stato;''')
    count = c.fetchone()[0]

    message = "<b>This is the list of users who executed /start</b>:\n"
    for res in users_list:
        message = message+str(res[0])+", "

    message = message + "\n<b>In total, there are "+str(count)+" users.</b>"
    chat.send(message)


@bot.process_message
def cerca_treno(chat, message):
    state, completato, success, error = API.db.getState(chat.id)
    if state != "treno1":
        return

    id_treno = str(message.text)
    data, success, error = API.orarioTreni.cercaTreno(id_treno)
    if success == False and error == 404:
        testo = ("<b>Errore</b>"
                "\n<i>404: Treno non trovato</i>"
                "\nIl numero di treno non è valido, digitane un altro oppure premi <b>Annulla</b>")
        bot.api.call("sendMessage", {"chat_id": chat.id, "text":testo,"parse_mode":"HTML",\
            "reply_markup":'{"inline_keyboard":[[{"text":"❌Annulla","callback_data":"home"}]]}'})
        return

    testo = API.Messaggi.treno1(data)
    callbackdata1 = "list@"+id_treno
    callbackdata2 = "agg@"+id_treno
    bot.api.call("sendMessage", {"chat_id": chat.id, "text":testo,"parse_mode":"HTML",
    "reply_markup":
        '{"inline_keyboard":[[{"text":"🚉Lista fermate","callback_data":"'+callbackdata1+'"},'
        '{"text":"🔄Aggiorna le informazioni","callback_data":"'+callbackdata2+'"}],'
        '[{"text":"🔙Torna indietro","callback_data":"home"}]]}'})
    API.db.updateState(chat.id, "nullstate", 0)

@bot.process_message
def cerca_stazione(chat, message):
    state, completato, success, error = API.db.getState(chat.id)

    if state != "stazione1":
        return

    stazione = message.text

    esiste, data = API.orarioTreni.stazione.check(stazione)
    if esiste == 0:
        testo = ("<b>Errore</b>"
                "\n<i>404: Stazione non trovata</i>"
                "\nNon è stata trovata nessuna stazione con quel nome")
        bot.api.call("sendMessage", {"chat_id": chat.id, "text":testo,"parse_mode":"HTML",\
            "reply_markup":'{"inline_keyboard":[[{"text":"❌Annulla","callback_data":"home"}]]}'})
        return

    API.db.updateState(chat.id, "nullstate", 0)

    callbackdata1 = "arv$"+stazione
    callbackdata2 = "part$"+stazione
    callbackdata3 = "pos$"+stazione

    testo, inline_keyboard = API.Messaggi.listaStazioni(data)
    if testo == 1:
        testo = "<b>Informazioni della stazione di </b>"+stazione
        bot.api.call("sendMessage", {"chat_id": chat.id, "text":testo,"parse_mode":"HTML",
            "reply_markup":
                '{"inline_keyboard":[[{"text":"Arrivi","callback_data":"'+callbackdata1+'"},{"text":"Partenze","callback_data":"'+callbackdata2+'"}],'\
                '[{"text":"📍Posizione","callback_data":"'+callbackdata3+'"}],[{"text":"🔙Torna indietro","callback_data":"home"}]]}'}
            )

    bot.api.call("sendMessage", {
    "chat_id":chat.id, "text":testo, "parse_mode":"HTML", "reply_markup":'{'
        '"inline_keyboard":'+inline_keyboard+'}'
    })

@bot.process_message
def sottoscrivi_itinerario_stazione1(chat, message): #CHIEDE NOME RICEVE USERNAME
    state, completato, success, error = API.db.getState(chat.id)

    if state != "itinerario1":
        conn.commit()
        return

    stazione = message.text
    esiste, data = API.orarioTreni.stazione.check(stazione)
    if esiste == False:
        testo = ("<b>🛤Cerca itinerario</b>\n❌La stazione selezionata non è <b>valida</b>")
        bot.api.call("sendMessage", {"chat_id":chat.id, "text":testo, "parse_mode":"HTML",
            "reply_markup":
                '{"inline_keyboard":[[{"text":"❌Annulla","callback_data":"home"}]]}'
                })
        return

    messaggio, inline_keyboard = API.Messaggi.listaStazioni(data)
    if messaggio != 1:
        bot.api.call("sendMessage", {"chat_id":chat.id, "text":messaggio, "parse_mode":"HTML",
            "reply_markup":
                '{"inline_keyboard":'+inline_keyboard+'}'
                })
        return

    API.db.creaTutto()
    c.execute('''DELETE FROM itinerario WHERE userid=?''',(chat.id,))
    c.execute('''INSERT INTO itinerario VALUES(?,?,?,?)''',(chat.id, "None", "None", "None",))
    c.execute('''UPDATE itinerario SET stazione1=? WHERE userid=?''',(message.text, chat.id,))
    conn.commit()
    API.db.updateState(chat.id, "itinerario1", 1)

    testo = ("<b>🛤Cerca itinerario</b>\n🚉Inserisci la <b>stazione di arrivo</b>")
    bot.api.call("sendMessage", {"chat_id":chat.id, "text":testo, "parse_mode":"HTML",
            "reply_markup":
                '{"inline_keyboard":[[{"text":"❌Annulla","callback_data":"home"}]]}'
    })


    success, error = API.db.updateState(chat.id, "itinerario2", 0)
    if success == False:
        API.Messaggi.erroreDatabase(message, error)
        return
    conn.commit()
    return


@bot.process_message
def sottoscrivi_itinerario_stazione2(chat, message): #CHIEDE NOME RICEVE USERNAME
    state, completato, success, error = API.db.getState(chat.id)
    conn.commit()

    if state != "itinerario2":
        conn.commit()
        return

    if completato == 0 and state == "itinerario2":
        c.execute('''UPDATE stato SET completato=1 WHERE userid=?''',(chat.id,))
        conn.commit()
        return

    if completato == 1 and state == "itinerario2":
        stazione = message.text
        esiste, data = API.orarioTreni.stazione.check(stazione)
        if esiste == False:
            testo = ("<b>🛤Cerca itinerario</b>\n❌La stazione selezionata non è <b>valida</b>")
            bot.api.call("sendMessage", {"chat_id":chat.id, "text":testo, "parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":[[{"text":"❌Annulla","callback_data":"home"}]]}'
                    })
            return

        API.db.creaTutto()
        c.execute('''UPDATE itinerario SET stazione2=? WHERE userid=?''',(message.text, chat.id))
        conn.commit()
        success, error = API.db.updateState(chat.id, "itinerario2", 2)

        messaggio, inline_keyboard = API.Messaggi.listaStazioni(data)
        if messaggio != 1:
            bot.api.call("sendMessage", {"chat_id":chat.id, "text":messaggio, "parse_mode":"HTML",
                "reply_markup":
                    '{"inline_keyboard":'+inline_keyboard+'}'
                    })
            return

        testo = ("<b>🛤Cerca itinerario</b>\nInserisci l'orario, in formato HH:MM."
                "\nEsempio: <code>22:05</code>, <code>09:15</code>, <code>13:53</code>"
                "\nSe vuoi cercare un itinerario per l'orario attuale, premi il pulsante 🕒Orario attuale")
        bot.api.call("sendMessage", {"chat_id": chat.id, "text":testo,"parse_mode":"HTML",
                "reply_markup":
                '{"inline_keyboard":[[{"text":"🕒Orario attuale","callback_data":"orarioNow"}],[{"text":"❌Annulla","callback_data":"home"}]]}'})
        success, error = API.db.updateState(chat.id, "itinerario3", 0)

        conn.commit()

@bot.process_message
def sottoscrivi_itinerario_orario(chat, message): #CHIEDE NOME RICEVE USERNAME
    if message.text == "Annulla":
        return
    state, completato, success, error = API.db.getState(chat.id)
    conn.commit()
    if state != "itinerario3": #or message.text == "Bot":
        conn.commit()
        return

    if completato == 0 and state == "itinerario3":
        c.execute('''UPDATE stato SET completato=1 WHERE userid=?''',(chat.id,))
        conn.commit()
        return

    if completato == 1 and state == "itinerario3":
        API.db.creaTutto()
        c.execute('''UPDATE itinerario SET orario=? WHERE userid=?''',(message.text, chat.id))
        conn.commit()
        success, error = API.db.updateState(chat.id, "bot3", 2)
        if success == False:
            API.Messaggi.erroreDatabase(message, error)
            return

    c.execute('''SELECT * FROM itinerario WHERE userid=?''',(chat.id,))
    info = c.fetchall()
    for res in info:
        st1 = res[1]
        st2 = res[2]
        ora = res[3]
        chatid = res[0]
    data, success, error = API.orarioTreni.cercaItinerario(st1, st2, ora)
    testo, inline_keyboard = API.Messaggi.itinerario(data)
    bot.api.call("sendMessage", {"chat_id":chat.id, "text":testo, "parse_mode":"HTML",
            "reply_markup":
                '{"inline_keyboard":'+inline_keyboard+'}'
                })
    API.db.updateState(chat.id, "nullstate", 0)

@bot.process_message
def nullstate(chat, message):
    state, completato, success, error = API.db.getState(chat.id)
    if state == "nullstate":
        return
    #Non fare assolutamente niente

@bot.command("feedback")
def feedback(chat, message, args):
    if len(args) == 0:
        message.reply("*Comando /feedback*"
                    "\nQuesto comando *invia* direttamente un *feedback* allo *sviluppatore* (@MarcoBuster)"
                    "\nUsalo liberamente per *segnalare problemi*, *chiedere assistenza* e *proporre nuove funzioni*"
                    "\n*Grazie per l'aiuto!*"
                        )
        return

    feedback = ' '.join(args)
    userid = str(message.sender.id)
    chatid = str(chat.id)
    if message.sender.username == None:
        username = "None"
    else:
        username = message.sender.username

    message.reply("Feedback inviato, *grazie mille*"
                "\nRicorda che le recensioni non sono uno spazio dove segnalare problemi!")
    bot.chat(26170256).send(
                        "<b>Hai ricevuto un feedback</b>"
                        "\n<b>Feedback</b>: {0}"
                        "\n<b>ID utente</b>: {1}"
                        "\n<b>Username utente</b>: @{2}"
                        "\n<b>ID chat</b>: {3}"
                        "\n<b>Tipo chat</b>: {4}".format(feedback, userid, username, chatid, chat.type)
    )

@bot.command("s")
def send(chat, message, args):
    if message.sender.id != 26170256:
       return

    chatid = args[0]
    text = "*Messaggio dallo sviluppatore!*\n"+' '.join(args[1:])+"\n\nSe vuoi rispondere fai */feedback risposta*"
    bot.chat(chatid).send(text)
    message.reply("Fatto!")

@bot.before_processing
def no_old_commands(chat, message):
    c = message.text
    if c == "/treno" or c == "/fermata" or c == "/itinerario" or c == "/traccia" or c == "/arrivi" or c == "/partenze" or c == "/help" or c == "/statistiche":
        message.reply("*Errore: Comando non trovato :(*"
                    "\n_Come? Che succede?_"
                    "\nIl bot è stato *completamente rivoluzionato*. Per cercare un treno non devi più usare questi comandi, ma delle comode *tastiere inline*"
                    "\nPer iniziare ad usare la *nuova versione* di questo bot, esegui il comando /start."
                    "\nTutti i *cambiamenti* e le fantastiche *novità* le trovi sul canale @OrarioTreni."
                    )
        return True

if __name__ == "__main__":
    bot.run()
