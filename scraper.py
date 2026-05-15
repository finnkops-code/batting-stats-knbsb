import json
import re
import urllib.request
from datetime import datetime, timezone

BATTING_URL = "https://stats.knbsbstats.nl/api/v1/stats/events/2026-lucky-day-hoofdklasse/index?section=players&stats-section=batting&language=en"

def fetch_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "nl-NL,nl;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def parse_name(html):
    last = re.search(r'class="lastname">(.*?)<', html)
    first = re.search(r'class="firstname">(.*?)<', html)
    return f"{first.group(1)} {last.group(1)}" if first and last else html

def fmt_avg(val):
    if val >= 1000:
        return "1.000"
    return f".{int(val):03d}"

def top5(data, key, label, formatter=None, min_ab=None):
    filtered = [p for p in data if p.get(key, 0) > 0]
    if min_ab:
        filtered = [p for p in filtered if p.get('ab', 0) >= min_ab]
    filtered = sorted(filtered, key=lambda x: x[key], reverse=True)[:5]
    return {
        "label": label,
        "leaders": [
            {
                "naam": parse_name(p['name']),
                "team": p['teamcode'],
                "waarde": formatter(p[key]) if formatter else p[key]
            }
            for p in filtered
        ]
    }

def main():
    print(f"Ophalen van {BATTING_URL}...")
    data = fetch_json(BATTING_URL)
    batting = data["data"]
    print(f"Spelers ontvangen: {len(batting)}")

    # Sla ruwe data op voor controle
    with open("batting.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ batting.json opgeslagen")

    # Verwerk naar leaders
    output = {
        "bijgewerkt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "bron": BATTING_URL,
        "categories": [
            top5(batting, "h",   "Hits"),
            top5(batting, "hr",  "Home Runs"),
            top5(batting, "avg", "Batting Average", formatter=fmt_avg, min_ab=5),
            top5(batting, "slg", "Slugging",        formatter=fmt_avg, min_ab=5),
            top5(batting, "ops", "OPS",             formatter=fmt_avg, min_ab=5),
        ]
    }

    with open("leaders.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("✅ leaders.json opgeslagen")

if __name__ == "__main__":
    main()
