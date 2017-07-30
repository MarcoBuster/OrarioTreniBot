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

import time
from urllib.error import HTTPError

import redis

import config
from .dateutils import format_timestamp
from .viaggiatreno import API, Utils
from ..main import bot

r = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password=config.REDIS_PASSWORD)
api = API()
utils = Utils()


def newTrack(train, departure_station, u):
    try:
        raw = api.call("andamentoTreno", departure_station, train)
    except HTTPError:
        return False

    if not raw:
        return False

    rhash = 'train_track:{x}'.format(x=int(r.get('train_track_last_id').decode('utf-8')) + 1)
    r.hset(rhash, 'train', train)
    r.hset(rhash, 'departure_station', departure_station)
    r.hset(rhash, 'by', u.id)
    r.hset(rhash, 'last_detected', raw['stazioneUltimoRilevamento'])
    r.hset(rhash, 'last_delay', raw['ritardo'])
    r.hset(rhash, 'last_update', int(time.time()))
    return True


def run():
    while True:
        tracks = r.keys('train_track:*')
        for track in tracks:
            train = r.hget(track, 'train').decode('utf-8')
            departure_station = r.hget(track, 'departure_station').decode('utf-8')
            user = int(r.hget(track, 'by').decode('utf-8'))
            last_detected = r.hget(track, 'last_detected').decode('utf-8')
            last_delay = int(r.hget(track, 'last_delay').decode('utf-8'))
            raw = api.call('andamentoTreno', departure_station, train)

            print("\n-- Train ", train)
            print("| departure station", departure_station)
            print("| user", user)
            print("| last detected", last_detected)
            print("| last delay", last_delay)

            if raw['stazioneUltimoRilevamento'] != last_detected:
                delay = raw['ritardo']
                if delay == 1:
                    status = '\n🕒 <b>In ritardo di {x} minuto</b>'.format(x=delay)
                elif delay > 1:
                    status = '\n🕒 <b>In ritardo di {x} minuti</b>'.format(x=delay)
                elif delay < 0:
                    status = '\n🕒 <b>In anticipo di {x} minuti</b>'.format(x=abs(delay))
                else:
                    status = '\n🕒 <b>In perfetto orario</b>'

                if delay > last_delay:
                    delay_info = "(+{diff}m)".format(diff=delay - last_delay)
                elif delay < last_delay:
                    delay_info = "(-{diff}m)".format(diff=last_delay - delay)
                else:
                    delay_info = ""

                r.hset(track, 'last_detected', raw['stazioneUltimoRilevamento'])
                r.hset(track, 'last_delay', raw['ritardo'])
                r.hset(track, 'last_updated', int(time.time()))

                bot.chat(user).send(
                    "🚅 <b>Tracciamento treno {train}</b>"
                    "\n🚉 <b>Rilevato a {last_detected}</b> alle ore {last_detected_time}"
                    "\n{status} {delay_info}".format(
                        train=train, last_detected=raw['stazioneUltimoRilevamento'],
                        last_detected_time=format_timestamp(raw['oraUltimoRilevamento'], "%H:%M"),
                        status=status, delay_info=delay_info
                    )
                )

        time.sleep(1)
