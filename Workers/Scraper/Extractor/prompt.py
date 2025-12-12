import json
import datetime
import textwrap

PROMPT_HEADER = textwrap.dedent("""
You are a structured extractor whose job is to update an existing JSON record about a university using
information from a single MARKDOWN_CHUNK. The LLM MUST return a single valid JSON object (the updated
record) and nothing else (no markdown, no commentary, no apologies).

But make sure to complete the response within 6500 tokens since any amount of tokens above that are curtailed and chopped off. This is extremely important. 

This prompt has been extended to correctly model multi-campus universities. Each campus may have its own
programs, admissions rules, fees, contacts, and facilities. The canonical output will include a `campuses`
array where each campus contains its own `programs` array.

Requirements summary (enforced):
- INPUTS embedded below: PREVIOUS_JSON (the previously-extracted record) and MARKDOWN_CHUNK (the new markdown text).
- OUTPUT: one JSON object only — the full updated record following the JSON template below.
- Do not output any explanation text.
- Set `extraction.last_updated` to today's date (YYYY-MM-DD). Update `extraction.updated_fields` and
  `extraction.per_field_confidence` for any fields you changed in this pass.

Merging & campus assignment rules (apply strictly):
1. If the MARKDOWN_CHUNK explicitly names a campus (e.g., "Lahore Campus", "Main Campus", "City Branch"), attach
   extracted program/fee/contact details to that campus object inside `campuses`. If such a campus does not yet exist in
   PREVIOUS_JSON, create it with `name` equal to the extracted campus name and set `location`/`contacts` if available.
2. If the chunk clearly refers to "main" or the university homepage without specifying a campus, attach new data to the
   `campuses` entry whose `is_main` flag is true (create `is_main: true` for the primary campus). 
3. If the chunk mentions multiple campus names and lists campus-specific items, create or update the relevant campus entries
   and attach only the corresponding programs/fees/contacts to each.
4. If no campus can be determined from the chunk note uncertainty in `notes`.
5. Follow the previous merging / conflict rules: never delete existing data; append or preserve previous values when conflicts occur.

Normalization rules (apply when possible):
- Dates → ISO `YYYY-MM-DD`. If only month+year present use `YYYY-MM-01` and set a `notes` entry explaining approximation.
- Currency → 3-letter ISO code if present (e.g., PKR, USD). Keep numeric in `amount`. Do NOT perform currency conversion.
- Durations → store numeric + units (`months`/`years`/`semesters`).
- Phone numbers → store as-is but strip excessive whitespace.
- Standardized tests → normalize names (IELTS, TOEFL, GRE, GMAT, SAT).

Confidence guideline (use as hint):
- 0.9-1.0: explicit exact statements in the chunk ("Tuition: PKR 450,000 per year").
- 0.6-0.89: clearly stated but with slight ambiguity ("about 2 years").
- 0.3-0.59: partially-specified or inferred.
- 0.0-0.29: guessy — prefer None and put reasoning into `notes`.

IMPORTANT: the model must produce VALID JSON only. No additional text is allowed.
""")

