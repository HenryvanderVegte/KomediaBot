import time
import json
import requests
import urllib
import config as cfg
import textmessagehandler
from dbmanager import DBManager


db = DBManager()

TOKEN = cfg.api["key"]
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

GERMAN_WEEKDAYS = {
    "Monday": "Montag",
    "Tuesday": "Dienstag",
    "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag",
    "Friday": "Freitag",
    "Saturday": "Samstag",
    "Sunday": "Sonntag"
}


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def post_url(url, file):
    response = requests.post(url, files=file)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def handle_updates(updates):
    for update in updates["result"]:
        try:
            if "text" in update["message"]:
                 textmessagehandler.handle_msg(update)
                 # elif "photo" in update["message"]:
                 # Do something
                 # elif "location" in update["message"]:
            #      # Do something
        except KeyError:
            pass


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    print("[BOT]:: Sending new response to telegram bot api: " + url)
    get_url(url)

def send_message_html(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode={}".format(text, chat_id,'html')
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    print("[BOT]:: Sending new response to telegram bot api: " + url)
    get_url(url)

def send_photo(chat_id, photo):
    url = URL + "sendPhoto?chat_id={}".format(chat_id)
    print("[BOT]:: Sending new image to telegram bot api: " + url)
    post_url(url, photo)

def send_document(chat_id, photo):
    url = URL + "sendDocument?chat_id={}".format(chat_id)
    print("[BOT]:: Sending new image to telegram bot api: " + url)
    post_url(url, photo)

def send_location(chat_id, longitude, latitude):
    url = URL + "sendlocation?chat_id={}&longitude={}&latitude={}".format(chat_id, longitude, latitude)
    print("[BOT]:: Sending new location to telegram bot api: " + url)
    get_url(url)

def build_keyboard(options):
    reply_markup = {"keyboard": options, "one_time_keyboard": True, "hide_keyboard": True}
    return json.dumps(reply_markup)

def build_lecture_keyboard(lectures):
    keyboard = [[lecture] for lecture in lectures]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

def build_keyboard_remove():
    reply_markup = {"remove_keyboard": True, "selective": True}
    return json.dumps(reply_markup)

def main():
    print("Started Server")
    db.setup_timetable()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
