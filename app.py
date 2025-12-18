from flask import Flask, render_template, request, jsonify
from scraper import FollowerScraper # Import our class
import logging
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
scraper = FollowerScraper() # Initialize global scraper instance

# --- ROUTES ---

import database

# Initialize DB
database.init_db()
DAILY_LIMIT = 50

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_target():
    data = request.json
    target_user = data.get('username')
    
    if not target_user:
        return jsonify({'error': 'Username is required'}), 400
        
    followers = scraper.get_followers(target_user, max_pages=2)
    
    # Mark users as 'followed' if they are in our history
    for user in followers:
        if database.is_already_followed(user['username']):
            user['already_followed'] = True
        else:
            user['already_followed'] = False

    return jsonify({
        'status': 'success',
        'mined_users': followers
    })

@app.route('/api/check_activity', methods=['POST'])
def check_activity():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({'error': 'Username required'}), 400
        
    is_active = scraper.profile_is_active(username)
    return jsonify({'username': username, 'is_active': is_active})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    count = database.get_today_follow_count()
    return jsonify({'daily_count': count, 'limit': DAILY_LIMIT})

@app.route('/api/follow', methods=['POST'])
def perform_follow():
    data = request.json
    target_user = data.get('username')
    cookies = data.get('cookies')
    
    if not target_user or not cookies:
        return jsonify({'error': 'Missing username or cookies'}), 400

    # 1. Check Daily Limit
    count = database.get_today_follow_count()
    if count >= DAILY_LIMIT:
        return jsonify({'status': 'error', 'message': f'Daily limit reached ({DAILY_LIMIT}/day). Safety first!'}), 400

    # 2. Check History
    if database.is_already_followed(target_user):
        return jsonify({'status': 'error', 'message': 'Already followed in the past.'}), 400

    logging.info(f"Action: Follow {target_user}")
    
    success, msg = scraper.follow_user(target_user, cookies)
    
    if success:
        # Log to DB
        database.log_follow(target_user)
        return jsonify({'status': 'success', 'message': f'Followed {target_user}'})
    else:
        return jsonify({'status': 'error', 'message': f'Follow failed: {msg}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
