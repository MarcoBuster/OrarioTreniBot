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

import base64
import json

from ..objects.user import User
from ..viaggiatreno import viaggiatreno, format


def process_deeplinking(bot, message, args):
    args = base64.b64decode(bytes("".join(args), "utf-8")).decode("utf-8")

    if "@" not in args:
        return

    u = User(message.sender)
    api = viaggiatreno.API()
    utils = viaggiatreno.Utils()

    arguments = args.split("@")

    if arguments[0] == "train":
        departure_station, train = arguments[1].split('_')[0:2]
        raw = api.call('andamentoTreno', departure_station, train)

        u.increaseStat('stats_trains_bynum')

        text = format.formatTrain(raw)
        bot.api.call('sendMessage', {
            'chat_id': message.chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
            json.dumps(
                {"inline_keyboard": [
                    [{"text": "🔄 Aggiorna le informazioni",
                      "callback_data": format.gTCQ(raw) + "@update"}],
                    [{"text": "🚉 Fermate", "callback_data": format.gTCQ(raw) + "@stops"},
                     {"text": "📊 Grafico ritardo", "callback_data": format.gTCQ(raw) + "@graph"}],
                    [{"text": "⬅️ Menù principale", "callback_data": "home"}]
                ]}
            )
        })

    elif arguments[0] == "station":
        station = arguments[1]
        station_name = utils.station_from_ID(station)

        u.increaseStat('stats_stations')

        text = format.formatStation(station_name)
        bot.api.call('sendMessage', {
            'chat_id': message.chat.id, 'text': text, 'parse_mode': 'HTML', 'reply_markup':
                json.dumps(
                    {"inline_keyboard": [
                        [{"text": "🚦 Arrivi", "callback_data": "station@" + station + "@arrivals"},
                         {"text": "🚦 Partenze", "callback_data": "station@" + station + "@departures"}],
                        [{"text": "⬅️ Menù principale", "callback_data": "home"}]
                    ]}
                )
        })
