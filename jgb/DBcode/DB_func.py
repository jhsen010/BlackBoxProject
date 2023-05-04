from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()


class Database:  ############################################클래스 미완성
    def __init__(self, ENDPOINT, PORT, USR, PWD, DBNAME):
        self.ENDPOINT = ENDPOINT
        self.PORT = PORT
        self.USR = USR
        self.PWD = PWD
        self.DBNAME = DBNAME


def rds_connect():
    # RDS endpoint, username, password, database name 설정
    ENDPOINT = os.environ.get("endpoint")
    PORT = os.environ.get("port")
    USR = os.environ.get("usr")
    PWD = os.environ.get("pwd")
    DBNAME = os.environ.get("dbname")

    # RDS에 연결
    try:
        conn = mysql.connector.connect(
            host=ENDPOINT, port=PORT, user=USR, password=PWD, database=DBNAME
        )
        print("Connected to RDS successfully!")
        return conn
    except Exception as e:
        print("Unable to connect to RDS.")
        print(e)


def sensor_insert(data, conn):
    strdate = data["strdate"]
    straccel = data["straccel"]
    strbreak = data["strbreak"]
    intspeed = data["intspeed"]
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sensor (date, accel, break, speed) VALUES ('%s', '%s', '%s', %d)"
        % (strdate, straccel, strbreak, intspeed)
    )
    cursor.execute("ALTER TABLE sensor AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
    cursor.execute("SET @COUNT = 0;")
    cursor.execute("UPDATE sensor SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
    conn.commit()
    return strdate, straccel, strbreak, intspeed


def sensor_select(conn):
    cursor = conn.cursor()
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


def normal_select(conn):
    cursor = conn.cursor()
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


def crash_select(conn):
    cursor = conn.cursor()
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


def normal_watch(conn, strvideodate):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ID, videodate FROM camera_normal WHERE videodate = '%s'" % strvideodate
    )
    bufferclean = cursor.fetchall()


def crash_watch(conn, strvideodate):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ID, videodate FROM camera_crash WHERE videodate = '%s'" % strvideodate
    )
    bufferclean = cursor.fetchall()


def normal_upload_insert(conn, file):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO camera_normal (videodate) VALUES ('%s')" % file.filename
    )
    cursor.execute("ALTER TABLE camera_normal AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
    cursor.execute("SET @COUNT = 0;")
    cursor.execute("UPDATE camera_normal SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
    conn.commit()


def crash_upload_insert(conn, file):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO camera_crash (videodate) VALUES ('%s')" % file.filename)
    cursor.execute("ALTER TABLE camera_crash AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
    cursor.execute("SET @COUNT = 0;")
    cursor.execute("UPDATE camera_crash SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
    conn.commit()


def normal_find(conn, data):
    strvideodate = data["strvideodate"]
    cursor = conn.cursor()
    findword = "%" + strvideodate + "%"
    cursor.execute(
        "SELECT ID, videodate FROM camera_normal WHERE videodate like  '%s'" % findword
    )
    records = cursor.fetchall()

    data = []
    for row in records:
        obj = {}
        obj["ID"] = row[0]
        obj["videodate"] = row[1]
        data.append(obj)

    return data


def crash_find(conn, data):
    strvideodate = data["strvideodate"]
    cursor = conn.cursor()
    findword = "%" + strvideodate + "%"
    cursor.execute(
        "SELECT ID, videodate FROM camera_crash WHERE videodate like  '%s'" % findword
    )
    records = cursor.fetchall()

    data = []
    for row in records:
        obj = {}
        obj["ID"] = row[0]
        obj["videodate"] = row[1]
        data.append(obj)

    return data


def eyes_insert(data, conn):
    strdate = data["strdate"]
    streyesnow = data["streyesnow"]
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO eyesnow (date, eyesnow) VALUES ('%s', '%s')"
        % (strdate, streyesnow)
    )
    cursor.execute("ALTER TABLE eyesnow AUTO_INCREMENT=1;")  # ID순서 꼬인거 풀기
    cursor.execute("SET @COUNT = 0;")
    cursor.execute("UPDATE eyesnow SET ID = @COUNT:=@COUNT+1")  # ID순서 꼬인거 풀기
    conn.commit()
    return strdate, streyesnow


def eyes_select(conn):
    cursor = conn.cursor()
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
