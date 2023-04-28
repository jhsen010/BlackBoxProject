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
        "SELECT ID, videodate FROM camera_normal WHERE videodate = '%s'"
        % strvideodate
    )
    bufferclean = cursor.fetchall()
    
def crash_watch(conn, strvideodate):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ID, videodate FROM camera_crash WHERE videodate = '%s'"
        % strvideodate
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