# Canonical JSON template the LLM should output. Keep field names stable.
# Note: top-level `campuses` array is the primary place to store campus-specific programs/fees/contacts.
JSON_TEMPLATE = textwrap.dedent("""
Remove any string , int , list,dict or any other field that is completely empty from the output json and do not include it there. (please don't do that)
{
  "university": {
    "name": "", //remove from output json if empty or null or None
    "short_description": "", //remove from output json if empty or null or None
    "established_year": None, //remove from output json if empty or null or None
    "type": "", //remove from output json if empty or null or None
    "ranking": []   //remove from output json if empty or null or None
  },

  "campuses": [
    {
      "name": "", //remove from output json if empty or null or None
      "is_main": False, //remove from output json if empty or null or None
      "location": { 
        "address": "", //remove from output json if empty or null or None
        "city": "",  //remove from output json if empty or null or None
        "region": "", //remove from output json if empty or null or None
        "country": "" //remove from output json if empty or null or None
      },
      "contacts": {
        "admissions": {"name": "", "email": "", "phone": "", "office_hours": ""}, //remove from output json if empty or null or None
        "international_office": {"email": "", "phone": ""}, //remove from output json if empty or null or None
        "general": {"phone": "", "fax": "", "mailing_address": ""}, //remove from output json if empty or null or None
        "social": {"facebook": "", "twitter": "", "instagram": "", "linkedin": "", "youtube": ""} //remove from output json if empty or null or None
      },

      "programs": [
        {
          "name": "", //remove from output json if empty or null or None 
          "department": "", //write full name if available //remove from output json if empty or null or None
          "duration": {"value": None, "units": "months|years|semesters"}, //remove from output json if empty or null or None
          "credits": None, //remove from output json if empty or null or None
          "tuition_notes": [],   //this tells about the tution fees that a national and international student has to pay to attend the program but make absolutely sure that there is an excerpt in the markdown for the aforementioned program that clearly states this fee amount for this program and also mention the text of that excerpt for every note mentioned here . do not approximate this and do not include any info unless backed by some excerpt//remove from output json if empty or null or None
          "minimum_requirements_to_get_admitted_to_program_notes": []  //this tells the criterion for a new applicant to join the course such as for a bachelors applicant the admission criterion might be some kind of scores in College/High school or/and some entry tests or some other tests //remove from output json if empty or null or None
          "minimum_requirements_to_pass_this_program_notes":[], //this is different from the admission criterion as it tells information about the requirements to pass the program for a student who is already enrolled such as credits to complete and min cgpa required and stuff like that, the other was for an applicant not an enrolled student //remove from output json if empty or null or None
          "curriculum_notes": [], //this only lists the courses taught in this program and nothing else //remove from output json if empty or null or None
          "careers_info_notes": [] //this tells about the future career opportunities that open after attending this program //remove from output json if empty or null or None
        }
      ],

      "facilities_notes": [] //this tells about the various facilities that the university offers like libraries and stuff //remove from output json if empty or null or None
    }
  ],

  "General Admission Steps": [], //this explains the general admission steps to guide a new applicant //remove from output json if empty or null or None

  "General Admission Notes": [], //this mentions any information that might have been left off //remove from output json if empty or null or None

  "Scholarship_notes": [], //remove from output json if empty or null or None

  "research_and_faculty_notes": [], //this tells about the various researches done by the university //remove from output json if empty or null or None

  "student_life": {"clubs": [], "sports": [], "health_services": {}, "disability_support": ""}, //remove from output json if empty or null or None

  "statistics": {"acceptance_rate": None, "enrollment_total": None, "international_percentage": None, "faculty_to_student_ratio": None}, //remove from output json if empty or null or None

  "policies": {"deferral_policy": "", "transfer_credits_policy": "", "grading_scale": ""}, //remove from output json if empty or null or None

  "extraction": {"last_updated": "", "updated_fields": [], "per_field_confidence": {}},

  "overall_confidence": 0.0,
  "notes": [] //remove from output json if empty or null or None
}

""")

# Human-readable explanation of how to fill key attributes (kept short and actionable for the model)
ATTR_EXPLANATION = textwrap.dedent("""
EXPLANATION OF SELECTED FIELDS (how to fill them) — campus-aware:

- campuses[].name: use explicit campus names from the chunk when present (e.g., "Lahore Campus", "Downtown Campus").
- campuses[].is_main: set true for the primary/main campus. If the chunk is the university homepage or clearly primary, mark is_main true.
- campuses[].location: fill address/city/country when available. coordinates only if explicit.

- campuses[].contacts: put campus-specific admissions/international/office contacts here. If the chunk lists a general university admissions email without campus specificity,
  put it at the top-level `admissions.application_portal` and in the `campuses` entries that appear most relevant (prefer main campus).

- admissions (top-level): use for application portal URLs and cross-campus deadlines or global rules that apply to all campuses.

- sources: append a minimal provenance object for anything you fill. Include a short quoted snippet (<= 200 chars) extracted from MARKDOWN_CHUNK and an extraction_timestamp (YYYY-MM-DD).

- extraction.per_field_confidence: map JSON pointer strings (e.g., "campuses[0].programs[0].tuition[0]") to the confidence you assign.

- overall_confidence: average of values in extraction.per_field_confidence (set to 0.0 if none).

U keep making the following mistakes, so i am listing them here so u don't repeat them:
1) u keep on adding the fields even though they have no value and are empty strings or empty lists or in general None
2) u keep confusing admission criterion with passing criterion, how can the admission criterion of a bachelors program be min 2.0 cgpa that is a passing criterion not an admission criterion. admission criterion of a bachelors program would be something like : scoring more than 60 percent in FSc (in pakistan's example. this fact is just an example so don't use this fact)
3) only provide the source excerpt for the tuition fees and no other field.
4) provide the response within 6500 tokens or around 1500 words so that it can fit inside the output size and won't curtail

If a value is ambiguous or inferred, prefer leaving it None and explain inference in `notes`.
""")


def _stringify_json(obj):
    """Return pretty-printed JSON string suitable for embedding into the prompt."""
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except Exception:
        if isinstance(obj, str):
            return obj
        return json.dumps({}, ensure_ascii=False)


