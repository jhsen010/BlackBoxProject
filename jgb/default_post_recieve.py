from flask import Flask, request, jsonify
from flask_restx import Api, Resource
import mysql.connector

app = Flask(__name__)
api = Api(app)

ENDPOINT = "moble.ckaipdhtuyli.ap-northeast-2.rds.amazonaws.com"
PORT = "3306"
USR = "moble_project"
PWD = "qoawkddj23"
DBNAME = "moble_project"

try:
    conn = mysql.connector.connect(host=ENDPOINT, port=PORT, user=USR, password=PWD, database=DBNAME)
    print("Connected to RDS successfully!")
except Exception as e:
    print("Unable to connect to RDS.")
    print(e)

@api.route('/sensor/insert', methods=['POST'])
class SensorInsert(Resource):
    def post(self):
        try:
            data = request.get_json()
            straccel = data['straccel']
            strbreak = data['strbreak']
            intspeed = data['intspeed']
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sensor (accel, break, speed) VALUES ('%s', '%s', %d)" % (straccel, strbreak, intspeed))
            conn.commit()
            return {"inserted successfully!" : "%s, %s, %d" % (straccel, strbreak, intspeed)}
        except mysql.connector.Error as error:
            print(f"Failed to insert record into MySQL table: {error}")
            return f"Failed to insert record into MySQL table: {error}"

if __name__ == '__main__':
    app.run(host='0.0.0.0')
