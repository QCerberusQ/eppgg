import requests

XML_URL = "https://raw.githubusercontent.com/QCerberusQ/eppgg/refs/heads/main/digiphpepg.xml"
OUTPUT_FILE = "epgdigideneme.xml"

def update_epg():
    print("🔎 XML indiriliyor:", XML_URL)
    try:
        r = requests.get(XML_URL, timeout=15)
        if r.status_code == 200 and "<tv" in r.text:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"✅ epg.xml başarıyla kaydedildi ({len(r.text)} karakter)")
        else:
            print("⚠ XML geçerli değil veya <tv> etiketi yok.")
    except Exception as e:
        print("❌ HATA:", e)

if __name__ == "__main__":
    update_epg()
