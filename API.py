import urllib.request
import json
import sqlite3
from datetime import datetime
import datetime
from urllib import *

conn = sqlite3.connect('OrarioTreni.db')
c = conn.cursor()

class db:
    """Gestisci database"""

    def creaTutto():
        """Crea la la connessione e la table"""
        conn = sqlite3.connect('OrarioTreniBot.db')
        c = conn.cursor()
        try:
            c.execute('''CREATE TABLE stato(userid INTEGER, stato STRING, completato INTEGER)''')
        except:
            pass

        try:
            c.execute('''CREATE TABLE bannati(userid INTEGER)''')
        except:
            pass

        try:
            c.execute('''CREATE TABLE itinerario(userid INTEGER, stazione1 STRING, stazione2 STRING, orario STRING)''')
        except:
            pass

        conn.commit()

    def updateState(userid, new_state, completato):
        try:
            c.execute('''DELETE FROM stato WHERE userid=?''',(userid,))
            c.execute('''INSERT INTO stato VALUES(?,?,?)''',(userid, new_state, completato))
            conn.commit()
            return True, None #return <success> <error>
        except Exception as e:
            return False, e

    def getState(userid):
        try:
            c.execute('''SELECT stato, completato FROM stato WHERE userid=?''',(userid,))
            rows = c.fetchall()
            for res in rows:
                return res[0], res[1], True, None #return <state> <completato> <success> <error>
            conn.commit()
        except Exception as e:
            return None, None, False, e

    def resetItinerario(userid):
        c.execute('''DELETE FROM itinerario WHERE userid=?''',(userid,))
        conn.commit()

