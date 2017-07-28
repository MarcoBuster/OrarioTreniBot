# Copyright (c) 2016-2017 The OrarioTreniBot Authors (see AUTHORS)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import base64
import json
import os
import random
import re
import string
from datetime import datetime

import botogram
import plotly
import plotly.graph_objs as go
import plotly.plotly as py
import pyowm
import wikipedia
from PIL import Image
from wikipedia.exceptions import PageError

import config
from . import dateutils
from . import viaggiatreno

api = viaggiatreno.API()
utils = viaggiatreno.Utils()
bot = botogram.create(config.BOT_TOKEN)
owm = pyowm.OWM(config.OWM_API_KEY)
plotly.tools.set_credentials_file(username=config.PLOTLY_USERNAME, api_key=config.PLOTLY_API_KEY)

wikipedia.set_lang("it")

ELEMENTS_FOR_PAGE = 5


def generateTrainCallbackQuery(raw: dict):
    if raw.get('idOrigine'):
        return "train@" + raw['idOrigine'] + "_" + str(raw['numeroTreno'])

    elif raw.get('codOrigine'):
        return "train@" + raw['codOrigine'] + "_" + str(raw['numeroTreno'])

    else:
        train_number = raw['numeroTreno']
        stop_station = raw['origine']

        results = api.call("cercaNumeroTrenoTrenoAutocomplete", train_number)
        if len(results) == 0:
            return False

        if len(results) == 1:
            return "train@" + results[0][1] + "_" + str(raw['numeroTreno'])

        if len(results) > 1:
            for result in results:
                train = api.call("andamentoTreno", result[1], train_number)
                for stop in train['fermate']:
                    if stop['stazione'].lower() == stop_station:
                        return "train@" + train['idOrigine'] + "_" + str(raw['numeroTreno'])
            return "train@" + results[0][1] + "_" + str(raw['numeroTreno'])


def generateStationCallbackQuery(raw: dict):
    return "station@" + raw['id']


def generateDeepLinkingHREF(query: str, text: str = "più informazioni"):
    if not query:
        return "<i>altre informazioni non disponibili</i>"

    url = "https://t.me/{username}?start={query}".format(username=bot.itself.username,
                                                         query=base64.b64encode(bytes(query, "utf-8")).decode("utf-8"))
    href = "<a href=\"{url}\">{text}</a>".format(url=url, text=text)
    return href

gTCQ = generateTrainCallbackQuery
gSCQ = generateStationCallbackQuery
gDLHREF = generateDeepLinkingHREF


def getWeather(station_id: str):
    path = os.getcwd() + '/'.join(['', 'data', 'viaggiatreno', 'stations_coords.json'])
    with open(path, 'r') as fp:
        station_coords = json.load(fp)

    if station_id not in station_coords:
        return ""

    code = owm.weather_at_coords(station_coords[station_id]["lat"], station_coords[station_id]["lon"])\
        .get_weather().get_weather_code()

    path = os.getcwd() + '/'.join(['', 'data', 'owm', 'weather_codes_it.json'])
    with open(path, 'r') as fp:
        weather_codes = json.load(fp)

    return weather_codes[str(code)]


def formatTrain(raw: dict):
    dh = dateutils.format_timestamp(raw.get('orarioPartenza'), fmt="%H:%M")
    ah = dateutils.format_timestamp(raw.get('orarioArrivo'), fmt="%H:%M")

    delay = raw['ritardo']
    if delay == 1:
        status = '\n🕒 <b>In ritardo di {x} minuto</b>'.format(x=delay)
    elif delay > 1:
        status = '\n🕒 <b>In ritardo di {x} minuti</b>'.format(x=delay)
    elif delay < 0:
        status = '\n🕒 <b>In anticipo di {x} minuti</b>'.format(x=abs(delay))
    else:
        status = '\n🕒 <b>In perfetto orario</b>'

    last_detection = raw['stazioneUltimoRilevamento']
    if last_detection in ['--', None] or last_detection == raw.get('origine'):
        status = '\n🕒 <b>Non ancora partito</b>'
    elif last_detection == raw.get('destinazione'):
        status += ' a {d} (arrivato a destinazione)'.format(d=last_detection)
    else:
        status += ' a {l} ({h})'.format(l=last_detection,
                                        h=dateutils.format_timestamp(raw.get('oraUltimoRilevamento'), fmt="%H:%M"))

    return (
        "🚅 <b>Treno {n}</b>"
        "\n🚉 <b>Stazione di partenza</b>: {d} ({dh})"
        "\n🚉 <b>Stazione di arrivo</b>: {a} ({ah})"
        "{s}"
        .format(n=raw.get('compNumeroTreno'),
                d=raw.get('origine'), dh=dh,
                a=raw.get('destinazione'), ah=ah,
                s=status)
    )


