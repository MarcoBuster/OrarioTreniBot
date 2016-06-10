"""
----------------------------------------------------------------------------------
GENERAL INFO
Orario treni: Il bot del vero pendolare!
Versione: 0.3
Telegram: @OrarioTreniBot
Supporto: @MarcoBuster
----------------------------------------------------------------------------------
"""
import botogram
import json
import urllib.request
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
    chat.send("*Orario treni*\n_Con questo bot potrai cercare il tuo treno e averne le informazioni principali._\nPer cercare un treno dal numero fare questo comando:\n`/treno numero-treno`.\nPer cercare le informazioni di un treno rispetto a una stazione (_binario, ritardo, ecc..._) fare:\n`/fermata numero-treno numero-fermata`\n_In numero fermata inserire il numero che trovate facendo_: \n`/fermata numero-treno lista`")
    chat.send("_Aiuto, domande, questioni tecniche:_ @MarcoBuster")
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
    except urrlib.error.HTTPError as e:
        if(e.code == 404):
            chat.send("_Errore_\n*Non ho trovato nulla. Forse perché...*:\n-Il numero di treno inserito non è valido;\n-Il treno non è ancora partito;\n-Non stai utilizzando il comando correttamente. Usa /info per il tutorial del comando")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    orarioPartenza = datetime.datetime.fromtimestamp(data['orarioPartenza'] / 1000).strftime('%H:%M')
    orarioArrivo = datetime.datetime.fromtimestamp(data['orarioArrivo'] / 1000).strftime('%H:%M')
    oraUltimoRilevamento = datetime.datetime.fromtimestamp(data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
    chat.send("_Informazioni sul treno _"+"_"+id_treno+"_"+"\n*Stazione di partenza*: "+data['origineZero']+" ("+(orarioPartenza)+")""\n*Stazione di arrivo*: "+data['destinazioneZero']+" ("+(orarioArrivo)+")"+"\n*Ritardo*: "+str(data['ritardo'])+"m"+"\n*Stazione ultimo rilevamento*: "+data['stazioneUltimoRilevamento']+" ("+(oraUltimoRilevamento)+")")
    if (data['subTitle'])=="":
        asd = 1
    else:
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
    except urrlib.error.HTTPError as e:
        if(e.code == 404):
            chat.send("_Errore_\n*Non ho trovato nulla. Forse perché...*:\n-Il numero di treno inserito non è valido;\n-Il treno non è ancora partito;\n-Non stai utilizzando il comando correttamente. Usa /info per il tutorial del comando")
    content = response.read()
    data = json.loads(content.decode("utf8"))
    staz = (args[1])
    try:
        s= int(args[1])
    except:
        pass
    try:
        sOrarioArrivoP = datetime.datetime.fromtimestamp(data['fermate'][s]['arrivo_teorico'] / 1000).strftime('%H:%M')
        sOrarioArrivoR = datetime.datetime.fromtimestamp(data['fermate'][s]['arrivoReale'] / 1000).strftime('%H:%M')
        sOrarioPartenzaP = datetime.datetime.fromtimestamp(data['fermate'][s]['partenza_teorica'] / 1000).strftime('%H:%M')
        sOrarioPartenzaR = datetime.datetime.fromtimestamp(data['fermate'][s]['partenzaReale'] / 1000).strftime('%H:%M')
    except:
        pass
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
        chat.send("*Informazioni di un treno rispetto a una fermata specifica*:_ "+data['fermate'][s]['stazione']+"_\n*Arrivo programmato: *"+str(sOrarioArrivoP)+"\n*Arrivo reale: *"+str(sOrarioArrivoR)+"\n*Ritardo arrivo: *"+str(data['fermate'][s]['ritardoArrivo'])+"\n*Partenza programmata: *"+str(sOrarioPartenzaP)+"\n*Partenza reale: *"+str(sOrarioPartenzaR)+"\n*Ritardo partenza: *"+str(data['fermate'][s]['ritardoPartenza'])+"\n*Binario: *"+str(data['fermate'][s]['binarioEffettivoPartenzaDescrizione']))
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
#Avvio del bot
if __name__ == "__main__":
    bot.run()
