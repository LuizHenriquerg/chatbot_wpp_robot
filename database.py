from importlib.resources import path
import pymongo
import json
import os

class Database:

    def __init__(self):
        config = json.loads(open('config.json', 'r').read())

        self.client = pymongo.MongoClient(config['connection'])
        
        self.db = self.client.get_database(config['db_name'])

    def insert(self, col_name, object):
        coll = self.db.get_collection(col_name)

        coll.insert_one(object)
    
    def update(self, col_name, object, query):
        coll = self.db.get_collection(col_name)

        coll.update_one(query, {'$set': object}, upsert=True)
    
    def delete(self, col_name, query):
        coll = self.db.get_collection(col_name)

        coll.delete_one(query)
    
    def select_col(self, col_name, query={}):
        coll = self.db.get_collection(col_name)
        
        return coll.find(query)
