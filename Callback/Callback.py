import botogram

import API
import Bot

from Callback import Generale, Treni, Stazioni, Itinerario

import sqlite3
conn = sqlite3.connect('OrarioTreni.db')
c = conn.cursor()

def process(bot, chains, update):
    Generale.callback(bot, chains, update)
    Treni.callback(bot, chains, update)
    Stazioni.callback(bot, chains, update)
    Itinerario.callback(bot, chains, update)
