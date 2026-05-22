import os
import feedparser

# 1. DEFINE SECURE, STABLE FEEDS
feeds = {
    "NYT": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "BBC": "https://feeds.bbci.co.uk/news/rss.xml"
}

# 2. FETCH HEADLINES
dashboard_data = {}
for pub, url in feeds.items():
    try:
        feed = feedparser.parse(url)
        # Safely grab titles, fallback to empty list if feed is down
        dashboard_data[pub] = [entry.title for entry in feed.entries[:10]] if feed.entries else []
    except Exception as e:
        print(f"Warning: Could not parse {pub}: {e}")
        dashboard_data[pub] = []

# 3. BUILD FRESH INDEX.HTML FROM SCRATCH
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Headlines Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }
        h1 { border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .pub-section { margin-bottom: 40px; }
        h2 { color: #0066cc; }
        ul { padding-left: 20px; }
        li { margin-bottom: 8px; line-height: 1.4; }
    </style>
</head>
<body>
    <h1>Live Headlines Dashboard</h1>
"""

# Dynamically inject the parsed headings into the markup string
for pub, headlines in dashboard_data.items():
    html_content += f"<div class='pub-section'><h2>{pub}</h2>"
    if headlines:
        html_content += "<ul>"
        for title in headlines:
            # Clean quotes to ensure the HTML string doesn't break
            safe_title = title.replace('"', '&quot;').replace("'", "&#39;")
            html_content += f"<li>{safe_title}</li>"
        html_content += "</ul>"
    else:
        html_content += "<p><em>No headlines available at this time.</em></p>"
    html_content += "</div>"

html_content += """
</body>
</html>
"""

# Overwrite or create index.html right in the runner workspace
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Success: index.html rebuilt perfectly.")
