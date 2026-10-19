import asyncio
import io
import math
import os
import re
import urllib.parse
import urllib.request
from PIL import Image

def fetch_topic_historical_archive(topic: str, max_images: int = 12) -> list[tuple[str, Image.Image]]:
    """Fetches high-quality authentic historical paintings, maps, and portraits from Wikipedia & Wikimedia Commons."""
    images = []
    seen_urls = set()
    headers = {"User-Agent": "BahaaAI-HistoryDocumentary/2.0 (contact@bahaa-ai.com)"}

    # Query 1: Wikipedia Search for the primary topic
    for query_str in [topic, f"{topic} history", f"{topic} battle"]:
        if len(images) >= max_images:
            break
        try:
            q = urllib.parse.quote(query_str)
            wiki_api = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={q}&gsrlimit=10&prop=pageimages&pithumbsize=1280&format=json"
            req = urllib.request.Request(wiki_api, headers=headers)
            with urllib.request.urlopen(req, timeout=7) as resp:
                data = json.loads(resp.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for p in pages.values():
                title = p.get("title", "")
                thumb = p.get("thumbnail", {}).get("source")
                if thumb and not thumb.lower().endswith(".svg") and thumb not in seen_urls:
                    seen_urls.add(thumb)
                    try:
                        i_req = urllib.request.Request(thumb, headers=headers)
                        with urllib.request.urlopen(i_req, timeout=8) as i_resp:
                            raw = i_resp.read()
                        im = Image.open(io.BytesIO(raw))
                        if im.width >= 300 and im.height >= 250:
                            images.append((title, im.convert("RGB")))
                            print(f"[Archive Fetched] {title} ({im.width}x{im.height})")
                            if len(images) >= max_images:
                                break
                    except Exception as e:
                        pass
        except Exception as e:
            print(f"[Archive Query Note] {e}")

    return images

import json
print("Testing historical image archive fetcher...")
res = fetch_topic_historical_archive("The Battle of Hastings 1066", max_images=6)
print(f"Total historical paintings fetched: {len(res)}")
for title, im in res:
    print(f" - {title}: {im.size}")
