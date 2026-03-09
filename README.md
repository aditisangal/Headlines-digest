# Headlines Dashboard

A personal news dashboard that automatically fetches and displays the latest headlines from 8 publications, updated daily.

## Publications

- The Atlantic
- The Economist
- New York Times
- The New Yorker
- New York Magazine
- The Cut
- Intelligencer
- Vox

## How it works

A Python script (`fetch_headlines.py`) fetches RSS feeds from each publication, filters to the last 7 days, and generates a clean HTML dashboard (`index.html`). GitHub Actions runs this script automatically every day and publishes the result via GitHub Pages.

## Setup

1. Enable GitHub Pages: **Settings → Pages → Source → Deploy from branch → main / root**
2. Enable GitHub Actions: the workflow in `.github/workflows/update.yml` runs automatically
3. Run the workflow manually once to populate the dashboard immediately: **Actions → Update Headlines Dashboard → Run workflow**

## Customizing the update time

Edit `.github/workflows/update.yml` and change the cron schedule. Use [crontab.guru](https://crontab.guru) to set your preferred time.
