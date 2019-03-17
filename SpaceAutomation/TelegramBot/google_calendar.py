from datetime import datetime, time, timedelta
import subprocess
import os
import sys

import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler
import bot_config as config
updater = Updater(token=config.token)

try:
        from icalevents.icalevents import events
        import calendar
except ImportError:
        output = subprocess.check_output(["pip3", "install -r" + str(os.path.join(os.path.dirname(__file__), "..\\")) + "requirements.txt"])
        sent_message = updater.bot.send_message(chat_id = next(iter(config.authorized_group2)) , text = str(output), parse_mode=telegram.ParseMode.MARKDOWN, disable_notification=True)
else:
        pass



calendar_url = "https://calendar.google.com/calendar/ical/4hbi6bp3lol50h2m422ljg81t0%40group.calendar.google.com/public/basic.ics"

def get_events(days_to_check = 14):
        
        #text = urlopen(calendar_url).read().decode('iso-8859-1')
        #c = Calendar(text)
        #c = Calendar(requests.get(calendar_url).text)
        #c = Calendar.from_ical(text)
        #for event in (event for event in c.events if event.begin > datetime.now):
        #        print(event)
        in_two_weeks = datetime.combine(datetime.today(), time.max) + timedelta(days=days_to_check)
        es = events(calendar_url,start=datetime.now(),end=in_two_weeks)
        message = ""
        for event in sorted(es):
                event.summary = event.summary.replace("Lunch Break Make", "MH")
                event.summary = event.summary.replace("Wednesday Making Hours","MH")
                event.summary = event.summary.replace("Making Hours","MH")
                event.summary = event.summary.replace("Do-Something Hours", "DS-H")
                message = f"{message}\n*{event.start.strftime('%A')}, {event.start.day:02}.{event.start.month:02}.{event.start.year:04}*\n    {event.start.hour:02}:{event.start.minute:02} - {event.end.hour:02}:{event.end.minute:02}\n    {event.summary}"
        #vobject code:
        #cal = next(vobject.readComponents(text))
        #for event in cal.vevent_list:
        #        print(event.summary.value)
                
        #for event in (event for event in cal.vevent_list if event.dtstart.value > datetime.utcnow().replace(tzinfo=pytz.utc)):
        #        print("Event '{}' starts on {}".format(event.summary.value, event.dtstart.value))
        return message


if __name__ == "__main__":
        message = get_events()
        print(message)
        if not message == None:
                
                message = f"Hey all, here are the events from our [google calendar](https://calendar.google.com/calendar/embed?src=4hbi6bp3lol50h2m422ljg81t0%40group.calendar.google.com&ctz=Europe%2FBerlin) of the next two weeks:{message}"
                sent_message = updater.bot.send_message(chat_id = config.small_group_id, text = message, parse_mode=telegram.ParseMode.MARKDOWN, disable_notification=True)