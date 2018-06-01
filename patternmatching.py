from kombot import send_message, send_message_html, send_photo, send_location, build_keyboard, build_lecture_keyboard, build_keyboard_remove, db, GERMAN_WEEKDAYS, send_document
from canteenmenuhelper import get_menu_as_string
import synonyms as syn
import json
import os


EMOJI_SAD = u'\U0001F613'
EMOJI_NERD = u'\U0001F913'

_wants_to_know_where = []
_wants_to_remove = []

g_skill_text = None
g_text = None
g_chat = None

# Checks for skill match and returns true if an answer was found, else false
# Sends answer to user immediately (if answer was found)
def get_skill_match(skill_name, skill_text, text, chat):
    global g_skill_text, g_text, g_chat
    g_skill_text = skill_text
    g_text = text
    g_chat = chat

    if skill_name == "AnswerHello":
        return answer_hello()
    if skill_name == "AnswerHowAreYou":
        return answer_how_are_you()
    if skill_name == "GetBotInformation":
        return get_bot_information()
    if skill_name == "GetCertificateOfStudy":
        return get_certificate_of_study()
    elif skill_name == "GetExamRegistration":
        return get_exam_registration()
    elif skill_name == "GetFreeSoftware":
        return get_free_software()
    elif skill_name == "GetHowToUse":
        return get_how_to_use()
    elif skill_name == "GetLearningGroup":
        return get_learning_group()
    elif skill_name == "GetLectureTime":
        return get_lecture_time()
    elif skill_name == "GetLecturePlace":
        return get_lecture_place()
    elif skill_name == "GetMenu":
        return get_menu()
    elif skill_name == "GetRoom":
        return get_room()
    elif skill_name == "GeneralWhere":
        return question_where()
    elif skill_name == "GetSemesterFee":
        return get_semester_fee()
    elif skill_name == "GetTestSubjectHours":
        return get_test_subject_hours()
    elif skill_name == "GetVPN":
        return get_vpn()
    elif skill_name == "GetLectures":
        return get_lectures()
    elif skill_name == "AddLectureToShedule":
        return add_lecture_to_shedule()
    elif skill_name == "GetMyShedule":
        return get_my_shedule()
    elif skill_name == "DeleteLectureFromShedule":
        return delete_lecture_from_shedule()
    else:
        print("Error: No pattern " + skill_name + " found.")

    return False

def answer_hello():
    global g_chat
    answer = "Hallo :)"
    send_message(answer, g_chat)
    return True

def answer_how_are_you():
    global g_chat
    answer = "Ich bin ein Bot und habe daher keine Gefühle"
    send_message(answer, g_chat)
    return True

def get_bot_information():
    global g_chat
    answer = "Hallo, ich bin der ganz persönliche Chatbot für Erstsemester des Komedia-Studiengangs. \n" \
             "Ich habe Informationen über die folgenden Bereiche: \n \n" \
             "- Vorlesungen und Zeiten \n" \
             "- Räume und Veranstaltungen\n" \
             "- Mensa-Speisepläne \n" \
             "- Semesterbeiträge \n" \
             "- Prüfungsanmeldungen \n" \
             "- Studienbescheinigungen \n" \
             "\n" \
             "...und noch vieles mehr!"

    send_message(answer, g_chat)
    return True


def get_certificate_of_study():
    global g_chat
    answer = "Die Studienbescheinigung ist unter folgendem Link verfügbar:\n" \
             "https://campus.uni-due.de/cm/ \n \n" \
             "Schritte:\n" \
             "1.) Mit Unikennung einloggen \n" \
             "2.) Auf \"Mein Studium\" -> \"Studienservice\" -> \"Bescheinigungen\" klicken \n" \
             "3.) .pdf-Datei mit Studienbescheinigung runterladen "
    send_message(answer, g_chat)
    return True


