#coding: utf-8
"""
--------------------------------------------------------------------------------
GENERAL INFO
Orario treni: Il bot del vero pendolare!
Versione: 2.1
Telegram: @OrarioTreniBot
Supporto: @MarcoBuster
--------------------------------------------------------------------------------
"""
import botogram
import botogram.objects.base
#Grazie a Pietro Albini (botogram) per l'aiuto in CallBackQuery
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
import json
import urllib.request
from datetime import datetime
import datetime
import time
import sqlite3
import html

bot = botogram.create("TOKEN")

bot.about = "Con questo bot potrai tracciare il tuo treno comodamente da Telegram. "\
    "Per iniziare fai /start"
bot.owner = "@MarcoBuster"
bot.lang = "it"
conn = sqlite3.connect('utenti.db')
c = conn.cursor()
try:
    c.execute('''CREATE TABLE news(user_id INTEGER, iscritto INTEGER''')
except:
    pass
conn.commit()

#Comando /news
#Visualizza i messaggi per l'iscrizione alle news e altre informazioni
#Utilizzo: /news
@bot.command("news")
def news(chat, message, args):
    message.reply("*Orario treni NEWS!*\n" \
        "Iscriviti alle notizie per avere notifiche instantanee su *scioperi*, *avvisi*" \
        "e molto altro riguardo le ferrovie in Italia!")
    message.reply("*Come iscriversi?*\nIscriversi è molto semplice:" \
        "basta scrivere /newson." \
        "Puoi disiscriverti quando vuoi facendo /newsoff")

#Comando /newson
#Iscrizione alle news
#Utilizzo: /newson
@bot.command("newson")
def newson(chat, message):
    try:
        c.execute('''DELETE FROM news WHERE user_id =?''',(message.sender.id,))
        c.execute('''INSERT INTO news(user_id, iscritto) VALUES(?, ?)''',(message.chat.id, 1))
        conn.commit()
        message.reply("*Fatto!*\nOra sei iscritto! Per disiscriverti fai" \
            "/newsoff")
        bot.chat(-1001057273480).send("#Comando #newson"\
            "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
            "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
            "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
            "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y")),syntax="html")
    except Exception as e:
        message.reply("*Errore*\nQualcosa è andato storto."\
            "\nContatta lo sviluppatore @MarcoBuster e inviagli questo messaggio d'errore: "+\
            str(e))
        bot.chat(-1001057273480).send("#Comando #newson"\
            "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
            "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
            "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
            "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y"))+\
            "\n<b>Altro</b>: "+"<b>Errore</b>: "+str(e),syntax="html")
        return

#Comando /viewnews
#Visualizza la lista delle persone iscritte alle news
#UTilizzo: /viewnews [SOLO AMMINISTRATORI]
@bot.command("viewnews")
def viewnews(chat, message):
    if message.sender.id != 26170256:
        message.reply("`ADMIN ONLY`\n*Non sei autorizzato ad eseguire questo comando."\
        "Esegui il comando /help per info sui comandi che puoi usare.*")
        return
    try:
        c.execute('''SELECT * from news''')
        rows = c.fetchall()
        for row in rows:
            chat.send(str(row))
    except Exception as e:
        message.reply("*Errore*: "+str(e))
        pass
    conn.commit()

#Comando /newsoff
#Discrizione alle news
#Utilizzo: /newsoff
@bot.command("newsoff")
def newsoff(chat, message):
    try:
        c.execute('''DELETE FROM news where user_id=?''',(message.chat.id,))
        message.reply("*Disiscritto*\nDisiscrizione completata!\n"\
            "Per iscriverti fai /newson")
        bot.chat(-1001057273480).send("#Comando #newsoff"\
            "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
            "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
            "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
            "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y")),syntax="html")
    except Exception as e:
        message.reply("*Errore*\nContatta @MarcoBuster per supporto"\
            "Codice di errore da inoltrare: "+str(e))
        bot.chat(-1001057273480).send("#Comando #newsoff"\
            "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
            "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
            "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
            "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y"))+\
            "\n<b>Altro</b>: "+"<b>Errore</b>: "+str(e),syntax="html")
    conn.commit()

#Comando /post
#Posta una news
#Utiizzo: /post <messaggio> [SOLO AMMINISTRATORE]
@bot.command("post")
def post(chat, message, args):
    if message.sender.id != 26170256:
        message.reply("`ADMIN ONLY`\n*Non sei autorizzato ad eseguire questo comando."\
        "Esegui il comando /help per info sui comandi che puoi usare.*")
        return
    messaggio_news = " ".join(message.text.split(" ", 1)[1:])
    message.reply("*Ecco il messaggio che stai per inviare*: "+str(messaggio_news)+"\n_Confermare?_")
    c.execute('''SELECT user_id FROM news''')
    lista_utenti= c.fetchall()
    message.reply("Lista destinatari"+", ".join(str(res[0]) for res in lista_utenti))
    for res in lista_utenti:
        try:
            bot.chat(res[0]).send(messaggio_news)
        except Exception as e:
            message.reply("*Errore* "+str(e))
    conn.commit()
