import unittest
from roommate_match.src.pairing import pairing
from roommate_match.src.system import RoommateSystem
from roommate_match.src.Student import Student

class TestPairing(unittest.TestCase):
    def setUp(self):
        self.mock_system = RoommateSystem()
        self.mock_system.students = [
            Student(205, "Alice", "alice@test.com", "123", "Montreal"),
            Student(305, "Ben", "ben@test.com", "123", "Detroit"),
            Student(405, "Cara", "cara@test.com", "123", "Dallas"),
            Student(505, "Dan", "dan@test.com", "123", "Syracuse"),
            Student(605, "Emma", "emma@test.com", "123", "Stamford"),
            Student(705, "Frank", "frank@test.com", "123", "Los Angeles"),
            Student(805, "Dennis", "dennis@test.com", "123", "Chicago"),
        ]

        RoommateSystem.students = self.mock_system.students

        self.pair1 = pairing(1, [205, 305])
        self.pair2 = pairing(2, [405, 505, 605])
        self.pair3 = pairing(3, [705, 805])

    def test_get_group_id(self):
        self.assertEqual(self.pair1.get_group_id(), 1)
        self.assertEqual(self.pair2.get_group_id(), 2)
        self.assertEqual(self.pair3.get_group_id(), 3)

    def test_get_students(self):
        self.assertEqual(self.pair1.get_students(), [205, 305])
        self.assertEqual(self.pair2.get_students(), [405, 505, 605])
        self.assertEqual(self.pair3.get_students(), [705, 805])


if __name__ == "__main__":
    unittest.main()