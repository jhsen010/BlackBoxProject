from dotenv import load_dotenv
import mysql.connector
import os
import threading

load_dotenv()


class Database:
    def __init__(self):
        self.ENDPOINT = os.environ.get("endpoint")
        self.PORT = os.environ.get("port")
        self.USR = os.environ.get("usr")
        self.PWD = os.environ.get("pwd")
        self.DBNAME = os.environ.get("dbname")
        self.conn = mysql.connector.connect(
            host=self.ENDPOINT,
            port=self.PORT,
            user=self.USR,
            password=self.PWD,
            database=self.DBNAME,
        )
        self.local = threading.local()

    def _get_conn(self):  # sensor insert 받아오기 쓰레드화 하기 위해 개별 conn 생성
        if not hasattr(self.local, "conn"):
            self.local.conn = mysql.connector.connect(
                host=self.ENDPOINT,
                port=self.PORT,
                user=self.USR,
                password=self.PWD,
                database=self.DBNAME,
            )
        return self.local.conn

    def _get_cursor(self):  # sensor insert 받아오기 쓰레드화 하기 위해 개별 conn 생성
        if not hasattr(self.local, "cursor"):
            self.local.cursor = self._get_conn().cursor()
        return self.local.cursor

    def sensor_insert(self, data):
        strdate = data["strdate"]
        straccel = data["straccel"]
        strbreak = data["strbreak"]
        intspeed = data["intspeed"]
        # cursor = self.conn.cursor()
        cursor = self._get_cursor()
        cursor.execute(
            "INSERT INTO sensor (date, accel, break, speed) VALUES ('%s', '%s', '%s', %d)"
            % (strdate, straccel, strbreak, intspeed)
        )
        cursor.execute("ALTER TABLE sensor AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
        cursor.execute("SET @COUNT = 0;")
        cursor.execute("UPDATE sensor SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
        # self.conn.commit()
        self._get_conn().commit()
        return {
            "inserted successfully!": "%s, %s, %s, %d"
            % (strdate, straccel, strbreak, intspeed)
        }

    def sensor_select(self):
        # cursor = self.conn.cursor()
        cursor = self._get_cursor()
        cursor.execute("ALTER TABLE sensor AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
        cursor.execute("SET @COUNT = 0;")
        cursor.execute("UPDATE sensor SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
        cursor.execute("SELECT * FROM sensor")
        records = cursor.fetchall()

        data = []
        for row in records:
            obj = {}
            obj["ID"] = row[0]
            obj["date"] = row[1]
            obj["accel"] = row[2]
            obj["break"] = row[3]
            obj["speed"] = row[4]
            data.append(obj)

        return data

    def normal_select(self):
        # cursor = self.conn.cursor()
        cursor = self._get_cursor()
        cursor.execute("ALTER TABLE camera_normal AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
        cursor.execute("SET @COUNT = 0;")
        cursor.execute("UPDATE camera_normal SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
        cursor.execute("SELECT * FROM camera_normal")
        records = cursor.fetchall()

        data = []
        for row in records:
            obj = {}
            obj["ID"] = row[0]
            obj["videodate"] = row[1]
            data.append(obj)

        return data

    def crash_select(self):
        # cursor = self.conn.cursor()
        cursor = self._get_cursor()
        cursor.execute("ALTER TABLE camera_crash AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
        cursor.execute("SET @COUNT = 0;")
        cursor.execute("UPDATE camera_crash SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
        cursor.execute("SELECT * FROM camera_crash")
        records = cursor.fetchall()

        data = []
        for row in records:
            obj = {}
            obj["ID"] = row[0]
            obj["videodate"] = row[1]
            data.append(obj)

        return data

    def normal_watch(self, strvideodate):
        # cursor = self.conn.cursor()
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT ID, videodate FROM camera_normal WHERE videodate = '%s'"
            % strvideodate
        )
        bufferclean = cursor.fetchall()

    def crash_watch(self, strvideodate):
        # cursor = self.conn.cursor()
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT ID, videodate FROM camera_crash WHERE videodate = '%s'"
            % strvideodate
        )
        bufferclean = cursor.fetchall()

    def normal_upload_insert(self, file):
        # cursor = self.conn.cursor()
        cursor = self._get_cursor()
        cursor.execute(
            "INSERT INTO camera_normal (videodate) VALUES ('%s')" % file.filename
        )
        cursor.execute("ALTER TABLE camera_normal AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
        cursor.execute("SET @COUNT = 0;")
        cursor.execute("UPDATE camera_normal SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
        self.conn.commit()

    def crash_upload_insert(self, file):
        # cursor = self.conn.cursor()
        cursor = self._get_cursor()
        cursor.execute(
            "INSERT INTO camera_crash (videodate) VALUES ('%s')" % file.filename
        )
        cursor.execute("ALTER TABLE camera_crash AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
        cursor.execute("SET @COUNT = 0;")
        cursor.execute("UPDATE camera_crash SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
        self.conn.commit()

    def normal_find(self, data):
        strvideodate = data["strvideodate"]
        # cursor = self.conn.cursor()
        cursor = self._get_cursor()
        findword = "%" + strvideodate + "%"
        cursor.execute(
            "SELECT ID, videodate FROM camera_normal WHERE videodate like  '%s'"
            % findword
        )
        records = cursor.fetchall()

        data = []
        for row in records:
            obj = {}
            obj["ID"] = row[0]
            obj["videodate"] = row[1]
            data.append(obj)

        return data

    def crash_find(self, data):
        strvideodate = data["strvideodate"]
        # cursor = self.conn.cursor()
        cursor = self._get_cursor()
        findword = "%" + strvideodate + "%"
        cursor.execute(
            "SELECT ID, videodate FROM camera_crash WHERE videodate like  '%s'"
            % findword
        )
        records = cursor.fetchall()

        data = []
        for row in records:
            obj = {}
            obj["ID"] = row[0]
            obj["videodate"] = row[1]
            data.append(obj)

        return data

    def eyes_insert(self, data):
        strdate = data["strdate"]
        streyesnow = data["streyesnow"]
        # cursor = self.conn.cursor()
        cursor = self._get_cursor()
        cursor.execute(
            "INSERT INTO eyesnow (date, eyesnow) VALUES ('%s', '%s')"
            % (strdate, streyesnow)
        )
        cursor.execute("ALTER TABLE eyesnow AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
        cursor.execute("SET @COUNT = 0;")
        cursor.execute("UPDATE eyesnow SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
        self.conn.commit()
        return strdate, streyesnow

    def eyes_select(self):
        # cursor = self.conn.cursor()
        cursor = self._get_cursor()
        cursor.execute("ALTER TABLE eyesnow AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
        cursor.execute("SET @COUNT = 0;")
        cursor.execute("UPDATE eyesnow SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
        cursor.execute("SELECT * FROM eyesnow")
        records = cursor.fetchall()

        data = []
        for row in records:
            obj = {}
            obj["ID"] = row[0]
            obj["date"] = row[1]
            obj["eyesnow"] = row[2]
            data.append(obj)

        return data
