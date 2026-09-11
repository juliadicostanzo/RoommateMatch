import sqlite3
import unittest

from roommate_match.src.Student import Student
from roommate_match.src.databaseHelper import bootstrap_database_and_system, create_system_from_database
from roommate_match.src.system import RoommateSystem


class TestDatabaseHelperClassRecreation(unittest.TestCase):

	def setUp(self):
		self.connection = sqlite3.connect(":memory:")
		self._create_schema()
		self._seed_data()

	def tearDown(self):
		self.connection.close()

	def _create_schema(self):
		self.connection.execute(
			"""
			CREATE TABLE students (
				id INTEGER PRIMARY KEY,
				name TEXT,
				email TEXT,
				password TEXT,
				hometown TEXT
			)
			"""
		)
		self.connection.execute(
			"""
			CREATE TABLE students_to_groups (
				student_id INTEGER,
				group_id INTEGER
			)
			"""
		)
		self.connection.execute(
			"""
			CREATE TABLE interests (
				id INTEGER PRIMARY KEY,
				title TEXT
			)
			"""
		)
		self.connection.execute(
			"""
			CREATE TABLE students_to_interests (
				student_id INTEGER,
				interest_id INTEGER
			)
			"""
		)
		self.connection.execute(
			"""
			CREATE TABLE preference_options (
				preference TEXT
			)
			"""
		)
		self.connection.execute(
			"""
			CREATE TABLE student_preferences (
				student_id INTEGER,
				preference TEXT
			)
			"""
		)

	def _seed_data(self):
		self.connection.executemany(
			"INSERT INTO students (id, name, email, password, hometown) VALUES (?, ?, ?, ?, ?)",
			[
				(1001, "Alice", "alice@test.com", "alicepass", "Ithaca"),
				(1002, "Bob", "bob@test.com", "bobpass", "Buffalo"),
			],
		)
		self.connection.executemany(
			"INSERT INTO students_to_groups (student_id, group_id) VALUES (?, ?)",
			[(1001, 44), (1002, 44)],
		)
		self.connection.executemany(
			"INSERT INTO interests (id, title) VALUES (?, ?)",
			[(1, "Cooking"), (2, "Gaming")],
		)
		self.connection.executemany(
			"INSERT INTO students_to_interests (student_id, interest_id) VALUES (?, ?)",
			[(1001, 1), (1001, 2), (1002, 2)],
		)
		self.connection.executemany(
			"INSERT INTO preference_options (preference) VALUES (?)",
			[("Clean",), ("Quiet",)],
		)
		self.connection.executemany(
			"INSERT INTO student_preferences (student_id, preference) VALUES (?, ?)",
			[(1001, "Clean"), (1002, "Quiet")],
		)
		self.connection.commit()

	def test_create_system_from_database_recreates_classes(self):
		system = create_system_from_database(self.connection)

		self.assertIsInstance(system, RoommateSystem)
		self.assertEqual(len(system.students), 2)

		alice = system.getStudentById(1001)
		bob = system.getStudentById(1002)

		self.assertIsInstance(alice, Student)
		self.assertIsInstance(bob, Student)
		self.assertEqual(alice.name, "Alice")
		self.assertEqual(bob.name, "Bob")
		self.assertEqual(alice.groupID, 44)
		self.assertEqual(bob.groupID, 44)
		self.assertEqual(alice.interests, ["Cooking", "Gaming"])
		self.assertEqual(bob.interests, ["Gaming"])
		self.assertEqual(alice.preferences, ["Clean"])
		self.assertEqual(bob.preferences, ["Quiet"])
		self.assertEqual(system.interest_options, ["Cooking", "Gaming"])
		self.assertEqual(system.preference_options, ["Clean", "Quiet"])

	def test_bootstrap_returns_connection_and_system(self):
		connection, system = bootstrap_database_and_system(":memory:")
		try:
			self.assertIsInstance(connection, sqlite3.Connection)
			self.assertIsInstance(system, RoommateSystem)
		finally:
			connection.close()


if __name__ == "__main__":
	unittest.main()
