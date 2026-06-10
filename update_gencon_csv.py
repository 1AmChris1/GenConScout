"""
Fetches the Gen Con GeekPreview export from BoardGameGeek and writes Gencon.csv.

Run locally:   python3 update_gencon_csv.py
Run in CI:     invoked by .github/workflows/update-csv.yml on a daily schedule

The BGG GeekPreview "Download as CSV" button hits a direct export endpoint.
This script requests that endpoint with your BGG bearer token (read from the
BGG_API_KEY environment variable) and saves the result to Gencon.csv.

If the export endpoint format changes, update PREVIEW_ID and/or EXPORT_URL below.
"""
import os
import sys
import requests

# The numeric ID from the GeekPreview URL:
# https://boardgamegeek.com/geekpreview/92/gen-con-2026-preview  ->  92
PREVIEW_ID = 92

# BGG's CSV export endpoint for a geekpreview.
# This mirrors the "Download as CSV" button on the preview page.
EXPORT_URL = f"https://boardgamegeek.com/geekpreview/{PREVIEW_ID}/export/csv"

OUTPUT_FILE = "Gencon.csv"


def main():
    api_key = os.environ.get("BGG_API_KEY", "").strip()
    headers = {"User-Agent": "gencon-scout-bot/1.0"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    print(f"Fetching {EXPORT_URL} ...")
    resp = requests.get(EXPORT_URL, headers=headers, timeout=60)

    if resp.status_code != 200:
        print(f"ERROR: got HTTP {resp.status_code}")
        print(resp.text[:500])
        sys.exit(1)

    content = resp.text
    # Sanity check: a real CSV should have a header row with a BGGId column
    first_line = content.splitlines()[0] if content.strip() else ""
    if "BGGId" not in first_line and "objectid" not in first_line.lower():
        print("ERROR: response doesn't look like the expected CSV.")
        print("First line was:", first_line[:200])
        print("This usually means the export needs an authenticated session,")
        print("or the export URL format has changed.")
        sys.exit(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    rows = len(content.splitlines()) - 1
    print(f"Wrote {OUTPUT_FILE} with {rows} rows.")


if __name__ == "__main__":
    main()