def get_exam_registration():
    global g_chat
    answer = "Die Prüfungsanmeldephase für das Sommersemester 2018 beginnt am 07.05.18 und endet am 18.05.18.\n" \
             "Eine Prüfung kann über folgendes Portal angemeldet werden: \n\n" \
             "https://campus.uni-due.de/lsf  \n\n" \
             "Terminpläne für Bachelor und Master sind unter folgendem Link zu finden: \n\n" \
             "https://www.uni-due.de/verwaltung/pruefungswesen/d_komed_startseite.php"
    send_message(answer, g_chat)
    return True

def get_free_software():
    global g_chat
    send_message("FreeSoftware", g_chat)
    return True

def get_how_to_use():
    global g_chat
    send_message("HowTo", g_chat)
    return True

def get_learning_group():
    global g_chat
    answer = "Lerngruppen findest du möglicherweise im komedia-Forum: \n" \
             "http://fsr-komedia.zim.uni-due.de/forum/ \n\n" \
             "Falls nicht: Geh in die Uni und sprich Kommilitonen an " + EMOJI_NERD
    send_message(answer, g_chat)
    return True

def get_lecture_time():
    global g_chat, g_text
    lectures = db.get_all_lecture_infos()
    for lecture in lectures:
        print(lecture)
    matched_lecture = match_lecture_name(g_text, lectures)
    message = ""
    if matched_lecture:
        message = "Die Vorlesung {} findet von {} Uhr bis {} Uhr am {} statt.".format(matched_lecture["title"], matched_lecture["start"], matched_lecture["end"], GERMAN_WEEKDAYS[matched_lecture["weekday"]])
    else:
        message = ("Ich kenne diese Vorlesung leider nicht, oder du hast nicht den richtigen Namen verwendet. Die Bezeichnungen findest du hier:"
                   "https://www.uni-due.de/imperia/md/content/vv/vvz_ws_2017-18_due_1011_inkowiss.pdf")
    send_message(message, g_chat)
    return True

def get_lecture_place():
    global g_chat, g_text
    lectures = db.get_all_lecture_infos()
    matched_lecture = match_lecture_name(g_text, lectures)
    message = ""
    found = False
    if matched_lecture:
        message = "Die Vorlesung {} findet im Raum {} statt.".format(matched_lecture["title"], matched_lecture["room_name"])
        found = True
    else:
        message = ("Ich kenne diese Vorlesung leider nicht, oder du hast nicht den richtigen Namen verwendet. Die Bezeichnungen findest du hier:"
                   "https://www.uni-due.de/imperia/md/content/vv/vvz_ws_2017-18_due_1011_inkowiss.pdf")
    send_message(message, g_chat)
    if found:
        send_location(g_chat, matched_lecture["room_longitude"], matched_lecture["room_latitude"])
    return True

def get_menu():
    global g_chat
    menu = get_menu_as_string()
    send_message_html(menu, g_chat)
    return True


def get_room():
    global g_chat, g_text
    rooms = db.get_all_room_infos()
    matched_room = match_room_name(g_text, rooms)
    message = ""
    found = False
    if matched_room:
        message = "Der Raum befindet sich hier:"
        found = True
    else:
        message = "Ich kenne diesen Raum leider nicht."
    send_message(message, g_chat)
    if found:
        send_location(g_chat, matched_room["longitude"], matched_room["latitude"])
    return True

def get_semester_fee():
    global g_chat
    answer = "Der Sozial- und Studierendenschaftsbeitrag beträgt für das Sommersemester 2018 insgesamt 304,62 €.\n" \
             "Der Beitrag kann bis zum 02.03.2018 überwiesen werden."
    send_message(answer, g_chat)
    return True

def get_test_subject_hours():
    global g_chat
    answer = "Versuchspersonenstunden (VPS) werden für die Teilnahme an wissenschaftlichen Studien vergeben. \n" \
             "Ausschreibungen findest du unter anderem im Komedia-Forum \n" \
             "http://fsr-komedia.zim.uni-due.de/forum/ \n" \
             "oder bei Facebook im Komedia-Versuchspersonenmarkt\n" \
             "https://www.facebook.com/groups/1089565127742196/ \n\n" \
             "Neben anderen Veranstaltungen sind 30 VPS die Voraussetzung um das Modul \"Methodologie psychologischer Forschung\" " \
             "abzuschließen."
    send_message(answer, g_chat)
    return True

