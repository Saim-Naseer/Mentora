import json
import datetime
import textwrap

PROMPT_HEADER = textwrap.dedent("""
You are a structured extractor whose job is to update an existing JSON record about a university using
information from a single MARKDOWN_CHUNK. The LLM MUST return a single valid JSON object (the updated
record) and nothing else (no markdown, no commentary, no apologies).

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
   `campuses` entry whose `is_main` flag is true (create `is_main: true` for the primary campus). If no campus is marked
   `is_main` yet, create a campus named "Main Campus" and mark it `is_main: true`.
3. If the chunk mentions multiple campus names and lists campus-specific items, create or update the relevant campus entries
   and attach only the corresponding programs/fees/contacts to each.
4. If no campus can be determined from the chunk, prefer updating the primary campus (Main Campus) and note uncertainty in `notes`.
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
{
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
      "campus_id": "",                /* optional unique id you may create */
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
""")

# Human-readable explanation of how to fill key attributes (kept short and actionable for the model)
ATTR_EXPLANATION = textwrap.dedent("""
EXPLANATION OF SELECTED FIELDS (how to fill them) — campus-aware:

- campuses[].name: use explicit campus names from the chunk when present (e.g., "Lahore Campus", "Downtown Campus").
- campuses[].is_main: set true for the primary/main campus. If the chunk is the university homepage or clearly primary, mark is_main true.
- campuses[].location: fill address/city/country when available. coordinates only if explicit.

- campuses[].contacts: put campus-specific admissions/international/office contacts here. If the chunk lists a general university admissions email without campus specificity,
  put it at the top-level `admissions.application_portal` and in the `campuses` entries that appear most relevant (prefer main campus).

- campuses[].programs: each program object should include program-level tuition, deadlines, and entry_requirements. This allows different campuses to have different fees/requirements.
  - tuition entries: {"amount": number, "currency": "XXX", "period": "year|semester|credit", "applicability": "domestic|intl|all", "notes":"", "source":"", "confidence": number}
  - entry_requirements.standardized_tests: normalized names with min_score where present.

- admissions (top-level): use for application portal URLs and cross-campus deadlines or global rules that apply to all campuses.

- sources: append a minimal provenance object for anything you fill. Include a short quoted snippet (<= 200 chars) extracted from MARKDOWN_CHUNK and an extraction_timestamp (YYYY-MM-DD).

- extraction.per_field_confidence: map JSON pointer strings (e.g., "campuses[0].programs[0].tuition[0]") to the confidence you assign.

- overall_confidence: average of values in extraction.per_field_confidence (set to 0.0 if none).

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
        "JSON_SCHEMA (the exact JSON object you MUST return, use the same keys):",
        JSON_TEMPLATE,
        "EXPLANATION (how to fill attributes):",
        ATTR_EXPLANATION,
        "PREVIOUS_JSON (this is the current extracted record — update/merge it):",
        prev_json_str,
        "MARKDOWN_CHUNK (extract from this text and update the JSON above):",
        markdown_chunk,
        "INSTRUCTIONS (required):",
        textwrap.dedent(f"""
- Identify whether the MARKDOWN_CHUNK refers to a specific campus. If a campus name is present, add or update that campus entry inside `campuses` and attach campus-level programs/fees/contacts there.
- If the chunk is global (no campus reference), update the primary campus (`is_main: true`) or top-level `admissions` if the info is clearly global.
- For each field you change or fill, include a `confidence` (0.0-1.0) near the field where schema supports it and add an entry to `extraction.per_field_confidence`.
- Append minimal provenance items to `sources`. Each provenance object should be: {{"snippet":"...", "extraction_timestamp":"{today}"}}. Keep the snippet <= 200 chars.
- Set `extraction.last_updated` to "{today}".
- Update `extraction.updated_fields` to list the top-level keys you changed in this call (e.g., ["campuses","admissions"]).
- Compute `overall_confidence` as the average of the per-field confidences you set (or 0.0 if none).
- IMPORTANT: RETURN ONLY THE FULL UPDATED JSON OBJECT. No comments, no code fences, no extra text.
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
