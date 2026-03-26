# 🔬 miniature

⚠️ This code executes arbitrary shell commands as directed by the LLM. Run it only in sandboxed or disposable environments.

A complete AI agent in ~225 lines of Python. No frameworks, no abstractions.

![demo](demo.gif)

```
runtime.py   agent loop, tools, memory, system prompt
model.py     local Hugging Face transformer inference + sampling
cli.py       terminal interface
```

## Quick start

```bash
# with ollama
ollama pull mistral-small3.2
pip install requests
python runtime.py

# with local Hugging Face models (needs GPU)
pip install torch transformers accelerate
# defaults to Qwen/Qwen2.5-7B-Instruct
python runtime.py --local-model

# enable verbose mode to inspect prompts sent to the LLM
python runtime.py --verbose
```

## Adding tools

```python
def calculator(expression):
    return str(eval(expression))

TOOLS["calculator"] = {"fn": calculator, "desc": "calculator(expression)"}
```

## License

MIT
