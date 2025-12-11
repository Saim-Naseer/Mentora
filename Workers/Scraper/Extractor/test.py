from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from prompt import build_prompt, _stringify_json
import os,time

model_id = "Qwen/Qwen2.5-7B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id)

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-7B-Instruct",
    device_map="auto",
    torch_dtype=torch.float16,
    load_in_4bit=True,
)


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


json= {
  "university": {
    "name": "",
    "aliases": [],
    "website": "",
    "short_description": "",
    "established_year": None,
    "type": "",
    "logo": "",
    "brochures": [],
    "ranking": [],
    "accreditation": []
  },

  "campuses": [
    {
      "campus_id": "", 
      "name": "",
      "is_main": False,
      "location": {
        "address": "",
        "city": "",
        "region": "",
        "postal_code": "",
        "country": "",
        "coordinates": {"lat": None, "lon": None}
      },
      "contacts": {
        "admissions": {"name": "", "email": "", "phone": "", "office_hours": ""},
        "international_office": {"email": "", "phone": ""},
        "general": {"phone": "", "fax": "", "mailing_address": ""},
        "social": {"facebook": "", "twitter": "", "instagram": "", "linkedin": "", "youtube": ""}
      },

      "programs": [
        {
          "program_id": "",
          "name": "",
          "degree": "",
          "level": "",
          "department": "",
          "duration": {"value": None, "units": "months|years|semesters"},
          "study_mode": ["full-time"],
          "start_terms": [],
          "credits": None,
          "tuition": [
            {"amount": None, "currency": "", "period": "year|semester|credit", "applicability": "domestic|intl|all", "notes": "", "source": "", "confidence": None}
          ],
          "fees_breakdown": [],
          "entry_requirements": {
            "min_qualification": "",
            "min_gpa": None,
            "grades_required": "",
            "standardized_tests": [],
            "work_experience_required": False,
            "documents_required": [],
            "english_requirements": {}
          },
          "application_deadlines": [],
          "application_url": "",
          "curriculum": {},
          "careers_info": {},
          "notes_raw": []
        }
      ],

      "facilities": {
        "housing": {},
        "libraries": [],
        "labs": [],
        "sports": []
      }
    }
  ],

  "admissions": {"application_portal": "", "general_deadlines": [], "application_steps": [], "deposit_amount": {"amount": None, "currency": "", "deadline": ""}, "refund_policy": ""},

  "fees_and_funding": {"typical_tuition_domestic": {"amount": None, "currency": ""}, "typical_tuition_international": {"amount": None, "currency": ""}, "mandatory_fees": [], "scholarships": [], "assistantships": [], "living_costs_monthly": {"amount": None, "currency": "", "notes": ""}},

  "research_and_faculty": {"centers": [], "notable_faculty": [], "research_partnerships": []},

  "student_life": {"clubs": [], "sports": [], "health_services": {}, "disability_support": ""},

  "statistics": {"acceptance_rate": None, "enrollment_total": None, "international_percentage": None, "faculty_to_student_ratio": ""},

  "policies": {"deferral_policy": "", "transfer_credits_policy": "", "grading_scale": ""},

  "sources": [],

  "extraction": {"last_updated": "", "updated_fields": [], "per_field_confidence": {}},

  "overall_confidence": 0.0,
  "notes": []
}

start_time = time.time()

file = open("pages","r")
markdown=file.read()
prompt = build_prompt(_stringify_json(json),markdown)

# Encode to get token IDs
tokens = tokenizer.encode(prompt)
token_count = len(tokens)

print(f"Token count of prompt: {token_count}")

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
output_ids = model.generate(
    **inputs,
    max_new_tokens=5000,
    temperature=0.7,
    do_sample=True,
    top_p=0.9,
)
generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

response = generated_text[len(prompt):].strip()
answer = generated_text[len(prompt):].strip()

end_time = time.time()

if os.path.exists("out.txt"):
    os.remove("out.txt")

outfile = open("out.txt","w")

outfile.write(answer)

print("\n\nTime Taken : "+str(end_time-start_time))

#     answer = response.split('\n\n')[0]
#     reasoning = response.split('\n\n')[1]
#     answers.append({"ans":answer,"reason":reasoning})

# for a in answers:
#     print("Answer = ",a["ans"])
#     print("Reasoning = ",a["reason"])
#     print("\n\n")


