// script.js - frontend <-> backend glue (complete)
const API_BASE = window.location.origin + "/api";

// helper
function el(tag, html='') { let e = document.createElement(tag); e.innerHTML = html; return e; }

// -------- Events & registration UI helpers ----------
async function fetchEventsForForm(selectId = "reg-event") {
  try {
    const res = await fetch(`${API_BASE}/events`);
    const events = await res.json();
    const sel = document.getElementById(selectId);
    if (!sel) return;
    sel.innerHTML = "";
    events.forEach(ev => {
      const o = document.createElement("option");
      o.value = ev.id;
      o.textContent = `${ev.name} (${ev.type}) - ${ev.date} [${ev.status}]`;
      sel.appendChild(o);
    });
  } catch (err) {
    console.error(err);
  }
}

async function fetchEventsList() {
  const cont = document.getElementById("events-list");
  if (!cont) return;
  cont.innerHTML = "<h3>Loading events…</h3>";
  const res = await fetch(`${API_BASE}/events`);
  const events = await res.json();
  cont.innerHTML = "";
  events.forEach(ev => {
    const c = el("div", `<div style="display:flex;justify-content:space-between;align-items:center">
      <div>
        <strong>${ev.name}</strong><br><small class="meta">${ev.type} • ${ev.date} • Capacity: ${ev.capacity || 'N/A'} • Status: ${ev.status}</small>
      </div>
      <div>
        <button class="btn" onclick="promptRegister(${ev.id}, '${ev.status}')">Register</button>
        <button class="btn" onclick="promptAttendance(${ev.id}, '${ev.status}')">Attendance</button>
        <button class="btn warning" onclick="promptFeedback(${ev.id}, '${ev.status}')">Feedback</button>
      </div>
    </div>`);
    c.className = "card";
    cont.appendChild(c);
  });
}

function promptRegister(eventId, status) {
  if (status === "cancelled") return alert("This event is cancelled. Registration is closed.");
  const name = prompt("Student Name (e.g. Tanvi B)");
  if (!name) return alert("Name required");
  const roll = prompt("Roll number (e.g. ABC001)");
  if (!roll) return alert("Roll required");
  registerStudent({ name, roll, event_id: eventId });
}

async function submitRegistration() {
  const name = document.getElementById("reg-name").value.trim();
  const roll = document.getElementById("reg-roll").value.trim();
  const event_id = document.getElementById("reg-event").value;
  if (!name || !roll || !event_id) { document.getElementById("reg-msg").innerText = "Fill all fields"; return; }
  await registerStudent({ name, roll, event_id });
}

async function registerStudent(payload) {
  try {
    const res = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok) {
      alert("Registered successfully (student id: " + data.student_id + ")");
      await fetchEventsList();
      if (document.getElementById("reg-msg")) document.getElementById("reg-msg").innerText = "Registered successfully";
    } else {
      alert("Error: " + (data.error || JSON.stringify(data)));
      if (document.getElementById("reg-msg")) document.getElementById("reg-msg").innerText = (data.error || JSON.stringify(data));
    }
  } catch (err) {
    console.error(err);
    alert("Network error");
  }
}

// -------- Attendance ----------
function promptAttendance(eventId, status) {
  if (status === "cancelled") return alert("This event is cancelled.");
  const roll = prompt("Student roll (e.g. ABC001)");
  if (!roll) return alert("Roll required");
  const statusVal = prompt("Status: present or absent", "present");
  if (!statusVal) return;
  markAttendanceByRoll({ roll, event_id: eventId, status: statusVal });
}

async function submitAttendance() {
  const roll = document.getElementById("att-roll").value.trim();
  const event_id = document.getElementById("att-event").value;
  const status = document.getElementById("att-status").value;
  if (!roll || !event_id) { document.getElementById("att-msg").innerText = "Fill roll and event"; return; }
  await markAttendanceByRoll({ roll, event_id, status });
}

async function markAttendanceByRoll({ roll, event_id, status }) {
  try {
    const sres = await fetch(`${API_BASE}/students?roll=${encodeURIComponent(roll)}`);
    const students = await sres.json();
    if (!students.length) { alert("Student not found. Register first."); return; }
    const student_id = students[0].id;

    const res = await fetch(`${API_BASE}/attendance`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ student_id, event_id, status })
    });
    const data = await res.json();
    if (res.ok) {
      alert("Attendance marked ✔");
      if (document.getElementById("att-msg")) document.getElementById("att-msg").innerText = "Attendance marked ✔";
    } else {
      alert("Error: " + (data.error || JSON.stringify(data)));
      if (document.getElementById("att-msg")) document.getElementById("att-msg").innerText = data.error || JSON.stringify(data);
    }
  } catch (err) {
    console.error(err);
    alert("Network error");
  }
}

// -------- Feedback ----------
function promptFeedback(eventId, status) {
  if (status === "cancelled") return alert("This event is cancelled.");
  const roll = prompt("Student roll (e.g. ABC001)");
  if (!roll) return alert("Roll required");
  const rating = prompt("Rating 1-5", "5");
  if (!rating) return;
  const comment = prompt("Optional comment","");
  submitFeedbackByRoll({ roll, event_id: eventId, rating, comment });
}

