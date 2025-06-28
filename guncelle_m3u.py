import xml.etree.ElementTree as ET

# Dosya yolları
epg_xml = "kabloepg.xml"
input_m3u = "mehmet.m3u"
output_m3u = "mehmet_guncel.m3u"

# 1. kabloepg.xml'den id ve isim eşleştirmesini al
tree = ET.parse(epg_xml)
root = tree.getroot()

# id -> isim haritası
id_name_map = {}
for channel in root.findall("channel"):
    ch_id = channel.attrib.get("id")
    ch_name = channel.findtext("display-name")
    if ch_id and ch_name:
        id_name_map[ch_id.strip()] = ch_name.strip()

# 2. mehmet.m3u'yu oku ve güncelle
with open(input_m3u, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # EXTINF satırı ise, id ve isim güncelle
    if line.startswith("#EXTINF"):
        # id'yi bul
        import re
        # Örnek: #EXTINF:-1 tvg-id="dcd25489-d139-48a7-ab90-a6b80f2a160b" tvg-name="Trace Urban" ...
        m = re.search(r'tvg-id="([^"]+)"', line)
        if m:
            old_id = m.group(1)
            new_id = old_id
            new_name = None

            # Eğer bu id kabloepg.xml'de varsa, güncelle
            if old_id in id_name_map:
                new_id = old_id
                new_name = id_name_map[old_id]
                # tvg-id ve tvg-name'i değiştir
                line = re.sub(r'tvg-id="([^"]+)"', f'tvg-id="{new_id}"', line)
                line = re.sub(r'tvg-name="([^"]+)"', f'tvg-name="{new_name}"', line)
                # #EXTINF sonunda isim varsa, onu da değiştir
                line = re.sub(r',.*$', f',{new_name}', line)
        new_lines.append(line)
        # Sonraki satır (stream url) de eklenir
        if i+1 < len(lines):
            new_lines.append(lines[i+1])
        i += 2
    else:
        new_lines.append(line)
        i += 1

# 3. Yeni M3U dosyasını kaydet
with open(output_m3u, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"Güncellenmiş M3U dosyası: {output_m3u}")