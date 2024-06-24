from flask import request, jsonify
from app.main import main
from app.main.services.youtube import (
    get_channel_id, get_channel_info, get_trending_hashtags, 
    get_related_keywords, RankTracker, TitleGenerator, 
    get_youtube_tags, extract_video_id, get_video_tags
)

API_KEY = "AIzaSyBw-ER74Nr2LAdpnWnG0xL9ZOgbWdExYZY"
rank_tracker = RankTracker(API_KEY)
title_generator = TitleGenerator(API_KEY)

@main.route('/channel-audit', methods=['POST'])
def channel_audit():
    if request.is_json:
        data = request.get_json()
        channel_id = data.get('channel_id')
    else:
        channel_id = request.form.get('channel_id')
    if not channel_id:
        return jsonify({"error": "Missing 'channel_input' in request data."}), 400
    channel_id = get_channel_id(API_KEY, channel_id)
    if channel_id:
        channel_info = get_channel_info(API_KEY, channel_id)
        if channel_info:
            return jsonify(channel_info)
        else:
            return jsonify({"error": "Channel information not found."}), 404
    else:
        return jsonify({"error": "Invalid channel URL or name."}), 400

@main.route('/hashtag-generator', methods=['POST'])
def hashtag_generator():
    target_keyword = request.json.get('target_keyword')
    if not target_keyword:
        return jsonify({"error": "Missing 'target_keyword' in request data."}), 400
    hashtags = get_trending_hashtags(API_KEY, target_keyword)
    if hashtags:
        hashtags_with_hash = ['#' + tag for tag in hashtags]
        return jsonify({"target_keyword": target_keyword, "hashtags": hashtags_with_hash})
    else:
        return jsonify({"error": "No hashtags found for the given keyword."}), 404

@main.route('/keyword-generator', methods=['POST'])
def keyword_generator():
    keyword = request.json.get('keyword')
    if not keyword:
        return jsonify({'error': 'Keyword parameter is required'})
    related_keywords = get_related_keywords(keyword)
    response = {
        'keyword': keyword,
        'related_keywords': related_keywords
    }
    return jsonify(response)

@main.route('/youtube-rank-tracker', methods=['POST'])
def youtube_rank_tracker():
    data = request.get_json()
    video_url = data.get('video_url')
    keyword = data.get('keyword')
    
    if video_url and keyword:
        rank_tracker.update_rankings(video_url, keyword)
        rankings = rank_tracker.get_rankings()
        return jsonify(rankings)
    else:
        return jsonify({'error': 'Missing video_url or keyword'}), 400

@main.route('/title-generator', methods=['POST'])
def title_generator_endpoint():
    if request.method == 'POST':
        keyword = request.form['keyword']
        generated_titles = title_generator.generate_titles(keyword, count=5)
        return jsonify(generated_titles=generated_titles)
    return jsonify(message="Please send a POST request with 'keyword' parameter.")

@main.route('/tags-generator', methods=['POST'])
def tags_generator():
    keyword = request.json.get("keyword")
    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400
    generated_tags = get_youtube_tags(keyword)
    return jsonify({"keyword": keyword, "tags": generated_tags})

@main.route('/extract-tags', methods=['POST'])
def extract_tags():
    data = request.get_json()
    if data and 'video_url' in data:
        video_url = data['video_url']
        video_id = extract_video_id(video_url)
        
        if video_id:
            tags = get_video_tags(video_id)
            
            if tags is not None:
                return jsonify({'tags': tags}), 200
            else:
                return jsonify({'error': 'Unable to fetch tags for the video.'}), 400
        else:
            return jsonify({'error': 'Invalid YouTube video URL.'}), 400
    else:
        return jsonify({'error': 'Missing video_url parameter.'}), 400
