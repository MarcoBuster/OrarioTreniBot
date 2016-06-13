"""
----------------------------------------------------------------------------------
GENERAL INFO
Orario treni: Il bot del vero pendolare!
Versione: 1.2
Telegram: @OrarioTreniBot
Supporto: @MarcoBuster
----------------------------------------------------------------------------------
"""
import botogram
import json
import urllib.request
from datetime import datetime
import datetime
import time
bot = botogram.create("TOKEN")
bot.about = "Con questo bot potrai tracciare il tuo treno comodamente da Telegram. Per iniziare fai /start"
bot.owner = "@MarcoBuster"
bot.lang = "it"
#Comando: /info
#Visualizza le informazioni sul bot
#Utilizzo: /info
@bot.command("info")
def infocommand(chat, message, args):
    message.reply("*Orario treni*\n_Con questo bot potrai cercare un treno, una fermata di un treno, una stazione e averne le informazioni principali._\n")
    message.reply("*Comando /treno*\nPer cercare un treno dal numero fare questo comando:\n`/treno numero-treno`.\n*Suggerimento*\nRicorda che puoi cercare un treno anche scrivendo in chat il numero di treno, senza necessariamente scrivere `/treno` prima.")
    message.reply("*Comando /fermata*\nPer cercare le informazioni di un treno rispetto a una stazione (_binario, ritardo, ecc..._) fare:\n`/fermata numero-treno numero-fermata`\n_In numero fermata inserire il numero che trovate facendo_: \n`/fermata numero-treno lista`")
    message.reply("*Comandi /arrivi e /partenze*\nPer cercare il tabellone arrivi o partenze di una stazione fare:\n`/arrivi nome-stazione` o `/partenze nome-stazione`")
    message.reply("*Comando /itinerario*\nPer cercare un treno che ferma tra due stazioni, fare:\n`/itinerario stazione1 stazione2`")
    message.reply("*[NEW] Messaggi dinamici*\nLa funzione è in BETA. Nei comandi /treno e nella ricerca rapida, le informazioni sul treno come ritardo, stazione ultimo rilevamento, eccetera, sono aggiornate ogni secondo, senza dover rinviare di nuovo il comando.")
    message.reply("*Informazione utile*\n*SOLO NEL COMANDO /itinerario*, quando devi mettere un nome di una stazione che ha uno spazio bisogna mettere un punto (`.`) al posto dello spazio.\n_Esempio_: `MILANO CENTRALE` diventa `MILANO.CENTRALE`.")
    message.reply("*Votaci!*\nVota il bot [qui](https://telegram.me/storebot?start=orario_treni_bot).*Grazie per il supporto!*\nCanale con notizie, aggiornamenti e molto altro [qui](https://telegram.me/orario_treni_channel) \n_Aiuto, domande, questioni tecniche:_ @MarcoBuster")
#Comando: /help
#Visualizza le informazioni sul bot
#Utilizzo: /help
@bot.command("help")
def helpcommand(chat, message, args):
    message.reply("*Orario treni*\n_Con questo bot potrai cercare un treno, una fermata di un treno, una stazione e averne le informazioni principali._\n")
    message.reply("*Comando /treno*\nPer cercare un treno dal numero fare questo comando:\n`/treno numero-treno`.\n*Suggerimento*\nRicorda che puoi cercare un treno anche scrivendo in chat il numero di treno, senza necessariamente scrivere `/treno` prima.")
    message.reply("*Comando /fermata*\nPer cercare le informazioni di un treno rispetto a una stazione (_binario, ritardo, ecc..._) fare:\n`/fermata numero-treno numero-fermata`\n_In numero fermata inserire il numero che trovate facendo_: \n`/fermata numero-treno lista`")
    message.reply("*Comandi /arrivi e /partenze*\nPer cercare il tabellone arrivi o partenze di una stazione fare:\n`/arrivi nome-stazione` o `/partenze nome-stazione`")
    message.reply("*Comando /itinerario*\nPer cercare un treno che ferma tra due stazioni, fare:\n`/itinerario stazione1 stazione2`")
    message.reply("*[NEW] Messaggi dinamici*\nLa funzione è in BETA. Nei comandi /treno e nella ricerca rapida, le informazioni sul treno come ritardo, stazione ultimo rilevamento, eccetera, sono aggiornate ogni secondo, senza dover rinviare di nuovo il comando.")
    message.reply("*Informazione utile*\n*SOLO NEL COMANDO /itinerario*, quando devi mettere un nome di una stazione che ha uno spazio bisogna mettere un punto (`.`) al posto dello spazio.\n_Esempio_: `MILANO CENTRALE` diventa `MILANO.CENTRALE`.")
    message.reply("*Votaci!*\nVota il bot [qui](https://telegram.me/storebot?start=orario_treni_bot).*Grazie per il supporto!*\nCanale con notizie, aggiornamenti e molto altro [qui](https://telegram.me/orario_treni_channel) \n_Aiuto, domande, questioni tecniche:_ @MarcoBuster")
    print("Qualcuno ha utilizzato il comando /help senza problemi")
