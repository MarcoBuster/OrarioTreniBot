import botogram

import API
import Bot

from Callback import *

from Inlinemode import Stazioni, Treni, Itinerario

def process(bot, chains, update):
    update_id = update.inline_query.id
    sender = update.inline_query.sender
    query = update.inline_query.query

    if not query:
        testo = "<b>Avviami in privata</b> per scoprire come si usa questo bot in <b>modalità inline</b>"
        bot.api.call("answerInlineQuery", {
                        "switch_pm_text":"Non sai come si usa? Clicca qui!",
                        "switch_pm_parameter":"inline",
                        "inline_query_id": update_id,
                        "cache_time": 0,
                        "results":'[{'+
                            '"type":"article",'+
                            '"id":"1",'+
                            '"title":"Benvenuto!",'+
                            '"thumb_url":"http://i.imgur.com/zCqJ7iT.png",'+
                            '"description":"Avviami in privata o premi il pulsante in alto per scoprire come funziona questo bot in inline mode",'+
                            '"input_message_content":{'+
                                '"message_text":"'+testo+'",'+
                                '"parse_mode":"HTML"'+
                            '}, '+
                            '"reply_markup":{"inline_keyboard":'+
                                '[[{"text":"🔙Vai al bot","url":"telegram.me/OrarioTreniBot?start=inline"}]]'+ #TODO
                            '}'+
                        '}]'
                })
        return

    tipo = API.orarioTreni.tipo(str(query))

    if tipo == "stazione":
        Stazioni.inline(bot, chains, update)

    if tipo == "itinerario":
        Itinerario.inline(bot, chains, update)

    if tipo == "treno":
        Treni.inline(bot, chains, update)

    if tipo == "not found":
        testo = ("Quello che hai digitato, non è né un <b>treno</b> né una <b>stazione</b> né un <b>itinerario</b> esistente"
                "\nVai al bot per scoprire come funziona la <b>modalità inline</b>")
        bot.api.call("answerInlineQuery", {
                        "switch_pm_text":"Non sai come si usa? Clicca qui!",
                        "switch_pm_parameter":"inline",
                        "inline_query_id": update_id,
                        "cache_time": 0,
                        "results":'[{'+
                            '"type":"article",'+
                            '"id":"1",'+
                            '"title":"Non ho trovato niente",'+
                            '"thumb_url":"http://i.imgur.com/f8whiXJ.png",'+
                            '"description":"Nessun treno, stazione o itinerari trovati per quello che hai cercato",'+
                            '"input_message_content":{'+
                                '"message_text":"'+testo+'",'+
                                '"parse_mode":"HTML"'+
                            '}, '+
                            '"reply_markup":{"inline_keyboard":'+
                                '[[{"text":"🔙Vai al bot","url":"telegram.me/OrarioTreniBot?start=inline"}]]'+
                            '}'+
                        '}]'
                })
        return
