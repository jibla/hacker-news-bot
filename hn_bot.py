import os
import requests
import schedule
import time
import sqlite3

# Environment variables
discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL', None)
slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL', None)
schedule_period = int(os.getenv('SCHEDULE_PERIOD', '60'))
fetch_top_stories_amount = int(os.getenv('FETCH_TOP_STORIES_AMOUNT', '5'))
storage_type = os.getenv('STORAGE', 'local')

# Constants for API and file/database paths
HN_TOP_STORIES_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json'
HN_ITEM_URL = 'https://hacker-news.firebaseio.com/v0/item/{}.json'
DISCORD_POSTED_STORIES_FILE = 'discord_posted_stories.txt'
SLACK_POSTED_STORIES_FILE = 'slack_posted_stories.txt'
DATABASE_FILE = '/app/data/posted_stories.db'

# Database functions if storage_type is 'database'
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute('''CREATE TABLE IF NOT EXISTS posted_stories (story_id TEXT, platform TEXT, PRIMARY KEY (story_id, platform))''')
    return conn

def save_posted_story_db(platform, story_id):
    with get_db_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO posted_stories (story_id, platform) VALUES (?, ?)", (story_id, platform))

def is_story_posted_db(platform, story_id):
    with get_db_connection() as conn:
        result = conn.execute("SELECT story_id FROM posted_stories WHERE story_id = ? AND platform = ?", (story_id, platform)).fetchone()
    return result is not None

# File-based functions if storage_type is 'local'
def save_posted_story_file(file_path, story_id):
    with open(file_path, 'a') as file:
        file.write(f"{story_id}\n")

def is_story_posted_file(file_path, story_id):
    if not os.path.exists(file_path):
        return False
    with open(file_path, 'r') as file:
        return story_id in file.read().splitlines()

# Wrapper functions to abstract away the storage details
def save_posted_story(platform, story_id):
    if storage_type == 'database':
        save_posted_story_db(platform, story_id)
    else:
        file_path = DISCORD_POSTED_STORIES_FILE if platform == 'discord' else SLACK_POSTED_STORIES_FILE
        save_posted_story_file(file_path, story_id)

def is_story_posted(platform, story_id):
    if storage_type == 'database':
        return is_story_posted_db(platform, story_id)
    else:
        file_path = DISCORD_POSTED_STORIES_FILE if platform == 'discord' else SLACK_POSTED_STORIES_FILE
        return is_story_posted_file(file_path, story_id)

# Fetch story details from Hacker News API
def fetch_story_details(story_id):
    response = requests.get(HN_ITEM_URL.format(story_id))
    return response.json()

# Helper function to post messages to Discord and Slack webhooks
def post_to_webhook(platform, url, message):
    if platform == 'discord':
        data = {"content": message, "username": "Hacker News Bot"}
    else:
        data = {"text": message}
    
    headers = {'Content-Type': 'application/json'}
    requests.post(url, json=data, headers=headers)

# The main function that fetches and posts the news
def fetch_and_post_news():
    for platform, webhook_url in (('discord', discord_webhook_url), ('slack', slack_webhook_url)):
        if not webhook_url:
            continue  # Skip if no webhook URL is provided for the platform

        new_stories_found = 0
        for story_id in requests.get(HN_TOP_STORIES_URL).json():
            if new_stories_found >= fetch_top_stories_amount:
                break

            if is_story_posted(platform, str(story_id)):
                continue  # Skip if the story has already been posted

            story = fetch_story_details(story_id)
            if story and 'url' in story:
                if platform == 'discord':
                    message = f"**{story['title']}**\n{story['url']}"
                else:  # slack
                    message = f"{story['title']}\n{story['url']}"
                post_to_webhook(platform, webhook_url, message)
                save_posted_story(platform, str(story_id))
                new_stories_found += 1

# Scheduling the job
schedule.every(schedule_period).minutes.do(fetch_and_post_news)

# The entry point for the script execution
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
