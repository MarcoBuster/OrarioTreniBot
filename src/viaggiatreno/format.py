# Copyright (c) 2016-2017 Marco Aceti <dev@marcoaceti.it>
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

from datetime import datetime

import wikipedia
from wikipedia.exceptions import PageError

import re

from . import dateutils
from . import viaggiatreno

utils = viaggiatreno.Utils()

wikipedia.set_lang("it")

ELEMENTS_FOR_PAGE = 5


def _generateTrainCallbackQuery(raw: dict):
    return "train@" + raw['idOrigine'] + "_" + str(raw['numeroTreno'])


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
        status += ' a {o} (in partenza)'.format(o=raw.get('origine'))
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


def cleanHTML(string: str):
    cleaner = re.compile('<.*?>')
    return re.sub(cleaner, '', string)


def getWikipediaSummary(station: str):
    try:
        result = wikipedia.summary("Stazione di {station}".format(station=station))
    except PageError:
        return "Nessuna informazione aggiuntiva disponibile"
    return cleanHTML(result) + " (da Wikipedia, l'enciclopedia libera)"


def formatStation(station: str):
    text = (
        "🚉 <b>Stazione di {name}</b>"
        "\nℹ️ <i>{wikipedia}</i>"
        .format(name=station.title(),
                wikipedia=getWikipediaSummary(station))
    )
    return text


def getPagesCount(raw: dict):
    x = 0
    for element in raw:
        del element
        x += 1

    return {'first': 0, 'last': x}


def generateStationPagesInlineKeyboard(current_range: list, pages_count: dict, station: str, kind: str, ):
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

        if train['binarioProgrammatoPartenzaDescrizione'] != train['binarioEffettivoPartenzaDescrizione'] and \
                train['binarioProgrammatoPartenzaDescrizione'] and train['binarioEffettivoPartenzaDescrizione']:
            binary = "{x} (invece di binario {y})".format(x=train['binarioEffettivoPartenzaDescrizione'].strip(),
                                                          y=train['binarioProgrammatoPartenzaDescrizione'].strip())

        elif (train['binarioProgrammatoPartenzaDescrizione'] == train['binarioEffettivoPartenzaDescrizione'] and
                train['binarioProgrammatoPartenzaDescrizione'] and train['binarioEffettivoPartenzaDescrizione']) or \
                (train['binarioProgrammatoPartenzaDescrizione'] and not train['binarioEffettivoPartenzaDescrizione']):
            binary = train['binarioProgrammatoPartenzaDescrizione'].strip()

        elif not (train['binarioProgrammatoPartenzaDescrizione'] and train['binarioEffettivoPartenzaDescrizione'] and
                  train['inStazione']):
            binary = "<i>sconosciuto</i>"

        else:
            binary = "<i>sconosciuto</i> (errore Trenitalia)"

        text += (
            "\n\n➖➖ <b>Treno {n}</b>"
            "\n🚉 <b>Destinazione</b>: {d}"
            "\n🛤 <b>Binario</b>: {b}"
            "\n🕒 <b>Orario di partenza</b>: {dt}"
            "\n🕘 <b>Ritardo</b>: {r}m"
            "\n⏺ <b>Stato</b>: {st}"
            .format(n=train['compNumeroTreno'], d=train['destinazione'], b=binary, dt=train['compOrarioPartenza'],
                    r=train['ritardo'], st='in partenza' if train['inStazione'] else 'partito')
        )
        x += 1

    if x == 0:
        text += "\n<i>Nessun treno in arrivo</i>"
    return text


