# Hacker News Discord Bot

## About This Repository

This repository hosts a Python script for a Discord bot designed to fetch the latest news from Hacker News (HN) and post it to a specified Discord channel via webhooks. The bot is optimized for Docker deployment, offering flexibility in data storage methods between local file storage and an SQLite database to track which news stories have been posted, ensuring no duplicates.

## How It Works

The bot is programmed to:

1. Fetch the top Y news stories from Hacker News at a regular interval, as specified by the `FETCH_TOP_STORIES_AMOUNT` environment variable.
2. Check against a stored list of already-posted stories to identify which stories are new.
3. Post these new stories to the Discord channel linked through the provided webhook URL.
4. Update the stored list with the IDs of the newly posted stories, ensuring no story is posted more than once.

### Logic Summary

- **Scheduled Fetching**: Periodically, every X minutes (defined by `SCHEDULE_PERIOD`), the bot queries Hacker News for the latest top Y stories.
- **Unposted Stories Identification**: It filters these stories to find those that have not yet been posted, according to its stored records.
- **Discord Posting**: New, unposted stories are shared to the designated Discord channel.
- **Records Update**: The list or database of posted stories is updated to include the new posts.

## Running Locally

To run the bot locally, you will need either Python directly or Docker for containerized deployment.

### Environment Variables

- `DISCORD_WEBHOOK_URL`: The webhook URL for the Discord channel where news will be posted.
- `SCHEDULE_PERIOD`: The frequency (in minutes) at which the bot fetches and posts news.
- `FETCH_TOP_STORIES_AMOUNT`: The number of top stories the bot should fetch and attempt to post at each interval.
- `STORAGE`: Specifies the method for tracking posted stories (`local` for file storage, `database` for SQLite).

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

### Running with Docker

1. **Build**:

    ```shell
    docker build -t hn-discord-bot .
    ```
2. **Run the container with the necessary environment variables:**:

    ```shell
    docker run
     -e DISCORD_WEBHOOK_URL="your_webhook_url_here"
     -e SCHEDULE_PERIOD=60
     -e FETCH_TOP_STORIES_AMOUNT=5
     -e STORAGE=local
     hn-discord-bot
    ```
Replace 'YourWebhookURL' with your actual Discord webhook URL and adjust other environment variables as needed.


