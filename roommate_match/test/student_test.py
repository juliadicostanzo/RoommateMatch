import unittest
from unittest.mock import patch, MagicMock
from roommate_match.src.Student import Student
from roommate_match.src.system import RoommateSystem

class StudentTest(unittest.TestCase):
    student1 = Student(123, "John Doe", "john.doe@example.com", "password123", "New York")
    student2 = Student(234, "Jane Smith", "jane.smith@example.com", "password456", "Los Angeles")

    def test_sendRequest(self):
        system = RoommateSystem()

        s1 = Student(1, "A", "a@x.com", "pw", "Town")
        s2 = Student(2, "B", "b@x.com", "pw", "Town")
        s3 = Student(3, "C", "c@x.com", "pw", "Town")

        system.students = [s1, s2, s3]

        s1.system = system
        s1.sendRequest(2, 3)

        self.assertEqual(len(system.requests), 1)

        req = system.requests[0]

        # All responses start as None
        for rid in req.receiver_ids:
            self.assertIsNone(req.responses[rid])

        # Sender cannot send a second request
        with self.assertRaises(Exception):
            s1.sendRequest([2], system)

    def test_respondRequest(self):
        system = RoommateSystem()

        s1 = Student(1, "A", "a@x.com", "pw", "Town")
        s2 = Student(2, "B", "b@x.com", "pw", "Town")
        s3 = Student(3, "C", "c@x.com", "pw", "Town")

        system.students = [s1, s2, s3]

        s1.system = system
        s1.sendRequest(2, 3)
        req = system.requests[0]

        # s2 accepts
        s2.respondRequest(req.request_id, True, system)
        self.assertEqual(req.responses[2], True)

        # s3 rejects, entire request should be cancelled
        s3.respondRequest(req.request_id, False, system)

        # Request list should now be empty
        self.assertEqual(len(system.requests), 0)


        # Testing all accept
        s1.sendRequest(2, 3)
        req = system.requests[0]

        s2.respondRequest(req.request_id, True, system)
        s3.respondRequest(req.request_id, True, system)

        # Request should be removed and moved to pairings
        self.assertEqual(len(system.requests), 0)
        self.assertEqual(len(system.pairings), 1)

    
    def test_updatePassword(self):
        self.student1.updatePassword("newpassword123")
        self.assertEqual(self.student1.password, "newpassword123")

        self.student2.updatePassword("newpassword456")
        self.assertEqual(self.student2.password, "newpassword456")

        with self.assertRaises(ValueError):
            self.student1.updatePassword("")

        with self.assertRaises(ValueError):
            self.student2.updatePassword("")

    def test_updateName(self):
        self.student1.updateName("John Doe")
        self.assertEqual(self.student1.name, "John Doe")

        self.student2.updateName("Juliet Smith")
        self.assertEqual(self.student2.name, "Juliet Smith")

        with self.assertRaises(ValueError):
            self.student1.updateName("")

        with self.assertRaises(ValueError):
            self.student2.updateName("")

    def test_updateHometown(self):
        self.student1.updateHometown("Chicago")
        self.assertEqual(self.student1.hometown, "Chicago")

        self.student2.updateHometown("Nashville")
        self.assertEqual(self.student2.hometown, "Nashville")


        self.student1.updateHometown("")
        self.assertEqual(self.student1.hometown, "")

        self.student2.updateHometown("")
        self.assertEqual(self.student2.hometown, "")
    

    @patch("sqlite3.connect")
    @patch("builtins.input")
    def test_updateInterests(self, mock_input, mock_connect):

        mock_input.side_effect = [
            "1", "add",
            "1", "add",
            "999",
            "2", "remove",
            "q"
        ]

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "Music"), (2, "Sports")]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        s = Student(1, "Alex", "a@b.com", "pw", "NY")
        s.interests = ["Sports"]

        s.updateInterests("fake.db")

        self.assertIn("Music", s.interests)
        self.assertEqual(s.interests.count("Music"), 1)

        self.assertNotIn("Sports", s.interests)

        mock_cursor.execute.assert_any_call(
            "INSERT INTO students_to_interest (student_id, interest_id) VALUES (?, ?)",
            (1, 1)
        )

        mock_cursor.execute.assert_any_call(
            "DELETE FROM students_to_interest WHERE student_id = ? AND interest_id = ?",
            (1, 2)
        )



    @patch("sqlite3.connect")
    @patch("builtins.input")
    def test_updatePreferences(self, mock_input, mock_connect):

        mock_input.side_effect = [
            "1", "add",
            "1", "add",
            "999",
            "2", "remove",
            "q"
        ]

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, "Cleanliness"), (2, "Quiet Hours")]
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        s = Student(1, "Alex", "a@b.com", "pw", "NY")
        s.preferences = ["Quiet Hours"]

        s.updatePreferences("fake.db")

        self.assertIn("Cleanliness", s.preferences)
        self.assertEqual(s.preferences.count("Cleanliness"), 1)

        self.assertNotIn("Quiet Hours", s.preferences)

        mock_cursor.execute.assert_any_call(
            "INSERT INTO students_to_preference (student_id, preference_id) VALUES (?, ?)",
            (1, 1)
        )

        mock_cursor.execute.assert_any_call(
            "DELETE FROM students_to_preference WHERE student_id = ? AND preference_id = ?",
            (1, 2)
        )


    def test_viewStudents(self):
        system = RoommateSystem()
        system.addStudent("Alice", "alice@test.com", "123", "NY")
        system.addStudent("Bob", "bob@test.com", "123", "CA")
        system.addStudent("Charlie", "charlie@test.com", "123", "TX")

        students = system.viewStudents()

        # Ensures all 3 students are in list
        self.assertEqual(len(students), 3)
        for s in students:
            self.assertIsInstance(s, Student)

        # Checks each student in list to ensure they are correct
        names = [s.name for s in students]
        self.assertIn("Alice", names)
        self.assertIn("Bob", names)
        self.assertIn("Charlie", names)

    def test_searchStudents(self):
        system = RoommateSystem()
        s1 = system.addStudent("Alice", "alice@test.com", "123", "NY")
        s2 = system.addStudent("Bob", "bob@test.com", "123", "CA")

        # Checks result is Bob
        result = self.student1.searchStudents(str(s2.id), system)
        self.assertEqual(result.name, "Bob")

        # If ID is out of bounds
        with self.assertRaises(ValueError):
            self.student1.searchStudents("999", system)

        # If search field is not student ID
        with self.assertRaises(ValueError):
            self.student1.searchStudents("Alice", system)


    def test_rankStudentsByMatch(self):
        s1 = Student(1, "A", "a@a.com", "pw", "NY")
        s2 = Student(2, "B", "b@b.com", "pw", "NY")
        s3 = Student(3, "C", "c@c.com", "pw", "NY")
        s4 = Student(4, "D", "d@d.com", "pw", "NY")

        s1.interests = ["Music", "Sports", "Travel"]
        s1.preferences = ["Cleanliness", "Warm Room"]

        s2.interests = ["Music", "Travel"]
        s2.preferences = ["Cleanliness"]

        s3.interests = ["Sports"]
        s3.preferences = ["Warm Room"]

        s4.interests = ["Movies"]
        s4.preferences = ["Cool Room"]

        ranked = s1.rankStudentsByMatch([s1, s2, s3, s4])

        self.assertEqual(ranked[0].id, 2)
        self.assertEqual(ranked[1].id, 3)
        self.assertEqual(ranked[2].id, 4)


if __name__ == '__main__':
    unittest.main()