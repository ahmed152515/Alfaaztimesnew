from flask import Blueprint, jsonify, request, session
from pymongo import MongoClient
from datetime import datetime
from functools import wraps

admin = Blueprint('admin', __name__)

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://bpocrm:bpocrm@bpocrm.585mc7w.mongodb.net/AlfaazTimes?retryWrites=true&w=majority&appName=BPOCRM"
client = MongoClient(MONGO_URI)
db_mongo = client['AlfaazTimes']

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Unauthorized access'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Ticker Management
@admin.route('/api/admin/ticker', methods=['GET'])
def get_ticker():
    try:
        ticker = db_mongo.tickers.find_one() or {'content': []}
        return jsonify({'success': True, 'content': ticker.get('content', [])})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin.route('/api/admin/ticker', methods=['POST'])
@admin_required
def update_ticker():
    try:
        data = request.get_json()
        content = data.get('content', [])
        
        db_mongo.tickers.update_one(
            {},  # empty filter to match first document
            {'$set': {'content': content, 'updated_at': datetime.utcnow()}},
            upsert=True
        )
        
        return jsonify({'success': True, 'message': 'Ticker updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Categories Management
@admin.route('/api/admin/categories', methods=['GET'])
def get_categories():
    try:
        categories = list(db_mongo.categories.find({}, {'_id': 0}))
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin.route('/api/admin/categories', methods=['POST'])
@admin_required
def update_categories():
    try:
        data = request.get_json()
        categories = data.get('categories', [])
        new_category = data.get('newCategory', '').strip()

        # Update existing categories
        for cat_data in categories:
            db_mongo.categories.update_one(
                {'id': cat_data['id']},
                {'$set': {'active': cat_data['active']}}
            )

        # Add new category if provided
        if new_category:
            existing = db_mongo.categories.find_one({'name': new_category})
            if not existing:
                new_cat = {
                    'name': new_category,
                    'active': True,
                    'created_at': datetime.utcnow()
                }
                db_mongo.categories.insert_one(new_cat)

        return jsonify({'success': True, 'message': 'Categories updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Social Links Management
@admin.route('/api/admin/social-links', methods=['GET'])
def get_social_links():
    try:
        links = db_mongo.social_links.find_one() or {
            'facebook': '',
            'twitter': '',
            'instagram': ''
        }
        
        return jsonify({
            'success': True,
            'links': {
                'facebook': links.get('facebook', ''),
                'twitter': links.get('twitter', ''),
                'instagram': links.get('instagram', '')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin.route('/api/admin/social-links', methods=['POST'])
@admin_required
def update_social_links():
    try:
        data = request.get_json()
        links_data = data.get('links', {})
        
        db_mongo.social_links.update_one(
            {},  # empty filter to match first document
            {'$set': {
                'facebook': links_data.get('facebook', ''),
                'twitter': links_data.get('twitter', ''),
                'instagram': links_data.get('instagram', ''),
                'updated_at': datetime.utcnow()
            }},
            upsert=True
        )
        
        return jsonify({'success': True, 'message': 'Social links updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Footer Links Management
@admin.route('/api/admin/footer-links', methods=['GET'])
def get_footer_links():
    try:
        links = db_mongo.footer_links.find_one() or {
            'about': '/about',
            'contact': '/contact',
            'careers': '/careers'
        }
        
        return jsonify({
            'success': True,
            'links': {
                'about': links.get('about', '/about'),
                'contact': links.get('contact', '/contact'),
                'careers': links.get('careers', '/careers')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin.route('/api/admin/footer-links', methods=['POST'])
@admin_required
def update_footer_links():
    try:
        data = request.get_json()
        links_data = data.get('links', {})
        
        db_mongo.footer_links.update_one(
            {},  # empty filter to match first document
            {'$set': {
                'about': links_data.get('about', '/about'),
                'contact': links_data.get('contact', '/contact'),
                'careers': links_data.get('careers', '/careers'),
                'updated_at': datetime.utcnow()
            }},
            upsert=True
        )
        
        return jsonify({'success': True, 'message': 'Footer links updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500 