# X (Twitter) MCP

A simple [Model Context Protocol](https://modelcontextprotocol.io/) server for Twitter/X. Post tweets, threads, and get metrics.

## Features

| Tool | Description |
|------|-------------|
| `x_get_me()` | Verify auth, get your profile info |
| `x_post_tweet(text)` | Post a single tweet (max 280 chars) |
| `x_post_thread(text)` | Post a thread (separate tweets with `\n\n---\n\n`) |
| `x_get_tweet(id)` | Get tweet details and metrics |
| `x_delete_tweet(id)` | Delete a tweet |

## Requirements

- Python 3.10+
- Twitter API credentials (OAuth 1.0a)

## Setup

### 1. Get Twitter API Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a project and app
3. Enable OAuth 1.0a with read and write permissions
4. Generate Access Token and Secret

### 2. Install

```bash
git clone https://github.com/arnaldo-delisio/x-mcp.git
cd x-mcp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
TWITTER_API_KEY=your_api_key
TWITTER_API_KEY_SECRET=your_api_key_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### 4. Add to Claude Code

Add to your `.mcp.json` or Claude Code config:

```json
{
  "mcpServers": {
    "x": {
      "command": "/path/to/x-mcp/venv/bin/python",
      "args": ["/path/to/x-mcp/server.py"],
      "env": {}
    }
  }
}
```

## Usage

### Post a tweet

```
x_post_tweet("Hello world!")
```

### Post a thread

Separate tweets with `\n\n---\n\n`:

```
x_post_thread("1/ First tweet here

---

2/ Second tweet continues

---

3/ Final tweet")
```

### Get tweet metrics

```
x_get_tweet("1234567890")
```

Returns likes, retweets, replies, impressions, quotes, and bookmarks.

## Roadmap

- [ ] Upload media (images, video)
- [ ] Quote tweet
- [ ] Reply to tweet
- [ ] Batch metrics

## License

MIT
