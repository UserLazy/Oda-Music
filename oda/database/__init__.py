from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from oda.config import MONGO_DB_URI


MONGODB_CLI = MongoClient(MONGO_DB_URI)
db = MONGODB_CLI.wbb