async function submitFeedback() {
  const roll = document.getElementById("fb-roll").value.trim();
  const event_id = document.getElementById("fb-event").value;
  const rating = document.getElementById("fb-rating").value;
  const comment = document.getElementById("fb-comment").value.trim();
  if (!roll || !event_id || !rating) { document.getElementById("fb-msg").innerText = "Fill required fields"; return; }
  await submitFeedbackByRoll({ roll, event_id, rating, comment });
}

async function submitFeedbackByRoll({ roll, event_id, rating, comment }) {
  try {
    const sres = await fetch(`${API_BASE}/students?roll=${encodeURIComponent(roll)}`);
    const students = await sres.json();
    if (!students.length) { alert("Student not found. Register first."); return; }
    const student_id = students[0].id;

    const res = await fetch(`${API_BASE}/feedback`, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ student_id, event_id, rating, comment })
    });
    const data = await res.json();
    if (res.ok) {
      alert("Feedback submitted ✔");
      if (document.getElementById("fb-msg")) document.getElementById("fb-msg").innerText = "Feedback submitted ✔";
    } else {
      alert("Error: " + (data.error || JSON.stringify(data)));
      if (document.getElementById("fb-msg")) document.getElementById("fb-msg").innerText = data.error || JSON.stringify(data);
    }
  } catch (err) {
    console.error(err);
    alert("Network error");
  }
}

// -------- Admin ----------
async function adminCreateEvent() {
  const college_id = document.getElementById("admin-college").value;
  const name = document.getElementById("admin-name").value.trim();
  const type = document.getElementById("admin-type").value.trim();
  const date = document.getElementById("admin-date").value.trim();
  const capacity = document.getElementById("admin-capacity").value.trim() || null;
  if (!college_id || !name || !type || !date) { document.getElementById("admin-create-msg").innerText = "Fill required fields"; return; }

  const res = await fetch(`${API_BASE}/events`, {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ college_id, name, type, date, capacity })
  });
  const data = await res.json();
  if (res.ok) {
    document.getElementById("admin-create-msg").innerText = "Event created (ID: " + data.event_id + ")";
    fetchEventsForForm();
    fetchEventsList();
  } else {
    document.getElementById("admin-create-msg").innerText = data.error || JSON.stringify(data);
  }
}

async function adminCancelEvent() {
  const id = document.getElementById("admin-cancel-id").value.trim();
  if (!id) { document.getElementById("admin-cancel-msg").innerText = "Provide event id"; return; }
  const res = await fetch(`${API_BASE}/events/${id}/cancel`, { method: "POST" });
  const data = await res.json();
  if (res.ok) {
    document.getElementById("admin-cancel-msg").innerText = data.msg || "Cancelled";
    fetchEventsForForm();
    fetchEventsList();
  } else {
    document.getElementById("admin-cancel-msg").innerText = data.error || JSON.stringify(data);
  }
}

// -------- Reports ----------
async function fetchReports() {
  try {
    const popRes = await fetch(`${API_BASE}/reports/event-popularity`);
    const pop = await popRes.json();
    const popDiv = document.getElementById("report-popularity");
    popDiv.innerHTML = "<table class='table'><thead><tr><th>Event</th><th>Registrations</th></tr></thead><tbody>" +
      pop.map(r => `<tr><td>${r.name} (${r.type})</td><td>${r.registrations}</td></tr>`).join("") +
      "</tbody></table>";

    const partRes = await fetch(`${API_BASE}/reports/student-participation`);
    const part = await partRes.json();
    const partDiv = document.getElementById("report-participation");
    partDiv.innerHTML = "<table class='table'><thead><tr><th>Student</th><th>Attended</th></tr></thead><tbody>" +
      part.map(s => `<tr><td>${s.name} (${s.roll})</td><td>${s.attended}</td></tr>`).join("") +
      "</tbody></table>";

    const topRes = await fetch(`${API_BASE}/reports/top-students`);
    const top = await topRes.json();
    const topDiv = document.getElementById("report-top3");
    topDiv.innerHTML = "<table class='table'><thead><tr><th>Student</th><th>Attended</th></tr></thead><tbody>" +
      top.map(s => `<tr><td>${s.name} (${s.roll})</td><td>${s.attended}</td></tr>`).join("") +
      "</tbody></table>";
  } catch (err) {
    console.error(err);
  }
}

async function fetchAttendancePercent() {
  const event_id = document.getElementById("att-report-event").value.trim();
  if (!event_id) return alert("Provide event id");
  const res = await fetch(`${API_BASE}/reports/attendance-percent?event_id=${event_id}`);
  const data = await res.json();
  if (res.ok) {
    document.getElementById("report-att-percent").innerHTML = `<strong>${data.attendance_percent}%</strong> (${data.present}/${data.total_registered})`;
  } else {
    document.getElementById("report-att-percent").innerText = data.error || JSON.stringify(data);
  }
}

async function fetchAvgFeedback() {
  const event_id = document.getElementById("fb-report-event").value.trim();
  if (!event_id) return alert("Provide event id");
  const res = await fetch(`${API_BASE}/reports/avg-feedback?event_id=${event_id}`);
  const data = await res.json();
  if (res.ok) {
    document.getElementById("report-fb-avg").innerHTML = `<strong>Average: ${data.avg_rating}</strong> (${data.responses} responses)`;
  } else {
    document.getElementById("report-fb-avg").innerText = data.error || JSON.stringify(data);
  }
}
