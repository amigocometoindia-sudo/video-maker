import urllib.request
import json

def test():
    data = json.dumps({'topic': '2000 Years of Israel History', 'duration_minutes': 3.0}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8765/api/documentary/research', data=data, headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    d = json.loads(res.read())
    print("Success:", d.get("success"))
    print("Status:", d.get("status"))
    print("Word Count:", d.get("word_count"))
    chapters = d.get("outline", {}).get("chapters", [])
    print(f"Total Chapters: {len(chapters)}")
    for ch in chapters[:4]:
        print(f"  [{ch['era']}] {ch['scene_type']}: {ch['title']}")

if __name__ == '__main__':
    test()
