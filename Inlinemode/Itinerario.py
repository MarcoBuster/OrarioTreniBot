import botogram

import API
import Bot

from Inlinemode import Inline

def inline(bot, chains, update):
    update_id = update.inline_query.id
    sender = update.inline_query.sender
    query = update.inline_query.query

    stazione1 = query.split("-")[0].strip()
    stazione2 = query.split("-")[1].strip()

    data, success, error = API.orarioTreni.cercaItinerario(stazione1, stazione2, None)
    if data == None or data['soluzioni'] == []:
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

    messaggio, inline_keyboard = API.Messaggi.itinerario(data)

    bot.api.call("answerInlineQuery", {
                    "switch_pm_text":"Serve aiuto? Premi qui!",
                    "switch_pm_parameter":"inline",
                    "inline_query_id": update_id,
                    "cache_time": 0,
                    "results":'[{'+
                        '"type":"article",'+
                        '"id":"1",'+
                        '"title":"Ho trovato un itinerario tra '+query+'",'+
                        '"thumb_url":"http://i.imgur.com/sDO87j7.png",'+
                        '"description":"Clicca qui per visualizzare l\'itinerario '+query+'",'+
                        '"input_message_content":{'+
                            '"message_text":"'+messaggio+'",'+
                            '"parse_mode":"HTML"'+
                        '}, '+
                        '"reply_markup":{"inline_keyboard":'+
                            inline_keyboard+
                        '}'+
                    '}]'
            })


    return
