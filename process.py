import json, re
from datetime import datetime

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

with open("batting.json") as f:
    batting = json.load(f)["data"]

output = {
    "bijgewerkt": datetime.utcnow().strftime("%Y-%m-%d %H:%M") + " UTC",
    "categories": [
        top5(batting, "h",   "Hits"),
        top5(batting, "hr",  "Home Runs"),
        top5(batting, "avg", "Batting Average", formatter=fmt_avg, min_ab=5),
        top5(batting, "slg", "Slugging",        formatter=fmt_avg, min_ab=5),
        top5(batting, "ops", "OPS",             formatter=fmt_avg, min_ab=5),
    ]
}

with open("leaders.json", "w") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Klaar: {len(output['categories'])} categorieën opgeslagen.")
