# Parser.py (minimal viable speedup)
from transformers import AutoModelForCausalLM, AutoTokenizer
checkpoint = "jinaai/reader-lm-1.5b"
import os, re
from Chunker import chunker
import torch

# settings you can tune
device = "cuda"
batch_size = 4          # try 2,4,8 depending on your GPU memory
max_new_tokens = 1024   # lower this to speed up generation if acceptable

# files
in_file = "harvard_homepage.html"
out_file = "test.txt"
if os.path.exists(out_file):
    os.remove(out_file)

# load tokenizer and model in fp16
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
# Option A: load weights as fp16 directly (preferred if supported)
model = AutoModelForCausalLM.from_pretrained(checkpoint, torch_dtype=torch.float16).to(device)
# Option B (alternative): load then convert to half
# model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)
# model.half()

model.eval()   # important for inference

out_f = open(out_file, "a")
chunks = chunker(in_file)

# helper: generate for a list of chunk strings
def generate_batch(chunk_list):
    # build list of chat-formatted strings
    inputs_text = [tokenizer.apply_chat_template([{"role": "user", "content": c}], tokenize=False)
                   for c in chunk_list]

    # tokenize as a batch, pad to the longest
    inputs = tokenizer(inputs_text, return_tensors="pt", padding=True, truncation=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        # autocast to fp16 for faster kernels (works with model in fp16)
        with torch.cuda.amp.autocast(dtype=torch.float16):
            outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False, repetition_penalty=1.08)

    # decode outputs (batch)
    decoded_list = tokenizer.batch_decode(outputs, skip_special_tokens=False)
    return decoded_list

# iterate in batches
total = len(chunks)
i = 0
while i < total:
    batch_chunks = chunks[i:i+batch_size]
    print(f"Processing chunks {i+1}..{i+len(batch_chunks)} / {total}")
    decoded_list = generate_batch(batch_chunks)

    # extract assistant text from each decoded string and write
    for decoded in decoded_list:
        match = re.search(r"<\|im_start\|>assistant\s*(.*?)<\|im_end\|>", decoded, re.DOTALL)
        assistant_text = match.group(1).strip() if match else decoded.strip()
        out_f.write(assistant_text + "\n\n")

    i += batch_size

out_f.close()
