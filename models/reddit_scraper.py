# models/reddit_scraper.py
import requests
import time
import json
import os
from datetime import datetime, timedelta

def cache_results(func):
    def wrapper(self, subreddit, limit=100, cache=False, cache_duration_hours=24):
        cache_dir = '.cache'
        cache_file = os.path.join(cache_dir, f'{subreddit}_{limit}.json')
        
        if cache:
            os.makedirs(cache_dir, exist_ok=True)
            if os.path.exists(cache_file):
                modified_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                if datetime.now() - modified_time < timedelta(hours=cache_duration_hours):
                    with open(cache_file, 'r') as f:
                        return json.load(f)
        
        results = func(self, subreddit, limit)
        
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
    def get_subreddit_posts(self, subreddit, limit=100, cache=False, cache_duration_hours=24):
        posts = []
        after = None
        
        while len(posts) < limit:
            url = f"{self.base_url}/r/{subreddit}/new"
            params = {
                'limit': min(100, limit - len(posts)),
                'after': after
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            data = response.json()
            
            if 'data' not in data:
                break
                
            new_posts = data['data']['children']
            if not new_posts:
                break
                
            posts.extend([post['data'] for post in new_posts])
            after = new_posts[-1]['data']['name']
            
            time.sleep(2)  # Rate limiting
            
        return posts[:limit]