# Roommate Match Instructions

This document explains how to run and use the roommate match program.

## Setup & Installation

### Prerequisites

This project uses **uv** to manage Python dependencies.

### Steps

1. **Install uv** using the official installer:
   - [uv Installation Instructions](https://docs.astral.sh/uv/getting-started/installation/)

2. **Install dependencies** in the terminal:
   ```bash
   uv sync
   ```

## Running the Program

1. Open a terminal
2. Navigate to the project folder
3. Run the application:
   ```bash
   uv run python main.py
   ```

## User Guide

### Admin Menu

**Login:** 
- Email: `admin@campus.edu`
- Password: `admin`

**Available Options:**

- **Create Student**
  - Enter student information
  - A temporary password will be assigned to that student
  - The student can change this password when they log in

- **Finalize Pairing**
  - Pairings will show up here when all members of a request have accepted it
  - Admin can reject or approve all pairings
  - Once approved, a group ID is assigned and the group can be found under the view all groups button

### Student Menu

**Login:** 
- Use an email and password from the students.csv file

**Available Options:**

- **View Students/Make Requests**
  - Students are listed in order from most similar to least similar
  - A student can make a request if they have no requests outgoing or pending
  - A student can only send one request and can only receive one request
  - Click on multiple students to send a request all at once
  - If one person in the request group rejects the request, the request is void and a new request must be made

- **View Request Status**
  - View all members of the group and see their status (pending/accepted)

- **View Group Status**
  - A request becomes a group when all members of the request have accepted
  - Once a request becomes a group, the admin has the option to approve or deny this group
  - Approved groups will show an "Approved" status

- **Respond to Requests**
  - See pending requests and accept or reject them

- **Change Interests**
  - Click to toggle each of the interests

- **Change Preferences**
  - Click to toggle each of the preferences

- **Change Password**
  - Provide old password to change to a new password

## Testing

Run tests using a Python debugger. All tests passing indicates that the system is working correctly. We used the unittest framework.

## System Test Cases
#### test_update_request_list_accepted 
Creates three students. One student sends requests to the other two students. Both students accept the request and updateStatus() marks the request as accepted. The test first confirms that the request was successfully added to the system's request list by checking that there is exactly one request. Then, when updateRequestList() is called, the accepted requests should be removed from the request list and moved into the pairing list. When finalize pairing is called, it simulates the admin approving the pairing. The pairing is removed from the pairing list, and the students are assigned to the same groupID. Lastly, we check all three students have the same groupID.
#### test_update_request_list_rejected 
Creates three students. One student sends requests to the other two students. Both students reject the request and updateStatus() marks the request as rejected. The test first confirms that the rejected request was successfully added to the system's request list by checking that there is exactly one request. Then, when updateRequestList() is called, the rejected requests should be removed from the request list. Then we check that the request list is empty and the pairing list is empty. Lastly, we check all three students groupID is still -1.
#### test_one_rejected_request
Creates three students. One student sends requests to the other two students. One student reject the request and the other accepts. updateStatus() marks the request as rejected. The test first confirms that the rejected request was successfully added to the system's request list by checking that there is exactly one request. Then, when updateRequestList() is called, the rejected requests should be removed from the request list. Then we check that the request list is empty and the pairing list is empty. Lastly, we check all three students groupID is still -1.

## Component tests
### test_system.py
##### test_add_student
##### test_remove_student
##### test_get_student_by_name
##### test_get_student_by_id
##### test_finalize_pairing
##### test_view_students

### student_test.py
##### test_sendRequest
##### test_respondRequest
##### test_updatePassword
##### test_updateName
##### test_updateHometown
##### test_updateInterests
##### test_updatePreferences
##### test_viewStudents
##### test_searchStudents
##### test_rankStudentsByMatch

### test_admin.py
##### test_add_student
##### test_remove_student
##### test_view_all_students
##### test_get_student_by_name
##### test_get_student_by_id
##### test_add_preference_option
##### test_add_interest_option

### test_roommateRequest.py
##### test_initial_status
##### test_accept_request
##### test_reject_request
##### test_get_sender_id
##### test_get_receiver_ids

### test_pairing.py
##### test_get_group_id
##### test_get_students





