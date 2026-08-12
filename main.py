from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from bson.objectid import ObjectId

from db import notes_col, todos_col, reminders_col, cgpa_col, attendance_col, timetable_col

main_bp = Blueprint("main", __name__)

GRADE_POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0}
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
SLOTS = ["9:00", "10:00", "11:00", "12:00", "1:00", "2:00", "3:00", "4:00"]


def uid():
    return ObjectId(current_user.id)


# ---------------------------------------------------------------- dashboard
@main_bp.route("/")
@login_required
def dashboard():
    todos = list(todos_col.find({"user_id": uid()}))
    pending_todos = sum(1 for t in todos if not t.get("done"))

    reminders = list(reminders_col.find({"user_id": uid()}).sort("due", 1))
    upcoming_reminders = reminders[:3]

    semesters = list(cgpa_col.find({"user_id": uid()}).sort("created_at", 1))
    latest_cgpa = semesters[-1]["cumulative_cgpa"] if semesters else None

    att_records = list(attendance_col.find({"user_id": uid()}))
    if att_records:
        total_attended = sum(r["attended"] for r in att_records)
        total_held = sum(r["total"] for r in att_records)
        overall_attendance = round((total_attended / total_held) * 100, 1) if total_held else 0
        low_attendance_subjects = [r for r in att_records if r["percentage"] < 75]
    else:
        overall_attendance = None
        low_attendance_subjects = []

    notes = list(notes_col.find({"user_id": uid()}))

    return render_template(
        "dashboard.html",
        pending_todos=pending_todos,
        total_todos=len(todos),
        upcoming_reminders=upcoming_reminders,
        latest_cgpa=latest_cgpa,
        overall_attendance=overall_attendance,
        low_attendance_count=len(low_attendance_subjects),
        notes_count=len(notes),
    )


@main_bp.route("/profile")
@login_required
def profile():
    semesters = list(cgpa_col.find({"user_id": uid()}).sort("created_at", 1))
    latest_cgpa = semesters[-1]["cumulative_cgpa"] if semesters else None

    att_records = list(attendance_col.find({"user_id": uid()}))
    if att_records:
        total_attended = sum(r["attended"] for r in att_records)
        total_held = sum(r["total"] for r in att_records)
        overall_attendance = round((total_attended / total_held) * 100, 1) if total_held else 0
    else:
        overall_attendance = None

    notes_count = notes_col.count_documents({"user_id": uid()})
    todos_count = todos_col.count_documents({"user_id": uid()})

    return render_template(
        "profile.html",
        latest_cgpa=latest_cgpa,
        overall_attendance=overall_attendance,
        notes_count=notes_count,
        todos_count=todos_count,
        semesters_count=len(semesters),
    )


# -------------------------------------------------------------------- notes
@main_bp.route("/notes")
@login_required
def notes():
    items = list(notes_col.find({"user_id": uid()}).sort("created_at", -1))
    return render_template("notes.html", notes=items)


@main_bp.route("/notes/add", methods=["POST"])
@login_required
def notes_add():
    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    link = request.form.get("link", "").strip()

    if not title or not link:
        flash("Title and Google Drive link are required.", "error")
        return redirect(url_for("main.notes"))

    notes_col.insert_one({
        "user_id": uid(),
        "title": title,
        "subject": subject,
        "link": link,
        "created_at": datetime.utcnow(),
    })
    flash("Note link added.", "success")
    return redirect(url_for("main.notes"))


@main_bp.route("/notes/delete/<note_id>", methods=["POST"])
@login_required
def notes_delete(note_id):
    notes_col.delete_one({"_id": ObjectId(note_id), "user_id": uid()})
    return redirect(url_for("main.notes"))


# --------------------------------------------------------------------- todo
@main_bp.route("/todo")
@login_required
def todo():
    items = list(todos_col.find({"user_id": uid()}).sort("created_at", -1))
    return render_template("todo.html", todos=items)


