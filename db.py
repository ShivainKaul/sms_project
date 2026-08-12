import certifi
from pymongo import MongoClient
from config import Config

_client = MongoClient(
    Config.MONGO_URI,
    serverSelectionTimeoutMS=5000,
    tlsCAFile=certifi.where(),
)
db = _client[Config.MONGO_DB_NAME]

# Collections used across the app
users_col = db["users"]
notes_col = db["notes"]
todos_col = db["todos"]
reminders_col = db["reminders"]
cgpa_col = db["cgpa_semesters"]
attendance_col = db["attendance"]
timetable_col = db["timetable"]


def init_indexes():
    """Create indexes once at startup. Safe to call every time the app boots."""
    users_col.create_index("email", unique=True)
    notes_col.create_index("user_id")
    todos_col.create_index("user_id")
    reminders_col.create_index("user_id")
    cgpa_col.create_index("user_id")
    attendance_col.create_index("user_id")
    timetable_col.create_index("user_id")
