from dotenv import load_dotenv
import os
import mysql.connector

def str
load_dotenv()
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
except Exception as e:
    print("Unable to connect to RDS.")
    print(e)
