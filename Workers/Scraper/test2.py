from transformers import AutoModelForCausalLM, AutoTokenizer
checkpoint = "jinaai/reader-lm-1.5b"
import os,re

#The input and output files are declared
in_file="test.html"
out_file="test.txt"

#The previous output file is removed
if os.path.exists(out_file):
    os.remove(out_file)

#The model is loaded
device = "cuda"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)

#The input file is read
in_f = open(in_file,"r")
html_content=in_f.read()

#The output is generated
messages = [{"role": "user", "content": html_content}]
input_text=tokenizer.apply_chat_template(messages, tokenize=False)

inputs = tokenizer(input_text, return_tensors="pt").to(device)
outputs = model.generate(**inputs, max_new_tokens=1024, do_sample=False, repetition_penalty=1.08)

decoded = tokenizer.decode(outputs[0])

#The assistant part is issolated and saved
match = re.search(r"<\|im_start\|>assistant\s*(.*?)<\|im_end\|>", decoded, re.DOTALL)
assistant_text = match.group(1).strip() if match else decoded.strip()

out_f = open(out_file,"w")
out_f.write(assistant_text)