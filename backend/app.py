# app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from models import db, College, Event, Student, Registration, Attendance, Feedback
from sqlalchemy import and_

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "events.db")
DB_URL = f"sqlite:///{DB_PATH}"

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)
db.init_app(app)

# ---------- helpers ----------
def event_to_dict(e):
    return {
        "id": e.id,
        "college_id": e.college_id,
        "name": e.name,
        "type": e.type,
        "date": e.date,
        "capacity": e.capacity,
        "status": e.status
    }

def student_to_dict(s):
    return {"id": s.id, "college_id": s.college_id, "roll": s.roll, "name": s.name, "email": s.email}

# ---------- static root ----------
@app.route("/")
def index():
    return app.send_static_file("index.html")

# ---------- Event APIs ----------
@app.route("/api/events", methods=["GET"])
def api_get_events():
    events = Event.query.order_by(Event.date).all()
    return jsonify([event_to_dict(e) for e in events])

@app.route("/api/events", methods=["POST"])
def api_create_event():
    data = request.get_json() or {}
    for key in ("college_id","name","type","date"):
        if key not in data:
            return jsonify({"error": f"{key} required"}), 400
    e = Event(
        college_id = data["college_id"],
        name = data["name"],
        type = data["type"],
        date = data["date"],
        capacity = data.get("capacity"),
        status = data.get("status", "active")
    )
    db.session.add(e)
    db.session.commit()
    return jsonify({"status":"ok","event_id": e.id}), 201

@app.route("/api/events/<int:event_id>/cancel", methods=["POST"])
def api_cancel_event(event_id):
    e = Event.query.get(event_id)
    if not e:
        return jsonify({"error":"event not found"}), 404
    e.status = "cancelled"
    db.session.commit()
    return jsonify({"status":"ok","msg":"event cancelled"})

# ---------- Student APIs ----------
@app.route("/api/students", methods=["GET"])
def api_get_students():
    roll = request.args.get("roll")
    college_id = request.args.get("college_id")
    q = Student.query
    if roll:
        q = q.filter_by(roll=roll)
    if college_id:
        q = q.filter_by(college_id=college_id)
    students = q.all()
    return jsonify([student_to_dict(s) for s in students])

@app.route("/api/students", methods=["POST"])
def api_create_student():
    data = request.get_json() or {}
    for key in ("college_id","roll","name"):
        if key not in data:
            return jsonify({"error": f"{key} required"}), 400
    existing = Student.query.filter_by(college_id=data["college_id"], roll=data["roll"]).first()
    if existing:
        return jsonify({"error":"student roll already exists for this college", "student_id": existing.id}), 400
    s = Student(college_id=data["college_id"], roll=data["roll"], name=data["name"], email=data.get("email"))
    db.session.add(s)
    db.session.commit()
    return jsonify({"status":"ok","student_id": s.id}), 201

# ---------- Registration ----------
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or {}
    event_id = data.get("event_id")
    if not event_id:
        return jsonify({"error":"event_id required"}), 400
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error":"event not found"}), 404
    if event.status == "cancelled":
        return jsonify({"error":"event is cancelled"}), 400

    # capacity
    if event.capacity:
        reg_count = Registration.query.filter_by(event_id=event_id).count()
        if reg_count >= (event.capacity or 0):
            return jsonify({"error":"event full"}), 400

    student_id = data.get("student_id")
    if student_id:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({"error":"student not found"}), 404
    else:
        name = data.get("name")
        roll = data.get("roll")
        college_id = data.get("college_id") or event.college_id or 1
        if not (name and roll):
            return jsonify({"error":"name and roll required to create student"}), 400
        student = Student.query.filter_by(college_id=college_id, roll=roll).first()
        if not student:
            student = Student(name=name, roll=roll, email=data.get("email"), college_id=college_id)
            db.session.add(student)
            db.session.commit()

    existing = Registration.query.filter_by(student_id=student.id, event_id=event_id).first()
    if existing:
        return jsonify({"error":"already registered"}), 400
    reg = Registration(student_id=student.id, event_id=event_id, registered_on=datetime.utcnow().isoformat())
    db.session.add(reg)
    db.session.commit()
    return jsonify({"status":"ok", "registration_id": reg.id, "student_id": student.id})

