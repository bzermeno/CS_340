"""
CRUD_Python_Module_Enhancement.py

Author: Beau Zermeno
Date: February 6, 2026

Description:
    Enhanced MongoDB CRUD operations module for the Animal Shelter database.
    This module provides Create, Read, Update, and Delete functionality for
    the animals collection in the AAC (Animal Adoption Center) database.

Enhancements Implemented:
    - Performance Optimization:
        * Compound indexes on frequently queried fields to improve query
          efficiency and reduce collection scan time.
    - Data Analysis and Aggregation:
        * MongoDB aggregation pipelines using $match, $group, and $sort
          to support basic data mining and trend analysis.
        * Analytical methods to identify adoption patterns by breed, age,
          and intake condition.
    - Scalability Improvements:
        * Database-side analytics to support larger datasets and more
          complex queries without increasing application overhead.

Technologies Used:
    - MongoDB
    - PyMongo
    - BSON

Usage:
    from CRUD_Python_Module import AnimalShelter

    shelter = AnimalShelter(user='username', pwd='password')

    # CRUD Operations
    shelter.create({...})
    shelter.read({...})
    shelter.update({...}, {...})
    shelter.delete({...})

    # Analytics
    shelter.adoption_trends_by_breed("Dog")
    shelter.adoption_trends_by_age("Cat")
    shelter.intake_condition_analysis()
"""


from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError


class AnimalShelter(object):
    """CRUD and analytics operations for Animal collection in MongoDB"""

    def __init__(self, user, pwd):
        self.USER = user
        self.PASS = pwd
        HOST = 'localhost'
        PORT = 27017
        DB = 'aac'
        COL = 'animals'

        self.client = MongoClient(
            f'mongodb://{self.USER}:{self.PASS}@{HOST}:{PORT}/?authSource={DB}'
        )
        self.database = self.client[DB]
        self.collection = self.database[COL]

        # Initialize indexes for performance
        self._create_indexes()

    # ---------- PERFORMANCE ENHANCEMENTS ----------

    def _create_indexes(self):
        """
        Creates compound indexes to improve query performance.
        Safe to call multiple times.
        """
        try:
            self.collection.create_index(
                [
                    ("animal_type", ASCENDING),
                    ("breed", ASCENDING),
                    ("age", ASCENDING)
                ],
                name="animal_breed_age_idx"
            )

            self.collection.create_index(
                [
                    ("intake_condition", ASCENDING),
                    ("animal_type", ASCENDING)
                ],
                name="intake_condition_idx"
            )

        except PyMongoError as e:
            print(f"Index creation failed: {e}")

    # ---------- CRUD OPERATIONS ----------

    def get_next_record_number(self):
        last_record = self.collection.find_one(
            sort=[("rec_num", -1)]
        )
        return last_record["rec_num"] + 1 if last_record else 1

    def create(self, data):
        if not data:
            raise ValueError("Nothing to save; 'data' parameter is empty")

        if "rec_num" not in data:
            data["rec_num"] = self.get_next_record_number()

        try:
            return self.collection.insert_one(data).acknowledged
        except PyMongoError as e:
            print(f"Insert failed: {e}")
            return False

    def read(self, query=None):
        try:
            return list(self.collection.find(query or {}))
        except PyMongoError as e:
            print(f"Query failed: {e}")
            return []

    def update(self, query, values):
        if not query or not values:
            raise ValueError("Both query and values must be provided")

        try:
            result = self.collection.update_many(query, {"$set": values})
            return result.modified_count
        except PyMongoError as e:
            print(f"Update failed: {e}")
            return 0

    def delete(self, query):
        if not query:
            raise ValueError("Query must be provided")

        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except PyMongoError as e:
            print(f"Delete failed: {e}")
            return 0

    # ---------- DATA ANALYTICS (AGGREGATION PIPELINES) ----------

    def adoption_trends_by_breed(self, animal_type):
        """
        Returns adoption counts grouped by breed.
        """
        pipeline = [
            {"$match": {"animal_type": animal_type}},
            {"$group": {"_id": "$breed", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]

        try:
            return list(self.collection.aggregate(pipeline))
        except PyMongoError as e:
            print(f"Aggregation failed: {e}")
            return []

    def adoption_trends_by_age(self, animal_type):
        """
        Groups animals by age and returns frequency counts.
        """
        pipeline = [
            {"$match": {"animal_type": animal_type}},
            {"$group": {"_id": "$age", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]

        try:
            return list(self.collection.aggregate(pipeline))
        except PyMongoError as e:
            print(f"Aggregation failed: {e}")
            return []

    def intake_condition_analysis(self):
        """
        Analyzes intake conditions across all animals.
        """
        pipeline = [
            {"$group": {"_id": "$intake_condition", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]

        try:
            return list(self.collection.aggregate(pipeline))
        except PyMongoError as e:
            print(f"Aggregation failed: {e}")
            return []
