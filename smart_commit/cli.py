import json
import urllib.request

url = "http://localhost:11434/api/generate"

payload = {
    "model": "gemma4:e4b",
    "prompt": "Explain what a git commit is in a short sentence",
    "stream":False
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read().decode("utf-8"))
    print(result["response"])