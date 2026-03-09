import feedparser
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

FEEDS = [
    {
        "name": "The Atlantic",
        "url": "https://www.theatlantic.com/feed/all/",
        "color": "#C8102E"
    },
    {
        "name": "The Economist",
        "url": "https://www.economist.com/latest/rss.xml",
        "color": "#E3120B"
    },
    {
        "name": "New York Times",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "color": "#000000"
    },
    {
        "name": "The New Yorker",
        "url": "https://www.newyorker.com/feed/everything",
        "color": "#D4001A"
    },
    {
       "name": "NYT Magazine",
       "url": "https://rss.nytimes.com/services/xml/rss/nyt/Magazine.xml",
       "color": "#FF3A2F"
   },
  {
       "name": "n+1",
       "url": "https://www.nplusonemag.com/feed/",
       "color": "#FF6B6B"
   },
   {
       "name": "Reason",
       "url": "https://reason.com/feed/",
       "color": "#003366"
   },
    {
        "name": "Intelligencer",
        "url": "https://feeds.feedburner.com/nymag/intelligencer",
        "color": "#0057A8"
    },
    {
        "name": "Vox",
        "url": "https://www.vox.com/rss/index.xml",
        "color": "#FFDB00"
    },
]

KEEP_DAYS = 7  # How many days of headlines to retain

# ── Fetch & Parse ────────────────────────────────────────────────────────────

