#!/usr/bin/env python3
"""
X (Twitter) MCP Server
Simple Twitter integration - post, get, delete tweets
"""

import os
from typing import Any

import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("x")

# API Credentials
TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_KEY_SECRET: str = os.getenv("TWITTER_API_KEY_SECRET", "")
TWITTER_ACCESS_TOKEN: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET: str = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")

# Twitter OAuth1 for posting
twitter_auth = OAuth1(
    TWITTER_API_KEY,
    TWITTER_API_KEY_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET
)

# Thread separator
THREAD_SEPARATOR = "\n\n---\n\n"


# ============ Internal Functions ============

def _post_tweet(text: str, reply_to_id: str | None = None) -> dict[str, Any]:
    """Post a tweet using Twitter's official API v2"""
    url = "https://api.twitter.com/2/tweets"
    payload: dict[str, Any] = {"text": text}
    if reply_to_id:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to_id}

    resp = requests.post(url, auth=twitter_auth, json=payload)
    return {"status": resp.status_code, "data": resp.json()}


def _get_tweet(tweet_id: str) -> dict[str, Any]:
    """Get tweet details using Twitter's official API v2"""
    url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    params = {
        "tweet.fields": "public_metrics,created_at,author_id",
    }
    resp = requests.get(url, auth=twitter_auth, params=params)
    return {"status": resp.status_code, "data": resp.json()}


def _delete_tweet(tweet_id: str) -> dict[str, Any]:
    """Delete a tweet using Twitter's official API v2"""
    url = f"https://api.twitter.com/2/tweets/{tweet_id}"
    resp = requests.delete(url, auth=twitter_auth)
    return {"status": resp.status_code, "data": resp.json() if resp.text else {}}


def _get_me() -> dict[str, Any]:
    """Get authenticated user info"""
    url = "https://api.twitter.com/2/users/me"
    params = {
        "user.fields": "id,name,username,public_metrics"
    }
    resp = requests.get(url, auth=twitter_auth, params=params)
    return {"status": resp.status_code, "data": resp.json()}


# ============ MCP Tools ============

@mcp.tool()
def x_get_me() -> str:
    """Get authenticated user info to verify connection"""
    result = _get_me()

    if result["status"] != 200:
        return f"Error: {result['data']}"

    data = result["data"]["data"]
    metrics = data.get("public_metrics", {})

    return f"""Authenticated as: @{data['username']}
Name: {data['name']}
ID: {data['id']}
Followers: {metrics.get('followers_count', 'N/A')}
Following: {metrics.get('following_count', 'N/A')}
Tweets: {metrics.get('tweet_count', 'N/A')}"""


@mcp.tool()
def x_post_tweet(text: str) -> str:
    """
    Post a single tweet.

    Args:
        text: Tweet content (max 280 characters)

    Returns:
        Tweet ID and URL on success, error message on failure
    """
    if len(text) > 280:
        return f"Error: Tweet too long ({len(text)} chars). Max 280."

    result = _post_tweet(text)

    if result["status"] != 201:
        return f"Error posting tweet: {result['data']}"

    tweet_id = result["data"]["data"]["id"]
    return f"Tweet posted!\nID: {tweet_id}\nURL: https://twitter.com/i/status/{tweet_id}"


@mcp.tool()
def x_post_thread(text: str) -> str:
    """
    Post a thread. Tweets are separated by '\\n\\n---\\n\\n'.

    Args:
        text: Thread content with tweets separated by \\n\\n---\\n\\n

    Returns:
        List of tweet IDs and URLs on success, error message on failure

    Example:
        x_post_thread("1/ First tweet\\n\\n---\\n\\n2/ Second tweet\\n\\n---\\n\\n3/ Third tweet")
    """
    tweets = [t.strip() for t in text.split(THREAD_SEPARATOR) if t.strip()]

    if len(tweets) < 2:
        return "Error: Thread must have at least 2 tweets. Use '\\n\\n---\\n\\n' as separator."

    # Validate lengths
    for i, tweet in enumerate(tweets):
        if len(tweet) > 280:
            return f"Error: Tweet {i+1} too long ({len(tweet)} chars). Max 280."

    posted_ids: list[str] = []
    reply_to: str | None = None

    for i, tweet in enumerate(tweets):
        result = _post_tweet(tweet, reply_to_id=reply_to)

        if result["status"] != 201:
            return f"Error posting tweet {i+1}: {result['data']}\nPosted so far: {posted_ids}"

        tweet_id = result["data"]["data"]["id"]
        posted_ids.append(tweet_id)
        reply_to = tweet_id

    urls = [f"https://twitter.com/i/status/{tid}" for tid in posted_ids]

    return f"""Thread posted! ({len(posted_ids)} tweets)
IDs: {posted_ids}
First tweet: {urls[0]}"""


@mcp.tool()
def x_get_tweet(tweet_id: str) -> str:
    """
    Get tweet details and metrics.

    Args:
        tweet_id: The tweet ID to fetch

    Returns:
        Tweet details including text and metrics
    """
    result = _get_tweet(tweet_id)

    if result["status"] != 200:
        return f"Error: {result['data']}"

    data = result["data"]["data"]
    metrics = data.get("public_metrics", {})

    return f"""Tweet ID: {data['id']}
Text: {data.get('text', 'N/A')}
Created: {data.get('created_at', 'N/A')}

Metrics:
- Likes: {metrics.get('like_count', 0)}
- Retweets: {metrics.get('retweet_count', 0)}
- Replies: {metrics.get('reply_count', 0)}
- Impressions: {metrics.get('impression_count', 0)}
- Quotes: {metrics.get('quote_count', 0)}
- Bookmarks: {metrics.get('bookmark_count', 0)}"""


@mcp.tool()
def x_delete_tweet(tweet_id: str) -> str:
    """
    Delete a tweet.

    Args:
        tweet_id: The tweet ID to delete

    Returns:
        Success or error message
    """
    result = _delete_tweet(tweet_id)

    if result["status"] != 200:
        return f"Error deleting tweet: {result['data']}"

    return f"Tweet {tweet_id} deleted successfully."


# ============ Entry Point ============

if __name__ == "__main__":
    mcp.run()
