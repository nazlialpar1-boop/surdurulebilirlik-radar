import anthropic
  import json
  import os
  from datetime import date

  TODAY = date.today().isoformat()

  PROMPT = "Turkiye surdurulebilirlik regulasyonlari hakkinda guncel bilgi ver.
  Kategoriler: Raporlama, Karbon-Iklim, Ambalaj-Atik, Orman-Biyocesitlilik, Su,
  Enerji, Tedarik-Zinciri, Sirket-Haberleri, AB-Regulasyonlari,
  Finans-Taksonomi. Her kategori icin JSON formatinda 1-2 guncelleme yaz. Sadece
  JSON don: {\"updates\": [{\"id\": \"ID\", \"date\": \"DATE\", \"category\":
  \"cat\", \"categoryIcon\": \"icon\", \"title\": \"title\", \"summary\":
  \"summary\", \"source\": \"source\", \"sourceUrl\": \"\", \"tags\": [\"tag\"],
  \"importance\": \"high\"}]}"


  def load_existing(path):
      if os.path.exists(path):
          with open(path, "r", encoding="utf-8") as f:       
              return json.load(f)
      return {"lastUpdated": TODAY, "updates": []}


  def save_data(path, data):
      os.makedirs(os.path.dirname(path), exist_ok=True)
      with open(path, "w", encoding="utf-8") as f:
          json.dump(data, f, ensure_ascii=False, indent=2)

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