#Comando: /info
#Visualizza le informazioni sul bot
#Utilizzo: /info
@bot.command("info")
def infocommand(chat, message, args):
    help(chat, message, args)
#Comando: /help
#Visualizza le informazioni sul bot
#Utilizzo: /help
@bot.command("help")
def helpcommand(chat, message, args):
    message.reply("*Orario treni*\n_Con questo bot potrai cercare un treno, una fermata "\
        "di un treno, una stazione, un itinerario e averne le informazioni principali._\n"\
        "*Comando /treno*\nPer cercare un treno dal numero fare questo comando:\n"\
        "`/treno numero-treno`.\n*Suggerimento*\nRicorda che puoi cercare un treno "\
        "anche scrivendo in chat il numero di treno, senza necessariamente "\
        "scrivere `/treno` prima.\n"\
        "*Comando /fermata*\nPer cercare le informazioni di un treno "\
        "rispetto a una stazione (_binario, ritardo, ecc..._) fare:\n"\
        "`/fermata numero-treno numero-fermata`\n_In numero fermata inserire "\
        "il numero che trovate facendo_: \n`/fermata numero-treno lista`\n"\
        "*Comandi /arrivi e /partenze*\nPer cercare il tabellone arrivi o partenze "\
        "di una stazione fare:\n`/arrivi nome-stazione` o `/partenze nome-stazione`\n"\
        "*Suggerimento*\nRicorda che puoi cercare le *partenze* di una stazione "\
        "semplicemente scrivendo il nome della stazione in chat\n"\
        "*Comando /itinerario*\nPer cercare un treno che ferma tra due stazioni,"\
        " fare:\n`/itinerario stazione1 stazione2`\n*Solo in questo comando*, "\
        "i nomi delle stazioni vanno inserite con il punto al posto dello spazio.\n"\
        "Per esempio `MILANO CENTRALE` diventa `MILANO.CENTRALE`\n"\
        "*Comando /traccia*\nPer tracciare un treno e essere notificati "\
        "del cambiamento della stazione (di ultimo rilevamento) "\
        "o di grave accumulo di ritardo, fare: "\
        "`/traccia numero-treno minuti-massimi`\n"\
        "Il campo minuti massimi è facoltativo, se non impostato sarà impostato a 20m\n"
        "*Votaci!*\n[Vota il bot cliccando qui](https://telegram.me/storebot?start=OrarioTreniBot)"\
        "\n*Grazie per il supporto!*\n"\
        "[Canale con notizie, aggiornamenti e molto altro sul bot qui](https://telegram.me/OrarioTreni)"\
        "\n_Aiuto, domande, questioni tecniche:_ @MarcoBuster")
    bot.chat(-1001057273480).send("#Comando #help"\
        "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
        "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
        "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
        "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y")),syntax="html")
