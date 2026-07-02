  <details>
  <summary>İçerik</summary>

  import anthropic                                           
  import json
  import os
  from datetime import date                                  

  TODAY = date.today().isoformat()

  PROMPT = f"""Bugun {TODAY}. Turkiye'deki surdurulebilirlik regulasyonlari
  hakkinda guncelle.

  Asagidaki kategorilerden 1-2 guncelleme yaz:
  - Raporlama (TSRS, CSRD, ESRS)
  - Karbon ve Iklim (ETS, CBAM)
  - Ambalaj ve Atik
  - Orman ve Biyocesitlilik (EUDR)
  - Su
  - Enerji
  - Tedarik Zinciri (CSDDD)
  - Sirket Haberleri
  - AB Regulasyonlari
  - Finans ve Taksonomi

  Sadece JSON don dur:
  {{"updates": [{{"id": "{TODAY}-001", "date": "{TODAY}", "category":
  "kategori", "categoryIcon": "emoji", "title": "baslik", "summary": "2-3 cumle
  Turkce aciklama", "source": "kaynak", "sourceUrl": "", "tags": ["etiket"],
  "importance": "high"}}]}}
  """

  
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
      print("Claude API cagrisi yapiliyor...")
      message = client.messages.create(
          model="claude-opus-4-8",
          max_tokens=4000,
          messages=[{"role": "user", "content": PROMPT}]
      )
      raw = message.content[0].text.strip()
      if raw.startswith("```"):
          raw = raw.split("```")[1]
          if raw.startswith("json"):
              raw = raw[4:]
      raw = raw.strip()
      new_data = json.loads(raw)
      new_updates = new_data.get("updates", [])
      print(f"{len(new_updates)} guncelleme alindi.")
      data_path = "data/updates.json"
      existing = load_existing(data_path)
      existing["updates"] = [u for u in existing["updates"] if u["date"] !=
  TODAY]
      existing["updates"] = new_updates + existing["updates"]
      existing["updates"] = existing["updates"][:180]
      existing["lastUpdated"] = TODAY
      save_data(data_path, existing)
      print("Tamamlandi.")


  if __name__ == "__main__":
      fetch_updates()
                                                             
  </details>
