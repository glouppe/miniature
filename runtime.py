"""Agent loop, tools, and LLM backends."""

import json
import requests
import subprocess
import sys
import cli

# Tools

MEMORY_FILE = "memory.txt"

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()

def write_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)
    return f"wrote {filename}"

def shell_exec(command):
    r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
    return r.stdout if r.returncode == 0 else f"error: {r.stderr}"

def remember(text):
    with open(MEMORY_FILE, 'a') as f:
        f.write(text + "\n")
    return "remembered"

def load_memory():
    try:
        with open(MEMORY_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

TOOLS = {
    "read_file":  {"fn": read_file,  "desc": "read_file(filename)"},
    "write_file": {"fn": write_file, "desc": "write_file(filename, content)"},
    "shell_exec": {"fn": shell_exec, "desc": "shell_exec(command)"},
    "remember":   {"fn": remember,   "desc": "remember(text) - save something to long-term memory"},
}


# System prompt

SYSTEM_PROMPT = """You are Miniature, a helpful assistant with tools. Always use a tool when you need information you don't have (time, files, system state, etc.). Never refuse, use shell_exec if unsure.

To call a tool, output ONLY a JSON block:
```json
{"tool": "tool_name", "args": {"param": "value"}}
```

Tools:
""" + "\n".join(f"- {t['desc']}" for t in TOOLS.values()) + """

You will see the tool result, then can call another or reply normally.

Your memories:
""" + load_memory()


# LLM backends

def call_ollama(messages, model="mistral-small3.2", base_url="http://localhost:11434"):
    r = requests.post(
        f"{base_url}/v1/chat/completions",
        json={"model": model, "messages": messages, "temperature": 0.1, "stream": False},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def call_local(messages):
    from model import generate
    return generate(messages)


# Tool-call parsing and execution

def parse_tool_call(text):
    if "```json" not in text:
        return None
    try:
        start = text.index("```json") + 7
        end = text.index("```", start)
        parsed = json.loads(text[start:end])
        return parsed[0] if isinstance(parsed, list) else parsed
    except (json.JSONDecodeError, ValueError):
        return None

def execute_tool(name, args):
    if name not in TOOLS:
        return f"unknown tool: {name}"
    try:
        return TOOLS[name]["fn"](**args)
    except Exception as e:
        return f"error: {e}"


# Agent loop

def run(backend="ollama"):
    call = call_local if backend == "local" else call_ollama
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    cli.banner(backend)

    while True:
        user = cli.prompt()
        if user is None:
            break

        messages.append({"role": "user", "content": user})

        while True:
            cli.verbose_prompt(messages)
            response = call(messages)
            messages.append({"role": "assistant", "content": response})

            tc = parse_tool_call(response)
            if tc is None:
                cli.agent_response(response)
                break

            name, args = tc["tool"], tc.get("args", {})
            cli.tool_call(name, args)
            result = execute_tool(name, args)
            cli.tool_result(name, result)
            messages.append({"role": "tool", "content": f"{name}: {result}"})

    cli.goodbye()


if __name__ == "__main__":
    use_local = "--local-model" in sys.argv
    backend = "local" if use_local else "ollama"
    cli.verbose = "--verbose" in sys.argv
    run(backend=backend)