def formatArrivals(raw: dict, station: str, xrange: int):
    last = getPagesCount(raw)['last']
    text = "🚦 <b>Arrivi nella stazione di {station}</b>".format(station=utils.station_from_ID(station))
    text += "\n<i>Pagina {x}</i>)".format(x=(xrange // ELEMENTS_FOR_PAGE))
    x = 0
    for train in raw:
        if x > last:
            break

        if x < (xrange - ELEMENTS_FOR_PAGE):
            x += 1
            continue

        if x == xrange:
            break

        if train['binarioProgrammatoArrivoDescrizione'] != train['binarioEffettivoArrivoDescrizione'] and \
                train['binarioProgrammatoArrivoDescrizione'] and train['binarioEffettivoArrivoDescrizione']:
            binary = "{x} (invece di binario {y})".format(x=train['binarioEffettivoArrivoDescrizione'].strip(),
                                                          y=train['binarioProgrammatoArrivoDescrizione'].strip())

        elif (train['binarioProgrammatoArrivoDescrizione'] == train['binarioEffettivoArrivoDescrizione'] and
                train['binarioProgrammatoArrivoDescrizione'] and train['binarioEffettivoArrivoDescrizione']) or \
                (train['binarioProgrammatoArrivoDescrizione'] and not train['binarioEffettivoArrivoDescrizione']):
            binary = train['binarioProgrammatoArrivoDescrizione'].strip()

        elif not (train['binarioProgrammatoArrivoDescrizione'] and train['binarioEffettivoArrivoDescrizione'] and
                  train['inStazione']):
            binary = "<i>sconosciuto</i>"

        else:
            binary = "<i>sconosciuto</i> (errore Trenitalia)"

        text += (
            "\n\n➖➖ <b>Treno {n}</b>"
            "\n🚉 <b>Origine</b>: {d}"
            "\n🛤 <b>Binario</b>: {b}"
            "\n🕒 <b>Orario di arrivo</b>: {dt}"
            "\n🕘 <b>Ritardo</b>: {r}m"
            "\n⏺ <b>Stato</b>: {st}"
            .format(n=train['compNumeroTreno'], d=train['origine'], b=binary, dt=train['compOrarioArrivo'],
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

    x = 0
    for solution in raw['soluzioni']:
        if x == 5:
            break

        x += 1
        text += "\n\n➖➖ <b>Soluzione {n}</b>".format(n=x)
        text += "\n🕑 <b>Durata</b>: {t}".format(t=solution['durata'])
        for vehicle in solution['vehicles']:
            start_time = datetime.strptime(vehicle['orarioPartenza'], '%Y-%m-%dT%H:%M:%S').strftime('%H:%M')
            end_time = datetime.strptime(vehicle['orarioArrivo'], '%Y-%m-%dT%H:%M:%S').strftime('%H:%M')

            text += "\n➖ <b>Treno {n}</b>".format(n=vehicle['numeroTreno'])
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

        rail = stop['binarioEffettivoArrivoDescrizione'] or stop['binarioEffettivoPartenzaDescrizione'] \
            or stop['binarioProgrammatoArrivoDescrizione'] or stop['binarioProgrammatoPartenzaDescrizione'] \
            or "errore Trenitalia"

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
            "🚉 <b>Informazioni del treno {train} rispetto alla fermata {station}</b>"
            "{arrival}"
            "{departure}"
            "\n🛤 <b>Binario</b>: {rail}"
            .format(
                train=raw['compNumeroTreno'],
                station=stop['stazione'],
                arrival="\n🚥 <b>Arrivo</b>: {arrival}".format(arrival=arrival) if arrival else "",
                departure="\n🚥 <b>Partenza</b>: {departure}".format(departure=departure) if departure else "",
                rail=rail
            )
        )
        return text


def generateTrainStopInlineKeyboard(raw: dict, stop_number: int):
    x = 0
    inline_keyboard = []
    for stop in raw['fermate']:
        if x != stop_number:
            x += 1
            continue

        first = 0
        current = x
        last = len(raw['fermate']) - 1

        if current == first:
            inline_keyboard = [[
                {"text": "▶️ " + raw['fermate'][x + 1]['stazione'],
                 "callback_data": _generateTrainCallbackQuery(raw) + "@stop@" + str(x + 1)}
            ]]

        elif current == last:
            inline_keyboard = [[
                {"text": "◀️ " + raw['fermate'][x - 1]['stazione'],
                 "callback_data": _generateTrainCallbackQuery(raw) + "@stop@" + str(x - 1)}
            ]]

        else:
            inline_keyboard = [[
                {"text": "◀️ " + raw['fermate'][x - 1]['stazione'],
                 "callback_data": _generateTrainCallbackQuery(raw) + "@stop@" + str(x - 1)},
                {"text": "▶️ " + raw['fermate'][x + 1]['stazione'],
                 "callback_data": _generateTrainCallbackQuery(raw) + "@stop@" + str(x + 1)}
            ]]

        inline_keyboard.append(
            [{"text": "🔍 Stazione di " + raw['fermate'][x]['stazione'],
              "callback_data": "station@" + raw['fermate'][x]['id'] + "@send"}]
        )
        inline_keyboard.append(
            [{"text": "⬅️ Torna indietro", "callback_data": _generateTrainCallbackQuery(raw) + "@stops"}]
        )

    return inline_keyboard
