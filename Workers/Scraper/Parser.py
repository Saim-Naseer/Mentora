# minimal chunked version of your original script
import os, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

checkpoint = "jinaai/reader-lm-1.5b"
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)
model.eval()

# read html
html_content = open("harvard_homepage.html", "r", encoding="utf-8").read()
messages = [{"role": "user", "content": html_content}]
input_text = tokenizer.apply_chat_template(messages, tokenize=False)

# tokenize once to token ids
token_ids = tokenizer.encode(input_text, add_special_tokens=True)
print("Total input tokens:", len(token_ids))

# chunk settings (~4k chunks)
CHUNK = 4096
OVERLAP = 128
MAX_NEW_TOKENS = 512   # tweak down if you hit OOM
step = CHUNK - OVERLAP

OUT_FILE = "harvard_cleaned.txt"
if os.path.exists(OUT_FILE):
    os.remove(OUT_FILE)

i = 0
chunk_idx = 0
while i < len(token_ids):
    chunk_ids = token_ids[i : i + CHUNK]
    print(f"Chunk {chunk_idx}: tokens {i}..{i+len(chunk_ids)} (len={len(chunk_ids)})")
    input_ids = torch.tensor([chunk_ids], dtype=torch.long).to(device)
    attention_mask = torch.ones_like(input_ids, dtype=torch.long).to(device)

    try:
        with torch.inference_mode():
            torch.cuda.empty_cache()
            outputs = model.generate(
                input_ids,
                attention_mask=attention_mask,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                repetition_penalty=1.08,
                use_cache=True
            )
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        with open(OUT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n\n<!-- chunk {chunk_idx} -->\n")
            f.write(decoded)
        chunk_idx += 1
        i += step
    except RuntimeError as e:
        msg = str(e).lower()
        if "out of memory" in msg and CHUNK > 512:
            # reduce chunk and retry
            old = CHUNK
            CHUNK = max(512, CHUNK // 2)
            step = CHUNK - OVERLAP
            print(f"OOM -> reducing CHUNK {old} -> {CHUNK} and retrying this chunk")
            torch.cuda.empty_cache()
            continue
        else:
            raise

print("Done — output written to", OUT_FILE)
