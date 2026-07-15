# LinkedIn Ads Scripts

Python scripts for the LinkedIn Marketing API (v202601). Every script authenticates
through `client.py` (`get_session()`, `get_account_id()`, `BASE_URL`), which reads
credentials from `.env` via `config.py`.

## Setup

```
pip install requests python-dotenv tabulate
python oauth_server.py     # one-time: authorize and save your access token to .env
```

Required `.env` keys: `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_ACCOUNT_ID`. Ad creatives
that host media also need `LINKEDIN_ORG_ID` (your company Page's organization ID).

## Conventions

- **Account:** every script reads the ad account from `.env`. Pass `--account-id <id>`
  to target a different account for a single run.
- **Safety:** all campaign / campaign-group / creative creates default to PAUSED or
  DRAFT. Nothing serves or spends until you review and enable it in Campaign Manager.
- **Money units:** budgets and bids are in **cents** (e.g. `5000` = $50.00).

---

## Setup & auth

| Script | Purpose | Key args | Example |
|--------|---------|----------|---------|
| `oauth_server.py` | One-time OAuth flow to fetch and save an access token | (none) | `python oauth_server.py` |
| `client.py` | Shared authenticated session + account helpers (imported, not run) | - | - |
| `config.py` | Loads credentials from `.env` (imported, not run) | - | - |

## Structure - campaign groups & campaigns

| Script | Purpose | Key args | Example |
|--------|---------|----------|---------|
| `create_campaign_group.py` | Create a campaign group (the container for campaigns) | `--name`, `--status`, `--total-budget`, `--end-date` | `python create_campaign_group.py --name "Q2 Lead Gen"` |
| `create_campaign.py` | Create a campaign under a group (starts PAUSED) | `--name`, `--campaign-group-id`, `--objective`, `--daily-budget`, `--bid-strategy` | `python create_campaign.py --name "Lead Gen" --campaign-group-id 123 --objective LEAD_GENERATION --daily-budget 5000` |
| `update_campaign.py` | Update one campaign's status / budget / bid / name | `--campaign-id`, `--status`, `--daily-budget`, `--bid-amount`, `--bid-strategy`, `--name` | `python update_campaign.py --campaign-id 123 --status ACTIVE` |
| `bulk_edit.py` | Bulk pause/enable/rename/budget/bid across many campaigns | `--campaign-ids` or `--status`, `--pause`/`--enable`, `--daily-budget`, `--name-prefix` | `python bulk_edit.py --status PAUSED --enable` |
| `manage_bids.py` | View or set the bid / bid strategy on a campaign | `--campaign-id`, `--action view|set`, `--bid-amount`, `--bid-strategy` | `python manage_bids.py --campaign-id 123 --action set --bid-amount 500` |
| `attach_conversions.py` | Attach account conversions to a campaign (or list them) | `--campaign-id`, `--conversion-id` (repeatable), `--list` | `python attach_conversions.py --campaign-id 123` |

## Creatives - build ads

All ad builders create the creative PAUSED. Media builders need `LINKEDIN_ORG_ID`
(or `--org-id`).

| Script | Purpose | Key args | Example |
|--------|---------|----------|---------|
| `create_image_ad.py` | Single-image ad (single or CSV bulk) | `--campaign-id`, `--image`, `--headline`, `--body`, `--url`, `--name` | `python create_image_ad.py --campaign-id 123 --image ./ad.png --headline "..." --url "https://example.com/demo"` |
| `create_video_ad.py` | Single-video ad (chunked upload) | `--campaign-id`, `--video`, `--title`, `--body`, `--url`, `--cta`, `--name` | `python create_video_ad.py --campaign-id 123 --video ./ad.mp4 --title "See it" --url "https://example.com/demo" --cta REQUEST_DEMO` |
| `create_carousel_ad.py` | Carousel ad (2-10 cards) | `--campaign-id`, `--card "IMG|HEADLINE|URL"` (repeatable), `--body`, `--name` | `python create_carousel_ad.py --campaign-id 123 --card "./c1.png|Step 1|https://example.com/1" --card "./c2.png|Step 2|https://example.com/2"` |
| `create_document_ad.py` | Document (PDF) ad, optionally gated by a lead form | `--campaign-id`, `--file`, `--title`, `--body`, `--lead-form-id`, `--cta`, `--name` | `python create_document_ad.py --campaign-id 123 --file ./report.pdf --title "2026 Report" --name "Doc Ad"` |
| `create_thought_leader_ad.py` | Promote an existing post (share/ugcPost URN) as a Thought Leader Ad | `--campaign-id`, `--post-urn`, `--name` | `python create_thought_leader_ad.py --campaign-id 123 --post-urn "urn:li:share:730..." --name "TLA"` |
| `bulk_utm.py` | Re-tag existing single-image ads with UTM params (rebuilds as new PAUSED creatives) | `--campaign-ids`, `--utm-source`, `--utm-medium`, `--utm-campaign` | `python bulk_utm.py --campaign-ids 111,222 --utm-source linkedin --utm-medium paid_social` |
| `list_creatives.py` | List creatives (all or per campaign) | `--campaign-id` | `python list_creatives.py --campaign-id 123` |

## Lead gen & audiences

| Script | Purpose | Key args | Example |
|--------|---------|----------|---------|
| `create_lead_gen_form.py` | Create a lead gen form asset (owned by the account) | `--name`, `--headline`, `--privacy-url`, `--field` (repeatable), `--description` | `python create_lead_gen_form.py --name "Report DL" --headline "Get the report" --privacy-url "https://example.com/privacy"` |
| `list_lead_forms.py` | List lead gen forms on the account | (none) | `python list_lead_forms.py` |
| `upload_audience.py` | Upload a matched company or contact list (DMP segment) | `--name`, `--file`, `--type COMPANY|USER` | `python upload_audience.py --name "Target Accounts" --file accounts.csv --type COMPANY` |

## Reporting & analytics

| Script | Purpose | Key args | Example |
|--------|---------|----------|---------|
| `account_overview.py` | Account-level KPIs + top campaigns, optional period compare | `--date-range`, `--compare` | `python account_overview.py --date-range last_7d --compare` |
| `get_campaign_performance.py` | Per-campaign metrics table, optional daily breakdown | `--campaign-id`, `--date-range`, `--start-date`/`--end-date`, `--by-day` | `python get_campaign_performance.py --date-range last_30d` |
| `get_demographics.py` | Audience breakdown by job function / seniority / industry / company size / country | `--pivot` (repeatable), `--campaign-id`, `--date-range` | `python get_demographics.py --pivot JOB_FUNCTION` |
| `list_campaigns.py` | List campaigns, optionally filtered by status | `--status` | `python list_campaigns.py --status ACTIVE` |
| `report.py` | Self-contained HTML dashboard (7 / 30 / 90-day) | `--output`, `--brand` | `python report.py --brand "Your Agency"` |

---

## Notes

- **`--account-id` override** is available on all campaign / creative / analytics
  scripts. Without it, the account comes from `LINKEDIN_ACCOUNT_ID` in `.env`.
- **Thought Leader Ads:** this toolkit promotes a post you already have the
  `urn:li:share:` / `urn:li:ugcPost:` URN for. Promoting a member's *organic* post
  that you only have the feed URL for (the `-activity-<id>` URL) is not possible via
  the API and must be done in Campaign Manager.
- **Creative status on create:** creatives are created with `intendedStatus: PAUSED`.
  Media (image/video/document) uploads poll until the asset is `AVAILABLE` before the
  post is created.