def fetch_feed(feed_config):
    """Fetch a single RSS feed and return cleaned articles from the last KEEP_DAYS days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=KEEP_DAYS)
    articles = []

    try:
        parsed = feedparser.parse(feed_config["url"])
        for entry in parsed.entries:
            # Try to get publish date
            pub_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                pub_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

            # Skip if older than cutoff
            if pub_date and pub_date < cutoff:
                continue

            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary", "").strip()

            # Strip HTML tags from summary
            import re
            summary = re.sub(r"<[^>]+>", "", summary)
            if len(summary) > 160:
                summary = summary[:157] + "…"

            if title and link:
                articles.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "date": pub_date.strftime("%b %d, %I:%M %p") if pub_date else "",
                    "date_raw": pub_date.isoformat() if pub_date else "",
                })

    except Exception as e:
        print(f"  ⚠ Failed to fetch {feed_config['name']}: {e}")

    return articles


def fetch_all():
    """Fetch all feeds and return structured data."""
    results = []
    for feed in FEEDS:
        print(f"  Fetching {feed['name']}...")
        articles = fetch_feed(feed)
        print(f"    → {len(articles)} articles")
        results.append({
            "name": feed["name"],
            "color": feed["color"],
            "articles": articles,
            "count": len(articles),
        })
    return results


# ── HTML Generation ──────────────────────────────────────────────────────────

def generate_html(data):
    """Generate the full dashboard HTML."""
    now = datetime.now().strftime("%A, %B %d, %Y — %I:%M %p")
    total = sum(p["count"] for p in data)

    # Build publication nav tabs
    nav_tabs = ""
    for i, pub in enumerate(data):
        active = "active" if i == 0 else ""
        nav_tabs += f"""<button class="tab {active}" data-target="pub-{i}" style="--accent:{pub['color']}">{pub['name']} <span class="count">{pub['count']}</span></button>\n"""

    # Build publication sections
    sections = ""
    for i, pub in enumerate(data):
        display = "block" if i == 0 else "none"
        articles_html = ""

        if not pub["articles"]:
            articles_html = '<p class="empty">No recent articles found.</p>'
        else:
            for art in pub["articles"]:
                articles_html += f"""
                <article class="headline-card">
                    <div class="meta">{art['date']}</div>
                    <a href="{art['link']}" target="_blank" rel="noopener" class="headline-link">
                        {art['title']}
                    </a>
                    {f'<p class="summary">{art["summary"]}</p>' if art["summary"] else ""}
                </article>"""

        sections += f"""
        <section class="pub-section" id="pub-{i}" style="display:{display}">
            <div class="pub-header" style="--accent:{pub['color']}">
                <h2>{pub['name']}</h2>
                <span class="article-count">{pub['count']} stories · last 7 days</span>
            </div>
            <div class="articles">
                {articles_html}
            </div>
        </section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Headlines Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;500&family=IBM+Plex+Mono:wght@400&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        :root {{
            --bg: #0d0d0d;
            --surface: #161616;
            --surface2: #1e1e1e;
            --border: #2a2a2a;
            --text: #e8e6e1;
            --text-muted: #888;
            --text-dim: #555;
        }}

        body {{
            background: var(--bg);
            color: var(--text);
            font-family: 'IBM Plex Sans', sans-serif;
            font-weight: 300;
            min-height: 100vh;
        }}

        /* ── Header ── */
        header {{
            border-bottom: 1px solid var(--border);
            padding: 24px 24px 0;
            position: sticky;
            top: 0;
            background: var(--bg);
            z-index: 100;
        }}

        .header-top {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .masthead {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(1.4rem, 4vw, 2rem);
            font-weight: 700;
            letter-spacing: -0.02em;
            color: var(--text);
        }}

        .masthead span {{
            color: var(--text-muted);
            font-weight: 400;
        }}

        .dateline {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            color: var(--text-dim);
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }}

        .stats-bar {{
            font-size: 0.78rem;
            color: var(--text-muted);
            margin-bottom: 16px;
        }}

        /* ── Tabs ── */
        .tabs {{
            display: flex;
            gap: 2px;
            overflow-x: auto;
            scrollbar-width: none;
            padding-bottom: 0;
            -webkit-overflow-scrolling: touch;
        }}

        .tabs::-webkit-scrollbar {{ display: none; }}

        .tab {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.8rem;
            font-weight: 400;
            padding: 10px 14px;
            cursor: pointer;
            white-space: nowrap;
            border-bottom: 2px solid transparent;
            transition: color 0.15s, border-color 0.15s;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .tab:hover {{ color: var(--text); }}

        .tab.active {{
            color: var(--text);
            border-bottom-color: var(--accent);
            font-weight: 500;
        }}

        .tab .count {{
            background: var(--surface2);
            border-radius: 10px;
            font-size: 0.68rem;
            padding: 1px 6px;
            color: var(--text-dim);
        }}

        .tab.active .count {{
            background: var(--accent);
            color: white;
        }}

        /* ── Main Content ── */
        main {{
            max-width: 780px;
            margin: 0 auto;
            padding: 0 24px 80px;
        }}

        /* ── Publication Section ── */
        .pub-header {{
            display: flex;
            align-items: baseline;
            gap: 16px;
            padding: 28px 0 16px;
            border-bottom: 2px solid var(--accent);
            margin-bottom: 4px;
            flex-wrap: wrap;
        }}

        .pub-header h2 {{
            font-family: 'Playfair Display', serif;
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--text);
        }}

        .article-count {{
            font-size: 0.75rem;
            color: var(--text-dim);
            font-family: 'IBM Plex Mono', monospace;
            letter-spacing: 0.03em;
        }}

        /* ── Headline Cards ── */
        .headline-card {{
            padding: 16px 0;
            border-bottom: 1px solid var(--border);
            animation: fadeIn 0.2s ease;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(4px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .meta {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.68rem;
            color: var(--text-dim);
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 6px;
        }}

        .headline-link {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(1rem, 2.5vw, 1.15rem);
            font-weight: 400;
            line-height: 1.4;
            color: var(--text);
            text-decoration: none;
            display: block;
            transition: color 0.15s;
        }}

        .headline-link:hover {{
            color: var(--accent, #aaa);
        }}

        .summary {{
            font-size: 0.85rem;
            color: var(--text-muted);
            line-height: 1.6;
            margin-top: 6px;
            font-weight: 300;
        }}

        .empty {{
            color: var(--text-dim);
            font-style: italic;
            padding: 32px 0;
            font-size: 0.9rem;
        }}

        /* ── Search ── */
        .search-wrap {{
            padding: 20px 0 0;
        }}

        #search {{
            width: 100%;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 4px;
            color: var(--text);
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.9rem;
            padding: 10px 14px;
            outline: none;
            transition: border-color 0.15s;
        }}

        #search:focus {{ border-color: #555; }}
        #search::placeholder {{ color: var(--text-dim); }}

        /* ── Footer ── */
        footer {{
            text-align: center;
            padding: 40px 24px;
            color: var(--text-dim);
            font-size: 0.75rem;
            font-family: 'IBM Plex Mono', monospace;
            letter-spacing: 0.04em;
            border-top: 1px solid var(--border);
        }}

        /* ── Mobile ── */
        @media (max-width: 600px) {{
            header {{ padding: 16px 16px 0; }}
            main {{ padding: 0 16px 60px; }}
            .tab {{ padding: 10px 10px; font-size: 0.75rem; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-top">
            <div class="masthead">Headlines <span>/ Daily</span></div>
            <div class="dateline">{now}</div>
        </div>
        <div class="stats-bar">{total} stories across {len(data)} publications · rolling 7 days</div>
        <div class="tabs">
            {nav_tabs}
        </div>
    </header>

    <main>
        <div class="search-wrap">
            <input type="search" id="search" placeholder="Search headlines…" autocomplete="off">
        </div>
        {sections}
    </main>

    <footer>
        Updated {now} · Headlines link to original publications
    </footer>

    <script>
        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {{
            tab.addEventListener('click', () => {{
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.pub-section').forEach(s => s.style.display = 'none');
                tab.classList.add('active');
                document.getElementById(tab.dataset.target).style.display = 'block';
                document.getElementById('search').value = '';
            }});
        }});

        // Search
        document.getElementById('search').addEventListener('input', function() {{
            const q = this.value.toLowerCase().trim();
            if (!q) {{
                // Restore tab view
                const activeTarget = document.querySelector('.tab.active').dataset.target;
                document.querySelectorAll('.pub-section').forEach(s => {{
                    s.style.display = s.id === activeTarget ? 'block' : 'none';
                }});
                return;
            }}
            // Show all sections while searching
            document.querySelectorAll('.pub-section').forEach(s => s.style.display = 'block');
            document.querySelectorAll('.headline-card').forEach(card => {{
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(q) ? 'block' : 'none';
            }});
        }});
    </script>
</body>
</html>"""

    return html


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Fetching headlines...")
    data = fetch_all()
    print("Generating dashboard...")
    html = generate_html(data)
    output_path = Path("index.html")
    output_path.write_text(html, encoding="utf-8")
    print(f"Done. Dashboard saved to {output_path}")
