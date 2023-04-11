from flask import Flask, request, jsonify
from flask_restx import Api, Resource  # Api 구현을 위한 Api 객체 import
import mysql.connector

app = Flask(__name__)
api = Api(app)  # Flask 객체에 Api 객체 등록

# RDS endpoint, username, password, database name 설정
ENDPOINT = "moble.ckaipdhtuyli.ap-northeast-2.rds.amazonaws.com"
PORT = "3306"
USR = "moble_project"
PWD = "qoawkddj23"
DBNAME = "moble_project"

# RDS에 연결
try:
    conn = mysql.connector.connect(host=ENDPOINT, port=PORT, user=USR, password=PWD, database=DBNAME)
    print("Connected to RDS successfully!")
except Exception as e:
    print("Unable to connect to RDS.")
    print(e)

@api.route('/hello')  # 데코레이터 이용, '/hello' 경로에 클래스 등록
class HelloWorld(Resource):
    def get(self):  # GET 요청시 리턴 값에 해당 하는 dict를 JSON 형태로 반환
        return {"hello" : "/sensor/insert or /sensor/select"}

@api.route('/sensor/insert', methods=['POST'])
class sensorinsert(Resource):
    def post(self):
        try:
            data = request.get_json()
            strdate = data['strdate']
            straccel = data['straccel']
            strbreak = data['strbreak']
            intspeed = data['intspeed']
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sensor (date, accel, break, speed, dateforsearch) VALUES ('%s', '%s', '%s', %d)" % (strdate, straccel, strbreak, intspeed))
            cursor.execute("ALTER TABLE sensor AUTO_INCREMENT=1;") #ID순서 꼬인거 풀기
            cursor.execute("SET @COUNT = 0;")
            cursor.execute("UPDATE sensor SET ID = @COUNT:=@COUNT+1") #ID순서 꼬인거 풀기
            conn.commit()
            return {"inserted successfully!" : "%s, %s, %s, %d" % (strdate, straccel, strbreak, intspeed)}
        # except Exception as e:
        #     print("Error inserting record.")
        #     print(e)
        #     return "Error inserting record."
        except mysql.connector.Error as error: #원인찾기용도
            print(f"Failed to insert record into MySQL table: {error}")
            return f"Failed to insert record into MySQL table: {error}"

@api.route('/finddate/logdata', methods=['POST'])
class select(Resource):
    def post(self):
        try:
            data = request.get_json()
            strlogdate = data['strlogdate']
            cursor = conn.cursor()
            findword = '%'+strlogdate+'%'
            cursor.execute("SELECT ID, date, accel, break, speed FROM sensor WHERE date LIKE '%s'" % findword)
            records = cursor.fetchall()
            return str(records)
        except Exception as e:
            print("Error finding log.")
            print(e)
            return "Error finding log."

@api.route('/Nvideo/upload', methods=['POST'])
class sensorinsert(Resource):
    def post(self):
        try:
            
            return "normal video upload seccesfuly"
        except Exception as e:
            print("Error uploading bormal video.")
            print(e)
            return "Error uploading bormal video."

if __name__ == '__main__':
    app.run(host='0.0.0.0')
