from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

app = Flask(__name__)

URL = "https://www.live-timing.com/race2.php?r=304230"
TOP_N = 3

def time_to_seconds(t):
    parts = t.split(":")
    return int(parts[0]) * 60 + float(parts[1])

def seconds_to_time(s):
    minutes = int(s // 60)
    seconds = s % 60
    return f"{minutes}:{seconds:05.2f}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/standings")
def standings():
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    teams = defaultdict(list)

    rows = soup.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue

        team = cols[2].text.strip()
        time_str = cols[4].text.strip()

        try:
            teams[team].append(time_to_seconds(time_str))
        except:
            continue

    results = []

    for team, times in teams.items():
        if len(times) < TOP_N:
            continue

        times.sort()
        total = sum(times[:TOP_N])

        results.append({
            "team": team,
            "total": seconds_to_time(total),
            "total_sec": total
        })

    results.sort(key=lambda x: x["total_sec"])

    return jsonify(results)

if __name__ == "__main__":
    app.run()
