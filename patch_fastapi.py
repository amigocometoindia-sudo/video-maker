import fastapi.routing

path = fastapi.routing.__file__
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

if "!!! BODY PARSE ERROR:" not in content:
    content = content.replace(
        'detail="There was an error parsing the body"',
        'detail="There was an error parsing the body"\n            )\n            print(f"\\n\\n!!! BODY PARSE ERROR: {e!r}\\n\\n", flush=True)'
    )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched successfully")
else:
    print("Already patched")