#Comando: /treno
#Cerca un treno e restituisce le informazioni principali
#Utilizzo: /treno <numero di treno>
@bot.command("treno")
def treno(chat, message, args):
    try:
        id_treno = (args[0])
    except Exception as e:
        message.reply("*Errore*\nNon hai inviato nessun numero di treno.\n"\
            "Scrivi qui direttamente in chat il numero di treno, oppure fai `/treno numero-treno`")
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/"\
        "viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
    response = urllib.request.urlopen(content)
    id_stazione = (str(response.read()).split("-")[-1][:-3])
    try:
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/"\
            "viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
    except:
        message.reply("*Errore, non trovato (404)*:\n"\
            "_That’s an error. That’s all we know:_\n"\
            "-Il numero di treno inserito non è valido;\n"\
            "-Non stai utilizzando il comando correttamente.\n"
            "Usa /help per il tutorial del comando")
        bot.chat(-1001057273480).send("#Comando #treno"\
            "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
            "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
            "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
            "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y"))+\
            "\n<b>Altro</b>: "+"<b>Errore</b>: treno non trovato",syntax="html")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    orarioPartenza = datetime.datetime.fromtimestamp(data['orarioPartenza'] / 1000).strftime('%H:%M')
    orarioArrivo = datetime.datetime.fromtimestamp(data['orarioArrivo'] / 1000).strftime('%H:%M')
    try:
        oraUltimoRilevamento = datetime.datetime.fromtimestamp(data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
    except:
        oraUltimoRilevamento = "Il treno non è ancora partito"
    testo=("_Informazioni sul treno _"+"_"+id_treno+"_"+\
        "\n*Stazione di partenza*: "+data['origineZero']+" ("+(orarioPartenza)+")"+\
        "\n*Stazione di arrivo*: "+data['destinazioneZero']+" ("+(orarioArrivo)+")"+\
        "\n*Ritardo*: "+str(data['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+\
    data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+\
        ")\n*Premi sul tasto in basso per aggiornare le informazioni del treno*")
    #Invia il messaggio utilizzando bot.api.call
    bot.api.call("sendMessage", {"chat_id": chat.id, "text":testo,"parse_mode":"Markdown",\
        "reply_markup":'{"inline_keyboard":[[{"text":"Aggiorna le informazioni sul treno",'\
        '"callback_data": "'+str(id_treno)+'"},{"text":"Traccia il treno","callback_data": "'+\
        str("t"+id_treno)+'"}]]}'})
    bot.chat(-1001057273480).send("#Comando #treno"\
        "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
        "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
        "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
        "\n<b>Treno</b>: "+id_treno+\
        "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y")),syntax="html")

    #Processando la callback
def process_callback(bot, chains, update):
    message = update.callback_query.message
    chat = message.chat
    callback_q = str(update.callback_query.data)
    if callback_q.find('t') >= 0: #Il bot deve tracciare il treno
        id_treno = str(callback_q).replace("t","") #Semplicemente toglie la "t" al numero di treno in modo da essere utilizzabile
        stop = 1200 #Il tracciamento si spegnerà dopo 1200 secondi
        #Cerca il treno
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/"\
            "viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        try:
            info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/"\
                "viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
            response = urllib.request.urlopen(info)
        except:
            message.reply("*Errore, non trovato (404)*:\n_That’s an error. "\
                "That’s all we know:_\n-Il numero di treno inserito non è valido;"\
                "\n-Non stai utilizzando il comando correttamente. "\
                "Usa /info per il tutorial del comando")
            tracciamento = False
            return #Se il treno non esiste, return
        tracciamento = True
        content = response.read()
        data = json.loads(content.decode("utf8"))
        orarioPartenza = datetime.datetime.fromtimestamp(data['orarioPartenza']
        / 1000).strftime('%H:%M')
        orarioArrivo = datetime.datetime.fromtimestamp(data['orarioArrivo']
        / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento = datetime.datetime.fromtimestamp(
            data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento = "Il treno non è ancora partito"
        ritardo = data['ritardo']
        stazioneUltimoRilevamento = data['stazioneUltimoRilevamento']
        if tracciamento is True and data['destinazioneZero'] == stazioneUltimoRilevamento:
            message.reply("*Errore*\nQuesto treno è già arrivato a destinazione!")
            tracciamento = False
            return
        testo=("_Informazioni sul treno _"+"_"+id_treno+"_"+"\n*Stazione di partenza*: "\
            +data['origineZero']+" ("+(orarioPartenza)+")""\n*Stazione di arrivo*: "+\
            data['destinazioneZero']+" ("+(orarioArrivo)+")"+"\n*Ritardo*: "+\
            str(data['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+\
            data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+\
            ")\n*Sto tracciando il treno*")
        try:
            bot.api.call("editMessageText", {"chat_id": chat.id,
                "message_id": message.message_id, "text":str(testo),
                "parse_mode":"Markdown","reply_markup":
                '{"inline_keyboard":[[{"text":"Aggiorna le informazioni sul treno",\
                "callback_data": "'+str(id_treno)+'"}]]}'})
        except:
            pass

        while tracciamento == True and stop > 0 and data['destinazioneZero'] != stazioneUltimoRilevamento:
            info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy"\
            "/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
            response = urllib.request.urlopen(info)
            content = response.read()
            data = json.loads(content.decode("utf8"))
            ritardo2 = data['ritardo']
            stop = stop-1
            stazioneUltimoRilevamento2 = data['stazioneUltimoRilevamento']
            differenzaritardo = ritardo2 - ritardo
            if stazioneUltimoRilevamento != stazioneUltimoRilevamento2: #Se le stazioni sono diverse...
                try:
                    oraUltimoRilevamento2 = datetime.datetime.fromtimestamp(
                    data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
                except:
                    oraUltimoRilevamento2 = "Il treno non è ancora partito"
                message.reply("*Traccia treno*\n_Il treno "+\
                    id_treno+" ha cambiato stazione!_\n*Stazione precedente*: "+\
                    stazioneUltimoRilevamento+" ("+oraUltimoRilevamento+")"+\
                    "\n*Stazione corrente*: "+stazioneUltimoRilevamento2+" ("+\
                    oraUltimoRilevamento2+")"+"\n*Ritardo: *"+str(ritardo2)+"m")
                stazioneUltimoRilevamento = data['stazioneUltimoRilevamento']
                oraUltimoRilevamento = data['oraUltimoRilevamento']
            if differenzaritardo == 10 or differenzaritardo > 10: #Se il treno ha subito un grave ritardo...
                message.reply("*Traccia treno*\n_Il treno "+id_treno+\
                    " ha accumulato ritardo!_\n*Ritardo precedente*: "+\
                    str(ritardo)+"m\n*Ritardo attuale:* "+str(ritardo2)+"m")
                ritardo = data['ritardo']
            if stop == 1: #Quando il tracciamento è finito...
                message.reply("*Traccia treno*\nFine del tracciamento del treno "+id_treno)
            time.sleep(1)
            continue
            if stop == 0:
                return #Stop
    else: #Il bot deve solo aggiornare il messaggio
        #Aggiornamento delle informazioni...
        id_treno = str(update.callback_query.data)
        callback_id = update.callback_query.id
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/"\
        "viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/"\
        "viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data = json.loads(content.decode("utf8"))
        orarioPartenza = datetime.datetime.fromtimestamp(
            data['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo = datetime.datetime.fromtimestamp(
            data['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento = datetime.datetime.fromtimestamp(
                data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento = "Il treno non è ancora partito"
            pass
        testo=("_Informazioni sul treno _"+"_"+id_treno+"_"+\
            "\n*Stazione di partenza*: "+data['origineZero']+" ("+\
            (orarioPartenza)+")""\n*Stazione di arrivo*: "+\
            data['destinazioneZero']+" ("+(orarioArrivo)+")"+\
            "\n*Ritardo*: "+str(data['ritardo'])+"m"+\
            "\n*Stazione ultimo rilevamento*: "+\
            data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+\
            ")\n*Premi sul tasto in basso per aggiornare le informazioni del treno*")
        try:
            #Edita il messaggio senza il tastino "TRACCIA TRENO"
            bot.api.call("editMessageText", {"chat_id": chat.id, "message_id":
            message.message_id, "text":str(testo),"parse_mode":"Markdown",
            "reply_markup":'{"inline_keyboard":'\
            '[[{"text":"Aggiorna le informazioni sul treno","callback_data": "'+str(id_treno)+'"}]]}'})
        except Exception as e:
            print(e)
        bot.api.call("answerCallbackQuery", {"callback_query_id": str(callback_id),\
         "text": "Messaggio aggiornato", "show_alert":False}) #Avviso sopra lo schermo
        return
bot.register_update_processor("callback_query", process_callback)

#INLINE MODE
def process_inline(bot, chains, update):
    #Inline mode
    user = update.inline_query.sender
    testo = update.inline_query.query
    if testo != None:
        try:
            int(testo)
        except:
            #Il numero di treno inserito non è un numero, quindi come può essere un numero di treno valido? return immediato...
            bot.api.call("answerInlineQuery", {"inline_query_id":update.inline_query.id,
                "cache_time":0, "results":'[{"type":"article","id":"2","title":"ERRORE",'\
                '"description":"Attenzione! Il numero di treno inserito non è un numero di treno",'\
                '"input_message_content":{"message_text":"*Errore*\n'\
                '_Non ho digitato un numero di treno. _\n'\
                'Per utilizzare questo bot devo scrivere, in qualsiasi chat,'\
                ' `@OrarioTreniBot numero di treno`","parse_mode":"Markdown"}}]'})
            return
        id_treno = str(testo)
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/"\
            "viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        try:
            info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/"\
                "viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
            response = urllib.request.urlopen(info)
        except:
            #Il treno non esiste
            bot.api.call("answerInlineQuery", {"inline_query_id":update.inline_query.id, \
                "cache_time":0, "results":'[{"type":"article","id":"2",'\
                '"title":"ERRORE","description":"Attenzione! Numero di treno'\
                ' inesistente!","input_message_content":{"message_text":'\
                '"*Errore*\n_Il treno non esiste_\nPer utilizzare questo bot'\
                ' devo scrivere, in qualsiasi chat, `@OrarioTreniBot numero di treno`"'\
                ',"parse_mode":"Markdown"}}]'})
            return
        content = response.read()
        data = json.loads(content.decode("utf8"))
        orarioPartenza = datetime.datetime.fromtimestamp(data['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo = datetime.datetime.fromtimestamp(data['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento = datetime.datetime.fromtimestamp(data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento = "Il treno non è ancora partito"
        testo=("_Informazioni sul treno _"+"_"+id_treno+"_"+\
            "\n*Stazione di partenza*: "+data['origineZero']+\
            " ("+(orarioPartenza)+")""\n*Stazione di arrivo*: "+\
            data['destinazioneZero']+" ("+(orarioArrivo)+")"+\
            "\n*Ritardo*: "+str(data['ritardo'])+"m"+\
            "\n*Stazione ultimo rilevamento*: "+data['stazioneUltimoRilevamento']+\
            " ("+(oraUltimoRilevamento)+")")
        descrizione = "Cerca il treno "+id_treno
        #Mostra le informazioni sul treno
        bot.api.call("answerInlineQuery", {"inline_query_id":update.inline_query.id,
            "cache_time":0, "switch_pm_text":"Vai al bot per altre funzioni",
            "results":'[{"type":"article","id":"1",'\
            '"title":"Cerca treno","description":'\
            '"'+str(descrizione)+'","input_message_content":'\
            '{"message_text":"'+testo+'","parse_mode":"Markdown"}}]'})
    if testo == None:
        bot.api.call("answerInlineQuery", {"inline_query_id":\
            update.inline_query.id, "cache_time":0, "results":\
            '[{"type":"article","id":"2","title":"ERRORE","description":'\
            '"Attenzione! Non hai scritto nessun numero di treno!",'\
            '"input_message_content":{"message_text":"*Errore*\n'\
            '_Non ho digitato nessun numero di treno. _\n'\
            'Per utilizzare questo bot devo scrivere, in qualsiasi chat, '\
            '`@OrarioTreniBot numero di treno`","parse_mode":"Markdown"}}]'})
bot.register_update_processor("inline_query", process_inline)

#Comando: /fermata
#Visualizza le informazioni di un treno rispetto a una fermata specifica
#Utilizzo: /fermata <numero di treno> <numero di fermata>:lista
@bot.command("fermata")
def fermata(chat, message, args):
    if len(args) < 1:
        message.reply("*Errore*\nPer utilizzare questo comando devi fare:"\
        "\n`/fermata numero-di-treno numero-di-fermata`"\
        "\nPer avere il numero fermata fai: `/fermata numero-treno`")
        return
    if len(args) == 1:
        staz = "lista"
    if len(args) == 2:
        staz = args[1]
    id_treno= (args[0])
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/"\
        "viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
    response = urllib.request.urlopen(content)
    id_stazione = (str(response.read()).split("-")[-1][:-3])
    try:
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/"\
            "viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
    except:
        message.reply("_Errore_\n*Non ho trovato nulla. Forse perché...*:"\
            "\n-Il numero di treno inserito non è valido;\n"\
            "-Il treno non è ancora partito;\n"\
            "-Non stai utilizzando il comando correttamente. "\
            "Usa /info per il tutorial del comando")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    #Codice sotto da migliorare
    try:
        s = int(staz)
    except:
        pass
    try:
        sOrarioArrivoP = str(
            datetime.datetime.fromtimestamp(data['fermate'][s]['arrivo_teorico'] / 1000).strftime('%H:%M'))
    except:
        sOrarioArrivoP = "--"
    try:
        sOrarioArrivoR = str(
            datetime.datetime.fromtimestamp(data['fermate'][s]['arrivoReale'] / 1000).strftime('%H:%M'))
    except:
        sOrarioArrivoR = "--"
    try:
        sOrarioPartenzaP = str(
            datetime.datetime.fromtimestamp(data['fermate'][s]['partenza_teorica'] / 1000).strftime('%H:%M'))
    except:
        sOrarioPartenzaP = "--"
    try:
        sOrarioPartenzaR = str(
            datetime.datetime.fromtimestamp(data['fermate'][s]['partenzaReale'] / 1000).strftime('%H:%M'))
    except:
        sOrarioPartenzaR = "--"
    try:
        ritardoArrivo = str(
            data['fermate'][s]['ritardoArrivo'])
    except:
        ritardoArrivo = "--"
    try:
        ritardoPartenza = str(
            data['fermate'][s]['ritardoPartenza'])
    except:
        ritardoPartenza = "--"
    if (staz == "lista"):
        message.reply("*Lista stazioni*\n"\
            "_Ecco la lista delle fermata, per vedere le "\
            "informazioni di una fermata in dettaglio fare_\n "\
            "`/fermata "+id_treno+" numero fermata`\n"\
            "_Il numero fermata è il numeretto, nella lista seguente, prima del nome della stazione_")
        b=""
        for k in range(0,51):
            try:
                a=str("["+str(k)+"] "+data['fermate'][k]['stazione'])
            except:
                break
            b=b+a
            b+="\n"
        message.reply(b,syntax="plain")
        bot.chat(-1001057273480).send("#Comando #fermata"\
            "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
            "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
            "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
            "\n<b>Treno</b>: "+id_treno+\
            "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y"))+\
            "\n<b>Altro</b>: Lista delle stazioni",syntax="html")
        return
    else:
        binario = data['fermate'][s]['binarioProgrammatoArrivoDescrizione']
        if binario=="None":
            binario = "Errore di Trenitalia/Trenord."
        else:
            binario = str(binario)
        message.reply("*Informazioni di un treno rispetto a una fermata specifica*"\
            ":_ "+data['fermate'][s]['stazione']+"_\n*Arrivo programmato: *"\
            +sOrarioArrivoP+"\n*Arrivo reale: *"+sOrarioArrivoR+\
            "\n*Ritardo arrivo: *"+ritardoArrivo+"m\n*Partenza programmata: *"\
            +sOrarioPartenzaP+"\n*Partenza reale: *"+sOrarioPartenzaR+\
            "\n*Ritardo partenza: *"+ritardoPartenza+"m\n*Binario: *"+binario)
    bot.chat(-1001057273480).send("#Comando #fermata"\
        "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
        "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
        "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
        "\n<b>Treno</b>: "+id_treno+\
        "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y")),syntax="html")

#Comando: /fermate
#Visualizza le informazioni di un treno rispetto a una fermata specifica
#REDIRECT COMANDO /FERMATA
#Utilizzo: /fermate <numero di treno> <numero di fermata>:lista
@bot.command("fermate")
def fermate(chat, message, args):
    fermata(chat, message, args)

#Comando: /statistiche
#Visualizza curiose statistiche sui treni italiani in tempo reale
#Utilizzo: /statistiche
@bot.command("statistiche")
def statistiche(chat, message, args):
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/statistiche/random"
    response = urllib.request.urlopen(content)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    message.reply("_Statistiche dei treni italiani in tempo reale_"+\
        "\n*Treni circolanti*: "+str(data['treniCircolanti'])+"\n*Treni totali di oggi*: "+str(data['treniGiorno']))
    bot.chat(-1001057273480).send("#Comando #statistiche"\
        "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
        "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
        "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
        "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y")))

#Comando: /arrivi
#Visualizza gli arrivi di una stazione
#Utilizzo: /arrivi <nome stazione>
@bot.command("arrivi")
def arrivi(chat, message, args):
    if len(args) == 0:
        message.reply("*Errore*\n_Nessuna stazione inserita_"\
            "\nPer cercare una stazione scrivere il nome della stazione dopo il comando. "\
            "Esempio: `/arrivi Milano Centrale`")
        return
    stazione = (args)
    stazione = ' '.join(stazione)
    stazione = stazione.replace(" ","%20").lstrip('%20')
    try:
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione
        response = urllib.request.urlopen(content)
    except:
        message.reply("*Errore*\n_Non ho trovato nessuna stazione con quel nome."\
        "_Sei sicuro di stare usando il comando correttamente?"\
            "\nEsempio di utilizzo: `/partenze Milano Centrale`")
        pass
        return
    content = response.read()
    data = json.loads(content.decode("utf8"))
    id_stazione = (str(data[0]['id']))
    datatempo = (datetime.datetime.now().strftime('%a %b %d %Y %H:%M:%S GMT+0100'))
    datatempo = datatempo.replace(" ","%20")
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/arrivi/"+id_stazione+"/"+datatempo
    response = urllib.request.urlopen(content)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    messaggio = []
    for k in range(0,5):
        try:
            sOrarioArrivoP = datetime.datetime.fromtimestamp(data[k]['orarioArrivo'] / 1000).strftime('%H:%M')
            binario = data[k]['binarioProgrammatoArrivoDescrizione']
            if (binario=="None"):
                binario = "Errore di Trenitalia/Trenord."
            stazione = stazione.replace("%20"," ")
            messaggio.append("_Treno "+str(data[k]['numeroTreno'])+\
                "_\n*Provenienza*: "+data[k]['origine']+\
                "\n*Orario di arrivo*: "+str(sOrarioArrivoP)+\
                "\n*Ritardo*: "+str(data[k]['ritardo'])+\
                "m\n*Binario*: "+str(binario))
        except:
            pass
    message.reply("*Arrivi della stazione di "+str(stazione)+"*\n"+"\n\n".join(messaggio))
    bot.chat(-1001057273480).send("#Comando #arrivi"\
        "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
        "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
        "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
        "\n<b>Stazione</b>: "+str(stazione)+\
        "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y")),syntax="html")

#Comando: /partenze
#Visualizza le partenze di una stazione
#Utilizzo: /partenze <nome stazione>
@bot.command("partenze")
def partenze(chat, message, args):
    if len(args) == 0:
        message.reply("*Errore*\n_Nessuna stazione inserita_\n"\
            "Per cercare una stazione scrivere il nome "\
            "della stazione dopo il comando. Esempio: `/partenze Milano Centrale`")
        return
    stazione = (args)
    stazione = ' '.join(stazione)
    stazione = stazione.replace(" ","%20").lstrip('%20')
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione
    response = urllib.request.urlopen(content)
    content = response.read()
    if (content ==b'[]') and chat.type == "private":
        message.reply("*Errore*"\
            "\n_Non ho trovato nessuna stazione con quel nome._"\
            "\nSei sicuro di stare usando il comando correttamente?"\
            "\nEsempio di utilizzo: `/partenze Milano Centrale`")
        return
    data = json.loads(content.decode("utf8"))
    id_stazione = (str(data[0]['id']))
    datatempo = (datetime.datetime.now().strftime('%a %b %d %Y %H:%M:%S GMT+0100'))
    datatempo = datatempo.replace(" ","%20")
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/partenze/"+id_stazione+"/"+datatempo
    response = urllib.request.urlopen(content)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    messaggio = []
    for k in range(0,5):
        try:
            sOrarioPartenzaP = datetime.datetime.fromtimestamp(data[k]['orarioPartenza'] / 1000).strftime('%H:%M')
            binario = data[k]['binarioProgrammatoPartenzaDescrizione']
            if (binario=="None"):
                binario = "Errore di Trenitalia/Trenord."
            stazione = stazione.replace("%20"," ")
            messaggio.append("_Treno "+str(data[k]['numeroTreno'])+\
                "_\n*Destinazione*: "+data[k]['destinazione']+\
                "\n*Orario di partenza*: "+str(sOrarioPartenzaP)+\
                "\n*Ritardo*: "+str(data[k]['ritardo'])+\
                "m\n*Binario*: "+str(binario))
        except:
            pass
    message.reply("*Partenze della stazione di "+str(stazione)+"*\n"+"\n\n".join(messaggio))
    bot.chat(-1001057273480).send("#Comando #partenze"\
        "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
        "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
        "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
        "\n<b>Stazione</b>: "+str(stazione)+\
        "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y")),syntax="html")

#Comando: /itinerario
#Cerca un itinerario tra due stazioni
#Utilizzo: /itinerario <stazione di partenza> <stazione di arrivo>
@bot.command("itinerario")
def itinerario(chat, message, args):
    if len(args) == 0:
        message.reply("*Errore*\nPer utilizzare questo comando"\
            " devi scrivere: `/itinerario stazione-1 stazione-2 (orario)`\n"\
            "Ricorda che se i nomi delle stazioni hanno degli spazi, devono"\
            " essere sostiuti con un punto.\n Per esempio `MILANO CENTRALE`"\
            " diventa `MILANO.CENTRALE`")
        return
    stazione1 = str(args[0])
    stazione1 = stazione1.replace(".","%20")
    stazione2 = str(args[1])
    stazione2 = stazione2.replace(".","%20")
    if len(args)>= 3:
        tempogrezzo = args[2]
        tempogrezzo = tempogrezzo + datetime.datetime.now().strftime(' %Y-%m-%d')
        tempo = datetime.datetime.strptime(tempogrezzo, '%H:%M %Y-%m-%d')
        tempo = tempo.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        tempo = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    #Cerca ID stazione 1
    try:
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione1
        response = urllib.request.urlopen(content)
    except:
        message.reply("*Errore: stazione di partenza non valida*"\
            "\nNon ho trovato nessuna stazione con quel nome."\
            "_Sei sicuro di stare usando il comando correttamente?"\
            "\nRicorda che se c'è uno spazio nel nome della stazione "\
            "(come Milano Centrale) devi mettere un punto dopo lo spazio (ovvero Milano.Centrale)_")
        return
    content = response.read()
    data = json.loads(content.decode("utf8"))
    id_stazione1 = (str(data[0]['id'])).split("S")[-1][:9].split("N")[-1][:9]
    #Cerca ID stazione 2
    try:
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione2
        response = urllib.request.urlopen(content)
    except:
        message.reply("*Errore: stazione di arrivo non valida*"\
            "\nNon ho trovato nessuna stazione con quel nome."\
            "_Sei sicuro di stare usando il comando correttamente?"\
            "\nRicorda che se c'è uno spazio nel nome della stazione "\
            "(come Milano Centrale) devi mettere un punto dopo lo spazio (ovvero Milano.Centrale)_")
        return
    content = response.read()
    data = json.loads(content.decode("utf8"))
    id_stazione2 = (str(data[0]['id'])).split("S")[-1][:9].split("N")[-1][:9]
    #Cerca itinerario
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/soluzioniViaggioNew/"+id_stazione1+"/"+id_stazione2+"/"+tempo
    response = urllib.request.urlopen(content)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    #Meccanismo per trovare quanti cambi ci sono
    m="*Ricerca di un treno per itinerario* ("+data['origine']+" ~ "+data['destinazione']+")\n*Durata del tragitto*: "+data['soluzioni'][0]['durata']+"\n\n"
    for dict in data['soluzioni'][0]['vehicles']:
        id_treno = str(dict['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data2 = json.loads(content.decode("utf8"))
        orarioPartenza = datetime.datetime.fromtimestamp(data2['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo = datetime.datetime.fromtimestamp(data2['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento = datetime.datetime.fromtimestamp(data2['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento = "Il treno non è ancora partito"
            pass
        m = m+"*Treno trovato*: "+dict['numeroTreno']+\
            "\n*Provienienza*: "+data2['origineZero']+" ("+str(orarioPartenza)+\
            ")\n*Destinazione*: "+data2['destinazioneZero']+" ("+\
            str(orarioArrivo)+")\n*Parte da "+dict['origine']+\
            "* alle "+dict['orarioPartenza'].split("T")[-1][:9].replace(":00","")+\
            "\n*Arriva a "+dict['destinazione']+"* alle "+\
            dict['orarioArrivo'].split("T")[-1][:9].replace(":00","")+\
            "\n*Ritardo*: "+str(data2['ritardo'])+"m"+\
            "\n*Stazione ultimo rilevamento*: "+\
            data2['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento)+")"+"\n\n"
    message.reply(m)
    bot.chat(-1001057273480).send("#Comando #itinerario"\
        "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
        "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
        "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
        "\n<b>Stazione di partenza</b>: "+str(data['origine'])+\
        "\n<b>Stazione di arrivo</b>: "+str(data['destinazione'])+\
        "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y")),syntax="html")

@bot.process_message
def ricerca_veloce(shared, chat, message):
    isTreno = None
    isStazione = None
    try:
        int(message.text)
        isTreno = True
    except:
        isTreno = False
        isStazione = True
    if message.text == None:
        return
    if isTreno == True:
        id_treno = str(message.text)
        try:
            treno(chat, message, str(message.text).split(" "))
        except Exception as e:
            pass
    if isStazione == True and len(message.text) > 5:
        stazione = str(message.text)
        partenze(chat, message, str(message.text).split(" "))

#Comando /traccia
#Traccia il treno con notifiche in tempo reale sul suo andamento
#Utilizzo: /traccia <numero di treno> [minuti massimi]
@bot.command("traccia")
def tracciaCOMMAND(chat, message, args):
    if len(args) == 0:
        message.reply("*Errore*\n_Sintassi del comando errata_\nPer tracciare un treno digita `/traccia numero-treno minuti-massimi`\nNon è obbligatorio inserire i minuti dopo i quali il tracciamento si conclude. Se non specificato dopo 10m il bot smetterà di tracciare il treno.")
        return
    if len(args) == 1:
        id_treno = args[0]
        stop = 10
        message.reply("*Attendere...*\n_Il tracciamento del treno "+id_treno+" si sta avviando._\nVisto che non hai messo nulla nel campo _minuti_ il bot traccierà il treno per 10m.\nLa prossima volta, se vuoi impostare un tempo differente, fai: `/traccia numero-treno minuti-massimi`")
        time.sleep(5)
    if len(args) == 2:
        id_treno = args[0]
        stop = int(args[1])
        message.reply("*Attendere...*\n_Il tracciamento del treno "+id_treno+" si sta avviando._\nTraccierà il treno per "+str(stop)+" minuti")
        time.sleep(5)
    stop = stop*60
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
    response = urllib.request.urlopen(content)
    id_stazione = (str(response.read()).split("-")[-1][:-3])
    try:
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
    except:
        message.reply("*Errore, non trovato (404)*:\n_That’s an error. That’s all we know:_\n-Il numero di treno inserito non è valido;\n-Non stai utilizzando il comando correttamente. Usa /info per il tutorial del comando")
        tracciamento = False
        return
    tracciamento = True
    content = response.read()
    data = json.loads(content.decode("utf8"))
    orarioPartenza = datetime.datetime.fromtimestamp(data['orarioPartenza'] / 1000).strftime('%H:%M')
    orarioArrivo = datetime.datetime.fromtimestamp(data['orarioArrivo'] / 1000).strftime('%H:%M')
    try:
        oraUltimoRilevamento = datetime.datetime.fromtimestamp(data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
    except:
        oraUltimoRilevamento = "Il treno non è ancora partito"
    ritardo = data['ritardo']
    stazioneUltimoRilevamento = data['stazioneUltimoRilevamento']
    bot.chat(-1001057273480).send("#Comando #traccia"\
        "\n<b>Nome</b>: "+html.escape(str(message.sender.name))+\
        "\n<b>Username</b>: @"+str("None" if message.sender.username is None else html.escape(message.sender.username))+\
        "\n<b>Id utente</b>: #id"+str(message.sender.id)+\
        "\n<b>Treno</b>: "+str(id_treno)+\
        "\n<b>Minuti</b>: "+str(stop)+\
        "\n<b>Data</b>: "+str(datetime.datetime.now().strftime("#data_%d_%m_%y")),syntax="html")
    if tracciamento is True and stop > 0 and data['destinazioneZero'] != stazioneUltimoRilevamento:
        message.reply("_Informazioni iniziali sul treno _"+"_"+id_treno+"_"+\
            "\n*Stazione di partenza*: "+data['origineZero']+\
            " ("+(orarioPartenza)+")""\n*Stazione di arrivo*: "+\
            data['destinazioneZero']+" ("+(orarioArrivo)+")"+\
            "\n*Ritardo*: "+str(data['ritardo'])+"m"+\
            "\n*Stazione ultimo rilevamento*: "+\
            data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+\
            ")\n_Appena il treno cambierà stazione o avrà un grave ritardo sarai notificato_")
    if tracciamento is True and stop > 0 and data['destinazioneZero'] == stazioneUltimoRilevamento:
        message.reply("*Errore*\nQuesto treno è già arrivato a destinazione!")
    while tracciamento is True and stop > 0 and data['destinazioneZero'] != stazioneUltimoRilevamento:
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data = json.loads(content.decode("utf8"))
        ritardo2 = data['ritardo']
        stop = stop-1
        stazioneUltimoRilevamento2 = data['stazioneUltimoRilevamento']
        differenzaritardo = ritardo2 - ritardo
        if stazioneUltimoRilevamento != stazioneUltimoRilevamento2:
            try:
                oraUltimoRilevamento2 = datetime.datetime.fromtimestamp(data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
            except:
                oraUltimoRilevamento2 = "Il treno non è ancora partito"
                pass
            message.reply("*Traccia treno*\n_Il treno "+id_treno+" ha cambiato stazione!_"\
                "\n*Stazione precedente*: "+stazioneUltimoRilevamento+\
                " ("+oraUltimoRilevamento+")"+"\n*Stazione corrente*: "+\
                stazioneUltimoRilevamento2+" ("+oraUltimoRilevamento2+")"+\
                "\n*Ritardo: *"+str(ritardo2)+"m")
            stazioneUltimoRilevamento = data['stazioneUltimoRilevamento']
            oraUltimoRilevamento = data['oraUltimoRilevamento']
        if differenzaritardo == 10 or differenzaritardo > 10:
            message.reply("*Traccia treno*\n_Il treno "+\
                id_treno+" ha accumulato ritardo!_\n*Ritardo precedente*: "+\
                str(ritardo)+"m\n*Ritardo attuale:* "+str(ritardo2)+"m")
            ritardo = data['ritardo']
        if stop == 1:
            message.reply("*Traccia treno*\nFine del tracciamento del treno "+id_treno)
        time.sleep(1)
        continue

#Avvio del bot
if __name__ == "__main__":
    bot.run()
