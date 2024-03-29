# Hacker News Bot

This is a simple Python script for a Discord and Slack bot, designed to fetch the latest news from Hacker News (HN) and post it to a specified Discord/Slack channel via webhooks. The bot is optimized for Docker deployment, offers different data storages (local files or SQLite) to track which news stories have been posted.

## How It Works

1. Fetches the top X news stories, from Hacker News top stories API, at a regular interval.
2. Checks against a stored list of already-posted stories, individually for Discord and Slack and if a story is not in the list, it is considered new, otherwise, bot tries to find next new story.
3. Post these new stories to the Discord/Slack channel linked through the provided webhook URL.

## Running Locally

To run the bot locally, you will need either Python directly or Docker for containerized deployment.

### Environment Variables

- `DISCORD_WEBHOOK_URL`: The webhook URL for the Discord channel where news will be posted.
- `SCHEDULE_PERIOD`: The frequency (in minutes) at which the bot fetches and posts news.
- `FETCH_TOP_STORIES_AMOUNT`: The number of top stories the bot should fetch and attempt to post at each interval.
- `STORAGE`: Specifies the method for tracking posted stories (`local` for file storage, `database` for SQLite).


### Running with Docker

    ```shell
    docker run
     -e DISCORD_WEBHOOK_URL="your_webhook_url_here"
     -e SLACK_WEBHOOK_URL="your_webhook_url_here"
     -e SCHEDULE_PERIOD=60
     -e FETCH_TOP_STORIES_AMOUNT=5
     -e STORAGE=local
     jibla/hn-bot
    ```

You can also build it from source using the Dockerfile:

    ```shell
    docker build -t hn-bot .
    ```

### Running with Python

1. **Install Dependencies**:
   ```shell
   pip install requests schedule sqlite3
    ```
2. **Set the required environment variables in your terminal**:
    ```shell
    export DISCORD_WEBHOOK_URL="your_webhook_url_here"
    export SCHEDULE_PERIOD=60
    export FETCH_TOP_STORIES_AMOUNT=5
    export STORAGE=local  # Or 'database'
    ```
3. **Run the script**:
    ```shell
    python hn_bot.py
    ```



