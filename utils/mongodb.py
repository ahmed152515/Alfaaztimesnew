from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Atlas connection string
MONGODB_URI = "mongodb+srv://bpocrm:bpocrm@bpocrm.585mc7w.mongodb.net/?retryWrites=true&w=majority&appName=BPOCRM"

try:
    # Create MongoDB client
    client = MongoClient(MONGODB_URI)
    db = client['AlfaazTimes']  # Specify the database name

    # Collections
    users = db['users']
    admins = db['admins']  # Separate collection for admins
    news = db['news']

    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

def get_user_by_username(username):
    """Get user by username"""
    try:
        user = users.find_one({'username': username})
        print(f"Found user in database: {user}")  # Debug print
        return user
    except Exception as e:
        print(f"Error finding user: {e}")
        return None

def get_admin_by_username(username):
    """Get admin by username"""
    try:
        admin = admins.find_one({'username': username})
        print(f"Found admin in database: {admin}")  # Debug print
        return admin
    except Exception as e:
        print(f"Error finding admin: {e}")
        return None

def verify_user(username, password):
    """Verify user credentials"""
    try:
        # First check if it's an admin
        admin = get_admin_by_username(username)
        if admin and admin['password'] == password:
            return {
                'success': True,
                'role': 'admin'
            }

        # If not admin, check regular user
        user = get_user_by_username(username)
        print(f"Verifying user: {user}")  # Debug print
        
        if not user:
            return {
                'success': False,
                'message': 'User not found'
            }
            
        if user['password'] != password:
            return {
                'success': False,
                'message': 'Invalid password'
            }
            
        # If we get here, the user exists and password matches
        return {
            'success': True,
            'role': user.get('role', 'user')  # Default to 'user' if role is not set
        }
    except Exception as e:
        print(f"Error verifying user: {e}")
        return {
            'success': False,
            'message': f'Error verifying credentials: {str(e)}'
        }

def create_admin(username, password):
    """Create a new admin user"""
    try:
        # Check if admin already exists
        if get_admin_by_username(username):
            return None, "Admin username already exists"
            
        admin = {
            'username': username,
            'password': password,
            'role': 'admin'
        }
        result = admins.insert_one(admin)
        return result, "Admin created successfully"
    except Exception as e:
        print(f"Error creating admin: {e}")
        return None, str(e)

def create_user(username, password, role='user'):
    """Create a new user"""
    try:
        # Check if user already exists
        if get_user_by_username(username):
            return None, "Username already exists"
            
        user = {
            'username': username,
            'password': password,
            'role': role
        }
        result = users.insert_one(user)
        return result, "User created successfully"
    except Exception as e:
        print(f"Error creating user: {e}")
        return None, str(e)

def update_user_password(username, new_password):
    """Update user password"""
    try:
        # Try updating admin first
        admin_result = admins.update_one(
            {'username': username},
            {'$set': {'password': new_password}}
        )
        if admin_result.modified_count > 0:
            return True

        # If not admin, try updating regular user
        user_result = users.update_one(
            {'username': username},
            {'$set': {'password': new_password}}
        )
        return user_result.modified_count > 0
    except Exception as e:
        print(f"Error updating password: {e}")
        return False 