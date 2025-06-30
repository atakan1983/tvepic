import xml.etree.ElementTree as ET
import re
import difflib

epg_xml = "kabloepg.xml"
input_m3u = "mehmet.m3u"
output_m3u = "mehmet_guncel.m3u"
epg_url = "https://raw.githubusercontent.com/atakan1983/tvepic/refs/heads/main/kabloepg.xml"

# EPG'den display-name -> id haritası
displayname_to_id = {}
epg_names = []

tree = ET.parse(epg_xml)
root = tree.getroot()

for channel in root.findall("channel"):
    ch_id = channel.attrib.get("id")
    ch_name = channel.findtext("display-name")
    if ch_id and ch_name:
        ch_name = ch_name.strip()
        ch_id = ch_id.strip()
        displayname_to_id[ch_name] = ch_id
        epg_names.append(ch_name)

with open(input_m3u, "r", encoding="utf-8") as f:
    lines = f.readlines()

# EPG URL'siyle #EXTM3U satırını hazırla
extm3u_line = f'#EXTM3U url-tvg="{epg_url}"\n'

# Eğer ilk satırda #EXTM3U varsa güncelle, yoksa ekle
if lines and lines[0].startswith("#EXTM3U"):
    lines[0] = extm3u_line
else:
    lines = [extm3u_line] + lines

new_lines = [lines[0]]
i = 1
while i < len(lines):
    line = lines[i]
    if line.startswith("#EXTINF"):
        tvg_name_match = re.search(r'tvg-name="([^"]+)"', line)
        ext_name_match = re.search(r',(.+)$', line)
        old_name = None
        if tvg_name_match:
            old_name = tvg_name_match.group(1).strip()
        elif ext_name_match:
            old_name = ext_name_match.group(1).strip()

        # EPG display-name'lere en yakınını bul
        new_name = old_name
        new_id = None
        if old_name:
            matches = difflib.get_close_matches(old_name, epg_names, n=1, cutoff=0.6)
            if matches:
                new_name = matches[0]
                new_id = displayname_to_id[new_name]

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
