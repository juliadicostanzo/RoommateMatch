CREATE Table students(
    id INT PRIMARY KEY,
    name VARCHAR(100),
    hometown VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(100)
);

CREATE Table admins(
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    password VARCHAR(100)
);

CREATE Table interests (
    id INT PRIMARY KEY,
    title VARCHAR(100)
);

CREATE Table preferences (
    id INT PRIMARY KEY,
    title VARCHAR(100)
);

CREATE Table students_to_preference (
    id INT PRIMARY KEY,
    student_id INT,
    preference_id INT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (preference_id) REFERENCES preferences(id)
);

CREATE Table groups (
    id INT PRIMARY KEY
);

CREATE Table students_to_interest (
    id INT PRIMARY KEY,
    student_id INT,
    interest_id INT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (interest_id) REFERENCES interests(id)
);

CREATE Table students_to_groups (
    id INT PRIMARY KEY,
    student_id INT,
    group_id INT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);

ALTER TABLE students
ADD group_id INT
REFERENCES groups(id);

DROP TABLE students_to_groups;

update admins set name = 'Admin', email = 'admin@campus.edu' where admins.id = 101; 