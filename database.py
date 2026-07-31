"""
MongoDB Connection
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from config import MONGO_URI

try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    client.admin.command("ping")

    db = client.get_default_database()

    # Collections
    users_collection = db["users"]
    medicines_collection = db["medicines"]

    print("MongoDB Connected Successfully")

except ConnectionFailure as error:

    print(f"Database Connection Failed\n{error}")

    exit()