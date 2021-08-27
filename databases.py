import re
from pymongo import MongoClient
import bcrypt
import uuid
import json

class Database:
    def __init__(self):
        self.credentials = json.load(open('config.json'))
        self.client = MongoClient(self.credentials['MONGO_URI'])

    def checkMail(self, mail):
        return bool(re.match('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', mail))
    
    def getUser(self, mail):
        return self.client.Cookbook.users.find_one({'mail': mail})

    def registerUser(self, username, mail, password):
        if self.checkMail(mail) and self.getUser(mail) is None:
            bp = bytes(password, encoding= 'utf-8')
            password = bcrypt.hashpw(bp, bcrypt.gensalt());
            self.client.Cookbook.users.insert_one({'_id':str(uuid.uuid4()), 'mail': mail, 'password': password, 'username': username})
            return True
        return False
    
    def loginUser(self, mail, password):
        if self.checkMail(mail):
            user = self.client.Cookbook.users.find_one({'mail': mail})
            if user is not None:
                if bcrypt.checkpw(password, user['password']):
                    return True
                return False
            return False
        return False