def get_vpn():
    global g_chat
    answer = "Der Zugriff auf Uni-Dienste von z.B. Zuhause aus kann über eine VPN-Verbindung gewährleistet werden." \
             "Windows-Nutzer können hierfür Cisco AnyConnect verwenden: \n" \
             "https://www.uni-due.de/zim/services/internetzugang/cisco-vpn-anyconnect \n\n" \
             "Für MacOS und Linux bietet sich OpenConnect an: \n" \
             "https://www.uni-due.de/zim/services/internetzugang/openconnect.php"
    send_message(answer, g_chat)
    return True

def question_where():
    global g_chat
    answer = "Du suchst anscheind einen Ort. Was genau suchst du?"
    options = [["Wo findet eine Vorlesung statt?"],["Wo befindet sich ein Raum?"]]
    _wants_to_know_where.append(g_chat)
    send_message(answer, g_chat, build_keyboard(options))
    return True

def get_lectures():
    g_chat
    lectures = db.get_all_lecture_infos()
    message = "Das sind alle Vorlesungen:\n"
    for lecture in lectures:
        message += "\n " + lecture["title"] + "\n"
    send_message(message, g_chat)
    return True

def add_lecture_to_shedule():
    g_chat, g_text
    lectures = db.get_all_lecture_infos()
    shedule = db.get_studentlectures(g_chat)
    matched_lecture = match_lecture_name(g_text, lectures)
    message = ""
    if matched_lecture["title"] in shedule:
        message = "Die Vorlesung {} ist bereits in deinem Stundenplan eingetragen.".format(matched_lecture["title"])
    elif matched_lecture:
        lecture_id = db.get_lecture_id(matched_lecture["title"])
        db.add_lecture(lecture_id, g_chat)
        message = "Ich habe die Vorlesung {} zu deinem Stundenplan hinzugefügt. Sie ist am {} von {} Uhr bis {} Uhr in {}.".format(matched_lecture["title"],                                                                                                                               GERMAN_WEEKDAYS[matched_lecture["weekday"]],
                                                matched_lecture["start"], matched_lecture["end"],
                                                matched_lecture["room_name"])
    else:
        message = ("Ich habe diese Vorlesung leider nicht gefunden." + EMOJI_SAD + "\nHier sind alle Vorlesungen aufgeführt:"
                   "https://www.uni-due.de/imperia/md/content/vv/vvz_ws_2017-18_due_1011_inkowiss.pdf")
    send_message(message, g_chat)
    return True

def delete_lecture_from_shedule():
    g_chat
    _wants_to_remove.append(g_chat)
    lectures = db.get_studentlectures(g_chat)
    keyboard = build_lecture_keyboard(lectures)
    send_message("Wähle eine Vorlesung aus, die gelöscht werden soll", g_chat, keyboard)
    return True

def get_my_shedule():
    g_chat
    lectures = db.get_studentlectures(g_chat)
    message = "Das sind alle deine Vorlesungen dieses Semester:\n"
    for lecture in lectures:
        message += "\n " + lecture + "\n"
    send_message(message, g_chat)
    return True

def match_lecture_name(input_text, lectures):
    titles = []
    synonyms_title = []
    for lecture in lectures:
        titles.append(lecture["title"])
    stripped_text = input_text.lower().replace(" ", "")
    for title in titles:
        try:
            synonyms_title = syn.synonyms[title]
        except KeyError:
            print("Error")#nothing
        print("Test")
        stripped_title = title.lower().replace(" ", "")
        if(stripped_title in stripped_text):
            return lectures[titles.index(title)]
        else:
            for synonym in synonyms_title:
                stripped_synonym = synonym.lower().replace(" ", "")
                print(stripped_synonym)
                if(stripped_synonym in stripped_text):
                    return lectures[titles.index(title)]
    return None

def match_room_name(input_text, rooms):
    names = []
    for room in rooms:
        names.append(room["name"].lower().replace(" ", ""))
    stripped_text = input_text.lower().replace(" ", "")
    for name in names:
        if(name in stripped_text):
            return rooms[names.index(name)]
    return None