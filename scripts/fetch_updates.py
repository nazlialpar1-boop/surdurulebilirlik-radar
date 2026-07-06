import anthropic
import json
import os
import re
import urllib.request
import urllib.parse
from datetime import date

TODAY = date.today().isoformat()

CATEGORIES = [
    "Raporlama", "Karbon & Iklim", "Ambalaj & Atik",
    "Orman & Biyocesitlilik", "Su", "Enerji",
    "Tedarik Zinciri", "Sirket Haberleri", "AB Regulasyonlari", "Finans & Taksonomi"
]


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


def tavily_search(query, api_key):
    url = "https://api.tavily.com/search"
    payload = json.dumps({
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": 10,
        "include_answer": False
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_updates():
    anthropic_key = os.environ["ANTHROPIC_API_KEY"]
    tavily_key = os.environ["TAVILY_API_KEY"]

    print("Haberler aranıyor...")
    queries = [
        "Türkiye sürdürülebilirlik çevre regülasyon 2026",
        "Türkiye ESG raporlama iklim yasa 2026",
        "Türkiye ambalaj atık enerji mevzuat 2026"
    ]
    articles = []
    for q in queries:
        try:
            result = tavily_search(q, tavily_key)
            for r in result.get("results", []):
                articles.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:300],
                    "source": r.get("url", "").split("/")[2] if r.get("url") else ""
                })
        except Exception as e:
            print("Tavily hata:", e)

    print(str(len(articles)) + " haber bulundu.")

    if not articles:
        print("Haber bulunamadı, çıkılıyor.")
        return

    articles_text = "\n\n".join([
        f"Baslik: {a['title']}\nURL: {a['url']}\nIcerik: {a['content']}"
        for a in articles
    ])

    client = anthropic.Anthropic(api_key=anthropic_key)
    prompt = f"""Bugun {TODAY}. Asagidaki haberleri analiz et ve Turkiye surdurulebilirlik radarı icin JSON olustur.
Kategoriler SADECE su listeden secilmeli: {", ".join(CATEGORIES)}
Sadece JSON don, baska hicbir sey yazma.
Format: {{"updates": [{{"id": "{TODAY}-001", "date": "{TODAY}", "category": "kategori adi", "categoryIcon": "emoji", "title": "baslik", "summary": "2-3 cumle aciklama", "source": "site adi", "sourceUrl": "https://...", "tags": ["etiket"], "importance": "high"}}]}}

Haberler:
{articles_text}"""

    print("Claude'a gonderiliyor...")
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}],
        timeout=60
    )
    raw = message.content[0].text
    print("Ham yanit:", raw[:300])
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
