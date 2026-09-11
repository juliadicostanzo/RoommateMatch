import unittest
from roommate_match.src.system import RoommateSystem
from roommate_match.src.roommateRequest import roommateRequest
from roommate_match.src.pairing import pairing

class TestRoommateSystem(unittest.TestCase):

    def setUp(self):
        self.system = RoommateSystem()

    def test_add_student(self):
        self.system.addStudent("Julia", "j@gmail.com", "123", "Ithaca")
        self.assertEqual(len(self.system.students), 1)

    def test_remove_student(self):
        self.system.addStudent("Julia", "j@test.com", "123", "NY")
        student = self.system.getStudentByName("Julia")
        studentID = student[0].id
        self.system.removeStudent(student[0].id)
        self.assertEqual(len(self.system.students), 0)
        self.assertEqual(self.system.removeStudent(705000000), "There is no student with id: 705000000")
        self.assertEqual(self.system.removeStudent(studentID), "There is no student with id: " + str(studentID))
        

    def test_get_student_by_name(self):
        self.system.addStudent("Julia", "j@test.com", "123", "NY")
        self.system.addStudent("Julia", "julia@test.com", "123", "CA")
        self.system.addStudent("Bob", "Bob@test.com", "123", "CA")
        student = self.system.getStudentByName("Julia")
        student = self.system.getStudentByName("Bob")
        self.assertEqual(len(student), 1)
        student = self.system.getStudentByName("Julia D")
        self.assertEqual(len(student), 0)

    def test_get_student_by_id(self):
        self.system.addStudent("Julia", "j@test.com", "123", "NY")
        student1 = self.system.students[0]
        foundById1 = self.system.getStudentById(student1.id)
        self.assertEqual(foundById1, student1)
        self.assertEqual(self.system.getStudentById(705000000), None)

    def test_update_request_list_accepted(self):
        self.system.addStudent("Julia", "j@test.com", "123", "NY")
        self.system.addStudent("April", "April@test.com", "123", "CA")
        self.system.addStudent("Bob", "Bob@test.com", "123", "CA")

        student1 = self.system.getStudentByName("Julia")
        stu1 = student1[0]
        student2 = self.system.getStudentByName("April")
        stu2ID = student2[0].id
        student3 = self.system.getStudentByName("Bob")
        stu3ID = student3[0].id

        stu1.sendRequest(stu2ID, stu3ID)
        self.system.requests[0].accept_request(stu2ID) #all receivers accept
        self.system.requests[0].accept_request(stu3ID)
        self.system.requests[0].updateStatus()  #sets accepted = True
        
        self.assertEqual(len(self.system.requests), 1)
        self.system.updateRequestList()
        self.assertEqual(len(self.system.requests), 0)

        self.assertEqual(len(self.system.pairings), 1)
        self.system.finalize_pairing()
        self.assertEqual(len(self.system.pairings), 0)

        self.assertEqual(stu1.groupID, student2[0].groupID)
        self.assertEqual(stu1.groupID, student3[0].groupID)
        self.assertEqual(student3[0].groupID, student2[0].groupID)

    def test_update_request_list_rejected(self):
        self.system.addStudent("Julia", "j@test.com", "123", "NY")
        self.system.addStudent("April", "April@test.com", "123", "CA")
        self.system.addStudent("Bob", "Bob@test.com", "123", "CA")

        student1 = self.system.getStudentByName("Julia")
        stu1 = student1[0]
        student2 = self.system.getStudentByName("April")
        stu2ID = student2[0].id
        student3 = self.system.getStudentByName("Bob")
        stu3ID = student3[0].id

        stu1.sendRequest(stu2ID, stu3ID)
        self.system.requests[0].reject_request(stu2ID) #reject
        self.system.requests[0].reject_request(stu3ID) #reject
        self.system.requests[0].updateStatus()

        self.assertEqual(len(self.system.requests), 1)
        self.system.updateRequestList()
        self.assertEqual(len(self.system.requests), 0)

        self.assertEqual(len(self.system.pairings), 0)
        self.assertEqual(stu1.groupID, -1)
        self.assertEqual(student2[0].groupID, -1)
        self.assertEqual(student2[0].groupID, -1)
        
    def test_one_rejected_request(self):
        self.system.addStudent("Julia", "j@test.com", "123", "NY")
        self.system.addStudent("April", "April@test.com", "123", "CA")
        self.system.addStudent("Bob", "Bob@test.com", "123", "CA")

        student1 = self.system.getStudentByName("Julia")
        stu1 = student1[0]
        student2 = self.system.getStudentByName("April")
        stu2ID = student2[0].id
        student3 = self.system.getStudentByName("Bob")
        stu3ID = student3[0].id

        stu1.sendRequest(stu2ID, stu3ID)
        self.system.requests[0].accept_request(stu2ID) #accept
        self.system.requests[0].reject_request(stu3ID) #reject
        self.system.requests[0].updateStatus()

        self.assertEqual(len(self.system.requests), 1)
        self.system.updateRequestList()
        self.assertEqual(len(self.system.requests), 0)

        self.assertEqual(len(self.system.pairings), 0)
        self.assertEqual(stu1.groupID, -1)
        self.assertEqual(student2[0].groupID, -1)
        self.assertEqual(student2[0].groupID, -1)
        

    def test_finalize_pairing(self):
        self.system.addStudent("Julia", "j@gmail.com", "123", "Ithaca") #adds students
        self.system.addStudent("Bob", "bob@gmail.com", "123", "Liverpool")
        self.system.addStudent("April", "april@gmail.com", "123", "Liverpool")
        self.system.addStudent("Dylan", "dylan@gmail.com", "123", "Liverpool")
        student1 = self.system.students[0] 
        student2 = self.system.students[1]
        student3 = self.system.students[2]
        student4 = self.system.students[3]
        self.assertEqual(student1.groupID, -1) #check they are both not assigned to a group
        self.assertEqual(student2.groupID, -1)
        self.system.pairings.append(pairing(1, [student1.id, student2.id])) #create a pairing
        self.assertEqual(len(self.system.pairings), 1) #check pairing was created
        self.system.finalize_pairing()
        self.assertEqual(len(self.system.pairings), 0) #check pairing was removed
        self.assertEqual(student1.groupID, 1) #check students are in the right group
        self.assertEqual(student2.groupID, 1)

        self.assertNotEqual(student3.groupID, 1)
        self.assertNotEqual(student4.groupID, 1)
        self.assertNotEqual(student1.groupID, student3.groupID)

    def test_view_students(self):
        self.system.addStudent("Julia", "j@gmail.com", "123", "Ithaca") #adds students
        self.system.addStudent("Bob", "bob@gmail.com", "123", "Liverpool")
        self.system.addStudent("April", "april@gmail.com", "123", "Liverpool")
        self.system.addStudent("Dylan", "dylan@gmail.com", "123", "Liverpool")
        self.assertEqual(len(self.system.viewStudents()), 4) #check view students returns all students
        self.system.addStudent("Ben", "ben@gmail.com", "123", "Ithaca")
        self.assertEqual(len(self.system.viewStudents()), 5)
        student1ID = self.system.students[0].id
        self.system.removeStudent(student1ID)
        self.assertEqual(len(self.system.viewStudents()), 4)
        
        

if __name__ == "__main__":
    unittest.main()


    