def cleanHTML(_string: str):
    cleaner = re.compile('<.*?>')
    return re.sub(cleaner, '', _string)


def getWikipediaSummary(station: str):
    try:
        result = wikipedia.summary("Stazione di {station}".format(station=station))
    except PageError:
        return "Nessuna informazione aggiuntiva disponibile"
    return cleanHTML(result) + " (da Wikipedia, l'enciclopedia libera)"


def formatStation(station: str, station_id: str, withWikiSummary=False):
    if withWikiSummary:
        text = (
            "🚉 <b>Stazione di {name}</b>"
            "\nℹ️ <i>{wikipedia}</i>"
            "\n\n{weather}"
            .format(name=station.title(),
                    wikipedia=getWikipediaSummary(station),
                    weather=getWeather(station_id=station_id))
        )
        return text
    else:
        text = (
            "🚉 <b>Stazione di {name}</b>"
            "\n<i>Premi il tasto sotto per mostrare le informazioni da Wikipedia</i>"
            "\n\n{weather}"
            .format(name=station.title(), weather=getWeather(station_id=station_id))
        )
        return text


def getPagesCount(raw: dict):
    x = 0
    for element in raw:
        del element
        x += 1

    return {'first': 0, 'last': x}


def generateStationPagesInlineKeyboard(current_range: list, pages_count: dict, station: str, kind: str):
    start = current_range[0]
    first = pages_count['first']
    end = current_range[1]
    last = pages_count['last']

    inline_keyboard = [[
        {"text": "⏮", "callback_data": "station@" + station + "@" + kind + "@" + str(first + ELEMENTS_FOR_PAGE)},
        {"text": "◀️", "callback_data": "station@" + station + "@" + kind + "@" + str(start)},
        {"text": "▶️", "callback_data": "station@" + station + "@" + kind + "@" + str(end + ELEMENTS_FOR_PAGE)},
        {"text": "⏭", "callback_data": "station@" + station + "@" + kind + "@" + str(last)}
    ],
        [
        {"text": "⬅️ Torna indietro", "callback_data": "station@" + station}
    ]]

    if start == first and end >= last:
        del inline_keyboard[0]
        return inline_keyboard

    if start == first:
        del inline_keyboard[0][0]
        del inline_keyboard[0][0]

    if end >= last:
        del inline_keyboard[0][2]
        del inline_keyboard[0][2]

    return inline_keyboard


