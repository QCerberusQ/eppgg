import requests
import os
import xml.etree.ElementTree as ET
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJMSVZFIiwiaXBiIjoiMCIsImNnZCI6IjA5M2Q3MjBhLTUwMmMtNDFlZC1hODBmLTJiODE2OTg0ZmI5NSIsImNzaCI6IlRSS1NUIiwiZGN0IjoiM0VGNzUiLCJkaSI6ImE2OTliODNmLTgyNmItNGQ5OS05MzYxLWM4YTMxMzIxOGQ0NiIsInNnZCI6Ijg5NzQxZmVjLTFkMzMtNGMwMC1hZmNkLTNmZGFmZTBiNmEyZCIsInNwZ2QiOiIxNTJiZDUzOS02MjIwLTQ0MjctYTkxNS1iZjRiZDA2OGQ3ZTgiLCJpY2giOiIwIiwiaWRtIjoiMCIsImlhIjoiOjpmZmZmOjEwLjAuMC4yMDYiLCJhcHYiOiIxLjAuMCIsImFibiI6IjEwMDAiLCJuYmYiOjE3NDUxNTI4MjUsImV4cCI6MTc0NTE1Mjg4NSwiaWF0IjoxNzQ1MTUyODI1fQ.OSlafRMxef4EjHG5t6TqfAQC7y05IiQjwwgf6yMUS9E"
}

CHANNELS_URL = "https://core-api.kablowebtv.com/api/channels"

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def dt_to_xmltv(dtstr):
    try:
        dt = datetime.strptime(dtstr, "%d.%m.%Y %H:%M")
        return dt.strftime("%Y%m%d%H%M00 +0300")
    except Exception:
        return ""

def main():
    output_dir = get_script_dir()
    epg_path = os.path.join(output_dir, "kabloepg.xml")

    # Kanal listesini çek
    r = requests.get(CHANNELS_URL, headers=headers)
    r.raise_for_status()
    data = r.json()
    channels = data["Data"]["AllChannels"]

    tv = ET.Element("tv")

    for idx, ch in enumerate(channels):
        ch_id = ch.get("UId")
        ch_name = ch.get("Name")
        ch_elem = ET.SubElement(tv, "channel", id=str(ch_id))
        display_name = ET.SubElement(ch_elem, "display-name")
        display_name.text = ch_name

        epgs = ch.get("Epgs", [])
        print(f"{idx+1}/{len(channels)}: {ch_name} ({ch_id}) - {len(epgs)} program")
        for prog in epgs:
            start = dt_to_xmltv(prog.get("StartDateTime", ""))
            stop  = dt_to_xmltv(prog.get("EndDateTime", ""))
            title = prog.get("Title") or ""
            desc  = prog.get("ShortDescription") or ""

            programme = ET.SubElement(tv, "programme", {
                "start": start,
                "stop": stop,
                "channel": str(ch_id)
            })
            title_elem = ET.SubElement(programme, "title", lang="tr")
            title_elem.text = title
            desc_elem = ET.SubElement(programme, "desc", lang="tr")
            desc_elem.text = desc

    tree = ET.ElementTree(tv)
    tree.write(epg_path, encoding="utf-8", xml_declaration=True)
    print("\nkabloepg.xml başarıyla oluşturuldu.")

if __name__ == "__main__":
    main()
