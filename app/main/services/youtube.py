import requests
import re
import random
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

API_KEY = "AIzaSyAVZhXNtFnRkq0Dzx8WZLTd4hxRo-w98q4"

def get_channel_id(api_key, channel_input):
    youtube = build("youtube", "v3", developerKey=api_key)
    parsed_url = urlparse(channel_input)
    if parsed_url.netloc == "www.youtube.com" and parsed_url.path == "/channel":
        query_params = parse_qs(parsed_url.query)
        return query_params.get("channel_id", [None])[0]
    search_response = youtube.search().list(
        q=channel_input,
        type="channel",
        part="id"
    ).execute()
    channel_id = search_response.get("items", [])[0]["id"]["channelId"] if search_response.get("items") else None
    return channel_id

def get_channel_info(api_key, channel_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    channel_response = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    ).execute()
    channel_data = channel_response.get("items", [])[0]
    if not channel_data:
        return None
    snippet = channel_data.get("snippet", {})
    statistics = channel_data.get("statistics", {})
    return {
        "channel_title": snippet.get("title"),
        "channel_description": snippet.get("description"),
        "published_at": snippet.get("publishedAt"),
        "subscriber_count": statistics.get("subscriberCount"),
        "view_count": statistics.get("viewCount"),
        "video_count": statistics.get("videoCount"),
    }

def get_trending_hashtags(api_key, target_keyword):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.search().list(
        q=target_keyword,
        part='snippet',
        type='video',
        order='viewCount',
        maxResults=50
    )
    response = request.execute()
    trending_hashtags = []
    hashtags_fetched = 0
    for item in response['items']:
        video_id = item['id']['videoId']
        video_response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        if 'tags' in video_response['items'][0]['snippet']:
            trending_hashtags.extend(video_response['items'][0]['snippet']['tags'])
            hashtags_fetched += len(video_response['items'][0]['snippet']['tags'])
            if hashtags_fetched >= 50:
                break
    return trending_hashtags

def get_related_keywords(keyword):
    search_response = build('youtube', 'v3', developerKey=API_KEY).search().list(
        q=keyword,
        type='video',
        part='snippet',
        maxResults=50
    ).execute()
    related_keywords = []
    for item in search_response.get('items', []):
        snippet = item.get('snippet', {})
        title = snippet.get('title', '')
        related_keywords.extend(title.split())
    related_keywords = list(set([keyword.lower() for keyword in related_keywords]))
    return related_keywords

class RankTracker:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.rankings = {}

    def search_videos(self, query):
        request = self.youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=50
        )
        response = request.execute()
        return response['items']

    def track_video_rank(self, video_url, keyword):
        video_id = video_url.split('=')[-1]
        search_results = self.search_videos(keyword)

        for index, item in enumerate(search_results):
            if item['id']['videoId'] == video_id:
                return index + 1

        return None

    def update_rankings(self, video_url, keyword):
        position = self.track_video_rank(video_url, keyword)
        self.rankings[keyword] = position

    def get_rankings(self):
        return self.rankings

class TitleGenerator:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_popular_videos(self, keyword, count=5):
        request = self.youtube.search().list(
            q=keyword,
            part='snippet',
            type='video',
            order='viewCount',
            maxResults=count
        )
        response = request.execute()
        return response['items']

    def generate_titles(self, keyword, count=5):
        popular_videos = self.get_popular_videos(keyword, count)
        titles = [video['snippet']['title'] for video in popular_videos]
        return titles

def get_youtube_tags(keyword):
    youtube_search = build('youtube', 'v3', developerKey=API_KEY).search().list(
        q=keyword,
        part='snippet',
        maxResults=10
    ).execute()
    tags = []
    for item in youtube_search['items']:
        video_id = item['id']['videoId']
        video_details = build('youtube', 'v3', developerKey=API_KEY).videos().list(
            id=video_id,
            part='snippet'
        ).execute()
        if 'tags' in video_details['items'][0]['snippet']:
            tags.extend(video_details['items'][0]['snippet']['tags'])
    return tags


def extract_video_id(video_url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, video_url)
    if match:
        return match.group(1)
    return None

def get_video_tags(video_id):
    API_KEY = "AIzaSyAVZhXNtFnRkq0Dzx8WZLTd4hxRo-w98q4"
    if not API_KEY:
        raise ValueError("Missing YOUTUBE_API_KEY environment variable")
    
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={API_KEY}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'items' in data and len(data['items']) > 0 and 'tags' in data['items'][0]['snippet']:
            return data['items'][0]['snippet']['tags']
        else:
            return []
    except requests.exceptions.RequestException as e:
        print(f'Error fetching video tags: {e}')
        return None
