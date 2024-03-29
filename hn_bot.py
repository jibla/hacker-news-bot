import os
import requests
import schedule
import time

webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
schedule_period = int(os.getenv('SCHEDULE_PERIOD', '60'))
fetch_top_stories_amount = int(os.getenv('FETCH_TOP_STORIES_AMOUNT', '5'))

HN_TOP_STORIES_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json'
HN_ITEM_URL = 'https://hacker-news.firebaseio.com/v0/item/{}.json'

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
    all_story_ids = requests.get(HN_TOP_STORIES_URL).json()
    new_stories_found = 0

    for story_id in all_story_ids:
        if new_stories_found >= fetch_top_stories_amount:
            break

        if str(story_id) in posted_stories:
            continue 

        story = fetch_story_details(story_id)
        if story and 'url' in story:
            message = f"**{story['title']}**\n{story['url']}"
            post_to_discord(message)
            save_posted_story(story_id)
            new_stories_found += 1

schedule.every(schedule_period).minutes.do(fetch_and_post_news)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
