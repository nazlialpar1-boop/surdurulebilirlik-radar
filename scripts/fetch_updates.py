import anthropic
import json
import os
import re
from datetime import date

TODAY = date.today().isoformat()


def load_existing(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"lastUpdated": TODAY, "updates": []}


def save_data(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_json(raw):
    raw = raw.strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return match.group(0)
    return raw


def fetch_updates():
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    with open("scripts/prompt.txt", "r", encoding="utf-8") as f:
        prompt = "Bugun " + TODAY + ". " + f.read().replace("TARIH", TODAY)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text
    print("Ham yanit:", raw[:200])
    raw = extract_json(raw)
    new_data = json.loads(raw)
    new_updates = new_data.get("updates", [])
    data_path = "data/updates.json"
    existing = load_existing(data_path)
    existing["updates"] = [u for u in existing["updates"] if u["date"] != TODAY]
    existing["updates"] = new_updates + existing["updates"]
    existing["updates"] = existing["updates"][:180]
    existing["lastUpdated"] = TODAY
    save_data(data_path, existing)
    print("Bitti. " + str(len(new_updates)) + " guncelleme eklendi.")


if __name__ == "__main__":
    fetch_updates()