def build_prompt(previous_json, markdown_chunk):
    """Construct the full prompt string.

    Args:
      previous_json (dict or JSON-string): the current JSON object (may be partial). If dict, it will be stringified.
      markdown_chunk (str): the markdown text chunk the model should extract information from.

    Returns:
      str: a single large prompt string you can send to your model.
    """
    # Normalize previous_json input to a JSON string for embedding into the prompt
    prev_json_str = _stringify_json(previous_json)
    today = datetime.date.today().isoformat()

    prompt_parts = [
        PROMPT_HEADER,
        "**Extremely Extremely Important **: make sure to answer within 7000 tokens because majority of your responses are being curtailed"
        "**IMPORTANT**: correct information extraction is 100 times more important that filling fields with hallucinated data",
        "**IMPORTANT**: You must respond with ONLY the final answer (json object).  No chain of thought. No explanations. No examples. No reasoning. No nothing except the json object",
        """
        **Extremely Important**:
        When solving tasks, provide only the final answer. 
            Do not explain your reasoning. 
            Do not provide examples or context. 
            Do not analyze the question.
            Return only the output requested, nothing more.""",
        "JSON_SCHEMA (the exact JSON object you MUST return, use the same keys):",
        "**EXTREMELY IMPORTANT NOTICE**: the prev json might not have all the fields since it only has the fields it has the info of. so tahts why u are provided with the template, so u can fill in and add any new fields if you find info about them, or update any old field in the previous provided json",
        JSON_TEMPLATE,
        "**IMPORTANT**: the most important information is program information and the course information. especially the admission criterion and fee structure. Make extremely sure to fill as many as possible and give the most attention to filling these. if you are not certain and don't have a markdown chunk excerpt to backup your fact, don't include it. these are the most crucial information of this whole extraction process",
        "EXPLANATION (how to fill attributes):",
        ATTR_EXPLANATION,
        "PREVIOUS_JSON (this is the current extracted record — update/merge it):",
        prev_json_str,
        "MARKDOWN_CHUNK (extract from this text and update the JSON above):",
        "**IMPORTANT**: i want u to read the markdown chunk that i would provide to u piece by piece and keep filling all the fields. u should not fill in any field until unless you have identified a piece of the meta data chunk that explicitly mentions the fact that you are including into the json object otherwise keep it empty or the previous value that it had",
        markdown_chunk,
        "INSTRUCTIONS (required):",
        textwrap.dedent(f"""
- **DO NOT i repeat DO NOT** provide notes such as u can find amdission details on this site or those details on that site. 
- It is **EXTREMELY IMPORTANT** for you to only include the fields in the output json, for which u have a value for. if you do not have the value of any one of the fields, u should not include that field in the output json. due to lack of output tokens, we have to only include the fields which provide valuable info and not the ones that are empty.
- Identify whether the MARKDOWN_CHUNK refers to a specific campus. If a campus name is present, add or update that campus entry inside `campuses` and attach campus-level programs/fees/contacts there.
- If the chunk is global (no campus reference), update the primary campus (`is_main: true`) or top-level `admissions` if the info is clearly global.
- For each field you change or fill, include a `confidence` (0.0-1.0) near the field where schema supports it and add an entry to `extraction.per_field_confidence`.
- Set `extraction.last_updated` to "{today}".
- Update `extraction.updated_fields` to list the top-level keys you changed in this call (e.g., ["campuses","admissions"]).
- Compute `overall_confidence` as the average of the per-field confidences you set (or 0.0 if none).
- IMPORTANT: RETURN ONLY THE FULL UPDATED JSON OBJECT. No comments, no code fences, no extra text.
- **Extremely Important**: at the end you have to reread the entire  chunk provided to you and make sure that no information is missed. u should follow the following checklist:
    -have u extracted all the university regarding information?
    -have u extracted information regarding each campus of the university, and the programs they offer?
    -does each program entry has the requirements mentioned for the new admission and the general credtits and fees of that program?
    -is everything related the admission process mentioned?
    -also review the markdown chunk 3 times to make sure that u extracted everything from every angle that u could.
- It is also **extremely important** for u to make sure that majority or all of the previous json is information is passed through to the next json and doesn't just vanish
""")
    ]

    return "".join(prompt_parts)


# # Convenience constant: a minimal empty template you can use as a starting PREVIOUS_JSON
# EMPTY_TEMPLATE = json.loads(JSON_TEMPLATE)


# if __name__ == "__main__":
#     # quick local test/demo
#     demo_prev = EMPTY_TEMPLATE
#     demo_chunk = """
# ### Lahore Campus — Computer Science (MSc)
# Duration: 2 years (full-time). Tuition (Lahore campus): PKR 450,000 per year for international students; PKR 180,000 per year for domestic students.
# Start: Fall (September). Requirements: Bachelor's degree in CS or equivalent, minimum 16 years of education, IELTS 6.5 overall.
# Apply at https://example.edu/apply
# Contact admissions: lahore-admissions@example.edu; +92 42 111 222 333
# """
#     print(build_prompt(demo_prev, demo_chunk)[:2000])  # print first 2k chars of prompt for quick verification
