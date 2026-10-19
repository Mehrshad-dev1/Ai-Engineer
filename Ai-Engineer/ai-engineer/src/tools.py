
import os
import pathlib
import subprocess
import time

from config import CLIENT, MODEL, MAX_SEARCHES_PER_SESSION, SEARCH_CACHE_TTL_SECONDS

_search_count = {"n": 0}
_search_cache = {}  # query -> (timestamp, result)


def calculate(operation: str, a: float, b: float) -> str:
    """Do exact arithmetic on two numbers."""
    if operation == "add":
        return str(a + b)
    if operation == "subtract":
        return str(a - b)
    if operation == "multiply":
        return str(a * b)
    if operation == "divide":
        return "Error: division by zero" if b == 0 else str(a / b)
    return f"Error: unknown operation {operation}"


def read_file(path: str) -> str:
    """Read the contents of a file."""
    try:
        return pathlib.Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Error: file not found: {path}"


def write_file(path: str, content: str) -> str:
    """Write text to a file, creating or overwriting it."""
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} characters to {path}"


def list_files(directory: str = ".") -> str:
    """List files and directories in a directory."""
    try:
        names = sorted(os.listdir(directory))
    except FileNotFoundError:
        return f"Error: directory not found: {directory}"
    return "\n".join(names) if names else f"{directory} is empty"


def delete_file(path: str) -> str:
    """Delete a file. Irreversible."""
    try:
        os.remove(path)
        return f"Deleted {path}"
    except FileNotFoundError:
        return f"Error: file not found: {path}"


def make_directory(path: str) -> str:
    """Create a directory, including parent directories."""
    try:
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        return f"Created directory {path}"
    except Exception as e:
        return f"Error creating directory: {e}"


def web_search(query: str) -> str:
    """Search the web for current information. Cached (TTL) and rate-limited."""
    now = time.time()

    if query in _search_cache:
        cached_time, cached_result = _search_cache[query]
        if now - cached_time < SEARCH_CACHE_TTL_SECONDS:
            return cached_result

    if _search_count["n"] >= MAX_SEARCHES_PER_SESSION:
        return "Error: search limit reached for this session."

    _search_count["n"] += 1
    r = CLIENT.responses.create(
        model=MODEL,
        tools=[{"type": "web_search"}],
        input=f"Search the web and answer concisely: {query}",
        max_output_tokens=150,
    )
    _search_cache[query] = (now, r.output_text)
    return r.output_text


def run_command(command: str) -> str:
    """Run a shell command and return its output."""
    try:
        p = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return "Command timed out after 60s"
    output = (p.stdout or "") + (p.stderr or "")
    if p.returncode != 0:
        return f"Command failed (exit {p.returncode}):\n{output}"
    return output or "(no output)"
