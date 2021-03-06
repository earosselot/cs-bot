#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import telegram 
import logging
import json
import pickle
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

# Configure Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger()


# get Token
MODE = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")


file = open('grenades.pkl', 'rb')
grenades = pickle.load(file)


if MODE == "dev":
    # run the bot locally
    def run(updater):
        updater.start_polling()
        print("BOT LOADED")
        updater.idle() # halt bot with Ctrl + C
elif MODE == 'prod':
    # run the bot on heroku
    def run(update):
        PORT = int(os.environ.get('PORT', '8843'))
        HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME')
        updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN)
        updater.bot.set_webhook(f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")
else:
    logger.info("No se especifico el MODE.")
    sys.exit()


def start(update, context):
    update.message.reply_text("Que onda vieja?, para buscar grandas poné: \n /nades mapa \n ej: para buscar grandas en nuke: \n /nades nuke")     #respuesta del bot


def nades(update, context):
    """Function for '/nades map' command"""
    try:
        # gather granade types available in the map
        context.user_data['map'] = context.args[0]
        types = []
        favoriteCount = []
        for nade in grenades[context.user_data['map']]:
            types.append(nade['type'])
            favoriteCount.append(nade['favoriteCount'])
        types = list(dict.fromkeys(types))      # remove duplicates
        types_data = list(types)

        # keyboard generation
        keyboard = keyboardGenerator(types, types_data)
        reply_markup = InlineKeyboardMarkup(keyboard)

        # keyboard reply
        name = update.effective_user['first_name']
        update.message.reply_text(f"Que tipo de Granada {name}?", reply_markup=reply_markup)

    except:
        update.message.reply_text("NaM, Not a Map")

    return


def keyboardGenerator(array_options, array_data):
    """Given an array of options and other for callback_data 
    returns a keyboard with 2 buttons per row"""

    keyboard = []
    while (0 < len(array_options)):
        if len(array_options) == 1:
            option1 = array_options.pop(0)
            data1 = array_data.pop(0)
            keyboard.append([ 
                InlineKeyboardButton(option1, callback_data=data1) 
                ])
        else:
            option1 = array_options.pop(0)
            option2 = array_options.pop(0)
            data1 = array_data.pop(0)
            data2 = array_data.pop(0)
            keyboard.append([ 
                InlineKeyboardButton(option1, callback_data=data1), 
                InlineKeyboardButton(option2, callback_data=data2) 
                ])
    return keyboard
        

def button(update, context):
    query = update.callback_query['data']  # Takes "data" from the query (dict with data of user and chat)

    # button handling with nadeType query
    if query == 'flash' or query == 'smoke' or query == 'molotov' or query == 'hegrenade':
        nadeType = query
        endPositions = []
        ids = []
        for nade in grenades[context.user_data['map']]:
            if nade['type'] == nadeType:
                if 'tickrate' in nade.keys():
                    if nade['tickrate'] == 'tick128':
                        tickRate = '(128)'
                    elif nade['tickrate'] == 'tick64':
                        tickRate = '(64)'
                    elif nade['tickrate'] == 'any':
                        tickRate = '(*)'
                    else:
                        tickRate = ''
                else:
                    tickRate = ''
                endPositions.append(nade['endPosition'] + ' ' + tickRate)
                ids.append(nade['id'])
                
        # 'tickrate': None, 'any', 'tick128', 'tick64' or not existent

        keyboard = keyboardGenerator(endPositions, ids)
        reply_markup1 = InlineKeyboardMarkup(keyboard)

        # keyboard reply
        update.callback_query.edit_message_text("Que vas a detonar, hater?", reply_markup=reply_markup1)
    
    # buttonhandling with endPosition query
    else: 
        nadeId = query
        i = 0
        nades = grenades[context.user_data['map']]
        nades_len = len(nades)
        chat_id = update['callback_query']['message']['chat']['id']

        while (nades[i]['id'] != nadeId) and (i < nades_len):
            i += 1

        if i == len(nades):
            smallVideoUrl = "Sorry, no video"
        else:
            smallVideoUrl = grenades[context.user_data['map']][i]['gfycat']['smallVideoUrl']
            largeVideoUrl = grenades[context.user_data['map']][i]['gfycat']['largeVideoUrl']
            if grenades[context.user_data['map']][i]['images']['lineupUrl']:
                lineupUrl = grenades[context.user_data['map']][i]['images']['lineupUrl']
                bot.send_photo(chat_id=chat_id, photo=lineupUrl)
            else:
                bot.send_message(chat_id=chat_id, text="Sorry, no lineup")

        try:
            bot.send_video(chat_id=chat_id, video=largeVideoUrl)
        except:
            bot.send_video(chat_id=chat_id, video=smallVideoUrl)
            bot.send_message(chat_id=chat_id, text=largeVideoUrl)
        

def practica(update):
    chat_id = update['callback_query']['message']['chat']['id']
    practicaCfg = "sv_cheats 1; bot_kick; mp_warmup_end; mp_freezetime 0; mp_roundtime_defuse 999; sv_grenade_trajectory 1; sv_grenade_trajectory_time 10; sv_showimpacts 1; sv_infinite_ammo 1; mp_limitteams 0; mp_autoteambalance 0; ammo_grenade_limit_total 5; bot_stop 1; mp_maxmoney 60000; mp_startmoney 60000; mp_buy_anywhere 1; sv_restart 1;"
    bot.send_message(chat_id=chat_id, text=f'Dale *Sabueso*!!\nPracticá que hay que salvar el mundo!!\nPegate esto el la consola y latea para todos lados: \n {practicaCfg}')


if __name__ == '__main__':
    # Gather bot information
    bot = telegram.Bot(token=TOKEN)
    logger.info("Starting bot")

    # Link updater with bot
    updater = Updater(bot.token, use_context=True)
    dispatcher = updater.dispatcher

    # handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('nades', nades))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler('practica', practica))

    run(updater)