import unittest
from roommate_match.src.system import RoommateSystem
from roommate_match.src.admin import Admin

class TestAdmin(unittest.TestCase):
    
    def setUp(self):
        self.system = RoommateSystem()
        self.admin = Admin(1,"Admin1", "Admin1@gmail.com", "123", self.system)
        
    def test_add_student(self):
        self.admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        self.assertEqual(len(self.system.students), 1)

    def test_remove_student(self):
        self.admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        self.assertEqual(len(self.system.students), 1)
        students = self.admin.getStudentByName("Julia")
        self.admin.removeStudent(students[0].id)
        self.assertEqual(len(self.system.students), 0)

    def test_view_all_students(self):
        self.admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        self.admin.addStudent("Julia", "ju@gmail.com", "123", "Ithaca")
        self.admin.addStudent("Bob", "bob@gmail.com", "123", "Liverpool")

        students = self.admin.viewAllStudents()
        self.assertEqual(len(students), 3)

    def test_get_student_by_name(self):
        self.assertEqual(len(self.admin.getStudentByName("J")),0)
        self.admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        self.admin.addStudent("Bob", "j@gmail.com", "123", "Ithaca")
        self.assertEqual(len(self.admin.getStudentByName("Julia")),1)
        self.admin.addStudent("Bob", "bob@gmail.com", "123", "Liverpool")
        self.assertEqual(len(self.admin.getStudentByName("Bob")),2)


    def test_get_student_by_id(self):
        self.admin.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        student = self.system.students[0]  # grab from system
        studentFound = self.admin.getStudentById(student.id)
        self.assertEqual(studentFound, student)

    def test_add_preference_option(self):
        self.admin.addPreferenceOption("Clean")
        self.assertIn("Clean", self.system.preference_options)

    def test_interest_options(self):
        self.admin.addInterestOption("Sports")
        self.assertIn("Sports", self.system.interest_options)
        

if __name__ == "__main__":
    unittest.main()