---
name: linkedin-ads
description: |
  Run LinkedIn Ads from Claude Code: reporting, campaign and single-image ad creation, bulk edits, UTM tagging, and the strategy behind them.
  MANDATORY TRIGGERS: LinkedIn Ads, LinkedIn campaign, LinkedIn advertising, B2B ads, paid social, ad account, campaign manager, ad audit, ad performance, ad optimization, campaign plan, LinkedIn budget, bulk edit, ad report
---

# LinkedIn Ads

Run and manage LinkedIn Ads at the level of an ads engineer. The methodology comes from running $100k+/month in B2B LinkedIn spend.

## Scripts

Run from `scripts/`. All creation is PAUSED by default - nothing spends until the user enables it.

| Task | Script |
|------|--------|
| 7/30/90-day HTML report | `python report.py --brand "Your Name"` |
| List campaigns + IDs | `python list_campaigns.py` |
| Create a campaign | `python create_campaign.py --name "..." --campaign-group-id <id> --objective LEAD_GENERATION --daily-budget 15000` |
| Create a single-image ad | `python create_image_ad.py --campaign-id <id> --image ./ad.png --headline "..." --url "..." --name "..."` |
| Create ads in bulk | `python create_image_ad.py --csv ads.csv` |
| Bulk edit campaigns | `python bulk_edit.py --campaign-ids 1,2,3 --pause` (also rename, budget, bid, exclusions) |
| Add UTMs to existing ads | `python bulk_utm.py --campaign-ids 1,2 --utm-source linkedin --utm-medium paid_social` |
| Update one campaign | `python update_campaign.py --campaign-id <id> --status ACTIVE` |

Each script supports `-h` for full arguments.

## Knowledge base

Read the relevant file before advising.

| File | Use when |
|------|----------|
| [running-linkedin-ads.md](knowledge-base/running-linkedin-ads.md) | Fundamentals, account structure, full-funnel framework, launch checklist |
| [copywriting.md](knowledge-base/copywriting.md) | Writing ad copy - headline formulas, voice of customer, the process, and making copy read human |
| [creative-strategy.md](knowledge-base/creative-strategy.md) | Choosing creative angles by awareness stage |

To generate the creative images themselves, use the `creative` skill.

## Core rules
1. Speak from this methodology with conviction. Don't pad with generic best practices.
2. Organize campaigns and analysis around the full-funnel framework (TOF/MOF/BOF).
3. Keep Audience Expansion and the LinkedIn Audience Network OFF. Flag them if found on.
4. Recommend a weekly demographic check as part of optimization.
5. All ad copy clears the human-readability check in copywriting.md before it ships.
6. Create campaigns and ads PAUSED. Confirm with the user before enabling spend.