@main_bp.route("/todo/add", methods=["POST"])
@login_required
def todo_add():
    task = request.form.get("task", "").strip()
    if task:
        todos_col.insert_one({
            "user_id": uid(),
            "task": task,
            "done": False,
            "created_at": datetime.utcnow(),
        })
    return redirect(url_for("main.todo"))


@main_bp.route("/todo/toggle/<todo_id>", methods=["POST"])
@login_required
def todo_toggle(todo_id):
    item = todos_col.find_one({"_id": ObjectId(todo_id), "user_id": uid()})
    if item:
        todos_col.update_one({"_id": item["_id"]}, {"$set": {"done": not item.get("done")}})
    return redirect(url_for("main.todo"))


@main_bp.route("/todo/delete/<todo_id>", methods=["POST"])
@login_required
def todo_delete(todo_id):
    todos_col.delete_one({"_id": ObjectId(todo_id), "user_id": uid()})
    return redirect(url_for("main.todo"))


# --------------------------------------------------------------- reminders
@main_bp.route("/reminders")
@login_required
def reminders():
    items = list(reminders_col.find({"user_id": uid()}).sort("due", 1))
    now = datetime.utcnow()
    return render_template("reminders.html", reminders=items, now=now)


@main_bp.route("/reminders/add", methods=["POST"])
@login_required
def reminders_add():
    title = request.form.get("title", "").strip()
    due_str = request.form.get("due", "")
    note = request.form.get("note", "").strip()

    if not title or not due_str:
        flash("Title and due date/time are required.", "error")
        return redirect(url_for("main.reminders"))

    try:
        due = datetime.strptime(due_str, "%Y-%m-%dT%H:%M")
    except ValueError:
        flash("Invalid date/time.", "error")
        return redirect(url_for("main.reminders"))

    reminders_col.insert_one({
        "user_id": uid(),
        "title": title,
        "note": note,
        "due": due,
        "created_at": datetime.utcnow(),
    })
    flash("Reminder added.", "success")
    return redirect(url_for("main.reminders"))


@main_bp.route("/reminders/delete/<reminder_id>", methods=["POST"])
@login_required
def reminders_delete(reminder_id):
    reminders_col.delete_one({"_id": ObjectId(reminder_id), "user_id": uid()})
    return redirect(url_for("main.reminders"))


# --------------------------------------------------------------------- cgpa
@main_bp.route("/cgpa")
@login_required
def cgpa():
    semesters = list(cgpa_col.find({"user_id": uid()}).sort("created_at", 1))
    latest_cgpa = semesters[-1]["cumulative_cgpa"] if semesters else None
    return render_template("cgpa.html", semesters=semesters, latest_cgpa=latest_cgpa, grade_points=GRADE_POINTS)


@main_bp.route("/cgpa/add", methods=["POST"])
@login_required
def cgpa_add():
    semester_name = request.form.get("semester_name", "").strip()
    subject_names = request.form.getlist("subject_name[]")
    credits_list = request.form.getlist("credits[]")
    grades_list = request.form.getlist("grade[]")

    subjects = []
    total_credits = 0
    total_points = 0.0

    for name, credit_str, grade in zip(subject_names, credits_list, grades_list):
        name = name.strip()
        if not name or not credit_str:
            continue
        credit = float(credit_str)
        grade = grade.strip().upper()
        point = GRADE_POINTS.get(grade, 0)
        subjects.append({"name": name, "credits": credit, "grade": grade, "grade_point": point})
        total_credits += credit
        total_points += credit * point

    if not subjects or total_credits == 0:
        flash("Add at least one subject with credits.", "error")
        return redirect(url_for("main.cgpa"))

    sgpa = round(total_points / total_credits, 2)

    prev = list(cgpa_col.find({"user_id": uid()}))
    prev_credits = sum(s["credits_total"] for s in prev)
    prev_points = sum(s["credits_total"] * s["sgpa"] for s in prev)
    cumulative_credits = prev_credits + total_credits
    cumulative_points = prev_points + total_points
    cumulative_cgpa = round(cumulative_points / cumulative_credits, 2) if cumulative_credits else 0

    cgpa_col.insert_one({
        "user_id": uid(),
        "semester_name": semester_name or f"Semester {len(prev) + 1}",
        "subjects": subjects,
        "credits_total": total_credits,
        "sgpa": sgpa,
        "cumulative_cgpa": cumulative_cgpa,
        "created_at": datetime.utcnow(),
    })
    flash(f"Semester saved. SGPA: {sgpa}", "success")
    return redirect(url_for("main.cgpa"))


