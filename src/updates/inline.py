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

import random
import string
from datetime import datetime
from urllib.error import HTTPError

from ..viaggiatreno import viaggiatreno, format


def _gen_ran_string(string_len: int = 16):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(string_len))


def process_inline_query(bot, iq, u):
    def minifyStation(__str):
        __str = __str[1:]
        n = 0
        for i in __str:
            if i != "0":
                __str = __str[n:]
                break
            n += 1
        return __str

    def default_answer():
        iq.answer(
            results=[
                {
                    "type": "article",
                    "id": _gen_ran_string(),
                    "title": "❇️ Orario Treni in tutte le chat!",
                    "description": "👉 Clicca qui per scoprire come usare Orario Treni in qualsiasi chat!",
                    "input_message_content": {
                        "message_text": (
                            "❇️ <b>Usa Orario Treni in tutte le chat!</b>"
                            "\n⏺ <i>Cerca treni, stazioni e itinerari in qualsiasi chat</i>"
                            "\nPer usare questa funzione basta che scrivi <code>@{username} query</code> in qualsiasi chat: "
                            "si aprirà un pop-up da dove potrai selezionare il risultato desiderato."
                            "\n➖➖️ <b>Cerca treni e stazioni</b>"
                            "\nScrivi il <b>numero del treno</b> o il <b>nome della stazione</b>, "
                            "per esempio <code>@{username} 9650</code> o <code>@{username} Roma Termini</code>"
                            "\n➖➖️ <b>Cerca itinerari</b>"
                            "\nScrivi la <b>stazione di partenza</b>, un <b>trattino -</b> e la <b>stazione di arrivo</b>: "
                            "per esempio <code>@{username} Milano Centrale - Roma Termini</code>"
                            "\n<i>Gli itinerari cercati inline sono basati sull'orario attuale</i>"
                            .format(username=bot.itself.username)
                        ),
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    },
                    "reply_markup": {
                        "inline_keyboard": [
                            [{"text": "➡️ Orario Treni", "url": "https://t.me/OrarioTreniBot"}]
                        ]
                    },
                    "thumb_url": "http://i.imgur.com/hp9QUXx.png",
                }
            ]
        )

    def not_found_answer():
        iq.answer(
            results=[
                {
                    "type": "article",
                    "id": _gen_ran_string(),
                    "title": "❌ Non trovato",
                    "description": "👉 Clicca qui per scoprire come usare Orario Treni in qualsiasi chat!",
                    "input_message_content": {
                        "message_text": (
                            "❇️ <b>Usa Orario Treni in tutte le chat!</b>"
                            "\n⏺ <i>Cerca treni, stazioni e itinerari in qualsiasi chat</i>"
                            "\nPer usare questa funzione basta che scrivi <code>@{username} query</code> in qualsiasi chat: "
                            "si aprirà un pop-up da dove potrai selezionare il risultato desiderato."
                            "\n➖➖️ <b>Cerca treni e stazioni</b>"
                            "\nScrivi il <b>numero del treno</b> o il <b>nome della stazione</b>, "
                            "per esempio <code>@{username} 9650</code> o <code>@{username} Roma Termini</code>"
                            "\n➖➖️ <b>Cerca itinerari</b>"
                            "\nScrivi la <b>stazione di partenza</b>, un <b>trattino -</b> e la <b>stazione di arrivo</b>: "
                            "per esempio <code>@{username} Milano Centrale - Roma Termini</code>"
                            "\n<i>Gli itinerari cercati inline sono basati sull'orario attuale</i>"
                            .format(username=bot.itself.username)
                        ),
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    },
                    "reply_markup": {
                        "inline_keyboard": [
                            [{"text": "➡️ Orario Treni", "url": "https://t.me/OrarioTreniBot"}]
                        ]
                    },
                    "thumb_url": "http://i.imgur.com/hp9QUXx.png",
                }
            ]
        )

    if not iq.query:
        return default_answer()

    api = viaggiatreno.API()

    if iq.query.isnumeric():  # Search train
        try:
            results = api.call('cercaNumeroTrenoTrenoAutocomplete', iq.query)
        except HTTPError:
            results = []
        if len(results) == 0:
            return not_found_answer()

        u.increaseStat("stats_inline_queries")
        u.increaseStat("stats_trains_bynum")

        inline_results = []
        for result in results:
            raw = api.call('andamentoTreno', result[1], iq.query)
            text = format.formatTrain(raw)
            inline_results.append(
                {
                    "type": "article",
                    "id": _gen_ran_string(),
                    "title": "🚅 Treno {train}".format(train=raw['compNumeroTreno']),
                    "description": "👉 Informazioni del treno {train} da {o}".format(
                        train=raw['compNumeroTreno'],
                        o=raw['origine']
                    ),
                    "input_message_content": {
                        "message_text": text,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    },
                    "reply_markup": {
                        "inline_keyboard": [
                            [{"text": "🔄 Aggiorna le informazioni", "callback_data": "train@{d}_{n}@update"
                                .format(d=result[1],
                                        n=iq.query)}],
                            [{"text": "🚉 Fermate", "callback_data": "train@{d}_{n}@stops"
                                .format(d=result[1],
                                        n=iq.query)}]
                        ]},
                    "thumb_url": "http://i.imgur.com/hp9QUXx.png"
                }
            )

        iq.answer(results=inline_results)

    else:
        if "-" in iq.query:  # Search itinerary
            try:
                station_a = minifyStation(api.call('cercaStazione', iq.query.split("-")[0].strip())[0]['id'])
                station_b = minifyStation(api.call('cercaStazione', iq.query.split("-")[1].strip())[0]['id'])
                date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

                raw = api.call('soluzioniViaggioNew', station_a, station_b, date)
            except (KeyError, IndexError, HTTPError):
                return not_found_answer()

            u.increaseStat("stats_inline_queries")
            u.increaseStat("stats_trains_byiti")

            text = format.formatItinerary(raw)

            iq.answer(
                results=[
                    {
                        "type": "article",
                        "id": _gen_ran_string(),
                        "title": "🛤 Itinerari da {a} a {b}".format(
                            a=iq.query.split("-")[0].upper(),
                            b=iq.query.split("-")[1].upper()),
                        "description": "{x} soluzioni trovate".format(
                            x=len(raw['soluzioni']) if len(raw['soluzioni']) < 5 else 5),
                        "input_message_content": {
                            "message_text": text,
                            "parse_mode": "HTML",
                            "disable_web_page_preview": True
                        },
                        "thumb_url": "http://i.imgur.com/hp9QUXx.png",
                    }
                ]
            )

        else:  # Search station
            results = api.call('cercaStazione', iq.query)
            if len(results) == 0:
                return not_found_answer()

            elif len(results) > 0:
                u.increaseStat("stats_inline_queries")
                u.increaseStat("stats_stations")

                inline_results = []
                x = 0
                for station in results:
                    if x > 49:
                        break

                    inline_results.append(
                        {
                            "type": "article",
                            "id": _gen_ran_string(),
                            "title": "🚉 Stazione di {station}".format(station=station['nomeLungo']),
                            "description": "👉 Informazioni sulla stazione di {station}".format(station=station['nomeLungo']),
                            "input_message_content": {
                                "message_text": format.formatStation(station['nomeLungo']),
                                "parse_mode": "HTML",
                                "disable_web_page_preview": True
                            },
                            "reply_markup": {
                                "inline_keyboard": [
                                    [{"text": "🔘 Mostra le informazioni da Wikipedia", "callback_data":
                                        "station@" + station["id"] + "@wiki"}],
                                    [{"text": "🚦 Arrivi",
                                      "callback_data": "station@" + station["id"] + "@arrivals"},
                                     {"text": "🚦 Partenze",
                                      "callback_data": "station@" + station["id"] + "@departures"}],
                                ]},
                            "thumb_url": "http://i.imgur.com/hp9QUXx.png",
                        }
                    )
                    x += 1

                iq.answer(results=inline_results)
