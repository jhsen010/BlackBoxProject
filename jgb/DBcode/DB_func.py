def DBsensorinput(data, conn):
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
