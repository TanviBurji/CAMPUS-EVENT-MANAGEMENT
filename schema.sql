PRAGMA foreign_keys = ON;

-- Colleges
CREATE TABLE IF NOT EXISTS colleges (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  code TEXT
);

-- Students
CREATE TABLE IF NOT EXISTS students (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  college_id INTEGER NOT NULL,
  roll TEXT NOT NULL,
  name TEXT NOT NULL,
  email TEXT,
  FOREIGN KEY(college_id) REFERENCES colleges(id)
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_student_roll_college ON students(college_id, roll);

-- Events
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  college_id INTEGER NOT NULL,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  date TEXT NOT NULL,
  capacity INTEGER,
  status TEXT DEFAULT 'active',
  FOREIGN KEY(college_id) REFERENCES colleges(id)
);

-- Registrations
CREATE TABLE IF NOT EXISTS registrations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  event_id INTEGER NOT NULL,
  registered_on TEXT NOT NULL,
  FOREIGN KEY(student_id) REFERENCES students(id),
  FOREIGN KEY(event_id) REFERENCES events(id),
  UNIQUE(student_id, event_id)
);

-- Attendance
CREATE TABLE IF NOT EXISTS attendance (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  event_id INTEGER NOT NULL,
  status TEXT CHECK(status IN ('present','absent')) NOT NULL,
  marked_on TEXT NOT NULL,
  UNIQUE(student_id, event_id),
  FOREIGN KEY(student_id) REFERENCES students(id),
  FOREIGN KEY(event_id) REFERENCES events(id)
);

-- Feedback
CREATE TABLE IF NOT EXISTS feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER NOT NULL,
  event_id INTEGER NOT NULL,
  rating INTEGER CHECK (rating BETWEEN 1 AND 5) NOT NULL,
  comment TEXT,
  UNIQUE(student_id, event_id),
  FOREIGN KEY(student_id) REFERENCES students(id),
  FOREIGN KEY(event_id) REFERENCES events(id)
);

-- ===== Seed data (sample) =====
INSERT OR IGNORE INTO colleges (id, name, code) VALUES
  (1,'ABC College','ABC'),
  (2,'XYZ Institute','XYZ');

INSERT INTO students (college_id, roll, name, email) VALUES
  (1,'ABC001','Tanvi B','tanvi@example.com'),
  (1,'ABC002','Ravi K','ravi@example.com'),
  (1,'ABC003','Priya S','priya@example.com'),
  (2,'XYZ001','Aman L','aman@example.com'),
  (2,'XYZ002','Nisha T','nisha@example.com');

INSERT INTO events (college_id, name, type, date, capacity) VALUES
  (1,'Hackathon 2025','Hackathon','2025-09-10',200),
  (1,'Machine Learning Workshop','Workshop','2025-09-12',50),
  (1,'Tech Fest','Fest','2025-09-20',500),
  (2,'Entrepreneurship Seminar','Seminar','2025-09-15',100);

INSERT INTO registrations (student_id, event_id, registered_on) VALUES
  (1,1,'2025-08-25'),
  (2,1,'2025-08-26'),
  (3,2,'2025-08-30'),
  (1,2,'2025-08-28'),
  (4,4,'2025-08-29'),
  (5,4,'2025-08-30'),
  (1,3,'2025-09-01');

INSERT INTO attendance (student_id, event_id, status, marked_on) VALUES
  (1,1,'present','2025-09-10'),
  (2,1,'absent','2025-09-10'),
  (1,2,'present','2025-09-12'),
  (3,2,'present','2025-09-12'),
  (1,3,'present','2025-09-20');

INSERT INTO feedback (student_id, event_id, rating, comment) VALUES
  (1,1,5,'Great!'),
  (2,1,4,'Good'),
  (1,2,5,'Excellent workshop'),
  (3,2,4,'Very helpful'),
  (1,3,5,'Loved it');
