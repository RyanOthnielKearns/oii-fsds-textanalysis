# main.py
from models.reddit_scraper import RedditScraper
from utils.text_processor import preprocess_text
from utils.analysis import analyze_vocabulary, tfidf_analyze_subreddit
from config.settings import USER_AGENT

def main():
    
    scraper = RedditScraper(USER_AGENT)
    posts = scraper.get_subreddit_posts("python", limit=100)
    
    df = create_posts_dataframe(posts)
    
    results = tfidf_analyze_subreddit(posts)
    

if __name__ == "__main__":
    main()