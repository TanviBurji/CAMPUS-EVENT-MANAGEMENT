# CAMPUS-EVENT-MANAGEMENT
Project Overview:
This document describes the design for a Campus Event Management Platform that supports: 
Admin Portal (Web): For college staff to create and manage events.  
Student App (Mobile): For students to browse, register, check-in, and provide feedback.  
Assumptions: Each event belongs to a college and has a unique ID. Students are uniquely 
identified by roll number per college. Events can be Hackathons, Workshops, Fests, Seminars, etc. 
Feedback is optional but only one feedback per student per event is allowed. 
System scales to ~50 colleges, 500 students each.

My Understanding of the Problem:
“Admins need a way to create and manage events.”
“Students should be able to register and mark attendance.”
“Reports are needed to analyze popularity and participation.”
Assumptions (e.g., event IDs unique across colleges, prevent duplicate registrations).

Features Implemented:
Event creation (Admin).
Student registration.
Attendance marking.
Feedback collection.
Reports:
Event popularity
Student participation
Top 3 active students

Tech Stack:
Language/Framework (e.g., Python Flask / Node.js Express).
Database (SQLite for simplicity).
Tools (SQL queries for reports).

HOW TO RUN THE PROJECT:
install dependencies (pip install -r requirements.txt)
run the project (python app.py)
