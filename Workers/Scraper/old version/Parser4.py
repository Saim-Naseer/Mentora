# Parser_fast.py  (drop-in, minimal changes)
from transformers import AutoModelForCausalLM, AutoTokenizer
checkpoint = "jinaai/reader-lm-1.5b"
import os, re, time
from Chunker import chunker
import torch

# TUNABLES
device = "cuda"
batch_size = 4          # try 4,8; lower if OOM
max_new_tokens = 512    # reduce from 1024 -> big speedup
use_torch_compile = True  # try True if using PyTorch >=2.0
use_autocast = True     # use amp autocast for fp16
write_sep = "\n\n"

# files
in_file = "index.html"
out_file = "test.txt"
if os.path.exists(out_file):
    os.remove(out_file)

# load model/tokenizer (load as fp16 if supported)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint, torch_dtype=torch.float16).to(device)
model.eval()

if use_torch_compile:
    try:
        model = torch.compile(model)
    except Exception as e:
        print("torch.compile failed or not available:", e)

chunks = chunker(in_file)

# helper to build prompt string quickly (avoid heavy apply_chat_template per chunk)
def make_prompt_from_chunk(chunk_str):
    # simple chat-style wrapper - adjust if your tokenizer.chat template differs
    return f"<|im_start|>user\n{chunk_str}\n<|im_end|>\n<|im_start|>assistant\n"

# profiler
def now():
    torch.cuda.synchronize() if torch.cuda.is_available() else None
    return time.time()

out_f = open(out_file, "a")

# Timings
total_start = now()
i = 0
while i < len(chunks):
    batch_chunks = chunks[i:i+batch_size]
    i += batch_size

    prompts = batch_chunks

    # build prompt strings
    #prompts = [make_prompt_from_chunk(c) for c in batch_chunks]

    t0 = now()
    # tokenize as a batch (padding)
    inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True)
    t1 = now()

    # send to device
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # generate
    with torch.no_grad():
        if use_autocast:
            with torch.cuda.amp.autocast(dtype=torch.float16):
                outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False, repetition_penalty=1.08)
        else:
            outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False, repetition_penalty=1.08)
    t2 = now()

    # decode batch
    decoded_list = tokenizer.batch_decode(outputs, skip_special_tokens=False)
    t3 = now()

    # extract assistant part and write
    for decoded in decoded_list:
        match = re.search(r"<\|im_start\|>assistant\s*(.*?)<\|im_end\|>", decoded, re.DOTALL)
        assistant_text = match.group(1).strip() if match else decoded.strip()
        out_f.write(assistant_text + write_sep)

    # print timing
    print(f"Batch processed (chunks {i-len(batch_chunks)}..{i-1}): token_time={t1-t0:.2f}s gen_time={t2-t1:.2f}s decode_time={t3-t2:.2f}s total_batch={t3-t0:.2f}s")

total_end = now()
print("Total time:", total_end - total_start)
out_f.close()
