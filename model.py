"""Raw local inference. No model.generate()."""

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

# Model loading

MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"

device = "cuda" if torch.cuda.is_available() else "cpu"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, dtype=torch.float16, device_map="auto"
).eval()

# Sampling

def sample_token(logits, temperature=0.7):
    probs = F.softmax(logits / temperature, dim=-1)
    return torch.multinomial(probs, 1).item()

# Generation loop

@torch.no_grad()
def generate(messages, max_tokens=512, temperature=0.7):
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

    past_key_values = None
    generated = []

    for _ in range(max_tokens):
        out = model(input_ids, past_key_values=past_key_values, use_cache=True)
        logits = out.logits[0, -1, :]
        past_key_values = out.past_key_values

        tok = sample_token(logits, temperature)
        generated.append(tok)

        if tok == tokenizer.eos_token_id:
            break

        input_ids = torch.tensor([[tok]], device=device)

    return tokenizer.decode(generated, skip_special_tokens=True)
