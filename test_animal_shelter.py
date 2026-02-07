"""
test_animal_shelter.py

Author: Beau Zermeno
Date: February 6, 2026

Description:
    Unit test suite for the enhanced MongoDB CRUD and analytics module
    (CRUD_Python_Module.py). These tests validate the correctness,
    reliability, and robustness of Create, Read, Update, and Delete
    operations, as well as performance and data analysis enhancements.

Testing Scope:
    - CRUD operation success paths and error handling
    - Automatic record number assignment
    - MongoDB index creation for performance optimization
    - Aggregation pipeline methods for trend analysis
      (breed, age, and intake condition)

Testing Strategy:
    - Uses Python's built-in unittest framework
    - MongoDB interactions are mocked using unittest.mock to ensure
      tests run without a live database connection
    - Focuses on application logic rather than database internals

Dependencies:
    - unittest
    - unittest.mock

Usage:
    Run the test suite from the command line:
        python -m unittest test_animal_shelter.py
"""


import unittest
from unittest.mock import MagicMock, patch
from CRUD_Python_Module_Enhancement import AnimalShelter


class TestAnimalShelter(unittest.TestCase):

    @patch("CRUD_Python_Module.MongoClient")
    def setUp(self, mock_client):
        """
        Set up a mocked MongoDB connection for each test.
        """
        self.mock_collection = MagicMock()
        self.mock_db = {"animals": self.mock_collection}
        mock_client.return_value.__getitem__.return_value = self.mock_db

        self.shelter = AnimalShelter("user", "password")
        self.shelter.collection = self.mock_collection

    # ---------- CREATE ----------

    def test_create_success(self):
        self.mock_collection.insert_one.return_value.acknowledged = True
        self.shelter.get_next_record_number = MagicMock(return_value=1)

        result = self.shelter.create({"name": "Buddy"})
        self.assertTrue(result)

    def test_create_empty_data_raises_error(self):
        with self.assertRaises(ValueError):
            self.shelter.create({})

    # ---------- READ ----------

    def test_read_returns_documents(self):
        self.mock_collection.find.return_value = [{"name": "Buddy"}]

        results = self.shelter.read({"animal_type": "Dog"})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Buddy")

    # ---------- UPDATE ----------

    def test_update_returns_modified_count(self):
        self.mock_collection.update_many.return_value.modified_count = 2

        count = self.shelter.update({"animal_type": "Dog"}, {"age": 5})
        self.assertEqual(count, 2)

    def test_update_missing_arguments_raises_error(self):
        with self.assertRaises(ValueError):
            self.shelter.update({}, {"age": 5})

    # ---------- DELETE ----------

    def test_delete_returns_deleted_count(self):
        self.mock_collection.delete_many.return_value.deleted_count = 3

        count = self.shelter.delete({"animal_type": "Cat"})
        self.assertEqual(count, 3)

    def test_delete_missing_query_raises_error(self):
        with self.assertRaises(ValueError):
            self.shelter.delete({})

    # ---------- INDEX CREATION ----------

    def test_indexes_created(self):
        self.shelter._create_indexes()
        self.assertTrue(self.mock_collection.create_index.called)

    # ---------- AGGREGATION PIPELINES ----------

    def test_adoption_trends_by_breed(self):
        self.mock_collection.aggregate.return_value = [
            {"_id": "Labrador", "count": 5}
        ]

        results = self.shelter.adoption_trends_by_breed("Dog")
        self.assertEqual(results[0]["_id"], "Labrador")
        self.assertEqual(results[0]["count"], 5)

    def test_adoption_trends_by_age(self):
        self.mock_collection.aggregate.return_value = [
            {"_id": 2, "count": 4}
        ]

        results = self.shelter.adoption_trends_by_age("Cat")
        self.assertEqual(results[0]["_id"], 2)

    def test_intake_condition_analysis(self):
        self.mock_collection.aggregate.return_value = [
            {"_id": "Healthy", "count": 10}
        ]

        results = self.shelter.intake_condition_analysis()
        self.assertEqual(results[0]["_id"], "Healthy")


if __name__ == "__main__":
    unittest.main()
