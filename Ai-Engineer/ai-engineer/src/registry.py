# registry.py — the bridge between "what the model see" & "is real the function run"

from tools import (
    calculate, read_file, write_file, list_files,
    delete_file, make_directory, web_search, run_command,
)

# -- Tools schema -- 
TOOLS = [
    {"type": "function", 
     "name": "calculate",
     "description": "Do exact arithmetic on two numbers.",
     "parameters": {
            "type": "object",
            "properties": {
                        "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                        "a": {"type": "number"}, 
                        "b": {"type": "number"},
                    }, 
            "required": ["operation", "a", "b"]}},

    {"type": "function", "name": "read_file",
     "description": "Read the contents of a file.",
     "parameters": {"type": "object",
                     "properties": {"path": {"type": "string"}}, "required": ["path"]}},

    {"type": "function", "name": "write_file",
     "description": "Write text to a file, creating or overwriting it.",
     "parameters": {"type": "object",
                     "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                     "required": ["path", "content"]}},

    {"type": "function", "name": "list_files",
     "description": "List files and directories in a directory.",
     "parameters": {"type": "object",
                     "properties": {"directory": {"type": "string"}}, "required": []}},

    {"type": "function", "name": "delete_file",
     "description": "Delete a file. Irreversible.",
     "parameters": {"type": "object",
                     "properties": {"path": {"type": "string"}}, "required": ["path"]}},

    {"type": "function", "name": "make_directory",
     "description": "Create a directory, including parent directories.",
     "parameters": {"type": "object",
                     "properties": {"path": {"type": "string"}}, "required": ["path"]}},

    {"type": "function", "name": "web_search",
     "description": "Search the web for current information.",
     "parameters": {"type": "object",
                     "properties": {"query": {"type": "string"}}, "required": ["query"]}},

    {"type": "function", "name": "run_command",
     "description": "Run a shell command and return its output.",
     "parameters": {"type": "object",
                     "properties": {"command": {"type": "string"}}, "required": ["command"]}},
]


# -- TOOL_FNS dispatch 
TOOL_FNS = {
    "calculate": lambda x: calculate(x["operation"], x["a"], x["b"]),
    "read_file": lambda x: read_file(x["path"]),
    "write_file": lambda x: write_file(x["path"], x["content"]),
    "list_files": lambda x: list_files(x.get("directory", ".")),
    "delete_file": lambda x: delete_file(x["path"]),
    "make_directory": lambda x: make_directory(x["path"]),
    "web_search": lambda x: web_search(x["query"]),
    "run_command": lambda x: run_command(x["command"]),
}