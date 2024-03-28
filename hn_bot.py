import os
import requests
import schedule
import time

# Fetch the Discord webhook URL from an environment variable
webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

HN_TOP_STORIES_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json'
HN_ITEM_URL = 'https://hacker-news.firebaseio.com/v0/item/{}.json'

# File to track posted story IDs
POSTED_STORIES_FILE = 'posted_stories.txt'

def load_posted_stories():
    try:
        with open(POSTED_STORIES_FILE, 'r') as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

def save_posted_story(story_id):
    with open(POSTED_STORIES_FILE, 'a') as file:
        file.write(f"{story_id}\n")

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
    posted_stories = load_posted_stories()
    top_stories = fetch_top_stories(5)
    for story_id in top_stories:
        if str(story_id) in posted_stories:
            continue  # Skip this story if it has already been posted
        story = fetch_story_details(story_id)
        if story and 'url' in story:
            message = f"**{story['title']}**\n{story['url']}"
            post_to_discord(message)
            save_posted_story(story_id)

# Schedule to run every 60 minutes
schedule.every(1).minutes.do(fetch_and_post_news)

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)
