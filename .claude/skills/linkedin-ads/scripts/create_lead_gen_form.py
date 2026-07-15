#!/usr/bin/env python3
"""
Create a LinkedIn lead gen form.

The form is the asset a Lead Generation creative points to. It must be owned by
the sponsoredAccount (not the organization) or it will not show up in Campaign
Manager under Assets -> Lead Generation Forms.

Usage:
    python create_lead_gen_form.py \
        --name "Report Download" \
        --headline "Get the 2026 benchmark report" \
        --description "See how teams cut reporting time." \
        --privacy-url "https://example.com/privacy"

    # Choose which prefilled fields to collect (repeatable):
    python create_lead_gen_form.py --name "Demo Requests" \
        --headline "Book a demo" --privacy-url "https://example.com/privacy" \
        --field FIRST_NAME --field LAST_NAME --field WORK_EMAIL --field COMPANY_NAME --field JOB_TITLE

Default fields: FIRST_NAME, LAST_NAME, EMAIL, COMPANY_NAME.
The form is created PUBLISHED (a form asset does not spend budget on its own).
"""

import argparse
import sys

from client import get_session, get_account_id, BASE_URL


PREDEFINED_FIELDS = [
    "FIRST_NAME", "LAST_NAME", "EMAIL", "WORK_EMAIL", "COMPANY_NAME",
    "JOB_TITLE", "PHONE_NUMBER", "WORK_PHONE", "CITY", "STATE",
    "COUNTRY", "ZIP_CODE",
]

FIELD_LABELS = {
    "FIRST_NAME": "First name",
    "LAST_NAME": "Last name",
    "EMAIL": "Email address",
    "WORK_EMAIL": "Work email",
    "COMPANY_NAME": "Company name",
    "JOB_TITLE": "Job title",
    "PHONE_NUMBER": "Phone number",
    "WORK_PHONE": "Work phone",
    "CITY": "City",
    "STATE": "State",
    "COUNTRY": "Country",
    "ZIP_CODE": "Zip code",
}


def build_questions(fields):
    questions = []
    for f in fields:
        questions.append({
            "name": f.lower(),
            "responseRequired": True,
            "responseEditable": True,
            "questionDetails": {"textQuestionDetails": {}},
            "predefinedField": f,
            "question": {"localized": {"en_US": FIELD_LABELS.get(f, f.replace("_", " ").title())}},
        })
    return questions


def create_lead_gen_form(args):
    session = get_session()
    account_id = args.account_id or get_account_id()

    fields = args.field or ["FIRST_NAME", "LAST_NAME", "EMAIL", "COMPANY_NAME"]

    content = {
        "headline": {"localized": {"en_US": args.headline}},
        "legalInfo": {"consents": [], "privacyPolicyUrl": args.privacy_url},
        "questions": build_questions(fields),
    }
    if args.description:
        content["description"] = {"localized": {"en_US": args.description}}
    if args.thank_you_message:
        content["thankYouMessage"] = {"localized": {"en_US": args.thank_you_message}}
    if args.thank_you_url:
        content["landingPageUrl"] = args.thank_you_url

    payload = {
        "name": args.name,
        "owner": {"sponsoredAccount": f"urn:li:sponsoredAccount:{account_id}"},
        "state": "PUBLISHED",
        "creationLocale": {"language": "en", "country": "US"},
        "content": content,
    }

    resp = session.post(f"{BASE_URL}/leadForms", json=payload)

    if resp.status_code == 201:
        form_id = resp.headers.get("x-restli-id", "unknown")
        print(f"\nLead gen form created successfully!")
        print(f"  Form ID:  {form_id}")
        print(f"  Form URN: urn:li:adForm:{form_id}")
        print(f"  Name:     {args.name}")
        print(f"  Fields:   {', '.join(fields)}")
        print(f"\nNext step:")
        print(f"  Attach it to a Lead Generation creative's leadgenCallToAction.destination:")
        print(f"    urn:li:adForm:{form_id}")
    else:
        print(f"ERROR: Failed to create lead gen form: {resp.status_code}")
        print(resp.text)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a LinkedIn lead gen form")
    parser.add_argument("--name", required=True, help="Internal form name")
    parser.add_argument("--headline", required=True, help="Form headline shown to members")
    parser.add_argument("--privacy-url", required=True, help="Privacy policy URL (required by LinkedIn)")
    parser.add_argument("--description", help="Form description (max ~160 chars)")
    parser.add_argument("--field", action="append", choices=PREDEFINED_FIELDS,
                        help="Prefilled field to collect (repeatable). Default: FIRST_NAME LAST_NAME EMAIL COMPANY_NAME")
    parser.add_argument("--thank-you-message", help="Message shown after submission")
    parser.add_argument("--thank-you-url", help="Landing page URL offered after submission")
    parser.add_argument("--account-id", help="Override the ad account ID from config/.env")
    args = parser.parse_args()
    create_lead_gen_form(args)
