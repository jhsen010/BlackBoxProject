import pymysql
import requests
import json

# 데이터 베이스 연결
conn = pymysql.connect(
    user="root", password="0000", host="localhost", charset="utf8", database="Sensor"
)

# 데이터 가져오기
cur = conn.cursor()
cur.execute("SELECT DATE, SPEED, EXEL_VALUE, BREAK_VALUE FROM sensordata;")
rows = cur.fetchall()


# 데이터 전송
url = "http://43.201.154.195:5000/sensor/insert"
for row in rows:
    data = {
        "strdate": row[0],
        "straccel": row[2],
        "strbreak": row[3],
        "intspeed": row[1],
    }
    headers = {"Content-type": "application/json"}
    data_json = json.dumps(data)
    requests.post(url, data=data_json, headers=headers)
