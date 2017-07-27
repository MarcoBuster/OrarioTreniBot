
import redis
import time
import config
import json
import threading
from . import viaggiatreno

r = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, password=config.REDIS_PASSWORD)

def trainfollower(bot):
    api = viaggiatreno.API()
    watchlist = r.keys("follow_*")
    for k in watchlist:
        try:
            userlist = json.loads(r.get(k))
            departure_station, train = k.decode().replace("follow_", "").split("_")
            stato = api.call("andamentoTreno", departure_station, train)

            laststatusobject = r.get("followstatus_{s}_{n}".format(s=departure_station, n=train))
            if laststatusobject is not None:
                laststatus = json.loads(laststatusobject)
                if laststatus["stazioneUltimoRilevamento"] == stato["stazioneUltimoRilevamento"]:
                    continue

            r.set("followstatus_{s}_{n}".format(s=departure_station, n=train), json.dumps({
                'stazioneUltimoRilevamento': stato["stazioneUltimoRilevamento"]
            }))

            if stato["ritardo"] > 0:
                msg = "Stato treno {n} aggiornato: rilevato a {s} con ritardo di {r}" \
                    .format(n=train, s=stato["stazioneUltimoRilevamento"], r=stato["ritardo"])
            elif stato["ritardo"] < 0:
                msg = "Stato treno {n} aggiornato: rilevato a {s} in anticipo di {r}" \
                    .format(n=train, s=stato["stazioneUltimoRilevamento"], r=stato["ritardo"])
            else:
                msg = "Stato treno {n} aggiornato: rilevato a {s} in orario" \
                    .format(n=train, s=stato["stazioneUltimoRilevamento"])

            for uid in userlist:
                bot.chat(uid).send(msg)

            if stato["destinazione"] == stato["stazioneUltimoRilevamento"]:
                # Treno arrivato a destinazione
                for uid in userlist:
                    bot.chat(uid).send("Treno arrivato a destinazione, non ci saranno altre notifiche")
                r.delete(k)
                r.delete("followstatus_{s}_{n}".format(s=departure_station, n=train))
        except Exception as e:
            # TODO: print error thru log
            print(e)
