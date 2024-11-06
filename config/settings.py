import os

# config/settings.py
# Remember to replace the placeholder values with your own Reddit API credentials.
USER_AGENT = f"SDS_textanalysis/1.0 (by /u/{os.getenv('REDDIT_USERNAME')})"
API_BASE_URL = "https://api.reddit.com"
RATE_LIMIT_DELAY = 2
