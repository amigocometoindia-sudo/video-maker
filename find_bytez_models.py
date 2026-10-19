import requests

print("=== Bytez API Model Finder ===")
api_key = input("Please paste your Bytez API Key: ").strip()

print("\nFetching models from Bytez...")
try:
    response = requests.get(
        "https://api.bytez.com/models/v2/list/models",
        headers={"Authorization": f"Key {api_key}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        models = data if isinstance(data, list) else data.get("models", data.get("data", []))
        
        print("\nSuccess! Here are some exact Model IDs you can copy and paste into the app:\n")
        
        # Try to find some common fast models
        found = []
        for m in models:
            name = m.get("id", m.get("model", str(m))) if isinstance(m, dict) else str(m)
            if "llama" in name.lower() or "mistral" in name.lower() or "gemma" in name.lower() or "phi" in name.lower():
                found.append(name)
                
        # Print up to 10 good options
        for name in found[:10]:
            print(f"- {name}")
            
        if not found:
            print("Could not find standard Llama/Mistral models. Here are the first 5 available:")
            for m in models[:5]:
                name = m.get("id", m.get("model", str(m))) if isinstance(m, dict) else str(m)
                print(f"- {name}")
                
        print("\nJust copy one of the bullet points above and paste it into the 'Bytez Model ID' box in the web app!")
        
    elif response.status_code == 401:
        print("\nError: The API key provided is invalid.")
    else:
        print(f"\nError: Could not fetch models (Status {response.status_code}).")
        print(response.text)
        
except Exception as e:
    print(f"\nAn error occurred: {e}")

input("\nPress Enter to exit...")
