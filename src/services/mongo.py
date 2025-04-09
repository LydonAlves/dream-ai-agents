from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["dream_app"]  # use your actual database name here


def get_collection(name: str):
    return db[name]


# ✅ Test the connection
# if __name__ == "__main__":
#     try:
#         # Ping the server
#         client.admin.command("ping")
#         print("✅ Successfully connected to MongoDB!")

#         # List databases
#         print("📦 Databases:", client.list_database_names())

#         # List collections in your DB
#         print("📚 Collections in 'dream_app':", db.list_collection_names())

#     except Exception as e:
#         print("❌ Failed to connect to MongoDB:", e)
