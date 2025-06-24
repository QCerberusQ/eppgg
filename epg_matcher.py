import requests
import re
import xml.etree.ElementTree as ET
import difflib

M3U_URL = "https://raw.githubusercontent.com/atakan1983/kabloo/main/mehmet.m3u"
EPG_URL = "https://raw.githubusercontent.com/atakan1983/iptvepg/main/epg.xml"
OUTPUT_FILE = "m3u-epg.m3u"

# Özel kanal eşleştirme varyantları
ALTERNATIVE_NAMES = {
    "tv85": ["tv 8.5", "tv8.5", "tv 8 buçuk", "tv8 bucuk", "tvsekizbucuk", "tv8bucuk"],
}

def fetch_m3u():
    r = requests.get(M3U_URL)
    return r.text if r.status_code == 200 else None

def fetch_epg_ids():
    r = requests.get(EPG_URL)
    if r.status_code != 200:
        return {}
    epg_ids = {}
    root = ET.fromstring(r.text)
    for ch in root.findall("channel"):
        disp = ch.findtext("display-name")
        cid = ch.attrib.get("id")
        if disp and cid:
            key = clean_name(disp)
            epg_ids[key] = cid
    return epg_ids

def clean_name(name):
    name = name.lower()
    name = name.replace("&", "ve")
    name = re.sub(r'[^a-z0-9]', '', name)  # sadece harf ve rakam
    name = name.replace("ç", "c").replace("ğ", "g").replace("ı", "i").replace("ö", "o").replace("ş", "s").replace("ü", "u")
    return name.strip()

def fuzzy_match(name, epg_map):
    cleaned = clean_name(name)

    # Özel eşleştirme listesi
    for epg_key, aliases in ALTERNATIVE_NAMES.items():
        for alias in aliases:
            if clean_name(alias) == cleaned:
                return epg_map.get(epg_key, "")

    if cleaned in epg_map:
        return epg_map[cleaned]

    # fuzzy eşleşme
    matches = difflib.get_close_matches(cleaned, epg_map.keys(), n=1, cutoff=0.6)
    if matches:
        return epg_map[matches[0]]
    return ""

def process_m3u(m3u_data, epg_map):
    lines = m3u_data.splitlines()
    output = ['#EXTM3U url-tvg="https://raw.githubusercontent.com/atakan1983/iptvepg/main/epg.xml"']
    for i in range(len(lines)):
        line = lines[i]
        if line.startswith("#EXTINF:"):
            name_match = re.search(r',(.*)$', line)
            ch_name = name_match.group(1).strip() if name_match else ""
            tvg_id = fuzzy_match(ch_name, epg_map)

            line = re.sub(r'tvg-id="[^"]*"', '', line)
            line = re.sub(r'\s+', ' ', line)
            if tvg_id:
                line = line.replace("#EXTINF:-1", f'#EXTINF:-1 tvg-id="{tvg_id}"')
            else:
                line = line.replace("#EXTINF:-1", '#EXTINF:-1')
            output.append(line.strip())
        else:
            output.append(line)
    return "\n".join(output)

def save_output(content):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    print("🔄 M3U ve EPG verileri alınıyor...")
    m3u = fetch_m3u()
    epg_map = fetch_epg_ids()
    if not m3u or not epg_map:
        print("❌ Veri alınamadı.")
        return
    result = process_m3u(m3u, epg_map)
    save_output(result)
    print(f"✅ Yeni dosya oluşturuldu: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
