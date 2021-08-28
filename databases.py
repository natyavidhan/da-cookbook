import re
from pymongo import MongoClient
import bcrypt
import uuid
import json
import pyrebase


class Database:
    def __init__(self):
        self.credentials = json.load(open('config.json'))
        self.client = MongoClient(self.credentials['MONGO_URI'])
        self.firebase = pyrebase.initialize_app(
            self.credentials['firebaseConfig'])
        self.storage = self.firebase.storage()

    def checkMail(self, mail):
        return bool(re.match('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', mail))

    def getUser(self, mail):
        return self.client.Cookbook.users.find_one({'mail': mail})

    def registerUser(self, username, mail, password):
        if self.checkMail(mail) and self.getUser(mail) is None:
            bp = bytes(password, encoding='utf-8')
            password = bcrypt.hashpw(bp, bcrypt.gensalt())
            self.client.Cookbook.users.insert_one({
                '_id': str(uuid.uuid4()),
                'mail': mail,
                'password': password,
                'username': username,
                'recipies': [],
                'favorites': [],
                'liked': [],
                'following': [],
                'followers': 0})
            return True
        return False

    def loginUser(self, mail, password):
        if self.checkMail(mail):
            user = self.client.Cookbook.users.find_one({'mail': mail})
            if user is not None:
                if bcrypt.checkpw(password.encode('utf8'), user['password']):
                    return True
                return False
            return False
        return False

    def addRecipie(self, title: str, tags: list, user: str, description: str, ingredients: list, steps: list, image=None):
        ID = str(uuid.uuid4())
        if image is not None:
            self.storage.child(f"thumbnail/{user}/{ID}").put(image)
            extention = image.filename.split('.')[-1]
            link = self.storage.child(
                f"thumbnail/{user}/{ID}.{extention}").get_url(None)

        data = {
            "_id": ID,
            "title": title,
            "tags": tags,
            "by": user,
            "description": description,
            "ingredients": ingredients,
            "steps": steps,
            "image": link
        }
        self.client.Cookbook.recipies.insert_one(data)
        recipies = self.client.Cookbook.users.find_one({'_id': user})['recipies']
        recipies.append(ID)
        self.client.Cookbook.users.update_one({'_id': user}, {'$set': {'recipies': recipies}})

    def getRecipiesOfUser(self, user):
        return self.client.Cookbook.recipies.find({'by': user})

    def getRecipieByID(self, ID):
        return self.client.Cookbook.recipies.find_one({'_id': ID})
