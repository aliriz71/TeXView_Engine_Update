from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)

# Names of database and collections according to the provided context
# Assuming the database is named 'texviewdb' and the collection is 'texview'
db = client.texviewdb  
collection_name = db["texview"]  
collection_user = db["users"]  # Collection for user data
collection_user_texviewpdf = db["texviewpdf"]  # Collection for user PDF data

print("DB is:", collection_name.database.name)
print("COL is:", collection_name.name)
print("COL is:", collection_user.name)
print("COL is", collection_user_texviewpdf.name)
# print("COUNT is", collection_name.count_documents({}))