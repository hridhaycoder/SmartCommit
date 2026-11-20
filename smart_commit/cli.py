import json
import urllib.request
import sys
import subprocess

class Colors:
    BLUE = "\033[94m"
    DARK_BLUE = "\033[34m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    BLACK_BG = "\033[40m"
    BLUE_BG = "\033[44m"
    BOLD = "\033[1m" 
    RESET = "\033[0m"

def get_staged_diff():
    result = subprocess.run(
        ["git","diff","--cached"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def generate_commit_message(diff):
        
    url = "http://localhost:11434/api/generate"

    prompt = f"""You are an expert software developer. Analyze the follow git diff and write a concise commit message (e.g., feat:,fix:, refactor:, docs:, chore:).

Rules:
- Keep the first line under 72 characters.
- Output only the raw commit message test, do not give markdown code blocks, quotes, or anything conversational.

Git Diff:
{diff}"""

    payload = {
        "model": "gemma4:e4b",
        "prompt": prompt,
        "stream":False
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        return result["response"].strip()

diff = get_staged_diff()

if not diff:
    print("X No staged changes found! Run 'git add <file> first.")

commit_message = generate_commit_message(diff)

print("\n Suggested Commit Message:")
print("-"*40)
print(commit_message)
print("-" * 40)