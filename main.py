import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# กำหนดโครงสร้างข้อมูลที่จะรับ-ส่ง
class LocationData(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime

# เชื่อมต่อ MongoDB
client = MongoClient(MONGO_URI)
db = client["gps_tracker_db"]
collection = db["locations"]

app = FastAPI()

# ตั้งค่า CORS เพื่ออนุญาตให้หน้าเว็บ React เข้ามาขอข้อมูลได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # อนุญาตทุกโดเมน (สำหรับการทดสอบ)
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint สำหรับ "รับ" ข้อมูลตำแหน่งใหม่
@app.post("/locations/")
async def create_location(location: LocationData):
    collection.insert_one(location.dict())
    return {"status": "success", "data": location}

# Endpoint สำหรับ "ส่ง" ข้อมูลตำแหน่งทั้งหมดไปให้หน้าเว็บ
@app.get("/locations/", response_model=List[LocationData])
async def get_all_locations():
    locations = list(collection.find({}, {"_id": 0}))
    return locations