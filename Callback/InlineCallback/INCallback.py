import botogram

import API
import Bot

from Callback import Generale, Treni, Stazioni, Itinerario
from Callback.InlineCallback import INGenerale, INItinerario, INStazioni, INTreni

import sqlite3
conn = sqlite3.connect('OrarioTreni.db')
c = conn.cursor()

def process(bot, chains, update):
    INGenerale.callback(bot, chains, update)
    INTreni.callback(bot, chains, update)
    INStazioni.callback(bot, chains, update)
