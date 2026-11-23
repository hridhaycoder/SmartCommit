import json
import urllib.request
import sys
import subprocess
import textwrap

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

    subprocess.run(["git","add", "."], capture_output=True)

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
- Output ONLY the single-line commit message. 
- NO body paragraphs, NO explanations, NO markdown blocks, and NO quotes.
- Keep it under 72 characters.

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

def regenerate_with_feedback(diff,old_message, feedback):
    url = "http://localhost:11434/api/generate"

    prompt = f"""Here is a git diff and a previous commit message suggestion. The user wants to change it based on feedback

Git Diff:
{diff}

Previous Message:
{old_message}

User Feedback:
{feedback}

Rules:
- Rewrite the Conventional Commit message baed on the user's feedback.
- Output ONLY the single-line commit message. No body, no markdown blocks, quotes, or conversational filler.

"""
    payload = {
        "model": "gemma4:e4b",
        "prompt": prompt,
        "stream":False
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url,data=data, headers={"Content-Type": "application/json"})

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))
        full_response = result["response"].strip()
        return full_response.split("\n")[0].strip()

def render_chat_box(message):
    max_content_width = 70

    raw_lines = message.strip().split("\n")
    wrapped_lines = []
    for line in raw_lines:
        if not line.strip():
            wrapped_lines.append("")
        else:
            wrapped_lines.extend(textwrap.wrap(line, width=max_content_width))

        
    width = max(max((len(line) for line in wrapped_lines),default=50), 50) + 4
    
    top_border = f"{Colors.DARK_BLUE} {'-' * width} {Colors.RESET}"
    bottom_border = f"{Colors.DARK_BLUE}{'-'*width}{Colors.RESET}"

    print(f"\n{top_border}")
    print(f"{Colors.DARK_BLUE}|{' '*width}|{Colors.RESET}")

    for line in wrapped_lines:
        padding = width - len(line) - 2
        print(f"{Colors.DARK_BLUE}|{Colors.RESET} {Colors.WHITE}{Colors.BOLD}{line}{Colors.RESET}{' '*padding}{Colors.DARK_BLUE}|{Colors.RESET}")

    print(f"{Colors.DARK_BLUE}|{' '*width}|{Colors.RESET}")
    print(f"{bottom_border}\n")

def interactive_commit_loop(diff,initial_message):
    current_message = initial_message

    while True:
        render_chat_box(current_message)

        print(
            f"  {Colors.BLUE}[y]{Colors.WHITE} Commit   "
            f"{Colors.BLUE}[e]{Colors.WHITE} Edit   "
            f"{Colors.BLUE}[q]{Colors.WHITE} Quit   "
            f"{Colors.BLUE}[r]{Colors.WHITE} Regenerate   "
            f"{Colors.GRAY}(or type below to chat & refine){Colors.RESET}\n"
        )

        user_input = input(f"{Colors.BLUE}❯ {Colors.WHITE}").strip()
        print(Colors.RESET, end="")

        if user_input.lower() == "y":
            subprocess.run(["git", "commit", "-m", current_message])
            print(f"\n{Colors.BLUE}✔ {Colors.WHITE}{Colors.BOLD}Commited sucessfully.{Colors.RESET}\n")
            break
        elif user_input.lower() == "e":
            subprocess.run(["git","commit","-m",current_message, "--edit"])
            break
        elif user_input.lower() == "q":
            print(f"\n{Colors.GRAY}x Aborted.{Colors.RESET}\n")
            sys.exit(1)
        elif user_input.strip().lower() == "r":
            print(f"{Colors.WHITE}{Colors.BOLD} Regenerating...{Colors.RESET}")
            current_message = generate_commit_message(diff)

        elif user_input == "":
            continue
        else:
            print(f"\n{Colors.BLUE}*  {Colors.GRAY}Refining commit message...{Colors.RESET}")
            current_message = regenerate_with_feedback(diff,current_message, user_input)

def print_banner():
    art = """
  ____ ___ _____    ____  __  __    _    ____  _____     ____ ___  __  __ __  __ ___ _____ 
 / ___|_ _|_   _|  / ___||  \\/  |  / \\  |  _ \\|_   _|   / ___/ _ \\|  \\/  |  \\/  |_ _|_   _|
| |  _ | |  | |   | (___ | |\\/| | / _ \\ | |_)|  | |    | |  | | | | |\\/| | |\\/| || |  | |  
| |_| || |  | |    \\___ \\| |  | |/ ___ \\|  _ \\  | |    | |__| |_| | |  | | |  | || |  | |  
 \\____|___| |_|   |_____/|_|  |_/_/   \\_\\_| \\_\\ |_|     \\____\\___/|_|  |_|_|  |_|___| |_|  
"""
    print(f"{Colors.BLUE}{Colors.BOLD}{art}{Colors.RESET}{Colors.GRAY}{Colors.RESET}")

def main():
    print_banner()
    diff = get_staged_diff()
    if not diff:
        print(f"\n{Colors.BLUE}x {Colors.WHITE}No staged changes found! Run 'git add <file>' first.{Colors.RESET}\n")
        sys.exit(1)

    print(f"\n{Colors.BLUE}* {Colors.GRAY}Analyzing your changes...{Colors.RESET}")
    commit_message = generate_commit_message(diff)

    if not commit_message:
        print(f"\n{Colors.BLUE}x {Colors.WHITE}Failed to generate a commit message.{Colors.RESET}\n")
        sys.exit(1)

    interactive_commit_loop(diff,commit_message)

if __name__ == "__main__":
    main()

