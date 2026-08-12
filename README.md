# Student Management System

A Flask web app for tracking notes (linked to Google Drive), a to-do list,
reminders, a CGPA calculator, an attendance calculator, and a weekly
timetable — with login/signup and data stored in MongoDB Atlas.

## 1. Install Python dependencies

```bash
cd sms_project
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Set up MongoDB Atlas (cloud database)

1. Go to https://www.mongodb.com/cloud/atlas and create a free account / free
   M0 cluster.
2. In Atlas, go to **Database Access** and create a database user with a
   username and password (save them).
3. Go to **Network Access** and add your current IP address (or, for
   testing, "Allow access from anywhere" — `0.0.0.0/0`).
4. Go to your cluster, click **Connect > Drivers**, choose Python, and copy
   the connection string. It looks like:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. In MongoDB Compass (the desktop GUI app), you can paste the same
   connection string under **Connect** to browse the `sms_db` database and
   its collections (`users`, `notes`, `todos`, `reminders`,
   `cgpa_semesters`, `attendance`, `timetable`) once the app has created
   some data.

## 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:
- `MONGO_URI` — your Atlas connection string from step 2 (replace
  `<username>` and `<password>` with your real values, and add `sms_db` as
  the database name right after `.net/`, e.g.
  `.../sms_db?retryWrites=true...`)
- `SECRET_KEY` — any long random string

## 4. Run the app

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser. It will redirect you to
**Sign Up** first — create an account, then log in.

## Project structure

```
sms_project/
├── app.py              # Flask app factory, blueprint registration
├── config.py           # Loads settings from .env
├── db.py                # MongoDB connection + collections + indexes
├── auth.py              # Signup / login / logout (Flask-Login + password hashing)
├── main.py               # Dashboard, notes, to-do, reminders, CGPA, attendance, timetable
├── requirements.txt
├── .env.example
├── templates/            # Jinja2 HTML templates
└── static/
    ├── css/style.css
    └── js/app.js
```

## Notes on how things work

- **Auth**: passwords are hashed with Werkzeug's `generate_password_hash`
  (never stored in plain text). Sessions are handled by Flask-Login.
- **Notes**: each entry is just a title + subject + a Google Drive URL you
  paste in — clicking "Open in Drive" opens it in a new tab. This app does
  not host files itself.
- **CGPA**: uses a 10-point grade scale (O=10, A+=9, A=8, B+=7, B=6, C=5,
  P=4, F=0). Each semester you save computes an SGPA, and the app keeps a
  running cumulative CGPA across all saved semesters.
- **Attendance**: percentage per subject, plus a note on how many classes
  you need to attend (if below 75%) or can safely miss (if at/above 75%)
  to stay at the 75% threshold — adjust that threshold in `main.py` if your
  college uses a different cutoff.
- **Timetable**: one editable weekly grid per user (Mon–Sat, 9 AM–4 PM by
  default — edit the `DAYS` / `SLOTS` lists in `main.py` to change it).

## Extending it further

Ideas if you want to keep building:
- Exam countdown / calendar view
- File upload for notes instead of just Drive links (would need cloud
  storage like AWS S3 or Cloudinary)
- Email/SMS notifications for reminders (e.g. via Twilio, which you've
  used before)
- Charts (Chart.js) for CGPA trend across semesters and attendance history
