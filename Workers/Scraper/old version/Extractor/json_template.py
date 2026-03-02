json_template = """{
  "university": {
    "name": "",
    "aliases": [],
    "website": "",
    "short_description": "",
    "established_year": null,
    "type": "",                                 /* "public" / "private" / etc. */
    "logo": "",
    "brochures": [],                            /* {url, title, format} */
    "ranking": [],                              /* [{source, year, rank, notes}] */
    "accreditation": []                         /* [{body, scope, valid_until}] */
  },

  "locations": {
    "main_campus": {
      "address": "",
      "city": "",
      "region": "",
      "postal_code": "",
      "country": "",
      "coordinates": {"lat": null, "lon": null}
    },
    "other_campuses": [
      {"name": "", "address": "", "city": "", "country": "", "coordinates": {"lat": null, "lon": null}}
    ]
  },

  "contacts": {
    "admissions": {"name": "", "email": "", "phone": "", "office_hours": "" },
    "international_office": {"email": "", "phone": "" },
    "general": {"phone": "", "fax": "", "mailing_address": "" },
    "social": {"facebook": "", "twitter": "", "instagram": "", "linkedin": "", "youtube": ""}
  },

  "programs": [
    {
      "program_id": "",                /* unique id you can assign */
      "name": "",
      "degree": "",                    /* e.g., BSc, MSc, PhD, Diploma */
      "level": "",                     /* undergraduate / postgraduate / doctoral / certificate */
      "department": "",
      "duration": {"value": null, "units": "months|years|semesters"},
      "study_mode": ["full-time", "part-time", "online", "hybrid"],
      "start_terms": ["Fall", "Spring", "Summer", "Rolling"],
      "credits": null,
      "tuition": [
        {"amount": null, "currency": "", "period": "year|semester|credit", "applicability": "domestic|intl|all", "notes": "", "source": "", "confidence": null}
      ],
      "fees_breakdown": [{"name":"", "amount": null, "currency":"","source":"","confidence":null}],
      "entry_requirements": {
        "min_qualification": "",
        "min_gpa": null,
        "grades_required": "",
        "standardized_tests": [{"test":"IELTS|TOEFL|GRE|GMAT|SAT","min_score":null,"notes":""}],
        "work_experience_required": false,
        "documents_required": ["transcript", "passport", "SOP", "LOR", "portfolio"],
        "english_requirements": {"IELTS": null, "TOEFL": null, "other": ""}
      },
      "application_deadlines": [
        {"round":"Early/Regular/Final", "deadline_iso":"", "notes":"", "source":"", "confidence":null}
      ],
      "application_url": "",
      "curriculum": {"core_modules": [{"code":"","title":"","description":""}], "electives": []},
      "careers_info": {"internships": "", "placement_rate": null, "notable_employers": []},
      "notes_raw": []
    }
  ],

  "admissions": {                               /* cross-program info */
    "application_portal": "",
    "general_deadlines": [],
    "application_steps": [],
    "deposit_amount": {"amount": null, "currency": "", "deadline": ""},
    "refund_policy": ""
  },

  "fees_and_funding": {
    "typical_tuition_domestic": {"amount": null, "currency": ""},
    "typical_tuition_international": {"amount": null, "currency": ""},
    "mandatory_fees": [{"name":"", "amount": null, "currency": "", "source":"", "confidence":null}],
    "scholarships": [{"name":"", "eligibility":"", "value":"", "deadline":"", "apply_link":"", "source":"", "confidence":null}],
    "assistantships": [{"type":"TA|RA", "stipend":null, "notes":"", "source":"", "confidence":null}],
    "living_costs_monthly": {"amount": null, "currency": "", "notes":""}
  },

  "accommodation": {
    "on_campus": false,
    "types": [{"name":"", "cost":{"amount": null, "currency": ""}, "notes":"", "source":"", "confidence":null}],
    "off_campus_estimate": {"amount": null, "currency": "", "notes":""}
  },

  "international_students": {
    "visa_info": {"visa_type": "", "processing_weeks": null, "notes":""},
    "english_pathway": {"exists": false, "description": ""},
    "international_support": {"email":"", "phone": ""}
  },

  "research_and_faculty": {
    "centers": [],
    "notable_faculty": [{"name":"", "title":"", "research_interests": ""}],
    "research_partnerships": []
  },

  "student_life": {
    "clubs": [],
    "sports": [],
    "health_services": {},
    "disability_support": ""
  },

  "statistics": {
    "acceptance_rate": null,
    "enrollment_total": null,
    "international_percentage": null,
    "faculty_to_student_ratio": ""
  },

  "policies": {
    "deferral_policy": "",
    "transfer_credits_policy": "",
    "grading_scale": ""
  },

  "sources": [
    {"chunk_id": "", "url": "", "snippet": "", "extraction_timestamp": "" }
  ],

  "extraction": {
    "last_updated": "",
    "updated_fields": [],
    "per_field_confidence": { /* e.g. "programs[0].tuition[0]": 0.9 */ }
  },

  "overall_confidence": 0.0,
  "notes": []
}"""
