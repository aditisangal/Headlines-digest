import feedparser
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

FEEDS = [
    {"name": "The Atlantic",    "url": "https://www.theatlantic.com/feed/all/",                              "color": "#C8102E", "abbr": "ATL"},
    {"name": "The Economist",   "url": "https://www.economist.com/latest/rss.xml",                           "color": "#E3120B", "abbr": "ECO"},
    {"name": "New York Times",  "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",          "color": "#222222", "abbr": "NYT"},
    {"name": "NYT Magazine",    "url": "https://rss.nytimes.com/services/xml/rss/nyt/Magazine.xml",          "color": "#FF3A2F", "abbr": "MAG"},
    {"name": "The New Yorker",  "url": "https://www.newyorker.com/feed/everything",                          "color": "#D4001A", "abbr": "TNY"},
    {"name": "Intelligencer",   "url": "https://feeds.feedburner.com/nymag/intelligencer",                   "color": "#0057A8", "abbr": "INT"},
    {"name": "n+1",             "url": "https://www.nplusonemag.com/feed/",                                  "color": "#FF6B6B", "abbr": "N+1"},
    {"name": "Vox",             "url": "https://www.vox.com/rss/index.xml",                                  "color": "#FFDB00", "abbr": "VOX"},
    {"name": "Reason",          "url": "https://reason.com/feed/",                                           "color": "#003366", "abbr": "RSN"},
]

KEEP_DAYS = 7

# ── Fetch ─────────────────────────────────────────────────────────────────────

def fetch_feed(feed_config):
    cutoff = datetime.now(timezone.utc) - timedelta(days=KEEP_DAYS)
    articles = []
    try:
        parsed = feedparser.parse(feed_config["url"])
        for entry in parsed.entries:
            pub_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                pub_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

            if pub_date and pub_date < cutoff:
                continue

            title = entry.get("title", "").strip()
            link  = entry.get("link",  "").strip()

            if title and link:
                articles.append({
                    "title":    title,
                    "link":     link,
                    "date":     pub_date.strftime("%b %d") if pub_date else "",
                    "date_raw": pub_date.isoformat() if pub_date else "",
                })
    except Exception as e:
        print(f"  Failed to fetch {feed_config['name']}: {e}")
    return articles


def fetch_all():
    results = []
    for feed in FEEDS:
        print(f"  Fetching {feed['name']}...")
        articles = fetch_feed(feed)
        print(f"    -> {len(articles)} articles")
        results.append({**feed, "articles": articles, "count": len(articles)})
    return results


# ── HTML ──────────────────────────────────────────────────────────────────────

