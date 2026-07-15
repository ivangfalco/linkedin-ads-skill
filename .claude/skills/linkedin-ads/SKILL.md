---
name: linkedin-ads
description: |
  Run LinkedIn Ads from Claude Code end to end: reporting, campaign and campaign-group creation, every ad format (single image, document, video, carousel, thought-leader), lead gen forms, audiences, conversions, bulk edits, demographics, bidding, and the strategy behind them.
  MANDATORY TRIGGERS: LinkedIn Ads, LinkedIn campaign, LinkedIn advertising, B2B ads, paid social, ad account, campaign manager, ad audit, ad performance, ad optimization, campaign plan, LinkedIn budget, bulk edit, ad report, lead gen form, thought leader ad, document ad, matched audience
---

# LinkedIn Ads

Run and manage LinkedIn Ads at the level of an ads engineer. The methodology comes from running $100k+/month in B2B LinkedIn spend. Strategy lives in the knowledge base; the scripts are the execution layer. For cross-cutting frameworks (demand lifecycle, budget, measurement, writing style) read `ads-foundations/` at the repo root - `ads-foundations/writing-style.md` governs everything you write.

## Knowledge base (read the relevant file before advising)

**Start here for any strategy/operational question:**

| File | Use when |
|------|----------|
| [running-linkedin-ads.md](knowledge-base/running-linkedin-ads.md) | Fundamentals, account structure, how to run day to day |
| [full-funnel-framework.md](knowledge-base/full-funnel-framework.md) | The TOF/MOF/BOF full-funnel framework - the spine of structure and measurement |
| [campaign-structures.md](knowledge-base/campaign-structures.md) | Campaign group architecture by stage/persona, naming conventions |

**Deeper context (load when needed):**

| File | Use when |
|------|----------|
| [audience-sizing.md](knowledge-base/audience-sizing.md) | Targeting, job function + seniority vs title, matched audiences, sizing, exclusions |
| [bidding-strategy.md](knowledge-base/bidding-strategy.md) | Bid types, when to use each, cost control |
| [benchmarks.md](knowledge-base/benchmarks.md) | B2B LinkedIn benchmarks (CTR, CPC, CPL ranges) - reference ranges only, never invented |
| [creative-strategy.md](knowledge-base/creative-strategy.md) | Creative angles by awareness stage, format selection |
| [copywriting.md](knowledge-base/copywriting.md) | Headline formulas, voice of customer, the writing process |
| [copy-audit-framework.md](knowledge-base/copy-audit-framework.md) | Scoring and auditing existing ad copy |
| [document-ads.md](knowledge-base/document-ads.md) | Document/PDF ads - when they win, how to build |
| [conversation-ads.md](knowledge-base/conversation-ads.md) | Conversation/message ad strategy |
| [ctv-strategy.md](knowledge-base/ctv-strategy.md) | Connected TV on LinkedIn |
| [abm-strategy.md](knowledge-base/abm-strategy.md) | ABM and ABM 1:1 on LinkedIn |
| [landing-pages.md](knowledge-base/landing-pages.md) | Landing page strategy for LinkedIn traffic |
| [scaling-strategy.md](knowledge-base/scaling-strategy.md) | Scaling winners, budget scaling protocol |
| [audit-checklist.md](knowledge-base/audit-checklist.md) | Full account audit checklist |
| [launch-checklist.md](knowledge-base/launch-checklist.md) | Pre-launch checklist |
| [api-reference.md](api-reference.md) | LinkedIn Marketing API endpoints, versioning, payload schemas the scripts use |

## Scripts (execution layer)

Run from `scripts/` (auth via the shared `client.py`, credentials from `.env`). **All creation is PAUSED/DRAFT by default - nothing spends until the user enables it.** Budgets are in cents. Every script takes `--account-id` to override the default. Full index + args + examples: [scripts/README.md](scripts/README.md).

**Analyze / Report**

| Script | Use when you need to... |
|--------|------------------------|
| `account_overview.py` | Pull an account-level metrics snapshot |
| `get_campaign_performance.py` | Campaign analytics over a date range |
| `report.py` | 7/30/90-day branded HTML report (`--brand`) |
| `list_campaigns.py` / `list_creatives.py` / `list_lead_forms.py` | List objects + IDs |
| `get_demographics.py` | Demographic breakdown (job title, company, seniority, industry) |

**Create (default PAUSED / DRAFT)**

| Script | Use when you need to... |
|--------|------------------------|
| `create_campaign_group.py` | Create a campaign group |
| `create_campaign.py` | Create a campaign |
| `create_image_ad.py` | Single-image ad (single or bulk via `--csv`) |
| `create_document_ad.py` | Document / PDF ad (optionally lead-gen gated) |
| `create_video_ad.py` | Single-video ad |
| `create_carousel_ad.py` | 2-10 card carousel ad |
| `create_thought_leader_ad.py` | Promote an existing member/company post (Thought Leader Ad) |
| `create_lead_gen_form.py` | Lead gen form |

**Manage**

| Script | Use when you need to... |
|--------|------------------------|
| `update_campaign.py` | Change a campaign's status / budget / name |
| `bulk_edit.py` | Pause/enable, rename, budget, bid, exclusions across many campaigns |
| `bulk_utm.py` | Add UTM tracking to existing ads in bulk |
| `manage_bids.py` | Review / update bids |
| `attach_conversions.py` | Attach account conversions to a campaign (`--list` to see available) |

**Audiences**

| Script | Use when you need to... |
|--------|------------------------|
| `upload_audience.py` | Create / populate a matched (contact or company) audience |

To generate the creative images themselves, use the `creative` skill.

## Core rules
1. Speak from this methodology with conviction. Don't pad with generic best practices.
2. Organize campaigns and analysis around the full-funnel framework (TOF/MOF/BOF).
3. Keep Audience Expansion and the LinkedIn Audience Network OFF. Flag them if found on.
4. Recommend a weekly demographic check (`get_demographics.py`) as part of optimization.
5. All ad copy clears the human-readability standard in `ads-foundations/writing-style.md` before it ships. No AI slop, no em dashes, no emoji.
6. Create campaigns and ads PAUSED. Confirm with the user before enabling spend.
7. Never invent numbers or benchmarks. Pull live data, or cite `benchmarks.md` ranges as reference.