def formatDepartures(raw: dict, station: str, xrange: int):
    last = getPagesCount(raw)['last']
    text = "🚦 <b>Partenze nella stazione di {station}</b>".format(station=utils.station_from_ID(station))
    text += "\n<i>Pagina {x}</i>".format(x=(xrange // ELEMENTS_FOR_PAGE))
    x = 0
    for train in raw:
        if x > last:
            break

        if x < (xrange - ELEMENTS_FOR_PAGE):
            x += 1
            continue

        if x == xrange:
            break

        platform = "<i>sconosciuto</i> (errore Trenitalia)"

        if train['binarioProgrammatoPartenzaDescrizione'] and train['binarioEffettivoPartenzaDescrizione']:
            if train['binarioProgrammatoPartenzaDescrizione'].strip() != train['binarioEffettivoPartenzaDescrizione'].strip():
                platform = "{x} (invece di binario {y})".format(x=train['binarioEffettivoPartenzaDescrizione'].strip(),
                                                                y=train['binarioProgrammatoPartenzaDescrizione'].strip())

            elif train['binarioProgrammatoPartenzaDescrizione'].strip() == train['binarioEffettivoPartenzaDescrizione'].strip():
                platform = train['binarioProgrammatoPartenzaDescrizione'].strip()

        elif train['binarioProgrammatoPartenzaDescrizione'] and not train['binarioEffettivoPartenzaDescrizione']:
            platform = train['binarioProgrammatoPartenzaDescrizione'].strip()

        elif not (train['binarioProgrammatoPartenzaDescrizione'] and train['binarioEffettivoPartenzaDescrizione'] and
                  train['inStazione']):
            platform = "<i>sconosciuto</i>"

        else:
            platform = "<i>sconosciuto</i> (errore Trenitalia)"

        text += (
            "\n\n➖➖ <b>Treno {n}</b> ({href})"
            "\n🚉 <b>Destinazione</b>: {d}"
            "\n🛤 <b>Binario</b>: {b}"
            "\n🕒 <b>Orario di partenza</b>: {dt}"
            "\n🕘 <b>Ritardo</b>: {r}m"
            "\n⏺ <b>Stato</b>: {st}"
            .format(n=train['compNumeroTreno'], href=gDLHREF(gTCQ(train)),
                    d=train['destinazione'], b=platform, dt=train['compOrarioPartenza'],
                    r=train['ritardo'], st='in partenza' if train['inStazione'] else 'partito')
        )
        x += 1

    if x == 0:
        text += "\n<i>Nessun treno in partenza</i>"
    return text


def formatArrivals(raw: dict, station: str, xrange: int):
    last = getPagesCount(raw)['last']
    text = "🚦 <b>Arrivi nella stazione di {station}</b>".format(station=utils.station_from_ID(station))
    text += "\n<i>Pagina {x}</i>".format(x=(xrange // ELEMENTS_FOR_PAGE))
    x = 0
    for train in raw:
        if x > last:
            break

        if x < (xrange - ELEMENTS_FOR_PAGE):
            x += 1
            continue

        if x == xrange:
            break

        platform = "<i>sconosciuto</i> (errore Trenitalia)"

        if train['binarioProgrammatoArrivoDescrizione'] and train['binarioEffettivoArrivoDescrizione']:
            if train['binarioProgrammatoArrivoDescrizione'].strip() != train['binarioEffettivoArrivoDescrizione'].strip():
                platform = "{x} (invece di binario {y})".format(x=train['binarioEffettivoArrivoDescrizione'].strip(),
                                                                y=train['binarioProgrammatoArrivoDescrizione'].strip())

            elif train['binarioProgrammatoArrivoDescrizione'].strip() == train['binarioEffettivoArrivoDescrizione'].strip():
                platform = train['binarioProgrammatoArrivoDescrizione'].strip()

        elif train['binarioProgrammatoArrivoDescrizione'] and not train['binarioEffettivoArrivoDescrizione']:
            platform = train['binarioProgrammatoArrivoDescrizione'].strip()

        elif not (train['binarioProgrammatoArrivoDescrizione'] and train['binarioEffettivoArrivoDescrizione'] and
                  train['inStazione']):
            platform = "<i>sconosciuto</i>"

        else:
            platform = "<i>sconosciuto</i> (errore Trenitalia)"

        text += (
            "\n\n➖➖ <b>Treno {n}</b> ({href})"
            "\n🚉 <b>Origine</b>: {d}"
            "\n🛤 <b>Binario</b>: {b}"
            "\n🕒 <b>Orario di arrivo</b>: {dt}"
            "\n🕘 <b>Ritardo</b>: {r}m"
            "\n⏺ <b>Stato</b>: {st}"
            .format(n=train['compNumeroTreno'], href=gDLHREF(gTCQ(train)),
                    d=train['origine'], b=platform, dt=train['compOrarioArrivo'],
                    r=train['ritardo'], st='in arrivo' if not train['inStazione'] else 'arrivato')
        )
        x += 1

    if x == 0:
        text += "\n<i>Nessun treno in arrivo</i>"
    return text


def formatItinerary(raw: dict):
    text = (
        "<b>🛤 Cerca treno</b> per itinerario"
        "\n<i>Soluzioni di viaggio da {p} a {a}</i>"
        .format(p=raw['origine'], a=raw['destinazione'])
    )

    if not raw['soluzioni']:
        text += "\n<i>Nessuna soluzione trovata</i>"
        return text

    x = 0
    for solution in raw['soluzioni']:
        if x == 5:
            break

        x += 1
        text += "\n\n➖➖ <b>Soluzione {n}</b>".format(n=x)
        duration = solution.get('durata', '<i>sconosciuta</i>')
        text += "\n🕑 <b>Durata</b>: {t}".format(t=duration if duration is not None else '<i>sconosciuta</i>')
        for vehicle in solution['vehicles']:
            start_time = datetime.strptime(vehicle['orarioPartenza'], '%Y-%m-%dT%H:%M:%S').strftime('%H:%M')
            end_time = datetime.strptime(vehicle['orarioArrivo'], '%Y-%m-%dT%H:%M:%S').strftime('%H:%M')

            text += "\n➖ <b>Treno {n}</b> ({href})".format(n=vehicle['numeroTreno'], href=gDLHREF(gTCQ(vehicle)))
            text += "\n🚉 <b>Stazione di partenza</b>: {d} ({dh})".format(d=vehicle['origine'], dh=start_time)
            text += "\n🚉 <b>Stazione di arrivo</b>: {a} ({ah})".format(a=vehicle['destinazione'], ah=end_time)

    return text


def formatNews(raw: dict):
    def __toBool(__str: str) -> bool:
        return True if __str == "true" else False

    header = "📰 <b>Ultime news da viaggiatreno.it</b>"
    if not raw:
        return header + "\n<i>Nessuna news disponibile al momento</i>"

    text = header
    for news in raw:  # First pinned news
        if not __toBool(news['primoPiano']):
            continue
        text += (
            "\n\n{pinned}➖➖ <b>{title}</b>"
            "\n<b>Data</b>: {date}"
            "\n{text}"
            .format(
                pinned="📌",
                title=news['titolo'],
                date=dateutils.format_timestamp(news['data'], "%d/%m/%y %H:%M"),
                text=news['testo']
            )
        )

    for news in raw:  # Second not pinned news
        if __toBool(news['primoPiano']):
            continue

        text += (
            "\n\n{pinned}➖➖ <b>{title}</b>"
            "\n<b>Data</b>: {date}"
            "\n{text}"
            .format(
                pinned="",
                title=news['titolo'],
                date=dateutils.format_timestamp(news['data'], "%d/%m/%y %H:%M"),
                text=news['testo']
            )
        )

    return text


def getStopsInlineKeyboard(raw: dict, cb_query: str):
    inline_keyboard = []
    x = 0
    for stop in raw['fermate']:
        inline_keyboard.append([
            {"text": "🚉 " + stop["stazione"], "callback_data": cb_query.replace("stops", "stop") + "@" + str(x)}
        ])
        x += 1

    inline_keyboard.append([
        {"text": "⬅️ Torna indietro", "callback_data": cb_query.rstrip("stops")}
    ])
    return inline_keyboard


def formatTrainStop(raw: dict, stop_number: int):
    x = 0
    for stop in raw['fermate']:
        if x != stop_number:
            x += 1
            continue

        if stop['tipoFermata'] == "P":
            format_arrival = False
            format_departure = True

        elif stop['tipoFermata'] == "F":
            format_arrival = True
            format_departure = True

        elif stop['tipoFermata'] == "A":
            format_arrival = True
            format_departure = False

        else:
            return "ERROR (TODO)"

        arrival = ""
        departure = ""

        platform = stop['binarioEffettivoArrivoDescrizione'] or stop['binarioEffettivoPartenzaDescrizione'] \
            or stop['binarioProgrammatoArrivoDescrizione'] or stop['binarioProgrammatoPartenzaDescrizione'] \
            or "<i>sconosciuto</i>"

        if format_arrival:
            if stop['arrivoReale']:
                arrival = "<b>{p}</b> (arrivato alle {e})".format(
                    p=dateutils.format_timestamp(stop['arrivo_teorico'], "%H:%M"),
                    e=dateutils.format_timestamp(stop['arrivoReale'], "%H:%M"),
                    r=stop['ritardoArrivo']
                )
            else:
                arrival = "<b>{p}</b>".format(p=dateutils.format_timestamp(stop['arrivo_teorico'], "%H:%M"))

        if format_departure:
            if stop['partenzaReale']:
                departure = "<b>{p}</b> (partito alle {e})".format(
                    p=dateutils.format_timestamp(stop['partenza_teorica'], "%H:%M"),
                    e=dateutils.format_timestamp(stop['partenzaReale'], "%H:%M"),
                )
            else:
                departure = "<b>{p}</b>".format(p=dateutils.format_timestamp(stop['partenza_teorica'], "%H:%M"))

        text = (
            "🚉 <b>Informazioni del treno {train} rispetto alla fermata {station}</b> ({href})"
            "{arrival}"
            "{departure}"
            "\n🛤 <b>Binario</b>: {platform}"
            "\n{weather}"
            .format(
                train=raw['compNumeroTreno'],
                station=stop['stazione'], href=gDLHREF(gSCQ(stop), "più informazioni sulla stazione"),
                arrival="\n🚥 <b>Arrivo</b>: {arrival}".format(arrival=arrival) if arrival else "",
                departure="\n🚥 <b>Partenza</b>: {departure}".format(departure=departure) if departure else "",
                platform=platform,
                weather=getWeather(stop['id']),
            )
        )
        return text


def generateTrainStopInlineKeyboard(raw: dict, stop_number: int):
    x = 0
    inline_keyboard = []
    for stop in raw['fermate']:
        del stop

        if x != stop_number:
            x += 1
            continue

        first = 0
        current = x
        last = len(raw['fermate']) - 1

        if current == first:
            inline_keyboard = [[
                {"text": "▶️ " + raw['fermate'][x + 1]['stazione'],
                 "callback_data": gTCQ(raw) + "@stop@" + str(x + 1)}
            ]]

        elif current == last:
            inline_keyboard = [[
                {"text": "◀️ " + raw['fermate'][x - 1]['stazione'],
                 "callback_data": gTCQ(raw) + "@stop@" + str(x - 1)}
            ]]

        else:
            inline_keyboard = [[
                {"text": "◀️ " + raw['fermate'][x - 1]['stazione'],
                 "callback_data": gTCQ(raw) + "@stop@" + str(x - 1)},
                {"text": "▶️ " + raw['fermate'][x + 1]['stazione'],
                 "callback_data": gTCQ(raw) + "@stop@" + str(x + 1)}
            ]]

        inline_keyboard.append(
            [{"text": "⬅️ Torna indietro", "callback_data": gTCQ(raw) + "@stops"}]
        )

    return inline_keyboard


def generateTrainGraph(raw: dict):
    def apply(a, b):
        base = Image.open(a)
        logo = Image.open(b)
        logo.thumbnail((120, 120), Image.ANTIALIAS)
        base.paste(logo, (580, 5), mask=logo)
        base.save(a)

    stops = []
    delays = []

    for stop in raw['fermate']:
        if stop['actualFermataType'] == 0:
            break

        stops += [stop['stazione']]
        delays += [stop['ritardo']]

    if len(stops) < 2 or len(delays) < 2:
        return False

    line = go.Scatter(
        x=stops,
        y=delays,
        name='Ritardo',
        line=dict(
            color='rgb(205, 12, 24)',
            width=2,
        )
    )

    title = '<b>Ritardo del treno {train}</b>'.format(train=raw['compNumeroTreno'])
    layout = dict(
        title=title,
        xaxis=dict(title='Fermata'),
        yaxis=dict(title='Ritardo (minuti)')
    )

    filename = os.getcwd() + ''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10)) + '.png'

    fig = dict(data=[line], layout=layout)
    py.image.save_as(fig, filename=filename)

    apply(filename, os.getcwd() + "/data/img/logo_white_with_name.png")
    return filename
