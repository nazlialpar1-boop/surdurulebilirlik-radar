  import anthropic
  import json
  import os
  from datetime import date

  TODAY = date.today().isoformat()

  PROMPT = f"""Bugün {TODAY}. Türkiye'deki sürdürülebilirlik regülasyonları ve
  şirket haberleri hakkında güncel bilgi ver.

  Aşağıdaki kategorilerden her birinde varsa 1-2 önemli güncelleme yaz:
  - Raporlama (TSRS, CSRD, ESRS, GRI)
  - Karbon & İklim (ETS, CBAM, Paris Anlaşması)
  - Ambalaj & Atık (GÜS, plastik regülasyonları)
  - Orman & Biyoçeşitlilik (EUDR, TNFD)
  - Su (su stresi, deşarj standartları)
  - Enerji (yenilenebilir enerji, enerji verimliliği)
  - Tedarik Zinciri (CSDDD, Scope 3, insan hakları)
  - Şirket Haberleri (Türk şirketlerinin sürdürülebilirlik adımları)
  - AB Regülasyonları (Türkiye'yi etkileyen AB mevzuatı)
  - Finans & Taksonomi (yeşil tahvil, AB Taksonomisi)

  Her güncelleme için JSON formatında yanıt ver. Sadece JSON döndür, başka 
  hiçbir şey yazma.

  Format:
  {{
    "updates": [
      {{
        "id": "{TODAY}-001",
        "date": "{TODAY}",
        "category": "kategori adı",
        "categoryIcon": "emoji",
        "title": "kısa başlık (max 10 kelime)",
        "summary": "2-3 cümle, sade Türkçe, ne anlama geldiğini açıkla",
        "source": "kaynak adı",
        "sourceUrl": "",
        "tags": ["etiket1", "etiket2"],
        "importance": "high/medium/low"
      }}
    ]
  }}

  Önemli kurallar:
  - Sadece gerçek, güncel bilgiler yaz
  - Türkiye'ye etkisini mutlaka belirt
  - Özet sade ve anlaşılır olsun
  - importance: high = acil/zorunlu, medium = yakında etkili, low = bilgi amaçlı
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
      print(f"Claude'dan {TODAY} guncellemeleri aliniyor...")
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
      print(f"{len(new_updates)} yeni guncelleme alindi.")
      data_path = "data/updates.json"
      existing = load_existing(data_path)
      existing["updates"] = [u for u in existing["updates"] if u["date"] !=
  TODAY]
      existing["updates"] = new_updates + existing["updates"]
      existing["updates"] = existing["updates"][:180]
      existing["lastUpdated"] = TODAY
      save_data(data_path, existing)
      print(f"Tamamlandi. Toplam: {len(existing['updates'])} guncelleme.")


  if __name__ == "__main__":
      fetch_updates()
