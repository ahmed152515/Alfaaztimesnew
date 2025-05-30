from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
import os
import cloudinary
import cloudinary.uploader
from datetime import datetime
import json
from utils.mongodb import verify_user, update_user_password
from functools import wraps
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)  # For session management
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://bpocrm:bpocrm@bpocrm.585mc7w.mongodb.net/AlfaazTimes?retryWrites=true&w=majority&appName=BPOCRM"
client = MongoClient(MONGO_URI)
db_mongo = client['AlfaazTimes']

# Cloudinary configuration
cloudinary.config(
    cloud_name='drhqoykw6',
    api_key='429369422675559',
    api_secret='vTGubugguBQIiSv-JHOPnkWrb8E',
    secure=True
)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400

        print(f"Attempting login for username: {username}")  # Debug print
        
        result = verify_user(username, password)
        print(f"Login result: {result}")  # Debug print
        
        if result['success']:
            session['username'] = username
            session['role'] = result['role']
            print(f"Session set - username: {session['username']}, role: {session['role']}")  # Debug print
            return jsonify({
                'success': True,
                'role': result['role']
            })
        
        return jsonify({
            'success': False,
            'message': result.get('message', 'Invalid username or password')
        }), 401

    except Exception as e:
        print(f"Login error: {e}")  # Debug print
        return jsonify({
            'success': False,
            'message': f'An error occurred during login: {str(e)}'
        }), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/user')
@login_required
def user_panel():
    return render_template('user_panel.html')

@app.route('/politics')
@login_required
def politics():
    return render_template('politics.html')

@app.route('/business')
@login_required
def business():
    return render_template('business.html')

@app.route('/technology')
@login_required
def technology():
    return render_template('technology.html')

@app.route('/sports')
@login_required
def sports():
    return render_template('sports.html')

@app.route('/entertainment')
@login_required
def entertainment():
    return render_template('entertainment.html')

