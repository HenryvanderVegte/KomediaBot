from kombot import send_message, send_location, send_document, build_keyboard, build_lecture_keyboard, build_keyboard_remove, db, GERMAN_WEEKDAYS
from patternmatching import get_skill_match, _wants_to_know_where, _wants_to_remove
import json
import os

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

_wants_to_know_lecture_room = []
_wants_to_know_room = []


def handle_msg(msg):
    try:
        text = msg["message"]["text"]
        chat = msg["message"]["chat"]["id"]

        if text.startswith('/'):
            handle_command(text, chat)
        else:
            get_pattern_match(text, chat)
    except KeyError:
        pass


def get_pattern_match(text, chat):
    if(chat in _wants_to_remove):
        lectures = db.get_studentlectures(chat)
        if(text in lectures):
            db.delete_lecture_by_title(text, chat)
            _wants_to_remove.remove(chat)
            message = "Ich habe die Vorlesung {} aus deinem Studenplan gelöscht.".format(text)
        send_message(message, chat, build_keyboard_remove())
        return
    elif chat in _wants_to_know_where:
        message = ""
        if text == "Wo findet eine Vorlesung statt?":
            message = "Um welche Vorlesung geht es?"
            _wants_to_know_lecture_room.append(chat)
        elif text == "Wo befindet sich ein Raum?":
            message = "Um welchen Raum geht es?"
            _wants_to_know_room.append(chat)
        else:
            message = "Oh dann frag mich doch einfach etwas anderes."
        _wants_to_know_where.remove(chat)
        send_message(message, chat, build_keyboard_remove())
        return
    elif chat in _wants_to_know_lecture_room:
        text = "Wo findet {} statt?".format(text)
        _wants_to_know_lecture_room.remove(chat)
    elif chat in _wants_to_know_room:
        text = "Wo ist Raum {}?".format(text)
        _wants_to_know_room.remove(chat)

    cleaned_text = text.strip()
    removeChars = "_?!.-"
    for char in removeChars:
        cleaned_text = cleaned_text.replace(char, "")
    cleaned_text = cleaned_text.lower()

    gave_answer = False
    with open(os.path.join(__location__, 'patterns.dat'), encoding='utf-8') as file:
        for line in file:
            if len(line) <= 1:
                continue
            skill_name = line.split(' ', 1)[0]
            skill_text = line.split(' ', 1)[1]

            skill_text = skill_text.strip()
            skill_patterns = skill_text.split("_")

            pattern_match = True

            for x in range(0, len(skill_patterns)):
                if len(skill_patterns[x]) == 0:
                    continue
                skill_patterns[x] = skill_patterns[x].strip()
                skill_patterns[x] = skill_patterns[x].lower()
                if x == 0:
                    if not cleaned_text.startswith(skill_patterns[x]):
                        pattern_match = False
                        break
                elif x == len(skill_patterns) - 1:
                    if not cleaned_text.endswith(skill_patterns[x]):
                        pattern_match = False
                        break
                else:
                    if skill_patterns[x] not in cleaned_text:
                        pattern_match = False
                        break

            if pattern_match:
                if get_skill_match(skill_name, skill_text, cleaned_text, chat):
                    gave_answer = True
                    break

    if not gave_answer:
        with open("unknown_requests.txt", "a") as myfile:
            myfile.write(cleaned_text + "\n")
        send_message("Das habe ich leider nicht verstanden.", chat)

def handle_command(text, chat):
    args = None
    targs = None
    subs = text.split(" ")
    cmd = text[1:]
    if len(subs) > 1:
        targs = subs[1:]
        cmd = subs[0][1:]
    # Construct args
    if targs:
        first = None
        args = []
        for sub in targs:
            if first:
                first = first + " " + sub
                if "\"" in sub or "„" in sub or "“" in sub:
                    args.append(first[:len(first) - 1])
                    first = None
            else:
                if "\"" in sub or "„" in sub or "“" in sub:
                    first = sub[1:]
                else:
                    args.append(sub)
    check_for_command(cmd, chat, args)


