# (ส่วน import เหมือนเดิม)
import os
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List
from datetime import datetime
from dotenv import load_dotenv

# (ส่วนโหลด .env และเชื่อมต่อ MongoDB เหมือนเดิม)
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["gps_tracker_db"]
collection = db["locations"]

# --- 1. อัปเกรด Model ให้รู้จัก username ---
class LocationData(BaseModel):
    username: str  # <--- เพิ่มเข้ามาใหม่
    latitude: float
    longitude: float
    timestamp: datetime

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. อัปเกรด Endpoint "รับข้อมูล" (สำหรับอนาคต) ---
@app.post("/locations/")
async def create_location(location: LocationData):
    collection.insert_one(location.dict())
    return {"status": "success", "data": location}

# --- 3. (ใหม่!) Endpoint "รับข้อมูลทีละเยอะๆ" สำหรับการอัปโหลดไฟล์ ---
@app.post("/locations/batch/{username}")
async def create_locations_batch(username: str, locations: List[LocationData]):
    # รับ List ของพิกัด แล้วเติม username ให้ทุกอัน
    docs_to_insert = []
    for loc in locations:
        doc = loc.dict()
        doc["username"] = username # เติม username ให้ถูกต้อง
        docs_to_insert.append(doc)
        
    if docs_to_insert:
        collection.insert_many(docs_to_insert)
    return {"status": "success", "inserted_count": len(docs_to_insert)}

# --- 4. (ใหม่!) Endpoint "ค้นหา" เส้นทางของผู้ใช้ ---
@app.get("/locations/user/{username}", response_model=List[LocationData])
async def get_locations_by_user(username: str):
    # ค้นหาในฐานข้อมูล โดยหา "username" ที่ตรงกัน และเรียงตามเวลา
    locations = list(collection.find(
        {"username": username}, 
        {"_id": 0}
    ).sort("timestamp", 1)) # 1 = เรียงจากเก่าไปใหม่
    return locations

# --- 5. (ของเดิม) Endpoint "ดูทั้งหมด" (เผื่อยังอยากใช้) ---
@app.get("/locations/", response_model=List[LocationData])
async def get_all_locations():
    locations = list(collection.find({}, {"_id": 0}))
    return locations