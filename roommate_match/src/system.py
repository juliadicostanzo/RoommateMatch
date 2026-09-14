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
        student = self.getStudentById(id)
        if student is None:
            return False, f"There is no student with id: {id}"
        student_id = int(student.id)
        student_group_id = int(student.groupID)

        #Remove roommate request involving student
        self.requests = [
            request
            for request in self.requests
            if int(request.getSenderId()) != student_id
            and student_id not in [
            int(receiver_id)
            for receiver_id in request.getReceiverIds()
            ]
        ]
        # Remove request references stored on students
        for other_student in self.students:
            other_student.requestsSent = [
                request
                for request in other_student.requestsSent
                if int(request.getSenderId()) != student_id
                and student_id not in [
                    int(receiver_id)
                    for receiver_id in request.getReceiverIds()
                ]
            ]
            other_student.requestsReceived = [
                request
                for request in other_student.requestsReceived
                if int(request.getSenderId()) != student_id
                and student_id not in [
                    int(receiver_id)
                    for receiver_id in request.getReceiverIds()
                ]
            ]

            other_student.requests = [
                request
                for request in other_student.requests
                if int(request.getSenderId()) != student_id
                and student_id not in [
                    int(receiver_id)
                    for receiver_id in request.getReceiverIds()
                ]
            ]
        # Remove pending pairings containing student
        cleaned_pairings = []

        for current_pairing in self.pairings:

            if isinstance(current_pairing, dict):
                member_ids = [int(member_id) 
                for member_id in current_pairing.get("members", [])]
            else:
                member_ids = [int(member_id) 
                for member_id in getattr(current_pairing,"students",[])]

            if student_id not in member_ids:
                cleaned_pairings.append(current_pairing)

        self.pairings = cleaned_pairings

        # Remove student from approved groups
        cleaned_approved_groups = []

        for approved_group in self.approved_groups:
            if isinstance(approved_group, dict):
                member_ids = [int(member_id) 
                for member_id in approved_group.get("members",[])]

            if student_id in member_ids:
                member_ids.remove(student_id)

            # Keep group only if it still has 2+ students
            if len(member_ids) >= 2:
                approved_group["members"] = member_ids
                cleaned_approved_groups.append(approved_group)
        else:
            member_ids = [int(member_id)
                for member_id in getattr(
                    approved_group,
                    "students",
                    []
                )
            ]

            if student_id in member_ids:
                member_ids.remove(student_id)

            if len(member_ids) >= 2:
                approved_group.students = member_ids

                if hasattr(approved_group, "group"):
                    approved_group.group = member_ids

                cleaned_approved_groups.append(approved_group)

        self.approved_groups = cleaned_approved_groups

        # Remove student
        self.students.remove(student)

        # If old group has fewer than 2 members
        if student_group_id >= 0:

            remaining_group_members = [
                other_student
                for other_student in self.students
                if int(other_student.groupID) == student_group_id
            ]

            if len(remaining_group_members) < 2:

                for remaining_student in remaining_group_members:
                    remaining_student.groupID = -1

                self.approved_groups = [
                    group
                    for group in self.approved_groups
                    if (
                        int(
                            group.get("group_id", -1)
                            if isinstance(group, dict)
                            else getattr(group, "group_id", -1)
                        )
                        != student_group_id
                    )
                ]
        return True, f"{student.name} was successfully removed."
        

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