def check_for_command(cmd, chat, args=None):
    sargs = "None"
    if args:
        sargs = ''.join(args)
    print("[BOT]:: Checking for command : " + cmd
          + " with arguments : " + sargs)
    if cmd == "removelecture":
        _wants_to_remove.append(chat)
        lectures = db.get_studentlectures(chat)
        keyboard = build_lecture_keyboard(lectures)
        send_message("Wähle eine Vorlesung aus, die gelöscht werden soll",
                     chat,
                     keyboard)
    elif cmd == "addlecture":
        if args:
            print("ARGS = " + args[0])
            lectureid = -1
            # Check type
            if type(args[0]) is int:
                lectureid = args[0]
            elif type(args[0]) is str:
                # Find lectureID
                name = args[0]
                lectureid = db.get_lecture_id(name)
            print("[BOT]:: Command detected : ADD LECTURE with ID =  "
                  + str(lectureid))
            if lectureid >= 0:
                db.add_lecture(lectureid, chat)
                lectures = db.get_studentlectures(chat)
                message = "\n".join(lectures)
                send_message(message, chat)
    elif cmd == "getlectures":
        lectures = db.get_studentlectures(chat)
        message = ("Diese Vorlesungen hast du "
                   "in deinem Stundenplan:\n")
        for lecture in lectures:
            message += '\n' + lecture
        send_message(message, chat)
    elif cmd == "showlectures":
        lectures = db.get_lectures()
        message = ("Diese Vorlesungen hast du "
                   "in deinem Stundenplan:\n")
        for lecture in lectures:
            message += '\n' + lecture
        send_message(message, chat)
    elif cmd == "getlectureinfos":
        if args:
            lecture_id = -1
            try:
                lecture_id = int(args[0])
            except ValueError as err:
                return
            lecture_infos = db.get_lecture_infos(lecture_id)
            if lecture_infos:
                print("[BOT]:: Command detected : GET LECTURE INFOS = " + lecture_infos["title"] + " on " + lecture_infos["weekday"] + " from " + lecture_infos["start"] + " to " + lecture_infos["end"] + " in room " + lecture_infos["room_name"])
                message = "Die Vorlesung {} findet am {} von {} Uhr bis {} Uhr in Raum {} statt.".format(lecture_infos["title"],
                                                                                            GERMAN_WEEKDAYS[lecture_infos["weekday"]],
                                                                                            lecture_infos["start"],
                                                                                            lecture_infos["end"],
                                                                                            lecture_infos["room_name"])
                send_message(message, chat)
            else:
                print("[BOT]:: Command detected : GET LECTURE INFOS = NO LECTURE FOUND!" )
                message = "Tut mir Leid, ich weiß leider nichts über die Vorlesung mit dem Titel {}. Bist du dir sicher, dass sie existiert?".format(args[0])
                send_message(message, chat)
    elif cmd == "getroominfos":
        if args:
            room_infos = db.get_room_infos(args[0])
            if room_infos:
                print("[BOT]:: Command detected : GET ROOM INFOS = " + room_infos["name"] + " on floor " + str(room_infos["floor"]) + " at longitude " + room_infos["longitude"] + " and latitude " + room_infos["latitude"])
                message = "Der Raum, den du suchst befindet sich hier im {} Stock:".format(str(room_infos["floor"]))
                send_message(message, chat)
                send_location(chat, room_infos["longitude"], room_infos["latitude"])
            else:
                print("[BOT]:: Command detected : GET ROOM INFOS = NO ROOM FOUND!" )
                message = "Tut mir Leid, ich weiß leider nicht wo der Raum {} ist. Bist du dir sicher, dass er existiert?".format(args[0])
                send_message(message, chat)
    else:
        print("[BOT]:: Command not found : " + cmd)

def waiting_for(option, chat):
    if(option == "where"):
        _wants_to_know_where.append(chat)