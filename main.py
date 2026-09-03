import os
import asyncio
from pyrogram import Client, filters
from motor.motor_asyncio import AsyncIOMotorClient

# إعدادات قاعدة البيانات (MongoDB Atlas)
MONGO_URL = "mongodb+srv://nyxydm_db_user:0Z6xRSQEeU8PTQp@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority"

db_client = AsyncIOMotorClient(MONGO_URL)
db = db_client["bot_maker_db"]
users_col = db["users"]

# بيانات المطور والحقوق
DEV_USERNAME = "@odox3"
CHANNEL_LINK = "@odox_6"

print("تم تشغيل صانع البوتات بنجاح بواسطة المطور " + DEV_USERNAME)
