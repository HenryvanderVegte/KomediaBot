from datetime import datetime, time
import time as T
import urllib3
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

MENSA_BASE_URL = 'https://www.stw-edu.de'
MENSA_DUISBURG_URL = 'https://www.stw-edu.de/gastronomie/standorte/mensen/mensen//show/mensa-campus-duisburg/'
SECONDS_PER_DAY = 86400

def get_menu_as_string(input_text):
    date = datetime.combine(datetime.today(), time.min)
    timestamp = int(T.mktime(date.timetuple()))
    answer_introduction = "In der Hauptmensa in Duisburg gibt es heute: \n \n"
    if " gestern" in input_text:
        timestamp -= SECONDS_PER_DAY
        answer_introduction = "In der Hauptmensa in Duisburg gab es gestern: \n \n"
    elif " vorgestern" in input_text:
        timestamp -= SECONDS_PER_DAY*2
        answer_introduction = "In der Hauptmensa in Duisburg gab es vorgestern: \n \n"
    elif " morgen" in input_text:
        timestamp += SECONDS_PER_DAY
        answer_introduction = "In der Hauptmensa in Duisburg gibt es morgen: \n \n"
    elif " übermorgen" in input_text:
        timestamp += SECONDS_PER_DAY*2
        answer_introduction = "In der Hauptmensa in Duisburg gibt es übermorgen: \n \n"


    return get_menu_at_date(timestamp, answer_introduction)

def get_menu_at_date(timestamp, answer_introduction):
    """
    timestamp must be a unix timestamp at midnight of that day
    """
    try:
        http = urllib3.PoolManager()

        response = http.request('GET', MENSA_DUISBURG_URL)
        soup = BeautifulSoup(response.data.decode('utf-8'),"html5lib")
        data_url = soup.find(id='speisejs').get('data-url')

        menu_xml = http.request('GET', MENSA_BASE_URL + data_url).data

        xml_root = ET.fromstring(menu_xml)

        requested_node = None
        for node in xml_root.findall('tag'):
            if int(node.attrib['timestamp']) == timestamp:
                requested_node = node
                break

        if requested_node is None:
            return "Leider ist für diesen Tag kein Speiseplan verfügbar"

        menu_as_string = answer_introduction
        has_menu = False

        for item in node.findall('item'):
            title = item.find('title')
            if title is None or title.text == 'geschlossen':
                continue

            item_menu = title.text

            price_students = item.find('preis1')
            if price_students is None or not price_students.text:
                continue

            item_menu += " " + price_students.text
            item_menu += "\n\n"
            menu_as_string += item_menu
            has_menu = True
        if has_menu:
            return menu_as_string
        return "Leider ist für diesen Tag kein Speiseplan verfügbar"
    except:
        return "Bei der Bearbeitung der Anfrage ist leider etwas schiefgelaufen."