# ---------- Attendance ----------
@app.route("/api/attendance", methods=["POST"])
def api_attendance():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    event_id = data.get("event_id")
    status = data.get("status")  # "present" or "absent"
    if not (student_id and event_id and status):
        return jsonify({"error":"student_id, event_id, status required"}), 400
    if status not in ("present","absent"):
        return jsonify({"error":"status must be 'present' or 'absent'"}), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error":"event not found"}), 404
    if event.status == "cancelled":
        return jsonify({"error":"event is cancelled"}), 400

    reg = Registration.query.filter_by(student_id=student_id, event_id=event_id).first()
    if not reg:
        return jsonify({"error":"student not registered for event"}), 400

    att = Attendance.query.filter_by(student_id=student_id, event_id=event_id).first()
    if not att:
        att = Attendance(student_id=student_id, event_id=event_id, status=status, marked_on=datetime.utcnow().isoformat())
        db.session.add(att)
    else:
        att.status = status
        att.marked_on = datetime.utcnow().isoformat()
    db.session.commit()
    return jsonify({"status":"ok"})

# ---------- Feedback ----------
@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    data = request.get_json() or {}
    student_id = data.get("student_id")
    event_id = data.get("event_id")
    rating = data.get("rating")
    comment = data.get("comment", "")
    if not (student_id and event_id and rating):
        return jsonify({"error":"student_id, event_id, rating required"}), 400
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError()
    except Exception:
        return jsonify({"error":"rating must be an integer 1..5"}), 400

    reg = Registration.query.filter_by(student_id=student_id, event_id=event_id).first()
    if not reg:
        return jsonify({"error":"student not registered for event"}), 400

    fb = Feedback.query.filter_by(student_id=student_id, event_id=event_id).first()
    if not fb:
        fb = Feedback(student_id=student_id, event_id=event_id, rating=rating, comment=comment)
        db.session.add(fb)
    else:
        fb.rating = rating
        fb.comment = comment
    db.session.commit()
    return jsonify({"status":"ok"})

# ---------- Reports ----------
@app.route("/api/reports/event-popularity", methods=["GET"])
def api_report_event_popularity():
    college_id = request.args.get("college_id")
    ev_type = request.args.get("type")
    q = db.session.query(
        Event.id, Event.name, Event.type, Event.date,
        db.func.count(Registration.id).label("registrations")
    ).outerjoin(Registration, Event.id == Registration.event_id)
    if college_id:
        q = q.filter(Event.college_id == college_id)
    if ev_type:
        q = q.filter(Event.type == ev_type)
    q = q.group_by(Event.id).order_by(db.desc("registrations"))
    rows = q.all()
    result = []
    for r in rows:
        result.append({
            "id": r.id, "name": r.name, "type": r.type, "date": r.date, "registrations": int(r.registrations)
        })
    return jsonify(result)

@app.route("/api/reports/attendance-percent", methods=["GET"])
def api_report_attendance_percent():
    event_id = request.args.get("event_id")
    if not event_id:
        return jsonify({"error":"event_id required"}), 400
    total = Registration.query.filter_by(event_id=event_id).count()
    present = Attendance.query.filter_by(event_id=event_id, status="present").count()
    percent = 0.0
    if total > 0:
        percent = (present / total) * 100.0
    return jsonify({"event_id": int(event_id), "total_registered": total, "present": present, "attendance_percent": round(percent,2)})

@app.route("/api/reports/avg-feedback", methods=["GET"])
def api_report_avg_feedback():
    event_id = request.args.get("event_id")
    if not event_id:
        return jsonify({"error":"event_id required"}), 400
    row = db.session.query(db.func.avg(Feedback.rating).label("avg_rating"), db.func.count(Feedback.id).label("count")).filter(Feedback.event_id==event_id).one()
    avg = float(row.avg_rating) if row.avg_rating is not None else 0.0
    return jsonify({"event_id": int(event_id), "avg_rating": round(avg,2), "responses": int(row.count)})

@app.route("/api/reports/student-participation", methods=["GET"])
def api_report_student_participation():
    q = db.session.query(
        Student.id, Student.name, Student.roll,
        db.func.count(Attendance.id).label("attended")
    ).outerjoin(Attendance, and_(Student.id == Attendance.student_id, Attendance.status=='present'))\
     .group_by(Student.id).order_by(db.desc("attended"))
    rows = q.all()
    return jsonify([{"student_id": r.id, "name": r.name, "roll": r.roll, "attended": int(r.attended)} for r in rows])

