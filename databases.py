from pymongo import MongoClient
import uuid
import json
import random
import config
from datetime import datetime

class Database:
    def __init__(self):
        self.db = MongoClient(config.MONGO_URI).Cookbook
        self.users = self.db.users
        self.recipes = self.db.recipes

    def addUser(self, email):
        user = {
            "_id": str(uuid.uuid4()),
            "email": email,
            "username": email.split('@')[0],
            "recipes": [],
            "favorites": [],
            "liked": [],
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.users.insert_one(user)
    
    def getUser(self, id):
        return self.users.find_one({'_id': id})
    
    def getUserWithMail(self, email):
        return self.users.find_one({'email': email})
    
    def userExists(self, email):
        return self.users.find_one({'email': email}) != None

    def getRecipesOfUser(self, user):
        return self.recipes.find({'by': user})

    def getRecipeByID(self, ID):
        return self.recipes.find_one({'_id': ID})
    
    def getRandomRecipes(self, number):
        return self.recipes.aggregate([{'$sample': {'size': number}}])
    
    def addRecipe(self, recipe):
        self.recipes.insert_one(recipe)
        self.users.update_one({'_id': recipe['by']}, {'$push': {'recipes': recipe['_id']}})
    
    def deleteRecipe(self, ID):
        recipe = self.getRecipeByID(ID)
        self.recipes.delete_one({'_id': ID})
        self.users.update_one({'_id': recipe['by']}, {'$pull': {'recipes': ID}})
        for like in recipe['likes']:
            self.users.update_one({'_id': like}, {'$pull': {'liked': ID}})
        for favorite in recipe['favorite']:
            self.users.update_one({'_id': favorite}, {'$pull': {'favorites': ID}})
    
    def likeRecipe(self, user, recipe):
        recipe = self.getRecipeByID(recipe)
        if user in recipe['likes']:
            return False
        self.users.update_one({'_id': user}, {'$push': {'liked': recipe['_id']}})
        self.recipes.update_one({'_id': recipe['_id']}, {'$push': {'likes': user}})
        return True
    
    def unlikeRecipe(self, user, recipe):
        recipe = self.getRecipeByID(recipe)
        if user not in recipe['likes']:
            return False
        self.users.update_one({'_id': user}, {'$pull': {'liked': recipe['_id']}})
        self.recipes.update_one({'_id': recipe['_id']}, {'$pull': {'likes': user}})
        return True
    
    def addFavorite(self, user, recipe):
        recipe = self.getRecipeByID(recipe)
        if user in recipe['favorite']:
            return False
        self.users.update_one({'_id': user}, {'$push': {'favorites': recipe['_id']}})
        self.recipes.update_one({'_id': recipe['_id']}, {'$push': {'favorite': user}})
        return True
    
    def removeFavorite(self, user, recipe):
        recipe = self.getRecipeByID(recipe)
        if user not in recipe['favorite']:
            return False
        self.users.update_one({'_id': user}, {'$pull': {'favorites': recipe['_id']}})
        self.recipes.update_one({'_id': recipe['_id']}, {'$pull': {'favorite': user}})
        return True
    
    def getFavorites(self, user):
        return self.users.find_one({'_id': user})['favorites']
    
    def getLiked(self, user):
        return self.users.find_one({'_id': user})['liked']
    
    def getUserRecipes(self, user):
        return self.users.find_one({'_id': user})['recipes']
    
    def getUserLikes(self, user):
        return self.users.find_one({'_id': user})['likes']