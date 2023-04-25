class Oper:
    def __init__(self):
        self.ENDPOINT
        self.PORT
        self.USR
        self.PWD
        self.DBNAME

    def insert(self, data):
        self.ENDPOINT = "moble.ckaipdhtuyli.ap-northeast-2.rds.amazonaws.com"
        self.PORT = "3306"
        self.USR = "moble_project"
        self.PWD = AWS_PASSWD
        self.DBNAME = "moble_project"
        return self.res
