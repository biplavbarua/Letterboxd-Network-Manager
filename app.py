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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_target():
    data = request.json
    target_user = data.get('username')
    
    if not target_user:
        return jsonify({'error': 'Username is required'}), 400
        
    logging.info(f"Received request to analyze: {target_user}")
    
    # 1. Scrape Followers (Phase 1)
    # Limit to 1 page (25 users) for now to keep it fast for testing
    followers = scraper.get_followers(target_user, max_pages=1)
    
    # 2. Filter Active Users (Phase 2)
    # This loop is slow (1 request per user), so for the MVP demo, 
    # we might just return them all and let the UI show "Check Status" 
    # OR checking just the first 5 for speed.
    # Let's check status for ALL of them but limit the list size to 10 for speed safety.
    
    mined_users = []
    
    # Process only top 10 for demo speed (to avoid 30x 2sec delays)
    for user in followers[:10]:
        user['is_active'] = scraper.profile_is_active(user['username'])
        mined_users.append(user)
    
    return jsonify({
        'status': 'success',
        'mined_users': mined_users
    })

@app.route('/api/follow', methods=['POST'])
def perform_follow():
    data = request.json
    target_user = data.get('username')
    cookies = data.get('cookies')
    
    if not target_user or not cookies:
        return jsonify({'error': 'Missing username or cookies'}), 400
        
    logging.info(f"Action: Follow {target_user}")
    
    success, msg = scraper.follow_user(target_user, cookies)
    
    if success:
        return jsonify({'status': 'success', 'message': f'Followed {target_user}'})
    else:
        return jsonify({'status': 'error', 'message': f'Follow failed: {msg}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
