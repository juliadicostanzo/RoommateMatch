# Roommate Match
Roommate Match is a terminal-based roommate matching application built with Python, Textual, and SQLite. Students can browse potential roommates, send roommate requests, manage preferences and interests, and form approved roommate groups. 

The application was originally developed as a four-person team project for a Software Engineering course at Ithaca College. After the course project was completed, I continued developing the application independently to improve its administrative functionality and data management.

## Features
- Student and administrator login
- Browse and compare potential roommates
- Send and respond to roommate requests
- Track pending and approved roommate groups
- Manage student interests and preferences
- Admin creation of student accounts
- Admin approval and rejection of roommate pairings
- Admin view of all students
- Admin removal of students
- Cleanup of related requests, pairings, groups, interests, and preferences when a student is deleted
- SQLite data persistence

## Technologies
- Python
- Textual
- SQLite
- SQL
- uv
- Git / GitHub
- unittest

## Running the Project
### 1. Clone the repository

```bash
git clone https://github.com/juliadicostanzo/RoommateMatch.git
cd RoommateMatch
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Run the application

```bash
uv run python main.py
```

## My Extension
I independently extended the original project by implementing a Manage Students feature for administrators.

The extension allows an administrator to:

- View all students in the system
- Select a student for removal
- Delete a student from the system
- Persist the deletion to the SQLite database:
- Remove related roommate requests
- Remove pending pairings
- Update approved roommate groups
- Remove student interests and preferences
- Remove Database relationship records

This cleanup prevents deleted students from leaving invalid references elsewhere in the application and helps maintain consistent application and database state.

## Original Project

This repository is based on a four-person Software Engineering course project.

Original repository:

https://github.com/VenkatCSClasses/project-2-roommate-match