def generate_html(data):
    now   = datetime.now().strftime("%A, %B %d, %Y")
    total = sum(p["count"] for p in data)

    all_articles = []
    for pub in data:
        for art in pub["articles"]:
            all_articles.append({**art, "pub": pub["name"], "color": pub["color"], "abbr": pub["abbr"]})

    all_articles.sort(key=lambda x: x.get("date_raw", ""), reverse=True)

    filter_btns = '<button class="filter-btn active" data-pub="all">All</button>\n'
    for pub in data:
        filter_btns += f'<button class="filter-btn" data-pub="{pub["name"]}" style="--c:{pub["color"]}">{pub["abbr"]}</button>\n'

    tiles = ""
    for art in all_articles:
        title_escaped = art['title'].replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        tiles += f"""
        <a class="tile" href="{art['link']}" target="_blank" rel="noopener"
           data-pub="{art['pub']}" style="--accent:{art['color']}">
            <div class="tile-inner">
                <div class="tile-top">
                    <span class="tile-abbr">{art['abbr']}</span>
                    <span class="tile-date">{art['date']}</span>
                </div>
                <p class="tile-headline">{title_escaped}</p>
                <div class="tile-bar"></div>
            </div>
        </a>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Headlines</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,400&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        :root {{
            --bg: #0f0f0f; --surface: #181818; --border: #282828;
            --text: #efefef; --muted: #777; --dim: #444;
        }}
        body {{ background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; min-height: 100vh; }}

        .profile {{
            max-width: 960px; margin: 0 auto; padding: 40px 20px 0;
            display: flex; align-items: center; gap: 40px;
        }}
        .profile-avatar {{
            width: 80px; height: 80px; border-radius: 50%;
            background: linear-gradient(135deg, #C8102E, #0057A8, #FFDB00);
            flex-shrink: 0; display: flex; align-items: center; justify-content: center;
            font-family: 'Playfair Display', serif; font-size: 1.4rem; color: white; font-style: italic;
        }}
        .profile-info {{ flex: 1; }}
        .profile-name {{ font-size: 1.3rem; font-weight: 500; letter-spacing: -0.01em; margin-bottom: 10px; }}
        .profile-stats {{ display: flex; gap: 28px; margin-bottom: 10px; }}
        .stat-num {{ font-weight: 500; font-size: 1rem; display: block; }}
        .stat-label {{ font-size: 0.72rem; color: var(--muted); font-family: 'DM Mono', monospace; }}
        .profile-bio {{ font-size: 0.8rem; color: var(--muted); font-family: 'DM Mono', monospace; }}

        .divider {{ max-width: 960px; margin: 28px auto 0; border: none; border-top: 1px solid var(--border); }}

        .filters {{
            max-width: 960px; margin: 0 auto; padding: 16px 20px;
            display: flex; gap: 8px; overflow-x: auto; scrollbar-width: none;
        }}
        .filters::-webkit-scrollbar {{ display: none; }}
        .filter-btn {{
            background: var(--surface); border: 1px solid var(--border); border-radius: 20px;
            color: var(--muted); font-family: 'DM Mono', monospace; font-size: 0.7rem;
            letter-spacing: 0.06em; padding: 5px 12px; cursor: pointer; white-space: nowrap;
            transition: all 0.15s;
        }}
        .filter-btn:hover {{ color: var(--text); border-color: #555; }}
        .filter-btn.active {{ background: var(--c, var(--text)); border-color: var(--c, var(--text)); color: white; }}
        .filter-btn[data-pub="all"].active {{ background: var(--text); border-color: var(--text); color: var(--bg); }}

        .search-wrap {{ max-width: 960px; margin: 0 auto; padding: 0 20px 16px; }}
        #search {{
            width: 100%; background: var(--surface); border: 1px solid var(--border);
            border-radius: 8px; color: var(--text); font-family: 'DM Sans', sans-serif;
            font-size: 0.85rem; padding: 9px 14px; outline: none; transition: border-color 0.15s;
        }}
        #search:focus {{ border-color: #555; }}
        #search::placeholder {{ color: var(--dim); }}

        .grid {{
            max-width: 960px; margin: 0 auto; padding: 2px 20px 80px;
            display: grid; grid-template-columns: repeat(3, 1fr); gap: 3px;
        }}

        .tile {{
            aspect-ratio: 1 / 1; background: var(--surface); border: 1px solid var(--border);
            text-decoration: none; color: var(--text); display: flex; overflow: hidden;
            position: relative; transition: transform 0.15s, border-color 0.15s;
        }}
        .tile:hover {{ border-color: var(--accent); transform: scale(1.02); z-index: 2; }}
        .tile-inner {{
            padding: 12px; display: flex; flex-direction: column;
            justify-content: space-between; width: 100%; height: 100%;
        }}
        .tile-top {{ display: flex; justify-content: space-between; align-items: center; }}
        .tile-abbr {{ font-family: 'DM Mono', monospace; font-size: 0.62rem; letter-spacing: 0.1em; color: var(--accent); }}
        .tile-date {{ font-family: 'DM Mono', monospace; font-size: 0.6rem; color: var(--dim); }}
        .tile-headline {{
            font-family: 'Playfair Display', serif; font-size: clamp(0.7rem, 1.4vw, 0.95rem);
            font-weight: 700; line-height: 1.35; color: var(--text);
            display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical;
            overflow: hidden; flex: 1; margin: 8px 0;
        }}
        .tile-bar {{ height: 2px; background: var(--accent); border-radius: 1px; opacity: 0.6; }}
        .tile.hidden {{ display: none; }}

        @media (max-width: 600px) {{
            .profile {{ padding: 24px 16px 0; gap: 20px; }}
            .profile-avatar {{ width: 60px; height: 60px; font-size: 1rem; }}
            .grid {{ grid-template-columns: repeat(3, 1fr); gap: 2px; padding: 2px 8px 60px; }}
            .tile-inner {{ padding: 8px; }}
            .tile-headline {{ font-size: 0.65rem; -webkit-line-clamp: 3; }}
            .filters, .search-wrap {{ padding-left: 16px; padding-right: 16px; }}
        }}
    </style>
</head>
<body>
    <div class="profile">
        <div class="profile-avatar">H</div>
        <div class="profile-info">
            <div class="profile-name">headlines</div>
            <div class="profile-stats">
                <div class="stat"><span class="stat-num">{total}</span><span class="stat-label">stories</span></div>
                <div class="stat"><span class="stat-num">{len(data)}</span><span class="stat-label">sources</span></div>
                <div class="stat"><span class="stat-num">7d</span><span class="stat-label">window</span></div>
            </div>
            <div class="profile-bio">updated daily · {now}</div>
        </div>
    </div>
    <hr class="divider">
    <div class="filters">{filter_btns}</div>
    <div class="search-wrap"><input type="search" id="search" placeholder="Search headlines…" autocomplete="off"></div>
    <div class="grid" id="grid">{tiles}</div>
    <script>
        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const pub = btn.dataset.pub;
                document.getElementById('search').value = '';
                document.querySelectorAll('.tile').forEach(tile => {{
                    tile.classList.toggle('hidden', pub !== 'all' && tile.dataset.pub !== pub);
                }});
            }});
        }});
        document.getElementById('search').addEventListener('input', function() {{
            const q = this.value.toLowerCase().trim();
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            document.querySelector('.filter-btn[data-pub="all"]').classList.add('active');
            document.querySelectorAll('.tile').forEach(tile => {{
                tile.classList.toggle('hidden', q ? !tile.textContent.toLowerCase().includes(q) : false);
            }});
        }});
    </script>
</body>
</html>"""


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Fetching headlines...")
    data = fetch_all()
    print("Generating dashboard...")
    html = generate_html(data)
    Path("index.html").write_text(html, encoding="utf-8")
    print("Done.")