class orarioTreni:
    """Cerca treni, arrivi, partenze, itinerari, statistiche"""
    def tipo(stringa):
        data, success, error = orarioTreni.cercaTreno(stringa)
        if success == True:
            return "treno"

        esiste, data = orarioTreni.stazione.check(stringa)
        if esiste == True:
            return "stazione"

        if stringa.find('-') > 0: #Formato itinerario: STAZIONEA - STAZIONEB (orario)
            return "itinerario"

        return "not found"

    def cercaTreno(id_treno):
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaNumeroTrenoTrenoAutocomplete/"+id_treno
        response = urllib.request.urlopen(content)
        id_stazione = (str(response.read()).split("-")[-1][:-3])
        try:
            info = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/andamentoTreno/"+id_stazione+"/"+id_treno
            response = urllib.request.urlopen(info)
        except: #errore urllib (non trovato)
            return None, False, 404 #data, success, error
        content = response.read()
        data = json.loads(content.decode("utf8"))
        return data, True, None

    def cercaItinerario(stazione1, stazione2, orario):
        if orario != None:
            tempogrezzo = orario
            try:
                tempogrezzo = tempogrezzo + datetime.datetime.now().strftime(' %Y-%m-%d')
                tempo = datetime.datetime.strptime(tempogrezzo, '%H:%M %Y-%m-%d')
                tempo = tempo.strftime('%Y-%m-%dT%H:%M:%S')
            except:
                return None, False, 100 #errore
        elif orario == None:
            tempo = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        try:
            content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione1.replace(" ","%20") #TODO
            response = urllib.request.urlopen(content)
        except: #errore
            return None, False, 405
        content = response.read()
        if content == b'[]':
            return None, False, 405
        data = json.loads(content.decode("utf8"))
        id_stazione1 = (str(data[0]['id'])).split("S")[-1][:9].split("N")[-1][:9]

        try:
            content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione2.replace(" ","%20") #TODO
            response = urllib.request.urlopen(content)
        except:
            return None, False, 406
        content = response.read()
        if content == b'[]':
            return None, False, 406
        data = json.loads(content.decode("utf8"))
        id_stazione2 = (str(data[0]['id'])).split("S")[-1][:9].split("N")[-1][:9]

        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/soluzioniViaggioNew/"+id_stazione1+"/"+id_stazione2+"/"+tempo
        response = urllib.request.urlopen(content)
        content = response.read()
        data = json.loads(content.decode("utf8"))
        return data, True, None

    def cercaStatistiche():
        content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/statistiche/random"
        response = urllib.request.urlopen(content)
        content = response.read()
        data = json.loads(content.decode("utf8"))
        return data, True, None

    class stazione:
        def check(stazione):
            stazione = urllib.parse.quote(stazione)
            try:
                content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione.replace(" ","%20") #soluzione temporanea TODO
                response = urllib.request.urlopen(content)
            except Exception as e:
                return False, None
            content = response.read()
            if content == b'[]':
                return False, None

            data = json.loads(content.decode("utf8"))

            return True, data

        def informazioni(stazione):
            stazione = urllib.parse.quote(stazione)
            try:
                content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione
                response = urllib.request.urlopen(content)
            except:
                return None, False, 404
            content = response.read()
            if content == b'[]':
                return None, False, 404
            data = json.loads(content.decode("utf8"))
            id_stazione = (str(data[0]['id']))
            content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/regione/"+id_stazione
            response = urllib.request.urlopen(content)
            id_regione = response.read()
            content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/dettaglioStazione/"+id_stazione+"/"+str(id_regione.decode("utf-8"))
            response = urllib.request.urlopen(content)
            content = response.read()
            data = json.loads(content.decode("utf8"))
            return data


        def arrivi(stazione):
            stazione = urllib.parse.quote(stazione)
            try:
                content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione
                response = urllib.request.urlopen(content)
            except:
                return None, False, 404
            content = response.read()
            if content == b'[]':
                return None, False, 404
            data = json.loads(content.decode("utf8"))
            id_stazione = (str(data[0]['id']))
            datatempo = datetime.datetime.now().strftime('%a %b %d %Y %H:%M:%S GMT+0100')
            datatempo = datatempo.replace(" ","%20")
            content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/arrivi/"+id_stazione+"/"+datatempo
            response = urllib.request.urlopen(content)
            content = response.read()
            data = json.loads(content.decode("utf8"))
            return data, True, None

        def partenze(stazione):
            stazione = urllib.parse.quote(stazione)
            try:
                content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/cercaStazione/"+stazione
                response = urllib.request.urlopen(content)
            except:
                return None, False, 404
            content = response.read()
            if content == b'[]':
                return None, False, 404
            data = json.loads(content.decode("utf8"))
            id_stazione = (str(data[0]['id']))
            datatempo = datetime.datetime.now().strftime('%a %b %d %Y %H:%M:%S GMT+0100')
            datatempo = datatempo.replace(" ","%20")
            content = "http://www.viaggiatreno.it/viaggiatrenonew/resteasy/viaggiatreno/partenze/"+id_stazione+"/"+datatempo
            response = urllib.request.urlopen(content)
            content = response.read()
            data = json.loads(content.decode("utf8"))
            return data, True, None

