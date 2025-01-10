import pymongo
import os

# Connect to MongoDB
client = pymongo.MongoClient(os.getenv(MONGODB_URI))
db = client["your_database_name"]
collection = db["your_collection_name"]
