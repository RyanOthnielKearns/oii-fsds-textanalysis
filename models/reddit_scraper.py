# models/reddit_scraper.py
import requests
import time
import json
import os
from datetime import datetime, timedelta

def cache_results(func):
    def wrapper(self, subreddit, limit=100, cache=False, cache_duration_hours=24, sort="new"):
        cache_dir = '.cache'
        cache_file = os.path.join(cache_dir, f'{subreddit}_{limit}.json')
        
        if cache:
            os.makedirs(cache_dir, exist_ok=True)
            if os.path.exists(cache_file):
                modified_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                if datetime.now() - modified_time < timedelta(hours=cache_duration_hours):
                    with open(cache_file, 'r') as f:
                        return json.load(f)
        
        results = func(self, subreddit, limit, sort)
        
        if cache:
            with open(cache_file, 'w') as f:
                json.dump(results, f)
        
        return results
    return wrapper


class RedditScraper:
    def __init__(self, user_agent):
        self.headers = {'User-Agent': user_agent}
        self.base_url = "https://api.reddit.com"
    
    @cache_results
    def get_subreddit_posts(self, subreddit, limit=100, sort="new"): 
        """
        Fetches posts from a specified subreddit.
        Args:
            subreddit (str): The name of the subreddit to fetch posts from.
            limit (int, optional): The maximum number of posts to fetch. Defaults to 100.
            cache (bool, optional): Whether to cache the results. Defaults to False.
            cache_duration_hours (int, optional): The duration to cache the results in hours. Defaults to 24.
            sort (str, optional): The sorting method for posts. Defaults to 'new'.
        Returns:
            list: A list of posts from the specified subreddit.
        """
        url = f"{self.base_url}/r/{subreddit}/{sort}"
        print(f"Fetching posts from {url}")
        
        params = {'limit': limit}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # Debug print
            print(f"Response keys: {data.keys()}")
            if 'data' in data:
                posts = []
                for post in data['data']['children']:
                    post_data = post['data']
                    posts.append({
                        'id': post_data.get('id'),
                        'title': post_data.get('title'),
                        'selftext': post_data.get('selftext'),
                        'author': post_data.get('author'),
                        'score': post_data.get('score'),
                        'created_utc': post_data.get('created_utc'),
                        'num_comments': post_data.get('num_comments'),
                        'url': post_data.get('url')
                    })
                return posts
        return []
    
    
    def get_post_comments(self, post_id):
        """Get comments for a specific post."""
        url = f"{self.base_url}/comments/{post_id}"
        
        print(f"Fetching comments from {url}")
        
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
        
            comments_data = response.json()
            if len(comments_data) > 1 and 'data' in comments_data[1]:
                return self.parse_comments(comments_data[1]['data']['children'], post_id)
        return []


    def parse_comments(self, comments, post_id, parent_id=None):
        parsed_comments = []
        for comment in comments:
            if 'data' in comment:
                comment_data = comment['data']
                parsed_comments.append({
                    'comment_id': comment_data.get('id'),
                    'parent_id': parent_id,
                    'post_id': post_id,
                    'author': comment_data.get('author'),
                    'body': comment_data.get('body')
                })
                if 'replies' in comment_data and comment_data['replies']:
                    parsed_comments.extend(self.parse_comments(comment_data['replies']['data']['children'], post_id, comment_data.get('id')))
        return parsed_comments