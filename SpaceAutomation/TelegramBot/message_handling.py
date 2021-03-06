#Standard library imports.
import sys
import os
import subprocess
import threading
#Related third party imports.
import telegram
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, run_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import paho.mqtt.client as mqtt
import pandas as pd

#Local application/library specific imports.
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))  
from Ringtones import RandomizeRingtone
from WikiUsers import ActiveWikiUsers
import github_updates
from mqtt_handling import MqttHandler
import bot_config as config


class CoMakingBot:
    updater = Updater(token=config.token)
    dispatcher = updater.dispatcher
    mqtt_client = mqtt.Client("Telegram_Bot")

    @run_async
    def start (bot, update):
        message = f"Thank you for contacting me. Your Chat ID is: {update.message.chat_id}"
        message = f"{message}\n\nThis bot is for the [CoMakingSpace Heidelberg](https://comakingspace.org). You can find the documentation in the [wiki](https://https://wiki.comakingspace.de/Telegram_Group)."
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
        message = "Right now, I am listening to the following messages:"
        for handler in CoMakingBot.dispatcher.handlers[0]:
            if type(handler) == telegram.ext.commandhandler.CommandHandler:
                #message = message + "\n [/" + handler.command[0] + "](tg://bot_command?command=" + handler.command[0]
                message = f"{message} \n /{handler.command[0]}"
        if update.message.chat_id in config.authorized_group1:
            message = message + "\n You are also authorized for the following commands from group 1:"
            for handler in CoMakingBot.dispatcher.handlers[1]:
                if type(handler) == telegram.ext.commandhandler.CommandHandler:
                    message = f"{message} \n /{handler.command[0]}"
        if update.message.chat_id in config.authorized_group2:
            message = message + "\n You are also authorized for the following commands from group 2:"
            for handler in CoMakingBot.dispatcher.handlers[2]:
                if type(handler) == telegram.ext.commandhandler.CommandHandler:
                    message = f"{message} \n /{handler.command[0]}"
        bot.send_message(chat_id=update.message.chat_id, text=message)
    @run_async
    def wikiUser (bot, update):
        UserList = ActiveWikiUsers.getActiveUsers()
        del UserList['newlen']
        del UserList['ns']
        del UserList['oldlen']
        # The following code gives bad results (many spaces left to the user names)
        # This is described in https://github.com/pandas-dev/pandas/issues/9784
        # Should hopefully be fixed in one of the next pandas updates.
        #pd.set_option("display.max_colwidth", 10000)
        #message = "Here is the latest [CoMakingSpace Wiki Leaderboard](https://wiki.comakingspace.de/Special:RecentChanges):\nUser \t Changed bytes \t Number of changes"
        #UserString = UserList.to_string(header=False,index=False, formatters = {"user": "[{0}](https://wiki.comakingspace.de/User:{0})".format})
        ##UserString = UserList.to_html(header=True,index=False, formatters = {"user": "[{0}](https://wiki.comakingspace.de/User:{0})".format})
        #message = f"{message}\n{UserString}"

        #Workaround until the above mentioned issue is fixed
        message = "Here is the latest [CoMakingSpace Wiki Leaderboard](https://wiki.comakingspace.de/Special:RecentChanges):\nUser: Changed bytes (Number of changes)"
        for index,user in UserList.iterrows():
            message = f"{message}\n[{user['user']}](https://wiki.comakingspace.de/User:{user['user']}): {user['changedlen']} ({user['count']})"
        bot.send_message(chat_id=update.message.chat_id, text = message, parse_mode=telegram.ParseMode.MARKDOWN)
    @run_async
    def help (bot, update):
        message = "The documentation of this bot can be found in the [CoMakingSpace Wiki](https://wiki.comakingspace.de/Telegram_Group).\nIf you want to get the current list of commands, please use /start"
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
    @run_async
    def nerven (bot,update):
        bot.send_message(chat_id=update.message.chat_id, text="Sei einfach du selbst...")
    
    def update (bot,update):
        if update.message.chat_id in config.authorized_group2:
            bot.send_message(chat_id=update.message.chat_id, text="Starting the update...")
            output = subprocess.check_output(["git", "pull"])
            bot.send_message(chat_id=update.message.chat_id, text="The git output is: \n" + str(output))
            CoMakingBot._restart()
        else:
            bot.send_message(chat_id=update.message.chat_id, text = "not authorized")
    @run_async
    def new_ringtone (bot,update):
        if update.message.chat_id in config.authorized_group1:
            RandomizeRingtone.randomize_ringtone()
        else:
            bot.send_message(chat_id=update.message.chat_id, text = "not authorized")
    @run_async
    def fdd (bot,update,args):
        if update.message.chat_id in config.authorized_group1:
            text = ""
            for word in args:
                text = text + word + " "
            MqttHandler.send('/CommonRoom/FDD/Text',text[:-1])
        else:
            bot.send_message(chat_id=update.message.chat_id, text = "not authorized")
    @run_async
    def events(bot,update,args):
        import google_calendar
        if len(args) > 0:
                message = google_calendar.get_events(int(args[0]))
        else:
            message = google_calendar.get_events()
        if message == None:
            message = "Unfortunately, there is no event available in the given timeframe."
        bot.send_message(chat_id=update.message.chat_id, text = message, parse_mode=telegram.ParseMode.MARKDOWN)
    @run_async
    def github_events (bot,update,args):
        if len(args) > 0:
            message = github_updates.get_updates(int(args[0]))
        else:
            message = github_updates.get_updates()
        if message == None:
            message = "Unfortunately, there is no update available in the given timeframe."
        bot.send_message(chat_id=update.message.chat_id, text = message, parse_mode=telegram.ParseMode.MARKDOWN)
   
    @run_async
    def bell_sounds (bot, update):
        if update.message.chat_id in config.authorized_group1:
            ringtones = RandomizeRingtone.getFiles("/")
            keyboard = []
            message = "ringtones:"
            for ringtone in ringtones:
                message = message + "\n " + ringtone
                keyboard.append([InlineKeyboardButton(ringtone,callback_data=ringtone)])
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('Please choose:', reply_markup=reply_markup)
        else:
            bot.send_message(chat_id=update.message.chat_id, text = "not authorized")
        #thread1 = threading.Thread(target = CoMakingBot._getandsendtones, args = (bot,update))
        #thread1.start()
    @run_async
    def buttonReply (bot, update):
        #bot.send_message(chat_id=update.callback_query.from_user.id, text="button got pressed")
        query = update.callback_query
        message = "{{'command': 'play','payload': '{}'}}".format(query.data)
        MqttHandler.send("/DoorBell/Control",message)
        bot.send_message(chat_id=update.callback_query.from_user.id, text=f"Played the file {query.data}")
        #query.edit_message_text(text="Selected option: {}".format(query.data))

    def _getandsendtones(bot, update):
        #print("got the bell command")
        #bot.send_message(chat_id=update.message.chat_id, text="got the bell command") 
        #ringtones = ["test"]
        ringtones = RandomizeRingtone.getFiles("/")
        keyboard = []
        message = "ringtones:"
        #keyboard.append([InlineKeyboardButton("test",callback_data="test")])
        for ringtone in ringtones:
            message = message + "\n " + ringtone
            keyboard.append([InlineKeyboardButton(ringtone,callback_data=ringtone)])
        #bot.send_message(chat_id=update.message.chat_id, text=message) 
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)
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
        github_handler = CommandHandler('github',CoMakingBot.github_events,pass_args=True)
        google_handler = CommandHandler('events', CoMakingBot.events, pass_args=True)
        bell_handler = CommandHandler('doorbell',CoMakingBot.bell_sounds)
        bell_callback_handler = CallbackQueryHandler(CoMakingBot.buttonReply)

        CoMakingBot.dispatcher.add_handler(start_handler)
        CoMakingBot.dispatcher.add_handler(WikiUser_handler)
        CoMakingBot.dispatcher.add_handler(help_handler)
        CoMakingBot.dispatcher.add_handler(google_handler)
        CoMakingBot.dispatcher.add_handler(github_handler)
        CoMakingBot.dispatcher.add_handler(nerven_handler,1)
        CoMakingBot.dispatcher.add_handler(new_ringtone_handler,1)
        CoMakingBot.dispatcher.add_handler(bell_handler,1)
        CoMakingBot.dispatcher.add_handler(fdd_handler,1)
        CoMakingBot.dispatcher.add_handler(update_handler,2)
        CoMakingBot.dispatcher.add_handler(bell_callback_handler)

        #print("handlers registered")
    def run():
        CoMakingBot.updater.start_polling()
        print("bot started")

if __name__ == "__main__":
    CoMakingBot.setup()
    CoMakingBot.run()
