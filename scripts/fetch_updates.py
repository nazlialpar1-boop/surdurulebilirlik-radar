  import anthropic
  import json
  import os
  from datetime import date

  TODAY = date.today().isoformat()

  PROMPT = "Turkiye surdurulebilirlik regulasyonlari hakkinda guncel bilgi ver."


  def load_existing(path):
      if os.path.exists(path):
          with open(path, "r", encoding="utf-8") as f:
              return json.load(f)
      return {"lastUpdated": TODAY, "updates": []}


  def save_data(path, data):
      os.makedirs(os.path.dirname(path), exist_ok=True)
      with open(path, "w", encoding="utf-8") as f:
          json.dump(data, f, ensure_ascii=False, indent=2)


  def fetch_updates():
      client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
      prompt = "Bugun " + TODAY + ". Turkiye surdurulebilirlik regulasyonlari JSON guncelleme ver. Kategoriler: Raporlama,
  Karbon ve Iklim, Ambalaj ve Atik, Orman ve Biyocesitlilik, Su, Enerji, Tedarik Zinciri, Sirket Haberleri, AB
  Regulasyonlari, Finans ve Taksonomi. Her kategori icin 1-2 guncelleme. Sadece JSON: {\"updates\": [{\"id\": \"" + TODAY
  + "-001\", \"date\": \"" + TODAY + "\", \"category\": \"kategori\", \"categoryIcon\": \"emoji\", \"title\": \"baslik\",
  \"summary\": \"2-3 cumle aciklama\", \"source\": \"kaynak\", \"sourceUrl\": \"\", \"tags\": [\"etiket\"],
  \"importance\": \"high\"}]}"
      message = client.messages.create(
          model="claude-opus-4-8",
          max_tokens=4000,
          messages=[{"role": "user", "content": prompt}]
      )
      raw = message.content[0].text.strip()
      if raw.startswith("```"):
          raw = raw.split("```")[1]
          if raw.startswith("json"):
              raw = raw[4:]
      raw = raw.strip()
      new_data = json.loads(raw)
      new_updates = new_data.get("updates", [])
      data_path = "data/updates.json"
      existing = load_existing(data_path)
      existing["updates"] = [u for u in existing["updates"] if u["date"] != TODAY]
      existing["updates"] = new_updates + existing["updates"]
      existing["updates"] = existing["updates"][:180]
      existing["lastUpdated"] = TODAY
      save_data(data_path, existing)
      print("Bitti.")


  if __name__ == "__main__":
      fetch_updates()
