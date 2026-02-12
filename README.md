# 🔬 miniature

A complete AI agent in ~225 lines of Python. Built for teaching.

![demo](demo.gif)

## What this is

An LLM-powered agent with tool use and persistent memory, from scratch. No frameworks, no abstractions. The entire system fits in three files:

```
runtime.py   agent loop, tools, memory, system prompt   (132 lines)
model.py     raw transformer inference + sampling         (46 lines)
cli.py       terminal interface                           (47 lines)
```

Two inference backends:

- **Ollama**: any model via local API (default: mistral-small3.2)
- **Raw**: direct HuggingFace transformer, explicit autoregressive loop (Qwen2.5-1.5B)

## The idea

```
user input → [system prompt + memory + history] → LLM → tool call?
  yes → execute → feed result back → LLM again
  no  → display response → next input
```

The system prompt lists available tools and any saved memories. The model outputs JSON when it wants to call a tool. The runtime parses it, runs it, and loops. When the model responds without JSON, the turn is over.

Memory is just a text file (`memory.txt`) loaded into the system prompt at startup. The model can append to it via the `remember` tool. Stateless model, persistent memory.

## Quick start

```bash
# with ollama
ollama pull mistral-small3.2
pip install requests
python runtime.py

# with raw local inference (needs GPU)
pip install torch transformers accelerate
python runtime.py --raw-model
```

## Flags

```bash
python runtime.py                  # ollama
python runtime.py --raw-model      # raw inference (no ollama)
python runtime.py --raw-prompt     # inspect messages sent to the LLM
```

## Adding tools

Write a function, register it:

```python
def calculator(expression):
    return str(eval(expression))

TOOLS["calculator"] = {"fn": calculator, "desc": "calculator(expression)"}
```

The system prompt auto-generates from `TOOLS`.

## What students see

- **runtime.py**: how an agent loop works, how tools are defined and executed, how the LLM is steered via a system prompt, how memory is just text injected into context
- **model.py**: chat templates, tokenization, the autoregressive generation loop (forward pass → sample → append → repeat), KV caching, temperature sampling
- **cli.py**: separation of concerns

## License

MIT
