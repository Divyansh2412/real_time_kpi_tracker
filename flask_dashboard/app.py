# flask_dashboard/app.py
import json
import glob
import os
from flask import Flask, render_template

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
AGG_DIR = os.path.join(APP_ROOT, "..", "aggregator_output")

app = Flask(__name__, template_folder="templates")

def read_latest_aggregates():
    files = glob.glob(os.path.join(AGG_DIR, "*.json"))
    if not files:
        return []
    latest = max(files, key=os.path.getmtime)
    try:
        with open(latest, "r") as f:
            data = [json.loads(line) for line in f]
        return data
    except Exception as e:
        print("Error reading aggregate:", e)
        return []

@app.route("/")
def index():
    rows = read_latest_aggregates()
    return render_template("index.html", rows=rows)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
