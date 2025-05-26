"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import os
from pathlib import Path
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client["mergington"]
activities_collection = db["activities"]

# Pre-populate activities if collection is empty
PREPOPULATED_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in local leagues",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball skills and play friendly matches",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and participate in school theater productions",
        "schedule": "Mondays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["charlotte@mergington.edu", "jack@mergington.edu"]
    },
    "Art Workshop": {
        "description": "Explore painting, drawing, and sculpture techniques",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Prepare for math competitions and solve challenging problems",
        "schedule": "Fridays, 2:00 PM - 3:30 PM",
        "max_participants": 16,
        "participants": ["ethan@mergington.edu", "isabella@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["noah@mergington.edu", "harper@mergington.edu"]
    }
}

def prepopulate_activities():
    if activities_collection.count_documents({}) == 0:
        for name, data in PREPOPULATED_ACTIVITIES.items():
            doc = data.copy()
            doc["_id"] = name
            activities_collection.insert_one(doc)

prepopulate_activities()

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    activities = {}
    for doc in activities_collection.find():
        name = doc["_id"]
        activities[name] = {
            "description": doc["description"],
            "schedule": doc["schedule"],
            "max_participants": doc["max_participants"],
            "participants": doc.get("participants", [])
        }
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    doc = activities_collection.find_one({"_id": activity_name})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")
    if email in doc.get("participants", []):
        raise HTTPException(status_code=400, detail="Student already signed up")
    if len(doc.get("participants", [])) >= doc["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")
    activities_collection.update_one(
        {"_id": activity_name},
        {"$push": {"participants": email}}
    )
    return {"message": f"Signed up {email} for {activity_name}"}


@app.post("/activities/{activity_name}/remove")
def remove_participant(activity_name: str, email: str):
    doc = activities_collection.find_one({"_id": activity_name})
    if not doc:
        raise HTTPException(status_code=404, detail="Activity not found")
    if email not in doc.get("participants", []):
        raise HTTPException(status_code=404, detail="Participant not found")
    activities_collection.update_one(
        {"_id": activity_name},
        {"$pull": {"participants": email}}
    )
    return {"message": f"Removed {email} from {activity_name}"}