#Comando: /treno
#Cerca un treno e restituisce le informazioni principali
#Utilizzo: /treno <numero di treno>
def treno(chat, message, args):
    id_treno = (args[0])
    print ("Qualcuno ha cercato il treno: ",(args[0]))
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
    response = urllib.request.urlopen(content)
    id_stazione = (str(response.read()).split("-")[-1][:-3])
    try:
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
    except:
        message.reply("*Errore, non trovato (404)*:\n_That’s an error. That’s all we know:_\n-Il numero di treno inserito non è valido;\n-Non stai utilizzando il comando correttamente. Usa /info per il tutorial del comando")
        editing = False
    content = response.read()
    data = json.loads(content.decode("utf8"))
    orarioPartenza = datetime.datetime.fromtimestamp(data['orarioPartenza'] / 1000).strftime('%H:%M')
    orarioArrivo = datetime.datetime.fromtimestamp(data['orarioArrivo'] / 1000).strftime('%H:%M')
    try:
        oraUltimoRilevamento = datetime.datetime.fromtimestamp(data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
    except:
        oraUltimoRilevamento = "Il treno non è ancora partito"
    messaggio = message.reply("_Informazioni sul treno _"+"_"+id_treno+"_"+"\n*Stazione di partenza*: "+data['origineZero']+" ("+(orarioPartenza)+")""\n*Stazione di arrivo*: "+data['destinazioneZero']+" ("+(orarioArrivo)+")"+"\n*Ritardo*: "+str(data['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+")\n*Il messaggio dinamico è in caricamento...*")
    fermati = 500
    valore = 4
    editing = True
    while editing is True and fermati > 0:
        valore = valore +1
        try:
            orario = datetime.datetime.now().strftime('%H:%M')
            messaggio.edit("_Informazioni sul treno _"+"_"+id_treno+"_"+"\n*Stazione di partenza*: "+data['origineZero']+" ("+(orarioPartenza)+")""\n*Stazione di arrivo*: "+data['destinazioneZero']+" ("+(orarioArrivo)+")"+"\n*Ritardo*: "+str(data['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+")"+"\n*Orario attuale:* "+orario+"\n*Il messaggio dinamico scade fra "+str(fermati)+ " secondi circa*")
        except:
            pass
        fermati = fermati -1
        time.sleep(1)
        try:
            while (valore == 5):
                info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
                response = urllib.request.urlopen(info)
                content = response.read()
                data = json.loads(content.decode("utf8"))
                orarioPartenza = datetime.datetime.fromtimestamp(data['orarioPartenza'] / 1000).strftime('%H:%M')
                orarioArrivo = datetime.datetime.fromtimestamp(data['orarioArrivo'] / 1000).strftime('%H:%M')
                try:
                    oraUltimoRilevamento = datetime.datetime.fromtimestamp(data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
                except:
                    oraUltimoRilevamento = "Il treno non è ancora partito"
                if (data['destinazioneZero'] == data['stazioneUltimoRilevamento']):
                    messaggio.edit("_Informazioni sul treno _"+"_"+id_treno+"_"+"\n*Stazione di partenza*: "+data['origineZero']+" ("+(orarioPartenza)+")""\n*Stazione di arrivo*: "+data['destinazioneZero']+" ("+(orarioArrivo)+")"+"\n*Ritardo*: "+str(data['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+")"+"\n*Orario attuale:* "+orario+"\n*Messaggio dinamico disabilitato perché il treno è arrivato a destinazione*")
                    editing = False
                valore = 0
        except:
            continue
        continue
    if (data['subTitle']) != None:
        message.reply("*Informazioni cancellazione*: "+data['subTitle'])
#Comando: /fermata
#Visualizza le informazioni di un treno rispetto a una fermata specifica
#Utilizzo: /fermata <numero di treno> <numero di fermata>:lista
@bot.command("fermata")
def fermata(chat, message, args):
    id_treno= (args[0])
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
    response = urllib.request.urlopen(content)
    id_stazione = (str(response.read()).split("-")[-1][:-3])
    try:
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
    except:
        message.reply("_Errore_\n*Non ho trovato nulla. Forse perché...*:\n-Il numero di treno inserito non è valido;\n-Il treno non è ancora partito;\n-Non stai utilizzando il comando correttamente. Usa /info per il tutorial del comando")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    staz = (args[1])
    try:
        s= int(args[1])
    except:
        pass
    try:
        sOrarioArrivoP = str(datetime.datetime.fromtimestamp(data['fermate'][s]['arrivo_teorico'] / 1000).strftime('%H:%M'))
    except:
        sOrarioArrivoP = "--"
    try:
        sOrarioArrivoR = str(datetime.datetime.fromtimestamp(data['fermate'][s]['arrivoReale'] / 1000).strftime('%H:%M'))
    except:
        sOrarioArrivoR = "--"
    try:
        sOrarioPartenzaP = str(datetime.datetime.fromtimestamp(data['fermate'][s]['partenza_teorica'] / 1000).strftime('%H:%M'))
    except:
        sOrarioPartenzaP = "--"
    try:
        sOrarioPartenzaR = str(datetime.datetime.fromtimestamp(data['fermate'][s]['partenzaReale'] / 1000).strftime('%H:%M'))
    except:
        sOrarioPartenzaR = "--"
    try:
        ritardoArrivo = str(data['fermate'][s]['ritardoArrivo'])
    except:
        ritardoArrivo = "--"
    try:
        ritardoPartenza = str(data['fermate'][s]['ritardoPartenza'])
    except:
        ritardoPartenza = "--"
    if (staz == "lista"):
        message.reply("*Lista stazioni*\n_Ecco la lista delle fermata, per vedere le informazioni di una fermata in dettaglio fare_\n `/fermata "+id_treno+" numero fermata`\n_Il numero fermata è il numeretto, nella lista seguente, prima del nome della stazione_")
        b=""
        for k in range(0,51):
            try:
                a=str("["+str(k)+"] "+data['fermate'][k]['stazione'])
            except:
                break
            b=b+a
            b+="\n"
        message.reply(b)
    else:
        binario = data['fermate'][s]['binarioProgrammatoArrivoDescrizione']
        if (binario=="None"):
            binario = "Errore di Trenitalia/Trenord."
        else:
            binario = str(binario)
        message.reply("*Informazioni di un treno rispetto a una fermata specifica*:_ "+data['fermate'][s]['stazione']+"_\n*Arrivo programmato: *"+sOrarioArrivoP+"\n*Arrivo reale: *"+sOrarioArrivoR+"\n*Ritardo arrivo: *"+ritardoArrivo+"m\n*Partenza programmata: *"+sOrarioPartenzaP+"\n*Partenza reale: *"+sOrarioPartenzaR+"\n*Ritardo partenza: *"+ritardoPartenza+"m\n*Binario: *"+binario)
#Comando: /statistiche
#Visualizza curiose statistiche sui treni italiani in tempo reale
#Utilizzo: /statistiche
@bot.command("statistiche")
def statistiche(chat, message, args):
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/statistiche/random"
    response = urllib.request.urlopen(content)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    message.reply("_Statistiche dei treni italiani in tempo reale_"+"\n*Treni circolanti*: "+str(data['treniCircolanti'])+"\n*Treni totali di oggi*: "+str(data['treniGiorno']))
#Comando: /arrivi
#Visualizza gli arrivi di una stazione
#Utilizzo: /arrivi <nome stazione>
@bot.command("arrivi")
def arrivi(chat, message, args):
    stazione = (args)
    if (stazione == ""):
        message.reply("*Errore*\n_Nessuna stazione inserita_\nPer cercare una stazione scrivere il nome della stazione dopo il comando. Esempio: `/arrivi Milano Centrale`")
    stazione = ' '.join(stazione)
    stazione = stazione.replace(" ","%20").lstrip('%20')
    try:
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione
        response = urllib.request.urlopen(content)
    except:
        message.reply("*Errore*\n_Non ho trovato nessuna stazione con quel nome._Sei sicuro di stare usando il comando correttamente?\nEsempio di utilizzo: `/partenze Milano Centrale`")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    id_stazione = (str(data[0]['id']))
    datatempo = (datetime.datetime.now().strftime('%a %b %d %Y %H:%M:%S GMT+0100'))
    datatempo = datatempo.replace(" ","%20")
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/arrivi/"+id_stazione+"/"+datatempo
    response = urllib.request.urlopen(content)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    for k in range(0,5):
        sOrarioArrivoP = datetime.datetime.fromtimestamp(data[k]['orarioArrivo'] / 1000).strftime('%H:%M')
        binario = data[k]['binarioProgrammatoArrivoDescrizione']
        if (binario=="None"):
            binario = "Errore di Trenitalia/Trenord."
        stazione = stazione.replace("%20"," ")
        message.reply("*Informazioni degli arrivi nella stazione di* _"+stazione+"\nInformazioni del treno "+str(data[k]['numeroTreno'])+"_\n*Provenienza*: "+data[k]['origine']+"\n*Orario di arrivo*: "+str(sOrarioArrivoP)+"\n*Ritardo*: "+str(data[k]['ritardo'])+"m\n*Binario*: "+str(binario))
#Comando: /partenze
#Visualizza le partenze di una stazione
#Utilizzo: /partenze <nome stazione>
@bot.command("partenze")
def partenze(chat, message, args):
    stazione = (args)
    if (stazione == None):
        message.reply("*Errore*\n_Nessuna stazione inserita_\nPer cercare una stazione scrivere il nome della stazione dopo il comando. Esempio: `/partenze Milano Centrale`")
    stazione = ' '.join(stazione)
    stazione = stazione.replace(" ","%20").lstrip('%20')
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione
    response = urllib.request.urlopen(content)
    content = response.read()
    if (content ==b'[]'):
        message.reply("*Errore*\n_Non ho trovato nessuna stazione con quel nome._\nSei sicuro di stare usando il comando correttamente?\nEsempio di utilizzo: `/partenze Milano Centrale`")
    data = json.loads(content.decode("utf8"))
    id_stazione = (str(data[0]['id']))
    datatempo = (datetime.datetime.now().strftime('%a %b %d %Y %H:%M:%S GMT+0100'))
    datatempo = datatempo.replace(" ","%20")
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/partenze/"+id_stazione+"/"+datatempo
    response = urllib.request.urlopen(content)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    for k in range(0,5):
        sOrarioPartenzaP = datetime.datetime.fromtimestamp(data[k]['orarioPartenza'] / 1000).strftime('%H:%M')
        binario = data[k]['binarioProgrammatoPartenzaDescrizione']
        if (binario=="None"):
            binario = "Errore di Trenitalia/Trenord."
        stazione = stazione.replace("%20"," ")
        message.reply("*Informazioni delle partenze nella stazione di* _"+stazione+"\nInformazioni del treno "+str(data[k]['numeroTreno'])+"_\n*Destinazione*: "+data[k]['destinazione']+"\n*Orario di partenza*: "+str(sOrarioPartenzaP)+"\n*Ritardo*: "+str(data[k]['ritardo'])+"m\n*Binario*: "+str(binario))
#Comando: /itinerario
#Cerca un itinerario tra due stazioni
#Utilizzo: /itinerario <stazione di partenza> <stazione di arrivo>
@bot.command("itinerario")
def itinerario(chat, message, args):
    stazione1 = str((args[0]))
    stazione1 = stazione1.replace(".","%20")
    stazione2 = str((args[1]))
    stazione2 = stazione2.replace(".","%20")
    if len(args)>= 3:
        tempogrezzo = args[2]
        tempogrezzo = tempogrezzo + datetime.datetime.now().strftime(' %Y-%m-%d')
        tempo = datetime.datetime.strptime(tempogrezzo, '%H:%M %Y-%m-%d')
        tempo = tempo.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        tempo = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    print("Qualcuno ha cercato un itinerario tra la stazione di "+str(args[0])+" e la stazione di "+str(args[1]))
    #Cerca ID stazione 1
    try:
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione1
        response = urllib.request.urlopen(content)
    except:
        message.reply("*Errore: stazione di partenza non valida*\nNon ho trovato nessuna stazione con quel nome._Sei sicuro di stare usando il comando correttamente?\nRicorda che se c'è uno spazio nel nome della stazione (come Milano Centrale) devi mettere un punto dopo lo spazio (ovvero Milano.Centrale)_")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    id_stazione1 = (str(data[0]['id'])).split("S")[-1][:9].split("N")[-1][:9]
    #Cerca ID stazione 2
    try:
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione2
        response = urllib.request.urlopen(content)
    except:
        message.reply("*Errore: stazione di arrivo non valida*\nNon ho trovato nessuna stazione con quel nome._Sei sicuro di stare usando il comando correttamente?\nRicorda che se c'è uno spazio nel nome della stazione (come Milano Centrale) devi mettere un punto dopo lo spazio (ovvero Milano.Centrale)_")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    id_stazione2 = (str(data[0]['id'])).split("S")[-1][:9].split("N")[-1][:9]
    #Cerca itinerario
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/soluzioniViaggioNew/"+id_stazione1+"/"+id_stazione2+"/"+tempo
    response = urllib.request.urlopen(content)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    #Meccanismo per trovare quanti cambi ci sono
    try:
        for n in range (0,10):
            try:
                cambio = data['soluzioni'][0]['vehicles'][n]['numeroTreno']
            except:
                ncambi = n-1
                break
    except:
        pass
    if (ncambi == 0):
        id_treno = (data['soluzioni'][0]['vehicles'][0]['numeroTreno'])
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
        message.reply("*Ricerca di un treno per itinerario* ("+data['soluzioni'][0]['vehicles'][0]['origine']+" ~ "+data['soluzioni'][0]['vehicles'][0]['destinazione']+")\n*Treno trovato*: "+data['soluzioni'][0]['vehicles'][0]['numeroTreno']+"\n*Durata del tragitto*: "+data['soluzioni'][0]['durata']+"\n*Provienienza*: "+data2['origineZero']+" ("+str(orarioPartenza)+")\n*Destinazione*: "+data2['destinazioneZero']+" ("+str(orarioArrivo)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][0]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][0]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data2['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data2['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento)+")")
    if (ncambi == 1):
        id_treno = (data['soluzioni'][0]['vehicles'][0]['numeroTreno'])
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
        id_treno = (data['soluzioni'][0]['vehicles'][1]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data3 = json.loads(content.decode("utf8"))
        orarioPartenza3 = datetime.datetime.fromtimestamp(data3['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo3 = datetime.datetime.fromtimestamp(data3['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento3 = datetime.datetime.fromtimestamp(data3['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento3 = "Il treno non è ancora partito"
            pass
        message.reply("*Ricerca di un treno per itinerario*\n_1 cambio_ ("+data['soluzioni'][0]['vehicles'][0]['origine']+" ~ "+data['soluzioni'][0]['vehicles'][1]['destinazione']+")\n*Treno trovato*: "+data['soluzioni'][0]['vehicles'][0]['numeroTreno']+"\n*Durata del tragitto*: "+data['soluzioni'][0]['durata']+"\n*Provienienza*: "+data2['origineZero']+" ("+str(orarioPartenza)+")\n*Destinazione*: "+data2['destinazioneZero']+" ("+str(orarioArrivo)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][0]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][0]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data2['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data2['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][0]['destinazione']+" e prendere:\nNumero treno*: "+str(data3['numeroTreno'])+"\n*Provienienza*: "+data3['origineZero']+" ("+str(orarioPartenza3)+")\n*Destinazione*: "+data3['destinazioneZero']+" ("+str(orarioArrivo3)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][1]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][1]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][1]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][1]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data3['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data3['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento3)+")")
    #Due cambi
    if (ncambi == 2):
        id_treno = (data['soluzioni'][0]['vehicles'][0]['numeroTreno'])
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
        id_treno = (data['soluzioni'][0]['vehicles'][1]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data3 = json.loads(content.decode("utf8"))
        orarioPartenza3 = datetime.datetime.fromtimestamp(data3['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo3 = datetime.datetime.fromtimestamp(data3['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento3 = datetime.datetime.fromtimestamp(data3['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento3 = "Il treno non è ancora partito"
            pass
        id_treno = (data['soluzioni'][0]['vehicles'][2]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data4 = json.loads(content.decode("utf8"))
        orarioPartenza4 = datetime.datetime.fromtimestamp(data4['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo4 = datetime.datetime.fromtimestamp(data4['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento4 = datetime.datetime.fromtimestamp(data4['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento4 = "Il treno non è ancora partito"
            pass
        message.reply("*Ricerca di un treno per itinerario*\n_2 cambi_ ("+data['soluzioni'][0]['vehicles'][0]['origine']+" ~ "+data['soluzioni'][0]['vehicles'][2]['destinazione']+")\n*Treno trovato*: "+data['soluzioni'][0]['vehicles'][0]['numeroTreno']+"\n*Durata del tragitto*: "+data['soluzioni'][0]['durata']+"\n*Provienienza*: "+data2['origineZero']+" ("+str(orarioPartenza)+")\n*Destinazione*: "+data2['destinazioneZero']+" ("+str(orarioArrivo)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][0]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][0]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data2['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data2['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][0]['destinazione']+" e prendere:\nNumero treno*: "+str(data3['numeroTreno'])+"\n*Provienienza*: "+data3['origineZero']+" ("+str(orarioPartenza3)+")\n*Destinazione*: "+data3['destinazioneZero']+" ("+str(orarioArrivo3)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][1]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][1]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][1]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][1]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data3['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data3['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento3)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][1]['destinazione']+" e prendere:\nNumero treno*: "+str(data4['numeroTreno'])+"\n*Provienienza*: "+data4['origineZero']+" ("+str(orarioPartenza4)+")\n*Destinazione*: "+data4['destinazioneZero']+" ("+str(orarioArrivo4)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][2]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][2]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][2]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][2]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data4['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data4['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento4)+")")
    #Tre cambi
    if (ncambi == 3):
        id_treno = (data['soluzioni'][0]['vehicles'][0]['numeroTreno'])
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
        id_treno = (data['soluzioni'][0]['vehicles'][1]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data3 = json.loads(content.decode("utf8"))
        orarioPartenza3 = datetime.datetime.fromtimestamp(data3['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo3 = datetime.datetime.fromtimestamp(data3['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento3 = datetime.datetime.fromtimestamp(data3['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento3 = "Il treno non è ancora partito"
            pass
        id_treno = (data['soluzioni'][0]['vehicles'][2]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data4 = json.loads(content.decode("utf8"))
        orarioPartenza4 = datetime.datetime.fromtimestamp(data4['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo4 = datetime.datetime.fromtimestamp(data4['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento4 = datetime.datetime.fromtimestamp(data4['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento4 = "Il treno non è ancora partito"
            pass
        id_treno = (data['soluzioni'][0]['vehicles'][3]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data5 = json.loads(content.decode("utf8"))
        orarioPartenza5 = datetime.datetime.fromtimestamp(data5['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo5 = datetime.datetime.fromtimestamp(data5['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento5 = datetime.datetime.fromtimestamp(data5['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento5 = "Il treno non è ancora partito"
            pass
        message.reply("*Ricerca di un treno per itinerario*\n_3 cambi_ ("+data['soluzioni'][0]['vehicles'][0]['origine']+" ~ "+data['soluzioni'][0]['vehicles'][3]['destinazione']+")\n*Treno trovato*: "+data['soluzioni'][0]['vehicles'][0]['numeroTreno']+"\n*Durata del tragitto*: "+data['soluzioni'][0]['durata']+"\n*Provienienza*: "+data2['origineZero']+" ("+str(orarioPartenza)+")\n*Destinazione*: "+data2['destinazioneZero']+" ("+str(orarioArrivo)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][0]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][0]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data2['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data2['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][0]['destinazione']+" e prendere:\nNumero treno*: "+str(data3['numeroTreno'])+"\n*Provienienza*: "+data3['origineZero']+" ("+str(orarioPartenza3)+")\n*Destinazione*: "+data3['destinazioneZero']+" ("+str(orarioArrivo3)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][1]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][1]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][1]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][1]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data3['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data3['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento3)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][1]['destinazione']+" e prendere:\nNumero treno*: "+str(data4['numeroTreno'])+"\n*Provienienza*: "+data4['origineZero']+" ("+str(orarioPartenza4)+")\n*Destinazione*: "+data4['destinazioneZero']+" ("+str(orarioArrivo4)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][2]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][2]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][2]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][2]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data4['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data4['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento4)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][2]['destinazione']+" e prendere:\nNumero treno*: "+str(data5['numeroTreno'])+"\n*Provienienza*: "+data5['origineZero']+" ("+str(orarioPartenza5)+")\n*Destinazione*: "+data5['destinazioneZero']+" ("+str(orarioArrivo5)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][3]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][3]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][3]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][3]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data5['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data5['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento5)+")")
    #Quattro cambi
    if (ncambi == 4):
        id_treno = (data['soluzioni'][0]['vehicles'][0]['numeroTreno'])
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
        id_treno = (data['soluzioni'][0]['vehicles'][1]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data3 = json.loads(content.decode("utf8"))
        orarioPartenza3 = datetime.datetime.fromtimestamp(data3['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo3 = datetime.datetime.fromtimestamp(data3['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento3 = datetime.datetime.fromtimestamp(data3['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento3 = "Il treno non è ancora partito"
            pass
        id_treno = (data['soluzioni'][0]['vehicles'][2]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data4 = json.loads(content.decode("utf8"))
        orarioPartenza4 = datetime.datetime.fromtimestamp(data4['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo4 = datetime.datetime.fromtimestamp(data4['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento4 = datetime.datetime.fromtimestamp(data4['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento4 = "Il treno non è ancora partito"
            pass
        id_treno = (data['soluzioni'][0]['vehicles'][3]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data5 = json.loads(content.decode("utf8"))
        orarioPartenza5 = datetime.datetime.fromtimestamp(data5['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo5 = datetime.datetime.fromtimestamp(data5['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento5 = datetime.datetime.fromtimestamp(data5['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento5 = "Il treno non è ancora partito"
            pass
        id_treno = (data['soluzioni'][0]['vehicles'][4]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data6 = json.loads(content.decode("utf8"))
        orarioPartenza6 = datetime.datetime.fromtimestamp(data6['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo6 = datetime.datetime.fromtimestamp(data6['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento6 = datetime.datetime.fromtimestamp(data6['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento6 = "Il treno non è ancora partito"
            pass

        message.reply("*Ricerca di un treno per itinerario*\n_4 cambi (Un bel po')_ ("+data['soluzioni'][0]['vehicles'][0]['origine']+" ~ "+data['soluzioni'][0]['vehicles'][4]['destinazione']+")\n*Treno trovato*: "+data['soluzioni'][0]['vehicles'][0]['numeroTreno']+"\n*Durata del tragitto*: "+data['soluzioni'][0]['durata']+"\n*Provienienza*: "+data2['origineZero']+" ("+str(orarioPartenza)+")\n*Destinazione*: "+data2['destinazioneZero']+" ("+str(orarioArrivo)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][0]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][0]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data2['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data2['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][0]['destinazione']+" e prendere:\nNumero treno*: "+str(data3['numeroTreno'])+"\n*Provienienza*: "+data3['origineZero']+" ("+str(orarioPartenza3)+")\n*Destinazione*: "+data3['destinazioneZero']+" ("+str(orarioArrivo3)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][1]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][1]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][1]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][1]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data3['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data3['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento3)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][1]['destinazione']+" e prendere:\nNumero treno*: "+str(data4['numeroTreno'])+"\n*Provienienza*: "+data4['origineZero']+" ("+str(orarioPartenza4)+")\n*Destinazione*: "+data4['destinazioneZero']+" ("+str(orarioArrivo4)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][2]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][2]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][2]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][2]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data4['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data4['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento4)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][2]['destinazione']+" e prendere:\nNumero treno*: "+str(data5['numeroTreno'])+"\n*Provienienza*: "+data5['origineZero']+" ("+str(orarioPartenza5)+")\n*Destinazione*: "+data5['destinazioneZero']+" ("+str(orarioArrivo5)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][3]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][3]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][3]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][3]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data5['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data5['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento5)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][3]['destinazione']+" e prendere:\nNumero treno*: "+str(data6['numeroTreno'])+"\n*Provienienza*: "+data6['origineZero']+" ("+str(orarioPartenza6)+")\n*Destinazione*: "+data6['destinazioneZero']+" ("+str(orarioArrivo6)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][4]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][4]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][4]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][4]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data6['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data6['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento6)+")")
    #Cinque cambi
    if (ncambi == 5):
        id_treno = (data['soluzioni'][0]['vehicles'][0]['numeroTreno'])
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
        id_treno = (data['soluzioni'][0]['vehicles'][1]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data3 = json.loads(content.decode("utf8"))
        orarioPartenza3 = datetime.datetime.fromtimestamp(data3['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo3 = datetime.datetime.fromtimestamp(data3['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento3 = datetime.datetime.fromtimestamp(data3['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento3 = "Il treno non è ancora partito"
            pass
        id_treno = (data['soluzioni'][0]['vehicles'][2]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data4 = json.loads(content.decode("utf8"))
        orarioPartenza4 = datetime.datetime.fromtimestamp(data4['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo4 = datetime.datetime.fromtimestamp(data4['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento4 = datetime.datetime.fromtimestamp(data4['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento4 = "Il treno non è ancora partito"
            pass
        id_treno = (data['soluzioni'][0]['vehicles'][3]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data5 = json.loads(content.decode("utf8"))
        orarioPartenza5 = datetime.datetime.fromtimestamp(data5['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo5 = datetime.datetime.fromtimestamp(data5['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento5 = datetime.datetime.fromtimestamp(data5['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento5 = "Il treno non è ancora partito"
            pass
        id_treno = (data['soluzioni'][0]['vehicles'][4]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data6 = json.loads(content.decode("utf8"))
        orarioPartenza6 = datetime.datetime.fromtimestamp(data6['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo6 = datetime.datetime.fromtimestamp(data6['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento6 = datetime.datetime.fromtimestamp(data6['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento6 = "Il treno non è ancora partito"
            pass
        id_treno = (data['soluzioni'][0]['vehicles'][5]['numeroTreno'])
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
        content = response.read()
        data7 = json.loads(content.decode("utf8"))
        orarioPartenza7 = datetime.datetime.fromtimestamp(data7['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo7 = datetime.datetime.fromtimestamp(data7['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento6 = datetime.datetime.fromtimestamp(data3['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento6 = "Il treno non è ancora partito"
            pass

        message.reply("*Ricerca di un treno per itinerario*\n_5 cambi (Un bel po')_ ("+data['soluzioni'][0]['vehicles'][0]['origine']+" ~ "+data['soluzioni'][0]['vehicles'][5]['destinazione']+")\n*Treno trovato*: "+data['soluzioni'][0]['vehicles'][0]['numeroTreno']+"\n*Durata del tragitto*: "+data['soluzioni'][0]['durata']+"\n*Provienienza*: "+data2['origineZero']+" ("+str(orarioPartenza)+")\n*Destinazione*: "+data2['destinazioneZero']+" ("+str(orarioArrivo)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][0]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][0]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data2['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data2['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][0]['destinazione']+" e prendere:\nNumero treno*: "+str(data3['numeroTreno'])+"\n*Provienienza*: "+data3['origineZero']+" ("+str(orarioPartenza3)+")\n*Destinazione*: "+data3['destinazioneZero']+" ("+str(orarioArrivo3)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][1]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][1]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][1]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][1]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data3['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data3['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento3)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][1]['destinazione']+" e prendere:\nNumero treno*: "+str(data4['numeroTreno'])+"\n*Provienienza*: "+data4['origineZero']+" ("+str(orarioPartenza4)+")\n*Destinazione*: "+data4['destinazioneZero']+" ("+str(orarioArrivo4)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][2]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][2]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][2]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][2]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data4['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data4['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento4)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][2]['destinazione']+" e prendere:\nNumero treno*: "+str(data5['numeroTreno'])+"\n*Provienienza*: "+data5['origineZero']+" ("+str(orarioPartenza5)+")\n*Destinazione*: "+data5['destinazioneZero']+" ("+str(orarioArrivo5)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][3]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][3]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][3]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][3]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data5['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data5['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento5)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][3]['destinazione']+" e prendere:\nNumero treno*: "+str(data6['numeroTreno'])+"\n*Provienienza*: "+data6['origineZero']+" ("+str(orarioPartenza6)+")\n*Destinazione*: "+data6['destinazioneZero']+" ("+str(orarioArrivo6)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][4]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][4]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][4]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][4]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data6['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data6['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento6)+")")
        message.reply("\n*Scendere a "+data['soluzioni'][0]['vehicles'][4]['destinazione']+" e prendere:\nNumero treno*: "+str(data7['numeroTreno'])+"\n*Provienienza*: "+data7['origineZero']+" ("+str(orarioPartenza7)+")\n*Destinazione*: "+data7['destinazioneZero']+" ("+str(orarioArrivo7)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][5]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][5]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][5]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][5]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data7['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data7['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento7)+")")

    if (ncambi > 5):
        message.reply("*Errore*\n_Error 27_\nL'itinerario prevede un tragitto con troppi cambi (>5). Il bot supporterà più cambi nelle prossime versioni. In tanto, segui gli aggiornamenti su @orario_treni_channel")
#Comando: Ricerca rapida
#Con la ricerca rapida si possono cercare treni diretttamente in chat, senza scrivere /treno prima.
#Utilizzo: <numero di treno>
@bot.process_message
def ricerca_veloce(chat, message):
    id_treno = str(message.text)
    print("Qualcuno ha usato la ricerca rapida per cercare il treno "+str(id_treno))
    try:
        annulla = False
        id_treno2 = int(id_treno)
    except:
        annulla = True
        if chat.type == "private":
            message.reply("*Attenzione!*\nSei sicuro di stare utilizzando il comando correttamente? Ricorda che puoi inviarmi solo numeri di treni, qui direttamente in chat.\nPer imparare ad usare gli altri comandi utilizza il comando /help")
    if (annulla is False):
        message.reply("*Ricerca rapida*\nSto cercando con la ricerca rapida il treno "+id_treno)
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        try:
            info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
            response = urllib.request.urlopen(info)
        except:
            message.reply("*Errore, non trovato (404)*:\n_That’s an error. That’s all we know:_\n-Il numero di treno inserito non è valido;\n-Non stai utilizzando il comando correttamente. Usa /info per il tutorial del comando")
            editing = False
        content = response.read()
        data = json.loads(content.decode("utf8"))
        orarioPartenza = datetime.datetime.fromtimestamp(data['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo = datetime.datetime.fromtimestamp(data['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento = datetime.datetime.fromtimestamp(data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except:
            oraUltimoRilevamento = "Il treno non è ancora partito"
        orario = datetime.datetime.now().strftime('%H:%M')
        editing = True
        fermati = 500
        messaggio = message.reply("_Informazioni sul treno _"+"_"+id_treno+"_"+"\n*Stazione di partenza*: "+data['origineZero']+" ("+(orarioPartenza)+")""\n*Stazione di arrivo*: "+data['destinazioneZero']+" ("+(orarioArrivo)+")"+"\n*Ritardo*: "+str(data['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+")"+"\n*Orario attuale:* "+orario+"\n*Il messaggio dinamico scade fra "+str(fermati)+ " secondi circa*")
        #While numero uno
        valore = 4
        while editing is True and fermati > 0:
            valore = valore +1
            try:
                orario = datetime.datetime.now().strftime('%H:%M')
                messaggio.edit("_Informazioni sul treno _"+"_"+id_treno+"_"+"\n*Stazione di partenza*: "+data['origineZero']+" ("+(orarioPartenza)+")""\n*Stazione di arrivo*: "+data['destinazioneZero']+" ("+(orarioArrivo)+")"+"\n*Ritardo*: "+str(data['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+")"+"\n*Orario attuale:* "+orario+"\n*Il messaggio dinamico scade fra "+str(fermati)+ " secondi circa*")
            except:
                pass
            fermati = fermati -1
            time.sleep(1)
            try:
                while (valore == 5):
                    info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
                    response = urllib.request.urlopen(info)
                    content = response.read()
                    data = json.loads(content.decode("utf8"))
                    orarioPartenza = datetime.datetime.fromtimestamp(data['orarioPartenza'] / 1000).strftime('%H:%M')
                    orarioArrivo = datetime.datetime.fromtimestamp(data['orarioArrivo'] / 1000).strftime('%H:%M')
                    try:
                        oraUltimoRilevamento = datetime.datetime.fromtimestamp(data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
                    except:
                        oraUltimoRilevamento = "Il treno non è ancora partito"
                    if (data['destinazioneZero'] == data['stazioneUltimoRilevamento']):
                        messaggio.edit("_Informazioni sul treno _"+"_"+id_treno+"_"+"\n*Stazione di partenza*: "+data['origineZero']+" ("+(orarioPartenza)+")""\n*Stazione di arrivo*: "+data['destinazioneZero']+" ("+(orarioArrivo)+")"+"\n*Ritardo*: "+str(data['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+")"+"\n*Orario attuale:* "+orario+"\n*Messaggio dinamico disabilitato perché il treno è arrivato a destinazione*")
                        editing = False
                    valore = 0
            except:
                continue
            continue

        if (fermati == 0):
            messaggio.edit("_Informazioni sul treno _"+"_"+id_treno+"_"+"\n*Stazione di partenza*: "+data['origineZero']+" ("+(orarioPartenza)+")""\n*Stazione di arrivo*: "+data['destinazioneZero']+" ("+(orarioArrivo)+")"+"\n*Ritardo*: "+str(data['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+")"+"\n*Orario attuale:* "+orario+"\n*Messaggio dinamico scaduto.*")
        if (data['subTitle']) != None:
            message.reply(data['subTitle'])


#Avvio del bot
if __name__ == "__main__":
    bot.run()
