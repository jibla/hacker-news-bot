import os
import requests
import schedule
import time
import sqlite3

# Environment variables
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
schedule_period = int(os.getenv('SCHEDULE_PERIOD', '60'))
fetch_top_stories_amount = int(os.getenv('FETCH_TOP_STORIES_AMOUNT', '5'))
storage_type = os.getenv('STORAGE', 'local')

# Constants for API and file/database paths
HN_TOP_STORIES_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json'
HN_ITEM_URL = 'https://hacker-news.firebaseio.com/v0/item/{}.json'
POSTED_STORIES_FILE = 'posted_stories.txt'
DATABASE_FILE = '/app/data/posted_stories.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute('''CREATE TABLE IF NOT EXISTS posted_stories (story_id TEXT PRIMARY KEY)''')
    return conn

def save_posted_story_db(story_id):
    with get_db_connection() as conn:
        conn.execute("INSERT INTO posted_stories (story_id) VALUES (?)", (story_id,))

def is_story_posted_db(story_id):
    with get_db_connection() as conn:
        result = conn.execute("SELECT story_id FROM posted_stories WHERE story_id = ?", (story_id,)).fetchone()
    return result is not None

def save_posted_story(story_id):
    if storage_type == 'database':
        save_posted_story_db(story_id)
    else:
        with open(POSTED_STORIES_FILE, 'a') as file:
            file.write(f"{story_id}\n")

def is_story_posted(story_id):
    if storage_type == 'database':
        return is_story_posted_db(story_id)
    else:
        if not os.path.exists(POSTED_STORIES_FILE):
            return False
        with open(POSTED_STORIES_FILE, 'r') as file:
            return story_id in file.read().splitlines()

def fetch_top_stories(limit=5):
    response = requests.get(HN_TOP_STORIES_URL)
    story_ids = response.json()[:limit]
    return story_ids

def fetch_story_details(story_id):
    response = requests.get(HN_ITEM_URL.format(story_id))
    return response.json()

def post_to_discord(message):
    data = {
        "content": message,
        "username": "Hacker News Bot"
    }
    requests.post(webhook_url, json=data)

def fetch_and_post_news():
    posted_stories = set(filter(is_story_posted, requests.get(HN_TOP_STORIES_URL).json()))
    new_stories_found = 0

    for story_id in requests.get(HN_TOP_STORIES_URL).json():
        if new_stories_found >= fetch_top_stories_amount:
            break
        if story_id in posted_stories:
            continue
        story = fetch_story_details(story_id)
        if story and 'url' in story:
            message = f"**{story['title']}**\n{story['url']}"
            post_to_discord(message)
            save_posted_story(str(story_id))
            new_stories_found += 1

schedule.every(schedule_period).minutes.do(fetch_and_post_news)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
