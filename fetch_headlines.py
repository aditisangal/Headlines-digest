import os
import json
import feedparser
import requests

# 1. LOAD OLD HEADLINES (Memory)
old_headlines_file = "headlines_cache.json"
old_data = {}
if os.path.exists(old_headlines_file):
    with open(old_headlines_file, "r") as f:
        old_data = json.load(f)

# 2. FETCH NEW HEADLINES
new_data = {}
feeds = {
    "NYT": "https://rss.nytimes.comTo use Google Gemini via the `requests` library, you need to use the Google AI Studio endpoint. The structure is slightly different from OpenAI: the API key is passed as a URL parameter,/services/xml/rss/nyt/HomePage.xml",
    "WSJ": "https://feeds.a.dj.com/rss/RSS and the payload uses a `contents` and `parts` hierarchy.

### The Gemini Python Script
This script uses `gemini-1.5-flash` (WorldNews.xml" 
}

for pub, url in feeds.items():
    feed = feedparser.parse(url)
    new_data[pub] = [entry.title for entry in feed.entries[:10]]

# 3. GENERATE AI TOPLINE COMPARISON VIA GEMINI RESTwhich is fast and has a generous free tier) to analyze the news shift.
```python
import os
import json
import feedparser
import requests

# 1. LOAD OLD HEADLINES (Memory)
old_headlines_file = "headlines_cache.json"
old_data = {}
if os.path.exists(old_headlines_file):
    with open(old_headlines_file, "r") as f:
        old_data = json.load(f)

# 2. FETCH NEW HEADLINES
new_data = {}
feeds = {
    "NYT": "[https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml](https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml)",
    "BBC": "[https://feeds.bbci.co.uk/news/rss.xml](https://feeds.bbci.co.uk/news/rss.xml)"
}

for pub, url in feeds.items():
    feed = feedparser.parse(url)
    new_data[pub] = [entry.title for entry in feed.entries[:10]]

# 3. GENERATE AI TOPLINE VIA GEMINI API
api_key = os.environ.get("GEMINI_API_KEY")
toplines = {}

if api_key:
    # Google Gemini REST Endpoint
    # Using gemini-1.5-flash for speed and cost-efficiency
    model_id = "gemini-1.5-flash"
    url = f"[https://generativelanguage.googleapis.com/v1beta/models/](https://generativelanguage.googleapis.com/v1beta/models/){model_id}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}

    for pub in new_data:
        current_headlines = "\n".join(new_data[pub])
        previous_headlines = "\n".join(old_data.get(pub, ["No previous data available."]))
        
        prompt_text = f"""
        Compare the previous headlines for {pub} with the current ones.
        Identify how the editorial focus or primary news story has shifted.
        Write a single, punchy, one-sentence summary.
        
        PREVIOUS:
        {previous_headlines}
        
        CURRENT:
        {current_headlines}
        """

        # Gemini's specific JSON structure
        payload = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "maxOutputTokens": 100
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            res_json = response.json()
            
            # Extract text from Gemini's nested response structure
