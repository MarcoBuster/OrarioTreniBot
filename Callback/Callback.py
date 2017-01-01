import botogram

import API
import Bot

from Callback import Generale, Treni, Stazioni, Itinerario, Tracciamento

import sqlite3
conn = sqlite3.connect('OrarioTreni.db')
c = conn.cursor()

def process(bot, chains, update):
    Bot.logger.info("Utente {} callback {}".format(update.callback_query.sender.id, update.callback_query.data))

    Generale.callback(bot, chains, update)
    Treni.callback(bot, chains, update)
    Stazioni.callback(bot, chains, update)
    Itinerario.callback(bot, chains, update)
    Tracciamento.callback(bot, chains, update)
