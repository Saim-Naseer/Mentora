import json
import datetime
import textwrap

PROMPT_HEADER = textwrap.dedent("""
You are a structured extractor whose job is to update an existing JSON record about a university using
information from the MARKDOWN_LIST provided. The LLM MUST return a single valid JSON object (the updated
record) and nothing else (no markdown, no commentary, no apologies).

This prompt has been extended to correctly model multi-campus universities. Each campus may have its own
programs, admissions rules, fees, contacts, and facilities. The canonical output will include a `campuses`
array where each campus contains its own `programs` array.

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

JSON_TEMPLATE = textwrap.dedent("""
                                
{
  "university": 
  {
    "name": {"val": ..., "link": ..., "confidence": ...}, 
    "short_description": {"val": ..., "link": ..., "confidence": ...}, 
    "established_year": {"val": ..., "link": ..., "confidence": ...}, 
    "type": {"val": ..., "link": ..., "confidence": ...}, 
    "ranking": [{"val": ..., "link": ..., "confidence": ...}]   
  },
 "campuses": 
  [
    {
      "name": {"val": ..., "link": ..., "confidence": ...}, 
      "is_main": {"val": ..., "link": ..., "confidence": ...}, // set to True for the primary/main campus.
      "location": 
      { 
        "address": {"val": ..., "link": ..., "confidence": ...}, 
        "city": {"val": ..., "link": ..., "confidence": ...},  
        "region": {"val": ..., "link": ..., "confidence": ...}, 
        "country": {"val": ..., "link": ..., "confidence": ...} 
      },
      "contacts_notes": [{"val": ..., "link": ..., "confidence": ...}], //this is a list of various contact details for the campus such as admissions office contact details and international office contact details and general contact details and social media links

      "facilities_notes": [{"val": ..., "link": ..., "confidence": ...}] //this tells about the various facilities that the university offers like libraries and stuff 
    }
  ],

  "programs": 
    [
      {
        "name": {"val": ..., "link": ..., "confidence": ...},  
        "department": {"val": ..., "link": ..., "confidence": ...}, //write full name if available 
        "campuses": [], //list the campuses that offer this program
        "duration": {"value": ..., "units": "months|years|semesters" , "link": ..., "confidence": ...}, 
        "credits": {"val": ..., "link": ..., "confidence": ...}, 
        "tuition_notes": [{"val": ..., "link": ..., "confidence": ...}],   //this tells about the tution fees that a national and international student has to pay to attend the program but make absolutely sure that there is an excerpt in the markdown for the aforementioned program that clearly states this fee amount for this program and also mention the text of that excerpt for every note mentioned here . do not approximate this and do not include any info unless backed by some excerpt
        "admission_requirement_for_new_student": [{"val": ..., "link": ..., "confidence": ...}],  //this tells the criterion for a new applicant to join the course such as for a bachelors applicant the admission criterion might be some kind of scores in College/High school or/and some entry tests or some other tests 
        "passing_requirement_for_enrolled_student":[{"val": ..., "link": ..., "confidence": ...}], //this is different from the admission criterion as it tells information about the requirements to pass the program for a student who is already enrolled such as credits to complete and min cgpa required and stuff like that, the other was for an applicant not an enrolled student 
        "curriculum_notes": [{"val": ..., "link": ..., "confidence": ...}], //this only lists the courses taught in this program and nothing else 
        "careers_info_notes": [{"val": ..., "link": ..., "confidence": ...}] //this tells about the future career opportunities that open after attending this program 
      }
    ],                             

  "General Admission Steps": [{"val": ..., "link": ..., "confidence": ...}], //this explains the general admission steps to guide a new applicant 

  "General Admission Notes": [{"val": ..., "link": ..., "confidence": ...}], //this mentions any information that might have been left off 

  "Scholarship_notes": [{"val": ..., "link": ..., "confidence": ...}], //explains all the points related to scholarships such as the various scholarships offered by the university and their eligibility criteria and how to apply for them and all that stuff

  "research_and_faculty_notes": [{"val": ..., "link": ..., "confidence": ...}], //this tells about the various researches done by the university 

  "student_life": {"clubs": [{"val": ..., "link": ..., "confidence": ...}], "sports": [{"val": ..., "link": ..., "confidence": ...}], "health_services": {{"val": ..., "link": ..., "confidence": ...}}, "disability_support": {"val": ..., "link": ..., "confidence": ...}}, 

  "statistics": {"acceptance_rate": {"val": ..., "link": ..., "confidence": ...}, "enrollment_total": {"val": ..., "link": ..., "confidence": ...}, "international_percentage": {"val": ..., "link": ..., "confidence": ...}, "faculty_to_student_ratio": {"val": ..., "link": ..., "confidence": ...}}, 

  "policies": {"deferral_policy": {"val": ..., "link": ..., "confidence": ...}, "transfer_credits_policy": {"val": ..., "link": ..., "confidence": ...}, "grading_scale": {"val": ..., "link": ..., "confidence": ...}}, 

  "extraction": {"last_updated": , "updated_fields": [], "per_field_confidence": {}},

  "overall_confidence": 0.0,
  "notes": [{"val": ..., "link": ..., "confidence": ...}] 
}
""")

# Human-readable explanation of how to fill key attributes (kept short and actionable for the model)
ATTR_EXPLANATION = textwrap.dedent("""
SET OF RULES TO FILL THE ATTRIBUTES:
  1. each value entered into the schema should be of the following type:
    {
      "val": //this part contains the value,
      "link"://this part contains the link of the page from where this info was extracted,
      "confidence": //this part contains the confidence score for the extracted field 
    }
  2. if u find another piece of info that disregards the previous one, u should not delete the previous one but rather add the new one as another entry.
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
    # Normalize previous_json input to a JSON string for embedding into the prompt
    prev_json_str = _stringify_json(previous_json)
    today = datetime.date.today().isoformat()

    prompt_parts = [
        PROMPT_HEADER,
        "**IMPORTANT**: correct information extraction is 100 times more important that filling fields with hallucinated data",
        "**IMPORTANT**: You must respond with ONLY the final answer (json object).  No chain of thought. No explanations. No examples. No reasoning. No nothing except the json object",
        """
            Return only the output requested, nothing more.""",
        "***Sample JSON_SCHEMA*** (the exact JSON object you MUST return, use the same keys. this is only provided to explain the attributes present in the json and how to use them):",
        JSON_TEMPLATE,
        "***EXPLANATION*** (how to fill attributes):",
        ATTR_EXPLANATION,
        "***PREVIOUS_JSON*** (this is the current extracted record — update/merge it):",
        prev_json_str,
        "***MARKDOWN_LIST***"
        " (this contains a list of markdown chunks along with the link of their extracted site sources):",
        "**IMPORTANT**: i want u to read the markdown chunk that i would provide to u piece by piece and keep filling all the fields. u should not fill in any field until unless you have identified a piece of the meta data chunk that explicitly mentions the fact that you are including into the json object",
        _stringify_json(markdown_chunk),
        "INSTRUCTIONS (required):",
        textwrap.dedent(f"""
- If the chunk is global (no campus reference), update the primary campus (`is_main: true`) or top-level `admissions` if the info is clearly global.
- Set `extraction.last_updated` to "{today}".
- Update `extraction.updated_fields` to list the top-level keys you changed in this call (e.g., ["campuses","admissions"]).
- Compute `overall_confidence` as the average of the per-field confidences you set (or 0.0 if none).
- **Extremely Important**: at the end you have to reread the entire  chunk provided to you and make sure that no information is missed. u should follow the following checklist:
    -have u extracted all the university regarding information?
    -have u extracted information regarding each campus of the university, and the programs they offer?
    -does each program entry has the requirements mentioned for the new admission and the general credtits and fees of that program?
    -is everything related the admission process mentioned?
    -also review the markdown chunk 3 times to make sure that u extracted everything from every angle that u could.
- It is also **extremely important** for u to make sure that all of the previous json is information is passed through to the next json and doesn't just vanish
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