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


def process_markdown_files(folder):

    out_file = Path(__file__).parent.parent / "Crawler" / "out.json"
    f = open(out_file, "r", encoding="utf-8")
    data = json.load(f)
    f.close()

    markdown_list = []
    files = [f for f in folder.iterdir() if f.is_file()]

    for file in files:
        link = [d for d in data if d["save_dir"]==str(file)][0]["link"]
        content = file.read_text(encoding="utf-8")
        markdown_list.append({
            "link": link,
            "markdown": content
        })

    f = open("data.json", "r", encoding="utf-8")
    prev_json = json.load(f)
    f.close()


    tokenizer = AutoTokenizer.from_pretrained("./tokenizer")

    def estimate_tokens(text):
        return len(tokenizer.encode(text))

    batch_size = 3
    MIN_BATCH = 1
    MAX_TOKENS = 65000

    debug_prompt = []

    i = 0

    while i < len(markdown_list):

        current_batch_size = batch_size

        while current_batch_size >= 1:

            batch = markdown_list[i:i+current_batch_size]

            prompt = build_prompt(prev_json, batch)

            token_count = estimate_tokens(prompt)

            if token_count <= MAX_TOKENS:
                break 

            current_batch_size -= 1

        if current_batch_size < 1:
            i += 1
            continue

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
                        Return ONLY one valid JSON object.

                        Rules:
                        - Use double quotes for all keys and string values.
                        - Do not include any text outside the JSON.
                        - Preserve ALL information from the markdown.
                        - Do not remove or summarize important details.
                        - If a field is unknown, set it to null.
                        - Follow the exact schema provided in the system prompt.

                        Priority:
                        Correct JSON structure AND maximum information retention.
                        
                        ***Extremely Important***
                        This information is being extracted to help students decide which university and program to pursue based on their academic and financial requirements. so i need max info on these things.
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
            with open("bad_responses.log", "a", encoding="utf-8") as log:
                log.write(f"\n\nAPI ERROR for batch starting at {i}:\n{e}\n")
            i += current_batch_size
            continue

        try:
            result = json.loads(cleaned_resp)
        except:
            try:
                result = json.loads(repair_json(cleaned_resp))
            except:
                with open("bad_responses.log", "a", encoding="utf-8") as log:
                    log.write(cleaned_resp + "\n\n")
                i += current_batch_size
                continue


        prev_json = result

        i += current_batch_size

    with open("debug_prompts.json", "w", encoding="utf-8") as f:
        json.dump(debug_prompt, f, indent=4, ensure_ascii=False)

    return prev_json

        


path = Path(__file__).parent.parent / "Crawler" / "cleaned_pages"

folders = [f for f in path.iterdir() if f.is_dir()]

objects = []


for folder in folders:
    result = process_markdown_files(folder)
    objects.append({
        "uni": folder.name,
        "object": result
    })

with open("final_data.json", "w", encoding="utf-8") as f:
    json.dump(objects, f, indent=4, ensure_ascii=False)