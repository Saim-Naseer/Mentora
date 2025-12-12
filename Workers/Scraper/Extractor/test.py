from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from prompt import build_prompt, _stringify_json
import os,time
import json
import re

model_id = "Qwen/Qwen2.5-7B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id)

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct",
    device_map="auto",
    torch_dtype=torch.float16,
    load_in_4bit=True,
)

def extract_json(text):
    match = re.search(r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return None


def extraction(chunk):
    questions = [
        "What is your name?",
        "What is 2 + 2?",
        "Who is the president of the US?",
    ]

    answers = []

    for q in questions:
        prompt = f"Question: {q}. also note that i do not need any explanation along with the answer. u should only reply with the answer and no extra words\nAnswer:"
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        output_ids = model.generate(
            **inputs,
            max_new_tokens=50,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
        )
        generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        response = generated_text[len(prompt):].strip()
        answer = generated_text[len(prompt):].strip()
        print(answer)
        answers.append(answer)

    print(answers)

#extraction(1)

def chunk_text_with_overlap(text, chunk_size=5000, overlap=500):
    # Tokenize entire text
    tokens = tokenizer.encode(text)
    total_tokens = len(tokens)
    
    chunks = []
    start = 0
    
    while start < total_tokens:
        end = min(start + chunk_size, total_tokens)
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        chunks.append(chunk_text)
        
        # Move start pointer back by overlap for next chunk
        start = end - overlap if end - overlap > start else end

    with open("deb.txt","w") as file:
        file.write(str(chunks))

    return chunks


# json_obj= {
#   "university": {
#     "name": "",
#     "short_description": "",
#     "established_year": None,
#     "type": "",
#     "ranking": []
#   },

#   "campuses": [
#     {
#       "name": "",
#       "is_main": False,
#       "location": {
#         "address": "",
#         "city": "",
#         "region": "",
#         "country": ""
#       },
#       "contacts": {
#         "admissions": {"name": "", "email": "", "phone": "", "office_hours": ""},
#         "international_office": {"email": "", "phone": ""},
#         "general": {"phone": "", "fax": "", "mailing_address": ""},
#         "social": {"facebook": "", "twitter": "", "instagram": "", "linkedin": "", "youtube": ""}
#       },

#       "programs": [
#         {
#           "name": "",
#           "department": "",
#           "duration": {"value": None, "units": "months|years|semesters"},
#           "credits": None,
#           "tuition_notes": [],
#           "admission_criterion_notes": [],
#           "passing_criterion_notes":[],
#           "application_notes": [],
#           "curriculum_notes": [],
#           "careers_info_notes": []
#         }
#       ],

#       "facilities_notes": []
#     }
#   ],

#   "General Admission Steps": [],

#   "General Admission Notes": [],

#   "Scholarship_notes": [],

#   "research_and_faculty_notes": [],

#   "student_life": {"clubs": [], "sports": [], "health_services": {}, "disability_support": ""},

#   "statistics": {"acceptance_rate": None, "enrollment_total": None, "international_percentage": None, "faculty_to_student_ratio": None},

#   "policies": {"deferral_policy": "", "transfer_credits_policy": "", "grading_scale": ""},

#   "sources": [],

#   "extraction": {"last_updated": "", "updated_fields": [], "per_field_confidence": {}},

#   "overall_confidence": 0.0,
#   "notes": []
# }

json_obj={}
    


start_time = time.time()

file = open("pages","r")
markdown=file.read()


prompt = build_prompt(_stringify_json(json_obj),markdown)

# Encode to get token IDs
tokens = tokenizer.encode(prompt)
token_count = len(tokens)

print(f"Token count of prompt: {token_count}")

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(
    **inputs,
    max_new_tokens=8000,
    temperature=0.2,
    top_p=0.9,
    do_sample=False
)

generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
response = generated_text[len(prompt):].strip() 


# Remove prompt
model_output = generated_text[len(prompt):].strip()

# Extract strict JSON
# json_str = extract_json(model_output)
# if not json_str:
#     print("❌ Model did not return JSON")
#     print(model_output)

#json_obj = json.loads(json_str)


# markdown_tokens = tokenizer.encode(markdown)
# markdown_token_count = len(markdown_tokens)


# chunk_size = (markdown_token_count//100) * 25
# overlap_size = (chunk_size//100)*10

# chunks = chunk_text_with_overlap(markdown, chunk_size, overlap_size)

# print("markdown tokens : "+str(markdown_token_count))
# print("chunk Size : "+str(chunk_size))
# print("overlap size : "+str(overlap_size))

# i=0

# for c in chunks:
#     i+=1
#     print(str(i)+" / "+str(len(chunks)))
#     i_1 = time.time()
#     prompt = build_prompt(_stringify_json(json_obj),c)

#     # Encode to get token IDs
#     tokens = tokenizer.encode(prompt)
#     token_count = len(tokens)

#     print(f"Token count of prompt: {token_count}")

#     inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    # outputs = model.generate(
    #     **inputs,
    #     max_new_tokens=1500,
    #     temperature=0.2,
    #     top_p=0.9,
    #     do_sample=False,
    #     return_dict_in_generate=True,
    # )

    # generated_ids = outputs.sequences[0]
    # generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)

    # # Remove prompt
    # model_output = generated_text[len(prompt):].strip()

    # # Extract strict JSON
    # json_str = extract_json(model_output)
    # if not json_str:
    #     print("❌ Model did not return JSON")
    #     print(model_output)
    #     continue

    # json_obj = json.loads(json_str)


    # i_2 = time.time()
    # print("Time Taken : "+str(i_2-i_1))

    # print("\n\n")

end_time = time.time()
print("Time Taken : "+str(end_time-start_time))

if os.path.exists("out3.txt"):
    os.remove("out3.txt")

outfile = open("out3.txt","w")

#outfile.write(_stringify_json(json_obj))
outfile.write(model_output)


#     answer = response.split('\n\n')[0]
#     reasoning = response.split('\n\n')[1]
#     answers.append({"ans":answer,"reason":reasoning})

# for a in answers:
#     print("Answer = ",a["ans"])
#     print("Reasoning = ",a["reason"])
#     print("\n\n")


