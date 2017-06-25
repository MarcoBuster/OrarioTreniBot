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

from urllib.error import HTTPError

from ..viaggiatreno import viaggiatreno, format


def process_inline_query(bot, iq, u):
    def default_answer():
        iq.answer(
            results=[
                {
                    "type": "article",
                    "id": "0",
                    "title": "❇️ Orario Treni in ogni chat!",
                    "description": "👉 Clicca qui per scoprire come usare Orario Treni in ogni chat!",
                    "input_message_content": {
                        "message_text": (
                            "❇️ <b>Usa Orario Treni in ogni chat!</b>"
                            "\n⏺ <i>Cerca treni, stazioni e itinerari in qualsiasi chat</i>"
                            "\n➖➖️ <b>Cerca treni e stazioni</b>"
                            "\nScrivi semplicemente <b>il numero del treno</b> o <b>il nome della stazione</b>"
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
                    "id": iq.query,
                    "title": "❌ Non trovato",
                    "description": "👉 Clicca qui per scoprire come usare Orario Treni in ogni chat!",
                    "input_message_content": {
                        "message_text": (
                            "❇️ <b>Usa Orario Treni in ogni chat!</b>"
                            "\n⏺ <i>Cerca treni, stazioni e itinerari in qualsiasi chat</i>"
                            "\n➖➖️ <b>Cerca treni e stazioni</b>"
                            "\nScrivi semplicemente <b>il numero del treno</b> o <b>il nome della stazione</b>"
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

        if len(results) == 1:
            raw = api.call('andamentoTreno', results[0][1], iq.query)
            text = format.formatTrain(raw)
            iq.answer(
                results=[
                    {
                        "type": "article",
                        "id": iq.query,
                        "title": "🚅 Treno {train}".format(train=raw['compNumeroTreno']),
                        "description": "👉 Informazioni del treno {train}".format(train=raw['compNumeroTreno']),
                        "input_message_content": {
                            "message_text": text,
                            "parse_mode": "HTML",
                            "disable_web_page_preview": True,
                        },
                        "reply_markup": {
                            "inline_keyboard": [
                                [{"text": "🔄 Aggiorna le informazioni", "callback_data": "train@{d}_{n}@update"
                                    .format(d=results[0][1],
                                            n=iq.query)}],
                                [{"text": "🚉 Fermate", "callback_data": "train@{d}_{n}@stops"
                                  .format(d=results[0][1],
                                          n=iq.query)},
                                 {"text": "📊 Grafico ritardo", "callback_data": "train@{d}_{n}@graph"
                                  .format(d=results[0][1],
                                          n=iq.query)}]
                            ]},
                        "thumb_url": "http://i.imgur.com/hp9QUXx.png",
                    }
                ]
            )
    else:
        if "-" in iq.query:  # Search itinerary
            return default_answer()

        else:  # Search station
            results = api.call('cercaStazione', iq.query)
            if len(results) == 0:
                return not_found_answer()

            elif len(results) > 0:
                inline_results = []
                x = 0
                for station in results:
                    if x > 49:
                        break

                    inline_results.append(
                        {
                            "type": "article",
                            "id": iq.query + str(x),
                            "title": "🚉 Stazione di {station}".format(station=station['nomeLungo']),
                            "description": "👉 Informazioni sulla stazione di {station}".format(station=station['nomeLungo']),
                            "input_message_content": {
                                "message_text": (
                                    "🚉 <b>Stazione di {name}</b>"
                                    "\n<i>Premi il tasto sotto per mostrare le informazioni da Wikipedia</i>"
                                    .format(name=station['nomeLungo'].title())
                                ),
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