@app.route('/admin')
@login_required
def admin_panel():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    return render_template('admin_panel.html')

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    current_password = data.get('old_password')
    new_password = data.get('new_password')
    
    # Verify current password
    if not verify_user(session['username'], current_password)['success']:
        return jsonify({
            'success': False,
            'message': 'Current password is incorrect'
        })
    
    # Update password
    if update_user_password(session['username'], new_password):
        return jsonify({
            'success': True,
            'message': 'Password updated successfully'
        })
    
    return jsonify({
        'success': False,
        'message': 'Failed to update password'
    })

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    admin = db_mongo.admins.find_one({'username': username, 'password': password})
    if admin:
        session['username'] = username
        session['role'] = 'admin'
        return jsonify({'success': True, 'message': 'Admin login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/user/login', methods=['POST'])
def user_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = db_mongo.users.find_one({'username': username, 'password': password})
    if user:
        session['username'] = username
        session['role'] = 'user'
        return jsonify({'success': True, 'message': 'User login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/admin/upload_post', methods=['POST'])
def upload_post():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        heading = request.form.get('heading')
        caption = request.form.get('caption')
        post_type = request.form.get('post_type')  # 'image' or 'video'
        full_video_link = request.form.get('full_video_link')
        file = request.files.get('file')

        # Validate required fields
        if not file:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        if not heading:
            return jsonify({'success': False, 'message': 'Heading is required'}), 400
        if not caption:
            return jsonify({'success': False, 'message': 'Caption is required'}), 400
        if not post_type:
            return jsonify({'success': False, 'message': 'Post type is required'}), 400

        # Validate file type
        allowed_types = {'image/jpeg', 'image/png', 'image/gif', 'video/mp4'}
        if file.content_type not in allowed_types:
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400

        # Upload to Cloudinary
        resource_type = 'image' if post_type == 'image' else 'video'
        upload_result = cloudinary.uploader.upload(
            file,
            resource_type=resource_type,
            folder="alfaaz_times",  # Organize uploads in a folder
            use_filename=True,  # Use original filename
            unique_filename=True  # Add unique identifier to filename
        )
        
        url = upload_result['secure_url']
        
        # Create post document
        post = {
            'heading': heading,
            'caption': caption,
            'type': post_type,
            'url': url,
            'cloudinary_id': upload_result['public_id'],  # Store Cloudinary ID for future reference
            'full_video_link': full_video_link if post_type == 'video' else '',
            'created_at': datetime.utcnow(),
            'status': 'active'  # Add status field for future use
        }
        
        # Insert into MongoDB
        result = db_mongo.posts.insert_one(post)
        
        # Remove MongoDB's _id from response
        post.pop('_id', None)
        
        return jsonify({
            'success': True,
            'message': 'Post uploaded successfully',
            'post': post
        })
        
    except cloudinary.exceptions.Error as e:
        return jsonify({'success': False, 'message': f'Cloudinary upload error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error uploading post: {str(e)}'}), 500

@app.route('/admin/posts', methods=['GET'])
def get_admin_posts():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    posts = list(db_mongo.posts.find({}, {'_id': 0}))
    posts.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify({'success': True, 'posts': posts})

@app.route('/user/posts', methods=['GET'])
def get_user_posts():
    try:
        # Get active posts only
        posts = list(db_mongo.posts.find(
            {'status': 'active'},
            {'_id': 0}
        ).sort('created_at', -1))
        
        return jsonify({
            'success': True,
            'posts': posts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching posts: {str(e)}'
        }), 500

@app.route('/featured-posts')
def featured_posts():
    # Get the latest 3 posts as featured posts
    posts = list(db_mongo.posts.find({}, {'_id': 0}).sort('created_at', -1).limit(3))
    return jsonify({'success': True, 'posts': posts})

@app.route('/admin/home')
def admin_home():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    return render_template('admin_home.html', username=session.get('username'))

@app.route('/admin/home-cards')
@login_required
def admin_home_cards():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    return render_template('admin_home_cards.html')

@app.route('/api/home-cards', methods=['GET'])
def get_home_cards():
    try:
        cards = list(db_mongo.home_cards.find({}))
        # Convert ObjectId to string for JSON serialization
        for card in cards:
            card['_id'] = str(card['_id'])
        return jsonify({'success': True, 'cards': cards})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/home-cards', methods=['POST'])
@login_required
def create_home_card():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        card = {
            'sectionHeading': data.get('sectionHeading'),
            'title': data.get('title'),
            'description': data.get('description'),
            'imageUrl': data.get('imageUrl'),
            'layout': data.get('layout', 'square'),  # Default to square if not specified
            'created_at': datetime.utcnow()
        }
        
        result = db_mongo.home_cards.insert_one(card)
        card['_id'] = str(result.inserted_id)
        
        return jsonify({'success': True, 'card': card})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/home-cards/<card_id>', methods=['GET'])
def get_home_card(card_id):
    try:
        card = db_mongo.home_cards.find_one({'_id': ObjectId(card_id)})
        if card:
            card['_id'] = str(card['_id'])
            return jsonify({'success': True, 'card': card})
        return jsonify({'success': False, 'message': 'Card not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/home-cards/<card_id>', methods=['PUT'])
@login_required
def update_home_card(card_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.json
        card = {
            'sectionHeading': data.get('sectionHeading'),
            'title': data.get('title'),
            'description': data.get('description'),
            'imageUrl': data.get('imageUrl'),
            'layout': data.get('layout', 'square'),  # Default to square if not specified
            'updated_at': datetime.utcnow()
        }
        
        result = db_mongo.home_cards.update_one(
            {'_id': ObjectId(card_id)},
            {'$set': card}
        )
        
        if result.modified_count > 0:
            card['_id'] = card_id
            return jsonify({'success': True, 'card': card})
        return jsonify({'success': False, 'message': 'Card not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/home-cards/<card_id>', methods=['DELETE'])
@login_required
def delete_home_card(card_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        result = db_mongo.home_cards.delete_one({'_id': ObjectId(card_id)})
        if result.deleted_count > 0:
            return jsonify({'success': True, 'message': 'Card deleted successfully'})
        return jsonify({'success': False, 'message': 'Card not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/news')
def get_news():
    category = request.args.get('category')
    query = {'category': category} if category and category != 'All News' else {}
    articles = list(db_mongo.articles.find(query, {'_id': 0}))
    return jsonify({
        "success": True,
        "articles": articles
    })

@app.route('/api/trending')
def get_trending():
    # Sort articles by views and get top 5
    trending = list(db_mongo.articles.find({}, {'_id': 0}).sort('views', -1).limit(5))
    return jsonify({
        "success": True,
        "articles": trending
    })

@app.route('/api/most-read')
def get_most_read():
    # Sort articles by views and get top 5
    most_read = list(db_mongo.articles.find({}, {'_id': 0}).sort('views', -1).limit(5))
    return jsonify({
        "success": True,
        "articles": most_read
    })

@app.route('/api/ticker-news')
def get_ticker_news():
    # Get latest 5 articles for ticker
    ticker_news = list(db_mongo.articles.find({}, {'_id': 0}).sort('created_at', -1).limit(5))
    return jsonify({
        "success": True,
        "headlines": [
            {
                "id": article['id'],
                "title": article['title']
            } for article in ticker_news
        ]
    })

@app.route('/article/<int:article_id>')
def article(article_id):
    article = db_mongo.articles.find_one({'id': article_id}, {'_id': 0})
    if article:
        return render_template('article.html', article=article)
    return "Article not found", 404

@app.route('/api/home-cards/upload-image', methods=['POST'])
@login_required
def upload_home_card_image():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        # Validate file type
        allowed_types = {'image/jpeg', 'image/png', 'image/gif'}
        if file.content_type not in allowed_types:
            return jsonify({'success': False, 'message': 'Invalid file type. Only JPG, PNG, and GIF are allowed'}), 400
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file,
            folder="alfaaz_times/home_cards",
            use_filename=True,
            unique_filename=True,
            resource_type="image",
            transformation=[
                {'width': 800, 'height': 600, 'crop': 'fill'},
                {'quality': 'auto'},
                {'fetch_format': 'auto'}
            ]
        )
        
        return jsonify({
            'success': True,
            'url': upload_result['secure_url'],
            'public_id': upload_result['public_id']
        })
    except cloudinary.exceptions.Error as e:
        return jsonify({'success': False, 'message': f'Cloudinary upload error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error uploading image: {str(e)}'}), 500

@app.route('/api/admin/news', methods=['POST'])
@login_required
def admin_upload_news():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        youtube_link = request.form.get('youtubeLink')
        file = request.files.get('media')
        media_type = None
        media_url = None
        youtube_id = None
        if file:
            filename = secure_filename(file.filename)
            if file.mimetype.startswith('image/'):
                upload_result = cloudinary.uploader.upload(file, folder='alfaaz_news/images')
                media_type = 'image'
                media_url = upload_result['secure_url']
            elif file.mimetype.startswith('video/'):
                upload_result = cloudinary.uploader.upload(file, resource_type='video', folder='alfaaz_news/videos')
                media_type = 'video'
                media_url = upload_result['secure_url']
            else:
                return jsonify({'success': False, 'message': 'Unsupported file type'}), 400
        elif youtube_link:
            # Extract YouTube video ID
            import re
            match = re.search(r'(?:youtu\.be/|youtube\.com/(?:embed/|v/|watch\?v=|watch\?.+&v=))([\w-]{11})', youtube_link)
            if not match:
                return jsonify({'success': False, 'message': 'Invalid YouTube link'}), 400
            youtube_id = match.group(1)
            media_type = 'youtube'
            media_url = youtube_link
        else:
            return jsonify({'success': False, 'message': 'No media provided'}), 400
        article = {
            'title': title,
            'description': description,
            'category': category,
            'mediaType': media_type,
            'mediaUrl': media_url,
            'youtubeId': youtube_id,
            'created_at': datetime.utcnow()
        }
        db_mongo.articles.insert_one(article)
        return jsonify({'success': True, 'message': 'News uploaded successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/news', methods=['GET'])
@login_required
def admin_list_news():
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    news = list(db_mongo.articles.find().sort('created_at', -1))
    for n in news:
        n['_id'] = str(n['_id'])
        if 'created_at' in n:
            n['created_at'] = n['created_at'].strftime('%Y-%m-%d %H:%M')
    return jsonify({'success': True, 'news': news})

@app.route('/api/admin/news/<news_id>', methods=['DELETE'])
@login_required
def admin_delete_news(news_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    try:
        result = db_mongo.articles.delete_one({'_id': ObjectId(news_id)})
        if result.deleted_count == 1:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'News not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    # Use a different port and disable reloader for stability
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False) 