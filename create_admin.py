from pymongo import MongoClient

MONGO_URI = "mongodb+srv://bpocrm:bpocrm@bpocrm.585mc7w.mongodb.net/AlfaazTimes?retryWrites=true&w=majority&appName=BPOCRM"
client = MongoClient(MONGO_URI)
db = client['AlfaazTimes']

admin = db.admins.find_one({'username': 'Alfaaztimes'})
if not admin:
    db.admins.insert_one({'username': 'Alfaaztimes', 'password': 'Alfaaztimes123'})
    print('Admin created successfully!')
else:
    print('Admin already exists.') 