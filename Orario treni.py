"""
----------------------------------------------------------------------------------
GENERAL INFO
Orario treni: Il bot del vero pendolare!
Versione: 1.0
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
def info(chat, message, args):
    chat.send("*Orario treni*\n_Con questo bot potrai cercare un treno, una fermata di un treno, una stazione e averne le informazioni principali._\n")
    chat.send("*Comando /treno*\nPer cercare un treno dal numero fare questo comando:\n`/treno numero-treno`.")
    chat.send("*Comando /fermata*\nPer cercare le informazioni di un treno rispetto a una stazione (_binario, ritardo, ecc..._) fare:\n`/fermata numero-treno numero-fermata`\n_In numero fermata inserire il numero che trovate facendo_: \n`/fermata numero-treno lista`")
    chat.send("*Comandi /arrivi e /partenze*\nPer cercare il tabellone arrivi o partenze di una stazione fare:\n`/arrivi nome-stazione` o `/partenze nome-stazione`")
    chat.send("*Comando /itinerario*\nPer cercare un treno che ferma tra due stazioni, fare:\n`/itinerario stazione1 stazione2`")
    chat.send("*Informazione utile*\nSe nel bot devi mettere un nome di una stazione che ha uno spazio bisogna mettere un punto (`.`) al posto dello spazio.\n_Esempio_: `MILANO CENTRALE` diventa `MILANO.CENTRALE`.")
    chat.send("*Votaci!*\nVota il bot [qui](https://telegram.me/storebot?start=orario_treni_bot). *Grazie per il supporto!*\n_Aiuto, domande, questioni tecniche:_ @MarcoBuster")
#Comando: /treno
#Cerca un treno e restituisce le informazioni principali
#Utilizzo: /treno <numero di treno>
@bot.command("treno")
def treno(chat, message, args, shared):
    id_treno = (args[0])
    print ("Qualcuno ha cercato il treno: ",(args[0]))
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
    response = urllib.request.urlopen(content)
    id_stazione = (str(response.read()).split("-")[-1][:-3])
    try:
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
    except:
        chat.send("*Errore, non trovato (404)*:\n_That’s an error. That’s all we know:_\n-Il numero di treno inserito non è valido;\n-Non stai utilizzando il comando correttamente. Usa /info per il tutorial del comando")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    orarioPartenza = datetime.datetime.fromtimestamp(data['orarioPartenza'] / 1000).strftime('%H:%M')
    orarioArrivo = datetime.datetime.fromtimestamp(data['orarioArrivo'] / 1000).strftime('%H:%M')
    try:
        oraUltimoRilevamento = datetime.datetime.fromtimestamp(data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
    except:
        oraUltimoRilevamento = "Il treno non è ancora partito"
    chat.send("_Informazioni sul treno _"+"_"+id_treno+"_"+"\n*Stazione di partenza*: "+data['origineZero']+" ("+(orarioPartenza)+")""\n*Stazione di arrivo*: "+data['destinazioneZero']+" ("+(orarioArrivo)+")"+"\n*Ritardo*: "+str(data['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+")")
    if (data['subTitle']) != None:
        chat.send("*Informazioni cancellazione*: "+data['subTitle'])
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
        chat.send("_Errore_\n*Non ho trovato nulla. Forse perché...*:\n-Il numero di treno inserito non è valido;\n-Il treno non è ancora partito;\n-Non stai utilizzando il comando correttamente. Usa /info per il tutorial del comando")
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
        chat.send("*Lista stazioni*\n_Ecco la lista delle fermata, per vedere le informazioni di una fermata in dettaglio fare_\n `/fermata "+id_treno+" numero fermata`\n_Il numero fermata è il numeretto, nella lista seguente, prima del nome della stazione_")
        b=""
        for k in range(0,51):
            try:
                a=str("["+str(k)+"] "+data['fermate'][k]['stazione'])
            except:
                break
            b=b+a
            b+="\n"
        chat.send(b)
    else:
        binario = data['fermate'][s]['binarioProgrammatoArrivoDescrizione']
        if (binario=="None"):
            binario = "Errore di Trenitalia/Trenord."
        else:
            binario = str(binario)
        chat.send("*Informazioni di un treno rispetto a una fermata specifica*:_ "+data['fermate'][s]['stazione']+"_\n*Arrivo programmato: *"+sOrarioArrivoP+"\n*Arrivo reale: *"+sOrarioArrivoR+"\n*Ritardo arrivo: *"+ritardoArrivo+"m\n*Partenza programmata: *"+sOrarioPartenzaP+"\n*Partenza reale: *"+sOrarioPartenzaR+"\n*Ritardo partenza: *"+ritardoPartenza+"m\n*Binario: *"+binario)
#Comando: /statistiche
#Visualizza curiose statistiche sui treni italiani in tempo reale
#Utilizzo: /statistiche
@bot.command("statistiche")
def statistiche(chat, message, args):
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/statistiche/random"
    response = urllib.request.urlopen(content)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    chat.send("_Statistiche dei treni italiani in tempo reale_"+"\n*Treni circolanti*: "+str(data['treniCircolanti'])+"\n*Treni totali di oggi*: "+str(data['treniGiorno']))
#Comando: /arrivi
#Visualizza gli arrivi di una stazione
#Utilizzo: /arrivi <nome stazione>
@bot.command("arrivi")
def arrivi(chat, message, args):
    stazione = str((args[0]))
    stazione = stazione.replace(".","%20")
    try:
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione
        response = urllib.request.urlopen(content)
    except:
        chat.send("*Errore*\nNon ho trovato nessuna stazione con quel nome._Sei sicuro di stare usando il comando correttamente?\nRicorda che se c'è uno spazio nel nome della stazione (come Milano Centrale) devi mettere un punto dopo lo spazio (ovvero Milano.Centrale)_")
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
        chat.send("*Informazioni degli arrivi nella stazione di* _"+stazione+"\nInformazioni del treno "+str(data[k]['numeroTreno'])+"_\n*Provenienza*: "+data[k]['origine']+"\n*Orario di arrivo*: "+str(sOrarioArrivoP)+"\n*Ritardo*: "+str(data[k]['ritardo'])+"m\n*Binario*: "+str(binario))
#Comando: /partenze
#Visualizza le partenze di una stazione
#Utilizzo: /partenze <nome stazione>
@bot.command("partenze")
def partenze(chat, message, args):
    stazione = str((args[0]))
    stazione = stazione.replace(".","%20")
    try:
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione
        response = urllib.request.urlopen(content)
    except:
        chat.send("*Errore*\nNon ho trovato nessuna stazione con quel nome._Sei sicuro di stare usando il comando correttamente?\nRicorda che se c'è uno spazio nel nome della stazione (come Milano Centrale) devi mettere un punto dopo lo spazio (ovvero Milano.Centrale)_")
    content = response.read()
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
        chat.send("*Informazioni delle partenze nella stazione di* _"+stazione+"\nInformazioni del treno "+str(data[k]['numeroTreno'])+"_\n*Destinazione*: "+data[k]['destinazione']+"\n*Orario di partenza*: "+str(sOrarioPartenzaP)+"\n*Ritardo*: "+str(data[k]['ritardo'])+"m\n*Binario*: "+str(binario))
#Comando: /itinerario
#Cerca un itinerario tra due stazioni
#Utilizzo: /itinerario <stazione di partenza> <stazione di arrivo>
@bot.command("itinerario")
def itinerario(chat, message, args):
    stazione1 = str((args[0]))
    stazione1 = stazione1.replace(".","%20")
    stazione2 = str((args[1]))
    stazione2 = stazione2.replace(".","%20")
    tempo = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    #Cerca ID stazione 1
    try:
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione1
        response = urllib.request.urlopen(content)
    except:
        chat.send("*Errore: stazione di partenza non valida*\nNon ho trovato nessuna stazione con quel nome._Sei sicuro di stare usando il comando correttamente?\nRicorda che se c'è uno spazio nel nome della stazione (come Milano Centrale) devi mettere un punto dopo lo spazio (ovvero Milano.Centrale)_")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    id_stazione1 = (str(data[0]['id'])).split("S")[-1][:9]
    #Cerca ID stazione 2
    try:
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione2
        response = urllib.request.urlopen(content)
    except:
        chat.send("*Errore: stazione di arrivo non valida*\nNon ho trovato nessuna stazione con quel nome._Sei sicuro di stare usando il comando correttamente?\nRicorda che se c'è uno spazio nel nome della stazione (come Milano Centrale) devi mettere un punto dopo lo spazio (ovvero Milano.Centrale)_")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    id_stazione2 = (str(data[0]['id'])).split("S")[-1][:9]
    #Cerca itinerario
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/soluzioniViaggioNew/"+id_stazione1+"/"+id_stazione2+"/"+tempo
    response = urllib.request.urlopen(content)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    #Cerca altre informazioni sul treno
    id_treno = (data['soluzioni'][0]['vehicles'][0]['numeroTreno'])
    #Cerca ID stazione di partenza
    content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
    response = urllib.request.urlopen(content)
    id_stazione = (str(response.read()).split("-")[-1][:-3])
    #Cerca treno con la stazione
    try:
        info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
        response = urllib.request.urlopen(info)
    except:
        chat.send("_Errore_\n*Non ho trovato nulla. Forse perché...*:\n-Il numero di treno inserito non è valido;\n-Non stai utilizzando il comando correttamente. Usa /info per il tutorial del comando")
    content = response.read()
    #Informazioni itinerario=data[], informazioni treno=data2[]
    data2 = json.loads(content.decode("utf8"))
    orarioPartenza = datetime.datetime.fromtimestamp(data2['orarioPartenza'] / 1000).strftime('%H:%M')
    orarioArrivo = datetime.datetime.fromtimestamp(data2['orarioArrivo'] / 1000).strftime('%H:%M')
    try:
        oraUltimoRilevamento = datetime.datetime.fromtimestamp(data2['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
    except:
        oraUltimoRilevamento = "Il treno non è ancora partito"
        pass
    chat.send("*Ricerca di un treno per itinerario* ("+data['soluzioni'][0]['vehicles'][0]['origine']+" ~ "+data['soluzioni'][0]['vehicles'][0]['destinazione']+")\n*Treno trovato*: "+data['soluzioni'][0]['vehicles'][0]['numeroTreno']+"\n*Durata del tragitto*: "+data['soluzioni'][0]['durata']+"\n*Provienienza*: "+data2['origineZero']+" ("+str(orarioPartenza)+")\n*Destinazione*: "+data2['destinazioneZero']+" ("+str(orarioArrivo)+")\n*Parte da "+data['soluzioni'][0]['vehicles'][0]['origine']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioPartenza'].split("T")[-1][:9].replace(":00","")+"\n*Arriva a "+data['soluzioni'][0]['vehicles'][0]['destinazione']+"* alle "+data['soluzioni'][0]['vehicles'][0]['orarioArrivo'].split("T")[-1][:9].replace(":00","")+"\n*Ritardo*: "+str(data2['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data2['stazioneUltimoRilevamento']+" ("+str(oraUltimoRilevamento)+")")

#Avvio del bot
if __name__ == "__main__":
    bot.run()
