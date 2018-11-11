from datetime import datetime, time
import time as T
import urllib3
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

MENSA_BASE_URL = 'https://www.stw-edu.de'
MENSA_DUISBURG_URL = 'https://www.stw-edu.de/gastronomie/standorte/mensen/mensen//show/mensa-campus-duisburg/'

def get_menu_as_string(input_text):
    date = datetime.combine(datetime.today(), time.min)
    answer_introduction = "In der Hauptmensa in Duisburg gibt es heute: \n \n"
    if "gestern" in input_text:
        date -= datetime.timedelta(days=1)
        answer_introduction = "In der Hauptmensa in Duisburg gab es gestern: \n \n"
    elif "vorgestern" in input_text:
        date -= datetime.timedelta(days=2)
        answer_introduction = "In der Hauptmensa in Duisburg gab es vorgestern: \n \n"
    elif "morgen" in input_text:
        date += datetime.timedelta(days=1)
        answer_introduction = "In der Hauptmensa in Duisburg gibt es morgen: \n \n"
    elif "übermorgen" in input_text:
        date += datetime.timedelta(days=2)
        answer_introduction = "In der Hauptmensa in Duisburg gibt es übermorgen: \n \n"

    timestamp = int(T.mktime(date.timetuple()))
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
        for node in xml_root.find('tag'):
            if node.attrib['timestamp'] == timestamp:
                requested_node = node
                break

        if requested_node is None:
            return "Leider ist für diesen Tag kein Speiseplan verfügbar"

        menu_as_string = answer_introduction
        has_menu = False
        for meal in meals.find_all(attrs={"class": "item"}):
            titles = meal.find_all(attrs={"class": "item_title"})
            descriptions = meal.find_all(attrs={"class": "item_description"})
            prices = meal.find_all(attrs={"class": "item_price"})

            if len(titles) == 0:
                continue
            elif len(titles) == 1:
                print(len(titles))
                title = titles[0]
                print("Title :" + str(title.string))
                menu_as_string += titles[0].string

                if descriptions[0].string is not None:
                    menu_as_string += " " + descriptions[0].string
                    has_menu = True
                if prices[0].string is not None:
                    price_string = prices[0].string
                    price_string = price_string.replace(" ","")
                    if '–' in price_string:
                        menu_as_string += " <b>" + price_string.split('–')[0] + "</b>"
                    else:
                        menu_as_string += " <b>" + price_string + "</b>"
                menu_as_string += "\n\n"
            #else:
                # TODO: return something for supplements

        if has_menu:
            return menu_as_string
        return "Leider ist für heute kein Speiseplan verfügbar"
    except:
        return "Bei der Bearbeitung der Anfrage ist leider etwas schiefgelaufen."