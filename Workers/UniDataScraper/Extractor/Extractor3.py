import os
from pathlib import Path
from groq import Groq
import json
from dotenv import load_dotenv
from build_prompt import build_prompt
from transformers import AutoTokenizer
from json import JSONDecodeError
from json_repair import repair_json


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
dotenv_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path)

client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=300000)

tokenizer = AutoTokenizer.from_pretrained("./tokenizer")

def process_pdf_files(pdf_files):

    f = open("final_data2.json", "r", encoding="utf-8")
    data2 = json.load(f)
    f.close()

    uni = pdf_files[0]["uni"]

    if uni not in [d["uni"] for d in data2]:
        uni = "GCU"

    print("now processing uni", uni)

    prev_json = [d for d in data2 if d["uni"]==uni][0]["object"] 

    batch_size = 3

    debug_prompt = []

    for i in range(0,len(pdf_files),batch_size):

        prompt = build_prompt(prev_json, pdf_files[i:i+batch_size])

        debug_prompt.append(prompt)

        try:

            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                max_tokens=60000,
                temperature=0,
                top_p=0.9,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user", 
                        "content": """
                        Return one JSON object only. Do not return an array at the top level.
                        reply with only the json object as per the format mentioned in the prompt without any additional text or explanation.

                        Don't worry about tokens, fill in as much information as you can based on the markdown chunk.

                        Return STRICT valid JSON.
                        U may update content from the previous json
                        Provide the complete json, dont write things like "... (remaining programs unchanged except additions)". if something is unchanged, still include it. because i would just save your final provided json.
                        All objects must be real JSON objects, not strings.
                        Retrun the json object with all the fields filled as much as possible based on the information in the markdown chunk. u may only chose to not fill a field as null or empty if its confidence score is extremely low
                        
                        ***Extremely Important***
                        This information is being extracted to help students decide which university and program to pursue based on their academic and financial requirements. so i need max info on these things.
                        U should keep the previous information as is, but should also try to fill as many fields as u can (especially related to programs offered, their fees, academic requirements or anything an interested student should know). This is extremely vital.
                        """
                    }
                ],
                response_format = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "university_extraction",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "university",
                                "campuses",
                                "programs",
                                "General Admission Steps",
                                "General Admission Notes",
                                "Scholarship_notes",
                                "research_and_faculty_notes",
                                "student_life",
                                "statistics",
                                "policies",
                                "extraction",
                                "overall_confidence",
                                "notes"
                            ],
                            "properties": {
                                "university": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["name", "short_description", "established_year", "type", "ranking"],
                                    "properties": {
                                        "name": { "$ref": "#/$defs/value_string" },
                                        "short_description": { "$ref": "#/$defs/value_string" },
                                        "established_year": { "$ref": "#/$defs/value_integer" },
                                        "type": { "$ref": "#/$defs/value_string" },
                                        "ranking": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        }
                                    }
                                },

                                "campuses": {
                                    "type": "array",
                                    "items": { "$ref": "#/$defs/campus" }
                                },

                                "programs": {
                                    "type": "array",
                                    "items": { "$ref": "#/$defs/program" }
                                },

                                "General Admission Steps": {
                                    "type": "array",
                                    "items": { "$ref": "#/$defs/list_item" }
                                },

                                "General Admission Notes": {
                                    "type": "array",
                                    "items": { "$ref": "#/$defs/list_item" }
                                },

                                "Scholarship_notes": {
                                    "type": "array",
                                    "items": { "$ref": "#/$defs/list_item" }
                                },

                                "research_and_faculty_notes": {
                                    "type": "array",
                                    "items": { "$ref": "#/$defs/list_item" }
                                },

                                "student_life": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["clubs", "sports", "health_services", "disability_support"],
                                    "properties": {
                                        "clubs": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        },
                                        "sports": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        },
                                        "health_services": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        },
                                        "disability_support": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        }
                                    }
                                },

                                "statistics": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": [
                                        "acceptance_rate",
                                        "enrollment_total",
                                        "international_percentage",
                                        "faculty_to_student_ratio"
                                    ],
                                    "properties": {
                                        "acceptance_rate": { "$ref": "#/$defs/value_number" },
                                        "enrollment_total": { "$ref": "#/$defs/value_integer" },
                                        "international_percentage": { "$ref": "#/$defs/value_number" },
                                        "faculty_to_student_ratio": { "$ref": "#/$defs/value_string" }
                                    }
                                },

                                "policies": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["deferral_policy", "transfer_credits_policy", "grading_scale"],
                                    "properties": {
                                        "deferral_policy": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        },
                                        "transfer_credits_policy": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        },
                                        "grading_scale": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        }
                                    }
                                },

                                "extraction": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["last_updated", "updated_fields", "per_field_confidence"],
                                    "properties": {
                                        "last_updated": {
                                            "type": "string"
                                        },
                                        "updated_fields": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        },
                                        "per_field_confidence": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "additionalProperties": False,
                                                "required": ["field", "confidence"],
                                                "properties": {
                                                    "field": { "type": "string" },
                                                    "confidence": { "type": "number" }
                                                }
                                            }
                                        }
                                    }
                                },

                                "overall_confidence": {
                                    "type": "number"
                                },

                                "notes": {
                                    "type": "array",
                                    "items": { "$ref": "#/$defs/list_item" }
                                }
                            },

                            "$defs": {
                                "list_item": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["val", "link", "confidence"],
                                    "properties": {
                                        "val": {
                                            "type": ["string", "number", "boolean", "null"]
                                        },
                                        "link": {
                                            "type": "string"
                                        },
                                        "confidence": {
                                            "type": "number"
                                        }
                                    }
                                },

                                "value_string": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["val", "link", "confidence"],
                                    "properties": {
                                        "val": { "type": ["string", "null"] },
                                        "link": { "type": "string" },
                                        "confidence": { "type": "number" }
                                    }
                                },

                                "value_integer": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["val", "link", "confidence"],
                                    "properties": {
                                        "val": { "type": ["integer", "null"] },
                                        "link": { "type": "string" },
                                        "confidence": { "type": "number" }
                                    }
                                },

                                "value_number": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["val", "link", "confidence"],
                                    "properties": {
                                        "val": { "type": ["number", "null"] },
                                        "link": { "type": "string" },
                                        "confidence": { "type": "number" }
                                    }
                                },

                                "value_boolean": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["val", "link", "confidence"],
                                    "properties": {
                                        "val": { "type": ["boolean", "null"] },
                                        "link": { "type": "string" },
                                        "confidence": { "type": "number" }
                                    }
                                },

                                "campus": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["name", "is_main", "location", "contacts_notes", "facilities_notes"],
                                    "properties": {
                                        "name": { "$ref": "#/$defs/value_string" },
                                        "is_main": { "$ref": "#/$defs/value_boolean" },
                                        "location": {
                                            "type": "object",
                                            "additionalProperties": False,
                                            "required": ["address", "city", "region", "country"],
                                            "properties": {
                                                "address": { "$ref": "#/$defs/value_string" },
                                                "city": { "$ref": "#/$defs/value_string" },
                                                "region": { "$ref": "#/$defs/value_string" },
                                                "country": { "$ref": "#/$defs/value_string" }
                                            }
                                        },
                                        "contacts_notes": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        },
                                        "facilities_notes": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        }
                                    }
                                },

                                "program": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": [
                                        "name",
                                        "department",
                                        "campuses",
                                        "duration",
                                        "credits",
                                        "tuition_notes",
                                        "admission_requirement_for_new_student",
                                        "passing_requirement_for_enrolled_student",
                                        "curriculum_notes",
                                        "careers_info_notes"
                                    ],
                                    "properties": {
                                        "name": { "$ref": "#/$defs/value_string" },
                                        "department": { "$ref": "#/$defs/value_string" },
                                        "campuses": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        },
                                        "duration": {
                                            "type": "object",
                                            "additionalProperties": False,
                                            "required": ["val", "units", "link", "confidence"],
                                            "properties": {
                                                "val": {
                                                    "type": ["number", "null"]
                                                },
                                                "units": {
                                                    "type": "string"
                                                },
                                                "link": {
                                                    "type": "string"
                                                },
                                                "confidence": {
                                                    "type": "number"
                                                }
                                            }
                                        },
                                        "credits": { "$ref": "#/$defs/value_integer" },
                                        "tuition_notes": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        },
                                        "admission_requirement_for_new_student": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        },
                                        "passing_requirement_for_enrolled_student": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        },
                                        "curriculum_notes": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        },
                                        "careers_info_notes": {
                                            "type": "array",
                                            "items": { "$ref": "#/$defs/list_item" }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            )

            cleaned_resp = response.choices[0].message.content

        except Exception as e:
            with open("bad_responses2.log", "a", encoding="utf-8") as log:
                log.write(f"\n\nAPI ERROR for batch starting at {i}:\n{e}\n")
            continue
        try:
            result = json.loads(cleaned_resp)
        except:
            try:
                result = json.loads(repair_json(cleaned_resp))
            except:
                with open("bad_responses3.log", "a", encoding="utf-8") as log:
                    log.write(cleaned_resp + "\n\n")
                continue

        prev_json = result

    with open("debug_prompts.json", "w", encoding="utf-8") as f:
        json.dump(debug_prompt, f, indent=4, ensure_ascii=False)

    return prev_json

        

