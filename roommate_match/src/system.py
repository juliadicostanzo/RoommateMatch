from random import randint
from .Student import Student
from .roommateRequest import roommateRequest
from .pairing import pairing

class RoommateSystem:
    def __init__(self):
        self.students = []
        self.admins = []
        self.preference_options = []
        self.interest_options = []
        self.pairings = []
        self.approved_groups = []
        self.requests = []
        self.next_group_id = 1

    def generateId(self):
        newId = int("705" + str(randint(100000, 999999)))
        existing_ids = [s.id for s in self.students]

        while newId in existing_ids:
            newId = int("705" + str(randint(100000, 999999)))

        return newId

    def addStudent(self, name, email, password, hometown):
        student_id = self.generateId()
        student = Student(student_id, name, email, password, hometown)
        student.system = self
        self.students.append(student)
        return student

    def removeStudent(self, id):
        for student in self.students:
            if student.id == id:
                self.students.remove(student)
                return f"Student: {student} was successfully removed"
        return f"There is no student with id: {id}"

    def getStudentByName(self, name):
        studentList = []
        for student in self.students:
            if student.name == name:
                studentList.append(student)
        return studentList

    def getStudentById(self, id):
        for student in self.students:
            if student.id == id:
                return student
        return None
    
    def viewStudents(self):
        return self.students
    
    def generateGroupId(self):
        newGroupId = randint(1,50)
        existing_ids = [s.groupID for s in self.students]
        while newGroupId in existing_ids:
            newGroupId = randint(1,50)
        
        return newGroupId

    def updateRequestList(self, _request=None):
        for request in list(self.requests):
            if request.isAccepted() is True:
                senderID = request.getSenderId()
                group = [senderID]
                group.extend(request.getReceiverIds())

                new_pairing = pairing(self.generateGroupId(), group)
                self.pairings.append(new_pairing)
                self.requests.remove(request)
            elif request.isAccepted() is False:
                self.requests.remove(request)

    def finalize_pairing(self, approve: bool = True):
        processed_pairings = list(self.pairings)
        if not processed_pairings:
            return []

        if approve:
            for current_pairing in processed_pairings:
                if isinstance(current_pairing, dict):
                    group_members = [int(student_id) for student_id in current_pairing.get("members", [])]
                    group_id = int(current_pairing.get("group_id", -1))
                else:
                    group_members = [int(student_id) for student_id in getattr(current_pairing, "students", [])]
                    group_id = int(getattr(current_pairing, "group_id", -1))

                if group_id < 0:
                    continue

                for student in self.students:
                    if int(student.id) in group_members:
                        student.groupID = group_id
                self.approved_groups.append(current_pairing)

        self.pairings = []
        return processed_pairings

    def removeAllPairings(self):
        self.pairings = []
