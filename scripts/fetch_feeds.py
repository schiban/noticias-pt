import urllib.request
import json
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timezone

SOURCES = [
    {"id": "observador",   "name": "Observador",        "color": "#e8a84c", "url": "https://observador.pt/feed/"},
    {"id": "rtp",          "name": "RTP Notícias",       "color": "#e05252", "url": "https://www.rtp.pt/noticias/rss/"},
    {"id": "dn",           "name": "Diário de Notícias", "color": "#6b9fd4", "url": "https://www.dn.pt/rss/feed.xml"},
    {"id": "maisfutebol",  "name": "Maisfutebol",        "color": "#4fc48a", "url": "https://maisfutebol.iol.pt/rss"},
    {"id": "sapo",         "name": "SAPO",               "color": "#9b7ee8", "url": "https://sapo.pt/feed"},
    {"id": "nam",          "name": "Notícias ao Minuto", "color": "#e07a5f", "url": "https://www.noticiasaominuto.com/rss/ultima-hora"},
    {"id": "pplware",      "name": "Pplware",            "color": "#5bc4d4", "url": "https://pplware.sapo.pt/feed"},
    {"id": "autosport",    "name": "Autosport",          "color": "#f0c040", "url": "https://www.autosport.pt/feed"},
]

PER_SOURCE = 5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "pt-PT,pt;q=0.9",
}

NS = {
    "media":   "http://search.yahoo.com/mrss/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc":      "http://purl.org/dc/elements/1.1/",
}

def strip_html(s):
    return re.sub(r'<[^>]+>', '', s or '').strip()

def find_image(item):
    # enclosure
    enc = item.find("enclosure")
    if enc is not None and (enc.get("type", "").startswith("image") or enc.get("url", "")):
        return enc.get("url", "")
    # media:thumbnail
    for tag in ["media:thumbnail", "media:content"]:
        el = item.find(tag, NS)
        if el is not None:
            return el.get("url", "") or el.get("src", "")
    # img in description
    desc = item.findtext("description") or ""
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc)
    if m:
        return m.group(1)
    return ""

def fetch_source(source):
    try:
        req = urllib.request.Request(source["url"], headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as r:
            xml_bytes = r.read()
        root = ET.fromstring(xml_bytes)
        items = root.findall(".//item")[:PER_SOURCE]
        articles = []
        for item in items:
            title = item.findtext("title") or ""
            link  = item.findtext("link") or ""
            pub   = item.findtext("pubDate") or item.findtext("dc:date", namespaces=NS) or ""
            desc  = item.findtext("description") or item.findtext("content:encoded", namespaces=NS) or ""
            img   = find_image(item)
            if title and link:
                articles.append({
                    "sourceId":   source["id"],
                    "sourceName": source["name"],
                    "color":      source["color"],
                    "title":      strip_html(title),
                    "link":       link.strip(),
                    "pubDate":    pub.strip(),
                    "description": strip_html(desc)[:300],
                    "thumbnail":  img,
                })
        print(f"  ✓ {source['name']}: {len(articles)} artigos")
        return articles
    except Exception as e:
        print(f"  ✗ {source['name']}: {e}")
        return []

all_articles = []
for source in SOURCES:
    all_articles.extend(fetch_source(source))

output = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "articles": all_articles,
}

with open("docs/feeds.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nTotal: {len(all_articles)} artigos → docs/feeds.json")
