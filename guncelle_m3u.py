import xml.etree.ElementTree as ET
import difflib
import re
import unicodedata

def normalize(name):
    if not name:
        return ""
    table = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    name = name.translate(table)
    name = name.lower()
    name = unicodedata.normalize("NFKD", name)
    name = re.sub(r'[\W_]+', '', name)  # harf ve rakam dışı her şeyi kaldır
    return name

# Dosya yolları
epg_xml = "kabloepg.xml"
input_m3u = "mehmet.m3u"
output_m3u = "mehmet_guncel.m3u"

tree = ET.parse(epg_xml)
root = tree.getroot()

id_name_map = {}
name_id_map = {}
epg_names = []
epg_names_normalized = []

for channel in root.findall("channel"):
    ch_id = channel.attrib.get("id")
    ch_name = channel.findtext("display-name")
    if ch_id and ch_name:
        ch_id = ch_id.strip()
        ch_name = ch_name.strip()
        id_name_map[ch_id] = ch_name
        name_id_map[ch_name] = ch_id
        epg_names.append(ch_name)
        epg_names_normalized.append(normalize(ch_name))

with open(input_m3u, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith("#EXTINF"):
        tvg_name_match = re.search(r'tvg-name="([^"]+)"', line)
        tvg_id_match = re.search(r'tvg-id="([^"]+)"', line)

        old_name = tvg_name_match.group(1).strip() if tvg_name_match else None
        old_id = tvg_id_match.group(1).strip() if tvg_id_match else None

        new_name = old_name
        new_id = old_id

        # Kanalları normalize ederek eşleşme yap
        if old_name:
            norm = normalize(old_name)
            matches = difflib.get_close_matches(norm, epg_names_normalized, n=1, cutoff=0.7)
            if matches:
                match_norm = matches[0]
                idx = epg_names_normalized.index(match_norm)
                new_name = epg_names[idx]
                new_id = name_id_map[new_name]
        # tvg-name ve tvg-id güncelle
        if new_name:
            line = re.sub(r'tvg-name="([^"]*)"', f'tvg-name="{new_name}"', line)
            line = re.sub(r',.*$', f',{new_name}', line)
        if new_id:
            line = re.sub(r'tvg-id="([^"]*)"', f'tvg-id="{new_id}"', line)

        new_lines.append(line)
        if i+1 < len(lines):
            new_lines.append(lines[i+1])
        i += 2
    else:
        new_lines.append(line)
        i += 1

with open(output_m3u, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Güncellenmiş M3U dosyası: {output_m3u}")
