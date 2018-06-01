import sqlite3


class DBManager:

    def __init__(self, dbname="knowledge.db"):
        self.dbname = dbname
        self.connection = sqlite3.connect(dbname)

    def setup_timetable(self):
        tblstmt = ("CREATE TABLE IF NOT EXISTS studentlectures ("
                   "lecture integer,"
                   "owner text,"
                   "FOREIGN KEY (lecture) REFERENCES lecture(lectureid))")
        ownidx = ("CREATE INDEX IF NOT EXISTS ownIndex"
                  " ON studentlectures (owner ASC)")
        self.connection.execute(tblstmt)
        self.connection.execute(ownidx)
        self.connection.commit()

    def add_lecture(self, lecture_id, owner):
        stmt = ("INSERT INTO studentlectures (lecture, owner)"
                " VALUES (?,?)")
        args = (lecture_id, owner)
        self.connection.execute(stmt, args)
        self.connection.commit()

    def delete_lecture(self, lecture_id, owner):
        stmt = ("DELETE FROM studentlectures"
                " WHERE lecture = (?)"
                " AND owner = (?)")
        args = (lecture_id, owner)
        self.connection.execute(stmt, args)
        self.connection.commit()
        
    def delete_lecture_by_title(self, lecture_title, owner):
        stmt = ("DELETE FROM studentlectures"
                " WHERE lecture IN ("
                " SELECT lecture FROM studentlectures"
                " INNER JOIN lecture"
                " ON lecture.lectureid = studentlectures.lecture"
                " WHERE title = (?)"
                " AND owner = (?)"
                ")")
        args = (lecture_title, owner)
        self.connection.execute(stmt, args)
        self.connection.commit()

    def get_lecture_id(self, lecture_title):
        stmt = ("SELECT lectureid FROM lecture"
                " WHERE title = (?)")
        args = (lecture_title, )
        result = self.connection.execute(stmt, args).fetchone()
        print(result)
        if result:
            return int(result[0])
        else:
            return -1

    def get_lecture_infos(self, lecture_id):
        stmt = ("SELECT title, weekday, start, end, name, floor, longitude, latitude"
                " FROM lecture"
                " INNER JOIN room"
                " ON room.roomid = lecture.room"
                " WHERE lectureid = (?)")
        args = (lecture_id, )
        result = self.connection.execute(stmt, args).fetchone()
        lecture_infos = {
            "title": result[0],
            "weekday": result[1],
            "start": result[2],
            "end": result[3],
            "room_name": result[4],
            "room_floor": result[5],
            "room_longitude": result[6],
            "room_latitude": result[7]
        }
        return lecture_infos

    def get_all_lecture_infos(self):
         stmt = ("SELECT title, weekday, start, end, name, floor, longitude, latitude"
                " FROM lecture"
                " INNER JOIN room"
                " ON room.roomid = lecture.room")
         result = self.connection.execute(stmt)
         lectures = []
         for row in result:
             info = {
                "title": row[0],
                "weekday": row[1],
                "start": row[2],
                "end": row[3],
                "room_name": row[4],
                "room_floor": row[5],
                "room_longitude": row[6],
                "room_latitude": row[7]
             }
             lectures.append(info)
         return lectures

    def get_room_infos(self, room_name):
        stmt = ("SELECT floor, longitude, latitude"
                " FROM room"
                " WHERE name = (?)")
        args = (room_name, )
        result = self.connection.execute(stmt, args).fetchone()
        if result:
            room_infos = {
                "name": room_name,
                "floor": result[0],
                "longitude": result[1],
                "latitude": result[2]
                }
            return room_infos;
        else:
            return None
    def get_all_room_infos(self):
        stmt = ("SELECT name, floor, longitude, latitude"
                " FROM room")
        result = self.connection.execute(stmt)
        rooms = []
        for row in result:
            room = {
                "name": row[0],
                "floor": row[1],
                "longitude": row[2],
                "latitude": row[3]
                }
            rooms.append(room)
        return rooms

    def get_studentlectures(self, owner):
        stmt = ("SELECT title FROM lecture"
                " INNER JOIN studentlectures"
                " ON studentlectures.lecture = lecture.lectureid"
                " WHERE studentlectures.owner = (?)")
        args = (owner, )
        return [x[0] for x in self.connection.execute(stmt, args)]

    def get_lectures(self):
        stmt = "SELECT title FROM lecture"
        return [x[0] for x in self.connection.execute(stmt)]