out_file = Path(__file__).parent.parent / "Crawler" / "out3.json"
f = open(out_file, "r", encoding="utf-8")
data = json.load(f)
f.close()

unis = set([d["uni"] for d in data])

print(unis)

def estimate_tokens(text):
    return len(tokenizer.encode(text))

new_list = []
for d in data:
    tokens = estimate_tokens(str(d))
    if tokens>12000:
        pieces=(tokens//12000)+1
        length = len(d["text"])
        piece_length = length//pieces
        gap = piece_length//4
        for i in range(pieces):
            if i==0:
                link = d["link"]
                uni = d["uni"]
                text = d["text"][0:piece_length]
                new_list.append({"link":link,"uni":uni,"text":text})
            else:
                link = d["link"]
                uni = d["uni"]
                text = d["text"][(i*piece_length)-gap:(i+1)*piece_length]
                new_list.append({"link":link,"uni":uni,"text":text})
    else:
        new_list.append(d)

objects = []

for uni in unis:
    pdf_files = [d for d in new_list if d["uni"]==uni]
    result = process_pdf_files(pdf_files)
    objects.append({
        "uni": uni,
        "object": result
    })

with open("sample.json", "w", encoding="utf-8") as f:
    json.dump(objects, f, indent=4, ensure_ascii=False)

with open("final_data2.json", "r", encoding="utf-8") as f:
    uni_data = json.load(f)
    for d in uni_data:
        if d["uni"] not in [o["uni"] for o in objects]:
            objects.append(d)

with open("final_data3.json", "w", encoding="utf-8") as f:
    json.dump(objects, f, indent=4, ensure_ascii=False)