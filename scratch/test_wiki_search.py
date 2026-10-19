import urllib.request, urllib.parse, json

headers = {'User-Agent': 'BahaaAI-HistoryDocumentary/2.0 (contact@bahaa-ai.com)'}

def search_wiki_art(query):
    q_enc = urllib.parse.quote(query)
    url = f'https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={q_enc}&gsrlimit=5&prop=pageimages&pithumbsize=1280&format=json'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as r:
        d = json.loads(r.read().decode())
    pages = d.get('query', {}).get('pages', {})
    for p in pages.values():
        thumb = p.get('thumbnail', {}).get('source')
        if thumb and not thumb.endswith('.svg'):
            return p.get('title'), thumb
    return None, None

queries = [
    'William the Conqueror',
    'Harold Godwinson',
    'Bayeux Tapestry ships',
    'Battle of Hastings cavalry',
    'Death of Harold arrow'
]

for q in queries:
    title, url = search_wiki_art(q)
    print(f'Query "{q}": -> Title: {title} | Thumb: {url is not None}')