@app.route("/api/reports/top-students", methods=["GET"])
def api_report_top_students():
    college_id = request.args.get("college_id")
    q = db.session.query(
        Student.id, Student.name, Student.roll,
        db.func.count(Attendance.id).label("attended")
    ).outerjoin(Attendance, and_(Student.id == Attendance.student_id, Attendance.status=='present'))
    if college_id:
        q = q.filter(Student.college_id == college_id)
    q = q.group_by(Student.id).order_by(db.desc("attended")).limit(3)
    rows = q.all()
    return jsonify([{"student_id": r.id, "name": r.name, "roll": r.roll, "attended": int(r.attended)} for r in rows])

# ---------- Seed data ----------
def seed_data():
    if College.query.count() == 0:
        c1 = College(name="ABC College", code="ABC")
        c2 = College(name="XYZ Institute", code="XYZ")
        db.session.add_all([c1, c2])
        db.session.commit()

    if Event.query.count() == 0:
        e1 = Event(college_id=1, name="Hackathon 2025", type="Hackathon", date="2025-09-10", capacity=200)
        e2 = Event(college_id=1, name="Machine Learning Workshop", type="Workshop", date="2025-09-12", capacity=50)
        e3 = Event(college_id=1, name="Tech Fest", type="Fest", date="2025-09-20", capacity=500)
        e4 = Event(college_id=2, name="Entrepreneurship Seminar", type="Seminar", date="2025-09-15", capacity=100)
        db.session.add_all([e1, e2, e3, e4])
        db.session.commit()

    if Student.query.count() == 0:
        s1 = Student(college_id=1, roll="ABC001", name="Tanvi B", email="tanvi@example.com")
        s2 = Student(college_id=1, roll="ABC002", name="Ravi K", email="ravi@example.com")
        s3 = Student(college_id=1, roll="ABC003", name="Priya S", email="priya@example.com")
        s4 = Student(college_id=2, roll="XYZ001", name="Aman L", email="aman@example.com")
        s5 = Student(college_id=2, roll="XYZ002", name="Nisha T", email="nisha@example.com")
        db.session.add_all([s1, s2, s3, s4, s5])
        db.session.commit()

    if Registration.query.count() == 0:
        regs = [
            Registration(student_id=1, event_id=1, registered_on="2025-08-25"),
            Registration(student_id=2, event_id=1, registered_on="2025-08-26"),
            Registration(student_id=3, event_id=2, registered_on="2025-08-30"),
            Registration(student_id=1, event_id=2, registered_on="2025-08-28"),
            Registration(student_id=4, event_id=4, registered_on="2025-08-29"),
            Registration(student_id=5, event_id=4, registered_on="2025-08-30"),
            Registration(student_id=1, event_id=3, registered_on="2025-09-01")
        ]
        db.session.add_all(regs)
        db.session.commit()

    if Attendance.query.count() == 0:
        atts = [
            Attendance(student_id=1, event_id=1, status="present", marked_on="2025-09-10"),
            Attendance(student_id=2, event_id=1, status="absent", marked_on="2025-09-10"),
            Attendance(student_id=1, event_id=2, status="present", marked_on="2025-09-12"),
            Attendance(student_id=3, event_id=2, status="present", marked_on="2025-09-12"),
            Attendance(student_id=1, event_id=3, status="present", marked_on="2025-09-20"),
        ]
        db.session.add_all(atts)
        db.session.commit()

    if Feedback.query.count() == 0:
        fbs = [
            Feedback(student_id=1, event_id=1, rating=5, comment="Great!"),
            Feedback(student_id=2, event_id=1, rating=4, comment="Good"),
            Feedback(student_id=1, event_id=2, rating=5, comment="Excellent workshop"),
            Feedback(student_id=3, event_id=2, rating=4, comment="Very helpful"),
            Feedback(student_id=1, event_id=3, rating=5, comment="Loved it"),
        ]
        db.session.add_all(fbs)
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == "__main__":
    app.run(debug=True)
