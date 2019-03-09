#Standard library imports.
import sys
import os
import subprocess

#Related third party imports.
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
import paho.mqtt.client as mqtt

#Local application/library specific imports.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))  
from Ringtones import RandomizeRingtone
from WikiUsers import ActiveWikiUsers
from mqtt_handling import MqttHandler
import bot_config as config

class CoMakingBot:
    updater = Updater(token=config.token)
    dispatcher = updater.dispatcher
    mqtt_client = mqtt.Client("Telegram_Bot")

    def start (bot, update):
        message = "Thank you for contacting me. Your Chat ID is: " + str(update.message.chat_id) + "\n Right now, I am listening to the following messages:"
        for handler in CoMakingBot.dispatcher.handlers[0]:
            #message = message + "\n [/" + handler.command[0] + "](tg://bot_command?command=" + handler.command[0]
            message = message + "\n /" + handler.command[0]
        if update.message.chat_id in config.authorized_group1:
            message = message + "\n You are also authorized for the following commands from group 1:"
            for handler in CoMakingBot.dispatcher.handlers[1]:
                message = message + "\n /" + handler.command[0]
        if update.message.chat_id in config.authorized_group2:
            message = message + "\n You are also authorized for the following commands from group 2:"
            for handler in CoMakingBot.dispatcher.handlers[2]:
                message = message + "\n /" + handler.command[0]
        bot.send_message(chat_id=update.message.chat_id, text=message)  
    def wikiUser (bot, update):
        UserList = ActiveWikiUsers.getActiveUsers()
        del UserList['newlen']
        del UserList['ns']
        del UserList['oldlen']    
        bot.send_message(chat_id=update.message.chat_id, text = str(UserList))
    def help (bot, update):
        message = "The documentation of this bot might soon be found in the CoMakingSpace Wiki. \n For the moment, please refer to /start"
        bot.send_message(chat_id=update.message.chat_id, text=message)
    def nerven (bot,update):
        bot.send_message(chat_id=update.message.chat_id, text="Sei einfach du selbst...")
    def update (bot,update):
        if update.message.chat_id in config.authorized_group2:
            bot.send_message(chat_id=update.message.chat_id, text="Starting the update...")
            output = subprocess.check_output(["git", "pull"])
            bot.send_message(chat_id=update.message.chat_id, text="The git output is: \n" + str(output))
            _restart()
        else:
            bot.send_message(chat_id=update.message.chat_id, text = "not authorized")
    def new_ringtone (bot,update):
        if update.message.chat_id in config.authorized_group1:
            RandomizeRingtone.randomize_ringtone()
        else:
            bot.send_message(chat_id=update.message.chat_id, text = "not authorized")

    def fdd (bot,update,args):
        if update.message.chat_id in config.authorized_group1:
            text = ""
            for word in args:
                text = text + word + " "
            MqttHandler.send('/CommonRoom/FDD/Text',text[:-1])
        else:
            bot.send_message(chat_id=update.message.chat_id, text = "not authorized")
    def _restart():
        args = sys.argv[:]
        args.insert(0, sys.executable)
        if sys.platform == 'win32':
            args = ['"%s"' % arg for arg in args]
        os.chdir(os.getcwd())
        os.execv(sys.executable, args)
    def setup():
        start_handler = CommandHandler('start', CoMakingBot.start)
        WikiUser_handler = CommandHandler('WikiUser', CoMakingBot.wikiUser)
        nerven_handler = CommandHandler('wie_kann_ich_Martin_am_besten_nerven', CoMakingBot.nerven)
        new_ringtone_handler = CommandHandler('Randomize_Ringtone',CoMakingBot.new_ringtone)
        help_handler = CommandHandler('help', CoMakingBot.help)
        update_handler = CommandHandler('update', CoMakingBot.update)
        fdd_handler = CommandHandler('FDD',CoMakingBot.fdd,pass_args=True)

        CoMakingBot.dispatcher.add_handler(start_handler)
        CoMakingBot.dispatcher.add_handler(WikiUser_handler)
        CoMakingBot.dispatcher.add_handler(nerven_handler)
        CoMakingBot.dispatcher.add_handler(new_ringtone_handler,1)
        CoMakingBot.dispatcher.add_handler(help_handler)
        CoMakingBot.dispatcher.add_handler(fdd_handler,1)
        CoMakingBot.dispatcher.add_handler(update_handler,2)
    def run():
        CoMakingBot.updater.start_polling()
        print("bot started")