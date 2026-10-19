# safety.py — human acceptable need (The validation gate: precisely the seam between the 
# "model's decision" and the "actual execution.")
import re

RISKY = {"write_file", "delete_file", "run_command"}

# Dangerous patterns that don't even require asking the user — they are rejected outright ,
# there are more but cant right all. better run the agent in isolate-container(Docker)
DANGEROUS_PATTERNS = [
    r"\brm\s+-rf\b",            #rm -rf
    r"\brm\s+-fr\b",            # reverse flag
    r"\bdel\s+/s\s+/q\b",       # windows: del /s /q
    r"\brmdir\s+/s\s+/q\b",     # windows: rmdir /s /q
    r":\(\)\s*\{.*\};\s*:",     # fork bomb 
    r"\bformat\s+[a-zA-Z]:",    # format C:
    r"\bshutdown\b",            # turn off 
    r">\s*/dev/sd[a-z]",        # write on disk
]

def is_catastrophic(command: str) -> bool:
    """True if match with one of them"""
    return any(re.search(pattern, command, re.IGNORECASE) for pattern in DANGEROUS_PATTERNS)


def approve(name: str, args: dict) -> bool:
    '''reject base on :unction tool name & castastrophic'''
    if name not in RISKY:
        return True  # the safe tool run without permission

    # auto-reject without ask question 
    if name == "run_command" and is_catastrophic(args.get("command", "")):
        print(f"\n 🛑 BLOCKED (auto-deny, too dangerous): {name}({args})")
        return False
    
    print(f"\n ⚠ the agent wants to run: {name}({args})")
    answer = input(" approve? [y/N] ").strip().lower()
    return answer == "y"