# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class College(db.Model):
    __tablename__ = "colleges"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50))

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey("colleges.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer)
    status = db.Column(db.String(20), default="active")  # active / cancelled

    college = db.relationship("College", backref=db.backref("events", lazy=True))

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey("colleges.id"), nullable=False, default=1)
    roll = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200))

    __table_args__ = (db.UniqueConstraint('college_id','roll', name='uix_college_roll'),)

class Registration(db.Model):
    __tablename__ = "registrations"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    registered_on = db.Column(db.String(60))

    __table_args__ = (db.UniqueConstraint('student_id','event_id', name='uix_student_event'),)

class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'present' / 'absent'
    marked_on = db.Column(db.String(60))

    __table_args__ = (db.UniqueConstraint('student_id','event_id', name='uix_attendance_student_event'),)

class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1..5
    comment = db.Column(db.Text)

    __table_args__ = (db.UniqueConstraint('student_id','event_id', name='uix_feedback_student_event'),)
