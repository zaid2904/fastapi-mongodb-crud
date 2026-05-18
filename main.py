# Import FastAPI class
# FastAPI is used to create API server
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware


# Import BaseModel from pydantic
# BaseModel helps us define request body structure
from pydantic import BaseModel


# Import AsyncIOMotorClient
# This is MongoDB async driver for Python
from motor.motor_asyncio import AsyncIOMotorClient


# Import ObjectId from bson
# MongoDB automatically creates _id in ObjectId format
from bson import ObjectId


# Create FastAPI app object
# This is the main application
app = FastAPI()

# Allow frontend to connect with backend
app.add_middleware(
    CORSMiddleware,

    # Allow all origins
    allow_origins=["*"],

    # Allow credentials
    allow_credentials=True,

    # Allow all methods
    allow_methods=["*"],

    # Allow all headers
    allow_headers=["*"],
)


# -----------------------------------------
# DATABASE CONNECTION
# -----------------------------------------

# MongoDB local connection URL
# 27017 is default MongoDB port
MONGO_URL = "mongodb://localhost:27017"


# Create MongoDB client
# This connects Python with MongoDB
client = AsyncIOMotorClient(MONGO_URL)


# Create database named "school"
db = client["school"]


# Create collection named "students"
collection = db["students"]


# -----------------------------------------
# PYDANTIC MODEL
# -----------------------------------------

# Create Student model
# This defines what data user must send
class Student(BaseModel):

    # Student name should be string
    name: str

    # Student age should be integer
    age: int

    # Student course should be string
    course: str


# -----------------------------------------
# HOME ROUTE
# -----------------------------------------

# Simple test route
@app.get("/")
async def home():

    # Return simple JSON response
    return {"message": "FastAPI MongoDB CRUD Working"}


# -----------------------------------------
# CREATE STUDENT
# -----------------------------------------

# POST method used to create data
@app.post("/students")
async def create_student(student: Student):

    # Convert Pydantic object into dictionary
    student_dict = student.dict()

    # Insert data into MongoDB collection
    result = await collection.insert_one(student_dict)

    # Return success message with inserted ID
    return {
        "message": "Student created successfully",
        "id": str(result.inserted_id)
    }


# -----------------------------------------
# GET ALL STUDENTS
# -----------------------------------------

# GET method used to fetch data
@app.get("/students")
async def get_students():

    # Create empty list
    students = []

    # Find all documents from MongoDB
    async for student in collection.find():

        # Convert ObjectId into string
        student["_id"] = str(student["_id"])

        # Add student into list
        students.append(student)

    # Return all students
    return students


# -----------------------------------------
# GET SINGLE STUDENT
# -----------------------------------------

# Get student using MongoDB ID
@app.get("/students/{id}")
async def get_student(id: str):

    # Find one student using ObjectId
    student = await collection.find_one({"_id": ObjectId(id)})

    # If student exists
    if student:

        # Convert ObjectId to string
        student["_id"] = str(student["_id"])

        # Return student data
        return student

    # If student not found
    return {"message": "Student not found"}


# -----------------------------------------
# UPDATE STUDENT
# -----------------------------------------

# PUT method used to update data
@app.put("/students/{id}")
async def update_student(id: str, student: Student):

    # Convert incoming data to dictionary
    updated_data = student.dict()

    # Update MongoDB document
    result = await collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": updated_data}
    )

    # Check if document updated
    if result.modified_count == 1:

        # Success response
        return {"message": "Student updated successfully"}

    # If no student found
    return {"message": "Student not found"}


# -----------------------------------------
# DELETE STUDENT
# -----------------------------------------

# DELETE method removes data
@app.delete("/students/{id}")
async def delete_student(id: str):

    # Delete student from MongoDB
    result = await collection.delete_one(
        {"_id": ObjectId(id)}
    )

    # Check if document deleted
    if result.deleted_count == 1:

        # Return success message
        return {"message": "Student deleted successfully"}

    # If no student found
    return {"message": "Student not found"}