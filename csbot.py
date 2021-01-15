#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram 
import logging
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


# def start(update, context):
#     context.bot.send_message(chat_id=update.effective_chat.id, text="Que pasa monoo?? Sabe un Ceresoo ??")

# bot = telegram.Bot(token='1532917635:AAHiVZww3cecxQdkkhZR_hcLJv9fWhvhAHU')
# print(bot.get_me())
# {'id': 1532917635, 'first_name': 'Sabe-Cs-Bot', 'is_bot': True, 'username': 'Sabe_Cs_bot', 'can_join_groups': True, 'can_read_all_group_messages': False, 'supports_inline_queries': False}


def start_callback(update, context):
    # context.args -> array de strings con los argumentos
    user_says = " ".join(context.args)                      # genera un strings con los argumentos del array(context.args) separado por " "
    update.message.reply_text("You said: " + user_says)     #respuesta del bot


def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def nades(update, context):
    """Function for '/nades map' command"""
    
    # Loads .json file for requested map (argument)
    path = 'maps/' + context.args[0] + '.json'
    print(path)
    f = open(path)
    data = json.load(f)

    # data["pageProps"]["ssrNades"] -> where nades are. it's a list of dict's. Every dict is a nade
    nades = data["pageProps"]["ssrNades"]
    context.user_data["nades"] = nades
    
    # gater granade types available in the map
    types = []
    for nade in nades:
        types.append(nade["type"])
    types = list(dict.fromkeys(types))      # remove duplicates
    types_data = list(types)
    print(types)

    # keyboard generation
    keyboard = keyboardGenerator(types, types_data)
    reply_markup = InlineKeyboardMarkup(keyboard)

    # keyboard reply
    print("update type: ", type(update))
    print("update.message type: ", type(update.message))
    update.message.reply_text('Tipo de Granada?', reply_markup=reply_markup)
    return


def keyboardGenerator(array_options, array_data):
    """Given an array of options and other for callback_data 
    returns a keyboard with 2 buttons per row"""

    keyboard = []
    while (0 < len(array_options)):
        if len(array_options) == 1:
            option1 = array_options.pop()
            data1 = array_data.pop()
            keyboard.append([ 
                InlineKeyboardButton(option1, callback_data=data1) 
                ])
        else:
            option1 = array_options.pop()
            option2 = array_options.pop()
            data1 = array_data.pop()
            data2 = array_data.pop()
            keyboard.append([ 
                InlineKeyboardButton(option1, callback_data=data1), 
                InlineKeyboardButton(option2, callback_data=data2) 
                ])
    return keyboard
        

def button(update, context):
    query = update.callback_query["data"]  # Takes "data" from the query (dict with data of user and chat)
    print("query: ", query, "  type: ", type(query))
    # button handling with nadeType query
    if query == 'flash' or query == 'smoke' or query == 'molotov' or query == 'hegrenade':
        nadeType = query
        endPositions = []
        ids = []
        
        for nade in context.user_data["nades"]:
            if nade["type"] == nadeType:
                endPositions.append(nade["endPosition"])
                ids.append(nade["id"])          

        keyboard = keyboardGenerator(endPositions, ids)
        reply_markup1 = InlineKeyboardMarkup(keyboard)

        # keyboard reply
        update.callback_query.edit_message_text('Que vas a detonar, hater?', reply_markup=reply_markup1)
    
    # buttonhandling with endPosition query
    else: 
        nadeId = query
        print("nadeId: ", nadeId, "type: ", type(nadeId))
        i = 0
        nades = context.user_data["nades"]
        nades_len = len(nades)
        

        while (nades[i]["id"] != nadeId) and (i < nades_len):
        # while nades[i]["id"] != nadeId:
            print((nades[i]["id"] != nadeId))
            print ("i: ", i, "  id: ", nades[i]["id"], "  type: ", type(nades[i]["id"]))
            i += 1

        if i == len(nades):
            smallVideoUrl = "Sorry, no video"
        else:
            smallVideoUrl = context.user_data["nades"][i]["gfycat"]["smallVideoUrl"]
            lineupUrl = context.user_data["nades"][i]["images"]["lineupUrl"]
        update.callback_query.edit_message_text(smallVideoUrl)

        ## FALTA AGREGAR EL LINEUP, NO SE PUEDE ASI NOMAS, HAY QUE BUSCARLE LA VUELTA


def main():
    """Start the bot."""

    updater = Updater(token='1532917635:AAHiVZww3cecxQdkkhZR_hcLJv9fWhvhAHU', use_context=True)
    dispatcher = updater.dispatcher


    # start handler
    # start_handler = CommandHandler('start', start)
    start_handler = CommandHandler('start', start_callback)
    dispatcher.add_handler(start_handler)

    # message handler
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    # nades handler
    nades_handler = CommandHandler('nades', nades)
    dispatcher.add_handler(nades_handler)

    # button handler
    button_handler = CallbackQueryHandler(button)
    dispatcher.add_handler(button_handler)


    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()