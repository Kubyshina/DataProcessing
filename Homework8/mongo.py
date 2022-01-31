from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['insta']

insta = db.insta

# Пользователи, на которых подписан пользователь 47469340211
for user in insta.find({"user_id": "47469340211", "following_id": {"$exists": True}}):
    pprint(user)

print(insta.count_documents({"user_id": "47469340211", "following_id": {"$exists": True}}))

# Пользователи, которые подписаны на пользователя 47469340211
for user in insta.find({"user_id": "47469340211", "follower_id": {"$exists": True}}):
    pprint(user)

print(insta.count_documents({"user_id": "47469340211", "follower_id": {"$exists": True}}))
