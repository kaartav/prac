from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

DB_PASS = os.getenv("DB_PASSWORD")
uri = f"mongodb+srv://kaartav_db_user_practice:{DB_PASS}@cluster0.cbli1uw.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi("1"))
db = client.auth_db
users_collection = db.users
conversations_collection = db.conversations
