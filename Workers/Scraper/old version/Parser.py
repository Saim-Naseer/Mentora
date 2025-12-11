from transformers import AutoModelForCausalLM, AutoTokenizer
checkpoint = "jinaai/reader-lm-1.5b"
import os,re,time
from Chunker import chunker

#The input and output files are declared
in_file="harvard_homepage.html"
out_file="test.txt"

#The previous output file is removed
if os.path.exists(out_file):
    os.remove(out_file)

#The model is loaded
device = "cuda"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)

out_f = open(out_file, "a")

chunks = chunker(in_file)

start_time = time.time()
num=0
for c in chunks:
    num+=1
    print(num," / ",len(chunks))
    t0 = time.time()
    html_content = c
    #The output is generated
    messages = [{"role": "user", "content": html_content}]
    input_text=tokenizer.apply_chat_template(messages, tokenize=False)

    inputs = tokenizer(input_text, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=512, do_sample=False, repetition_penalty=1.08)

    decoded = tokenizer.decode(outputs[0])

    #The assistant part is issolated and saved
    match = re.search(r"<\|im_start\|>assistant\s*(.*?)<\|im_end\|>", decoded, re.DOTALL)
    assistant_text = match.group(1).strip() if match else decoded.strip()

    out_f.write(assistant_text)
    t1=time.time()
    print("Time : "+str(t1-t0))

end_time=time.time()
print("\n\n\nTotal Time"+str(end_time-start_time))
# #The input file is read
# in_f = open(in_file,"r")
# html_content=in_f.read()

# #The output is generated
# messages = [{"role": "user", "content": html_content}]
# input_text=tokenizer.apply_chat_template(messages, tokenize=False)

# inputs = tokenizer(input_text, return_tensors="pt").to(device)
# outputs = model.generate(**inputs, max_new_tokens=1024, do_sample=False, repetition_penalty=1.08)

# decoded = tokenizer.decode(outputs[0])

# #The assistant part is issolated and saved
# match = re.search(r"<\|im_start\|>assistant\s*(.*?)<\|im_end\|>", decoded, re.DOTALL)
# assistant_text = match.group(1).strip() if match else decoded.strip()

# out_f = open(out_file,"w")
# out_f.write(assistant_text)