# Example Python Code to Insert a Document 

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId 

class AnimalShelter(object): 
    """ CRUD operations for Animal collection in MongoDB """ 

    def __init__(self, user, pwd): 
        # Initializing the MongoClient. This helps to access the MongoDB 
        # databases and collections. This is hard-wired to use the aac 
        # database, the animals collection, and the aac user. 
        # 
        # You must edit the password below for your environment. 
        # 
        # Connection Variables 
        # 
        self.USER = user 
        self.PASS = pwd 
        HOST = 'localhost' 
        PORT = 27017 
        DB = 'aac' 
        COL = 'animals' 
        # 
        # Initialize Connection 
        # 
        self.client = MongoClient(f'mongodb://{self.USER}:{self.PASS}@{HOST}:{PORT}/?authSource={DB}') 
        self.database = self.client['%s' % (DB)] 
        self.collection = self.database['%s' % (COL)] 

        
    def get_next_record_number(self):
        """
        Returns the next available record number for a new document.
        Assumes documents have a "rec_num" field.
        """
        last_record = self.database.animals.find_one(
            sort=[("rec_num", -1)]
        )  # Find doc with highest rec_num

        if last_record and "rec_num" in last_record:
            return last_record["rec_num"] + 1
        else:
            return 1  # start from 1 if no docs exist

    
    def create(self, data):
        """
        Inserts a new document into the animals collection.
        Automatically assigns the next available record number if not provided.
        """
        if not data:
            raise ValueError("Nothing to save; 'data' parameter is empty")

        # assign record number if missing
        if "rec_num" not in data:
            data["rec_num"] = self.get_next_record_number()

        try:
            result = self.collection.insert_one(data)
            return result.acknowledged  # True if insert succeeded
        except PyMongoError as e:
            print(f"Insert failed: {e}")
            return False
 

    def read(self, query=None):
        """
        Reads documents from the animals collection.
        If query is None, returns all documents.
        """
        try:
            return list(self.collection.find(query))  # filtered docs
        except PyMongoError as e:
            print(f"Query failed: {e}")
            return []
        
    def update(self, query, values):
        """
        Update one or more documents in the animals collection.
        Returns the number of documents updated.
        """
        if not query or not values:
            raise ValueError("Both query and new_values must be provided")

        try:
            result = self.collection.update_many(query, {"$set": values})
            return result.modified_count  # number of documents updated
        except PyMongoError as e:
            print(f"Update failed: {e}")
            return 0

    def delete(self, query):
        """
        Delete one or more documents from the animals collection.
        Returns the number of documents deleted.
        """
        if not query:
            raise ValueError("Query must be provided for delete operation")

        try:
            result = self.collection.delete_many(query)
            return result.deleted_count  # number of documents deleted
        except PyMongoError as e:
            print(f"Delete failed: {e}")
            return 0
