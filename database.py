"""
MongoDB Connection and Collection Initializer
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from config import MONGO_URI

try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    # Test connection
    client.admin.command("ping")

    db = client.get_default_database()

    # Core Collections
    users_collection = db["users"]
    medicines_collection = db["medicines"]
    activity_logs_collection = db["activity_logs"]
    reports_collection = db["reports"]

    print("MongoDB Connected Successfully")

except ConnectionFailure as error:
    print(f"Database Connection Failed\n{error}")
    exit(1)