@main_bp.route("/cgpa/delete/<sem_id>", methods=["POST"])
@login_required
def cgpa_delete(sem_id):
    cgpa_col.delete_one({"_id": ObjectId(sem_id), "user_id": uid()})
    # Recompute cumulative CGPA for remaining semesters in order
    remaining = list(cgpa_col.find({"user_id": uid()}).sort("created_at", 1))
    running_credits = 0
    running_points = 0.0
    for sem in remaining:
        running_credits += sem["credits_total"]
        running_points += sem["credits_total"] * sem["sgpa"]
        new_cumulative = round(running_points / running_credits, 2) if running_credits else 0
        cgpa_col.update_one({"_id": sem["_id"]}, {"$set": {"cumulative_cgpa": new_cumulative}})
    return redirect(url_for("main.cgpa"))


# --------------------------------------------------------------- attendance
@main_bp.route("/attendance")
@login_required
def attendance():
    records = list(attendance_col.find({"user_id": uid()}).sort("created_at", -1))
    for r in records:
        if r["percentage"] < 75:
            needed = (0.75 * r["total"] - r["attended"]) / 0.25
            r["advice"] = f"Attend {int(needed) + 1} more class(es) in a row to reach 75%."
        else:
            skippable = (r["attended"] / 0.75) - r["total"]
            r["advice"] = f"You can miss {int(skippable)} more class(es) and stay at/above 75%."
    return render_template("attendance.html", records=records)


@main_bp.route("/attendance/add", methods=["POST"])
@login_required
def attendance_add():
    subject = request.form.get("subject", "").strip()
    attended = request.form.get("attended", "")
    total = request.form.get("total", "")

    if not subject or not attended or not total:
        flash("All fields are required.", "error")
        return redirect(url_for("main.attendance"))

    attended = int(attended)
    total = int(total)
    if total <= 0 or attended > total or attended < 0:
        flash("Enter valid class counts.", "error")
        return redirect(url_for("main.attendance"))

    percentage = round((attended / total) * 100, 1)

    attendance_col.update_one(
        {"user_id": uid(), "subject": subject},
        {"$set": {
            "user_id": uid(),
            "subject": subject,
            "attended": attended,
            "total": total,
            "percentage": percentage,
            "created_at": datetime.utcnow(),
        }},
        upsert=True,
    )
    flash(f"{subject}: {percentage}% attendance.", "success")
    return redirect(url_for("main.attendance"))


@main_bp.route("/attendance/delete/<rec_id>", methods=["POST"])
@login_required
def attendance_delete(rec_id):
    attendance_col.delete_one({"_id": ObjectId(rec_id), "user_id": uid()})
    return redirect(url_for("main.attendance"))


# --------------------------------------------------------------- timetable
@main_bp.route("/timetable")
@login_required
def timetable():
    doc = timetable_col.find_one({"user_id": uid()}) or {"grid": {}}
    return render_template("timetable.html", grid=doc.get("grid", {}), days=DAYS, slots=SLOTS)


@main_bp.route("/timetable/save", methods=["POST"])
@login_required
def timetable_save():
    grid = {}
    for day in DAYS:
        for slot in SLOTS:
            key = f"{day}|{slot}"
            value = request.form.get(key, "").strip()
            if value:
                grid[key] = value

    timetable_col.update_one(
        {"user_id": uid()},
        {"$set": {"user_id": uid(), "grid": grid, "updated_at": datetime.utcnow()}},
        upsert=True,
    )
    flash("Timetable saved.", "success")
    return redirect(url_for("main.timetable"))