class Messaggi:
    def erroreDB(message, error):
        message.reply("*Errore nel database*"
                    "\n_Ci scusiamo per il disagio._"
                    "\nInoltra questo messaggio *tecnico* a @MarcoBuster *[DEV]*:"
                    "`{}`".format(error))
    def treno1(data):
        orarioPartenza = datetime.datetime.fromtimestamp(data['orarioPartenza'] / 1000).strftime('%H:%M')
        orarioArrivo = datetime.datetime.fromtimestamp(data['orarioArrivo'] / 1000).strftime('%H:%M')
        try:
            oraUltimoRilevamento = datetime.datetime.fromtimestamp(data['oraUltimoRilevamento'] / 1000).strftime('%H:%M')
        except TypeError:
            oraUltimoRilevamento = "Il treno non è ancora partito"
        n_fermate = 0
        for dict in data['fermate']:
            n_fermate = n_fermate+1

        testo = ("🚅Treno {0} {1}"
            "\n🚉<b>Stazione di partenza</b>: {2} ({3})"
            "\n🚉<b>Stazione di arrivo</b>: {4} ({5})"
            "\n🕒<b>Ritardo</b>: {6}m"
            "\n🚧<b>Stazione ultimo rilevamento</b>: {7} ({8})"
            "\nℹ️<b>Numero di fermate</b>: {9}"
            .format(data['categoria'], str(data['numeroTreno']), data['origine'], orarioPartenza,
            data['destinazione'], orarioArrivo, str(data['ritardo']), data['stazioneUltimoRilevamento'],
            oraUltimoRilevamento, str(n_fermate)))
        return testo

    def arriviStazione(data, nomestazione):
        messaggio_iniziale = "<b>Arrivi della stazione di "+nomestazione+"</b>:\n"
        for k in range(0,4):
            messaggio = None
            try:
                data[k]['numeroTreno']
            except IndexError or TypeError:
                break
            sOrarioArrivoP = datetime.datetime.fromtimestamp(data[k]['orarioArrivo'] / 1000).strftime('%H:%M')
            binario = data[k]['binarioProgrammatoArrivoDescrizione']
            if data[k]['inStazione'] == False:
                inStazione = "No"
            elif data[k]['inStazione'] == True:
                inStazione == "Sì"
            messaggio = ("<i>🚅Treno {} {}</i>"
                                    "\n<b>🚉Proveniente da</b>: {}"
                                    "\n<b>🚧In stazione</b>: {}"
                                    "\n<b>🕒Ritardo</b>: {}m"
                                    "\n<b>🕰Arrivo previsto</b>: {}"
                                    "\n<b>🛤Binario</b>: {}\n\n"
                                .format(data[k]['categoria'], data[k]['numeroTreno'], data[k]['origine'], inStazione, data[k]['ritardo'], sOrarioArrivoP, str(binario)))
        if messaggio == None:
            messaggio = "\n<i>Non c'è nessun treno in arrivo in questa stazione</i>"
        testo = messaggio_iniziale + messaggio
        return testo

    def partenzeStazione(data, nomestazione):
        messaggio_iniziale = "<b>Partenze della stazione di "+nomestazione+"</b>:\n"
        for k in range(0,4):
            messaggio = None
            try:
                data[k]['numeroTreno']
            except IndexError or TypeError:
                break
            sOrarioPartenzaP = datetime.datetime.fromtimestamp(data[k]['orarioPartenza'] / 1000).strftime('%H:%M')
            binario = data[k]['binarioProgrammatoPartenzaDescrizione']
            if data[k]['inStazione'] == False:
                inStazione = "No"
            elif data[k]['inStazione'] == True:
                inStazione == "Sì"
            messaggio = ("<i>🚅Treno {} {}</i>"
                                    "\n<b>🚉Diretto a</b>: {}"
                                    "\n<b>🚧In stazione</b>: {}"
                                    "\n<b>🕒Ritardo</b>: {}m"
                                    "\n<b>🕰Partenza prevista</b>: {}"
                                    "\n<b>🛤Binario</b>: {}\n\n"
                                .format(data[k]['categoria'], data[k]['numeroTreno'], data[k]['destinazione'], inStazione, data[k]['ritardo'], sOrarioPartenzaP, str(binario)))
        if messaggio == None:
            messaggio = "\n<i>Non c'è nessun treno in partenza in questa stazione</i>"
        testo = messaggio_iniziale + messaggio
        return testo

    def itinerario(data):
        durata = data['soluzioni'][0]['durata']
        messaggio = "<b>Ho trovato questo itinerario da</b> <code>{0}</code> <b>a</b> <code>{1}</code>\n".format(data['origine'], data['destinazione'])
        n_cambi = -1
        inline_keyboard = '['
        for dict in data['soluzioni'][0]['vehicles']:
            n_cambi = n_cambi + 1
            orarioPartenza = (datetime.datetime.strptime(dict['orarioPartenza'], '%Y-%m-%dT%H:%M:%S')).strftime('%H:%M')
            orarioArrivo = (datetime.datetime.strptime(dict['orarioArrivo'], '%Y-%m-%dT%H:%M:%S')).strftime('%H:%M')
            if n_cambi > 0:
                a_capo = "\n\n🚧<b>Cambio</b>🚧\n"
            else:
                a_capo = ""
            messaggio =  messaggio + a_capo + (
                        "<b>🚅Treno {0} {1}</b>"
                        "\n<b>🚉Parte da </b><code>{2}</code><b> alle ore </b><code>{3}</code>"
                        "\n<b>🚉Arriva a </b><code>{4}</code><b> alle ore </b><code>{5}</code>".format(dict['categoriaDescrizione'], str(dict['numeroTreno']), dict['origine'], orarioPartenza, dict['destinazione'], orarioArrivo)
            )
            inline_keyboard = inline_keyboard + '[{"text":"🔍Altre informazioni sul treno '+dict['categoriaDescrizione']+" "+str(dict['numeroTreno'])+'", "callback_data": "agg@'+str(dict['numeroTreno'])+'"}],'

        inline_keyboard = inline_keyboard + '[{"text":"🔙Torna indietro", "callback_data":"home"}]]'
        return messaggio, inline_keyboard

    def listaStazioni(data):
        numero_dict = 0
        inline_keyboard = '['
        for dict in data:
            numero_dict = numero_dict + 1
            stazione = dict['nomeLungo']
            callback_data = "staz$"+dict['nomeLungo']
            inline_keyboard = inline_keyboard + '[{"text":"'+stazione+'","callback_data":"'+callback_data+'"}],'

        if numero_dict == 1:
            return 1, None

        messaggio = "<b>Ho trovato {} stazioni con quel nome</b>:".format(numero_dict)
        inline_keyboard = inline_keyboard + '[{"text":"🔙Torna indietro","callback_data":"home"}]]'
        return messaggio, inline_keyboard

    def fermata(data, numeroFermata):
        id_treno = data['numeroTreno']
        cat_treno = data['categoria']
        data = data['fermate'][int(numeroFermata)]

        Arrivo = None
        Partenza = None

        tipoFermata = data['tipoFermata'].replace("P", "stazione di partenza").replace("A", "stazione di destinazione").replace("F", "fermata intermedia")

        if data['tipoFermata'] == "P" and data['actualFermataType'] == 0: #Stazione di partenza del treno, non è ancora partito.
            orarioPartenzaTeorica = datetime.datetime.fromtimestamp(data['partenza_teorica'] / 1000).strftime('%H:%M')
            Partenza = "ℹ️Il treno è <b>previsto in partenza</b> alle ore <b>{0}</b> al <b>binario {1}</b>".format(orarioPartenzaTeorica, data['binarioProgrammatoPartenzaDescrizione'].strip())
            Arrivo = ""

        if data['tipoFermata'] == "P" and data['actualFermataType'] != 0:
            orarioPartenzaTeorica = datetime.datetime.fromtimestamp(data['partenza_teorica'] / 1000).strftime('%H:%M')
            orarioPartenzaEffettiva = datetime.datetime.fromtimestamp(data['partenzaReale'] / 1000).strftime('%H:%M')
            ritardoPartenza = data['ritardoPartenza']

            if ritardoPartenza == 1:
                ritardoPartenza = "con un <b>ritardo di 1 minuto</b>"
                emoji = "👍"
            elif ritardoPartenza == -1:
                ritardoPartenza = "in <b>anticipo di 1 minuto</b>"
                emoji = "👍"
            elif ritardoPartenza > 1:
                ritardoPartenza = "con un <b>ritardo di {} minuti</b>".format(str(ritardoPartenza))
                emoji = "❗️"
            elif ritardoPartenza < 1:
                ritardoPartenza = "in <b>anticipo di {} minuti</b>".format(str(abs(ritardoPartenza)))
                emoji = "⁉️"
            if data['ritardoPartenza'] == 0:
                ritardoPartenza = "in <b>perfetto orario</b>"
                emoji = "👌"

            if data['binarioEffettivoPartenzaDescrizione'] == None:
                binario = data['binarioProgrammatoPartenzaDescrizione'].strip()
            else:
                binario = data['binarioEffettivoPartenzaDescrizione'].strip()
            Partenza = "{3}Il treno è partito dal <b>binario {0}</b> alle ore <b>{1}</b> {2}".format(binario, orarioPartenzaEffettiva, ritardoPartenza, emoji)
            Arrivo = ""

        if data['tipoFermata'] == "F" and data['actualFermataType'] != 0: #il treno è arrivato in stazione e forse è anche partito. fermata INTERMEDIA
            orarioArrivoProgrammato = datetime.datetime.fromtimestamp(data['arrivo_teorico'] / 1000).strftime('%H:%M')
            orarioPartenzaProgrammato = datetime.datetime.fromtimestamp(data['partenza_teorica'] / 1000).strftime('%H:%M')
            if data['ritardoArrivo'] == 0:
                orarioArrivoEffettivo = orarioArrivoProgrammato
            else:
                orarioArrivoEffettivo = datetime.datetime.fromtimestamp(data['arrivoReale'] / 1000).strftime('%H:%M')
            if data['ritardoPartenza'] == 0:
                orarioPartenzaEffettiva = orarioPartenzaProgrammato
            else:
                orarioPartenzaEffettiva = datetime.datetime.fromtimestamp(data['partenzaReale'] / 1000).strftime('%H:%M')
            ritardoArrivo = data['ritardoArrivo']
            ritardoPartenza = data['ritardoPartenza']
            if data['partenzaReale'] == None: #ergo il treno non è ancora partito ed è fermo in stazione
                if ritardoArrivo == 1:
                    ritardoArrivo = "con un <b>ritardo di 1 minuto</b>"
                    emoji = "👍"
                elif ritardoArrivo == -1:
                    ritardoArrivo = "in <b>anticipo di 1 minuto</b>"
                    emoji = "👍"
                elif ritardoArrivo > 1:
                    ritardoArrivo = "con un <b>ritardo di {} minuti</b>".format(str(ritardoArrivo))
                    emoji = "❗️"
                elif ritardoArrivo < 1:
                    ritardoArrivo = "in <b>anticipo di {} minuti</b>".format(str(abs(RitardoArrivo)))
                    emoji = "⁉️"

                if data['ritardoArrivo'] == 0:
                    ritardoArrivo = "in <b>perfetto orario</b>"
                    emoji = "👌"

                if data['binarioEffettivoArrivoDescrizione'] == None:
                    binario = data['binarioProgrammatoArrivoDescrizione'].strip()
                else:
                    binario = data['binarioEffettivoArrivoDescrizione'].strip()
                Arrivo = "{3}Il treno è arrivato al <b>binario {0}</b> alle ore <b>{1}</b> {2}".format(binario, orarioArrivoEffettivo, ritardoArrivo, emoji)

                if data['binarioEffettivoPartenzaDescrizione'] == None:
                    binario = data['binarioProgrammatoPartenzaDescrizione'].strip()
                else:
                    binario = data['binarioEffettivoPartenzaDescrizione'].strip()
                Partenza = "▶️Il treno partirà dal <b>binario {0}</b> alle ore <b>{1}</b>".format(binario, orarioPartenzaProgrammato)
            else:
                if ritardoArrivo == 1:
                    ritardoArrivo = "con un <b>ritardo di 1 minuto</b>"
                    emoji = "👍"
                elif ritardoArrivo == -1:
                    ritardoArrivo = "in <b>anticipo di 1 minuto</b>"
                    emoji = "👍"
                elif ritardoArrivo > 1:
                    ritardoArrivo = "con un <b>ritardo di {} minuti</b>".format(str(ritardoArrivo))
                    emoji = "❗️"
                elif ritardoArrivo < 1:
                    ritardoArrivo = "in <b>anticipo di {} minuti</b>".format(str(abs(ritardoArrivo)))
                    emoji = "⁉️"
                if data['ritardoArrivo'] == 0:
                    ritardoArrivo = "in <b>perfetto orario</b>"
                    emoji = "👌"

                if data['binarioEffettivoArrivoDescrizione'] == None:
                    binario = data['binarioProgrammatoArrivoDescrizione'].strip()
                else:
                    binario = data['binarioEffettivoArrivoDescrizione'].strip()
                Arrivo = "{3}Il treno è arrivato al <b>binario {0}</b> alle ore <b>{1}</b> {2}".format(binario, orarioArrivoEffettivo, ritardoArrivo, emoji)
                if ritardoPartenza == 1:
                    ritardoPartenza = "con un <b>ritardo di 1 minuto</b>"
                    emoji = "👍"
                elif ritardoPartenza == -1:
                    ritardoPartenza = "in <b>anticipo di 1 minuto</b>"
                    emoji = "👍"
                elif ritardoPartenza > 1:
                    ritardoPartenza = "con un <b>ritardo di {} minuti</b>".format(str(ritardoPartenza))
                    emoji = "❗️"
                elif ritardoPartenza < 1:
                    ritardoPartenza = "in <b>anticipo di {} minuti</b>".format(str(abs(ritardoPartenza)))
                    emoji = "⁉️"
                if data['ritardoPartenza'] == 0:
                    ritardoPartenza = "in <b>perfetto orario</b>"
                    emoji = "👌"

                if data['binarioEffettivoPartenzaDescrizione'] == None:
                    binario = data['binarioProgrammatoPartenzaDescrizione'].strip()
                else:
                    binario = data['binarioEffettivoPartenzaDescrizione'].strip()
                Partenza = "{3}Il treno è partito dal <b>binario {0}</b> alle ore <b>{1}</b> {2}".format(binario, orarioPartenzaEffettiva, ritardoPartenza, emoji)

        if data['tipoFermata'] == "F" and data['actualFermataType'] == 0: #Il treno non è ancora arrivato alla stazione INTERMEDIA x
            orarioArrivoTeorica = datetime.datetime.fromtimestamp(data['arrivo_teorico'] / 1000).strftime('%H:%M')
            Arrivo = "ℹ️Il treno è <b>previsto in arrivo</b> alle ore <b>{0}</b> al <b>binario {1}</b>".format(orarioArrivoTeorica, data['binarioProgrammatoArrivoDescrizione'])
            orarioPartenzaTeorica = datetime.datetime.fromtimestamp(data['partenza_teorica'] / 1000).strftime('%H:%M')
            Partenza = "ℹ️Il treno è <b>previsto in partenza</b> alle ore <b>{0}</b> al <b>binario {1}</b>".format(orarioPartenzaTeorica, data['binarioProgrammatoPartenzaDescrizione'])


        if data['tipoFermata'] == "A" and data['actualFermataType'] != 0: #Il treno è arrivato alla stazione di arrivo finale x
            orarioArrivoTeorica = datetime.datetime.fromtimestamp(data['arrivo_teorico'] / 1000).strftime('%H:%M')
            if data['ritardoArrivo'] == 0:
                orarioArrivoEffettiva = orarioArrivoTeorica
            else:
                orarioArrivoEffettiva = datetime.datetime.fromtimestamp(data['arrivoReale'] / 1000).strftime('%H:%M')
            ritardoArrivo = data['ritardoArrivo']
            if ritardoArrivo == 1:
                ritardoArrivo = "con un <b>ritardo di 1 minuto</b>"
                emoji = "👍"
            elif ritardoArrivo == -1:
                ritardoArrivo = "in <b>anticipo di 1 minuto</b>"
                emoji = "👍"
            elif ritardoArrivo > 1:
                ritardoArrivo = "con un <b>ritardo di {} minuti</b>".format(str(ritardoArrivo))
                emoji = "❗️"
            elif ritardoArrivo < 1:
                ritardoArrivo = "in <b>anticipo di {} minuti</b>".format(str(abs(ritardoArrivo)))
                emoji = "⁉️"

            if data['ritardoArrivo'] == 0:
                ritardoArrivo = "in <b>perfetto orario</b>"
                emoji = "👌"

            if data['binarioEffettivoArrivoDescrizione'] == None:
                binario = data['binarioProgrammatoArrivoDescrizione'].strip()
            else:
                binario = data['binarioEffettivoArrivoDescrizione'].strip()
            Arrivo = "{3}Il treno è partito dal <b>binario {0}</b> alle ore <b>{1}</b> {2}".format(data['binarioEffettivoArrivoDescrizione'], orarioArrivoEffettiva, ritardoArrivo, emoji)
            Partenza = ""

        if data['tipoFermata'] == "A" and data['actualFermataType'] == 0:
            orarioArrivoTeorica = datetime.datetime.fromtimestamp(data['arrivo_teorico'] / 1000).strftime('%H:%M')
            Arrivo = "ℹ️Il treno è <b>previsto in arrivo</b> alle ore <b>{0}</b> al <b>binario {1}</b>".format(orarioArrivoTeorica, data['binarioProgrammatoArrivoDescrizione'].strip())
            Partenza = ""

        actualFermataType = data['actualFermataType']
        if actualFermataType == 0 or actualFermataType == 1:
            actualFermataType = ""
        elif actualFermataType == 2:
            actualFermataType = "\n❗️<b>Fermata non prevista</b>"
        elif actualFermataType == 3:
            actualFermataType = "\n‼️<b>Fermata soppressa</b>"

        ritardoArrivo, ritardoPartenza = data['ritardoArrivo'], data['ritardoPartenza']

        if Arrivo == None and Partenza == None and data['actualFermataType'] == 0:
            messaggio = ("<b>Errore sconosciuto</b>"
                        "\n<i>Un errore delle ferrovie dello Stato o del bot?</i>"
                        "\nNel dubbio, inoltra questo messaggio allo sviluppatore (@MarcoBuster) o esegui il comando /feedback"
                        "\n<b>Numero treno</b>: <code>{0}</code>"
                        "\n<b>ID stazione</b>: <code>{1}</code>"
                        "\n<b>Informazioni dell'arrivo</b>: <code>None</code>"
                        "\n<b>Informazioni di partenza</b>: <code>None</code>"
                        "\n<b>actualFermataType</b>: <code>{2}</code>"
                        "\n\n<i>Non arrabiarti con lo sviluppatore o lasciare recensioni negative, tu non immagini nemmeno quante variabili ci sono in ballo e quanto i dati di Trenitalia siano sballati a volte😢</i>" #A sad but true story
                        "\nGuarda il codice su GitHub, se non ci credi: www.github.com/MarcoBuster/OrarioTreniBot.".format(str(id_treno), str(numeroFermata), str(data['actualFermataType']))
            )
            return messaggio

        if Arrivo == None and Partenza == None:
            messaggio = (
                "<b>ℹ️Informazioni del treno {0} {1} rispetto alla fermata {2}</b>\n".format(cat_treno, id_treno, data['stazione'])
                +actualFermataType
                )
            return messaggio
        else:
            messaggio = (
                    "<b>ℹ️Informazioni del treno {0} {1} rispetto alla fermata {2}</b>\n".format(cat_treno, id_treno, data['stazione'])
                    +Arrivo+ ("\n" if Arrivo != "" else "")
                    +Partenza+ ("\n" if Partenza != "" else "")
                    +actualFermataType
            )
            return messaggio

    def statistiche(data):
        messaggio = ("<b>Statistiche dei treni circolanti</b>:"
                    "\n<b>🚅Treni oggi</b>: {}"
                    "\n<b>🚅Treni circolanti in questo momento</b>: {}"
                    "\n<b>✅Versione del bot</b>: <code>3.0 OPEN ALPHA</code>".format(str(data['treniGiorno']), str(data['treniCircolanti'])))

        return messaggio
