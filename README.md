# Ivan Falco's LinkedIn Ads Skills for Claude Code

**Run your LinkedIn Ads like an ads engineer - free.** This is a preview of the system my team uses to run LinkedIn Ads for B2B clients. It connects Claude Code to your ad account so you can report, build campaigns and ads, run bulk edits, and generate creatives and copy, all in plain English. Built from running $100k+/month in B2B LinkedIn ad spend.

> **Important:** this runs in **Claude Code on your own computer** - the `claude` CLI in your terminal, or the Claude Code desktop app (Local mode). It does **not** work in the Claude chat app (claude.ai / the Claude desktop chat), which can't run scripts on your machine. New to Claude Code? Install it: https://code.claude.com/docs

## Built by

**Ivan Falco** - I do ads engineering at [Frontal](https://frontal.so) (formerly ColdIQ Agency): I help B2B companies scale their paid motion with AI-native systems - ABM and ABM 1:1, syncing ad audiences with outbound, AI-native creative, and scaling accounts like an engineer.

This is the free, public version. The full system - the complete operating system, the creative production system, and hands-on management - is what we run for our clients (Series A/B B2B tech companies and agencies with $1M+ growth teams).

**Want a human to look at your setup?** Connect with me on LinkedIn (send a note): https://www.linkedin.com/in/ivanfalco/

---

## What's inside

**Scripts (connect to your LinkedIn ad account) - everything PAUSED by default:**
- **Report / analyze:** `report.py` (7/30/90-day HTML), `account_overview.py`, `get_campaign_performance.py`, `get_demographics.py`, `list_campaigns.py` / `list_creatives.py` / `list_lead_forms.py`
- **Create:** `create_campaign_group.py`, `create_campaign.py`, and every ad format - `create_image_ad.py`, `create_document_ad.py`, `create_video_ad.py`, `create_carousel_ad.py`, `create_thought_leader_ad.py` - plus `create_lead_gen_form.py`
- **Manage:** `bulk_edit.py`, `bulk_utm.py`, `update_campaign.py`, `manage_bids.py`, `attach_conversions.py`
- **Audiences:** `upload_audience.py` (matched contact/company audiences)

Full index with args + examples: [scripts/README.md](.claude/skills/linkedin-ads/scripts/README.md).

**Skills (no API needed):**
- **Creative generation** - your branding plus an image-gen workflow to produce creatives consistently
- **Copywriting** - headline formulas, voice-of-customer sourcing, and the writing process

**Knowledge base (17 files + a full API reference):**
- The full-funnel framework, campaign structure, audience sizing, bidding, B2B benchmarks, every ad format (image, document, video, carousel, conversation, CTV, thought-leader), ABM, landing pages, scaling, audit + launch checklists, and the copy-audit framework
- Plus `ads-foundations/` - the cross-cutting frameworks (demand lifecycle, budget allocation, measurement, and the no-AI-slop writing style that governs all copy)

**Prompt library** - see [PROMPTS.md](PROMPTS.md).

## Quick start

```bash
git clone https://github.com/ivangfalco/linkedin-ads-skill.git
cd linkedin-ads-skill
claude
```

Then run `/onboarding` and Claude walks you through connecting your account. Once connected:

```
"Build me the 30-day report"
"Create a single-image ad for this campaign"
"Pause every campaign under 0.4% CTR"
"Add UTMs to my retargeting ads"
"Write me three headline options for this audience"
```

## A note on API access

Getting LinkedIn Advertising API access can take a few days - LinkedIn reviews each app. I'm working with LinkedIn toward fuller access: soon an MCP and a proper UI to manage campaigns, with Google and Meta to follow. **Want in early? [Join the waitlist.](https://tally.so/r/9qrj61)**

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3.10+
- A LinkedIn ad account and Advertising API access (onboarding covers this)
- For creative generation: an OpenAI account (you generate images in ChatGPT - no API key needed in this repo)

## Who it's for

B2B marketers, growth operators, agencies, and founders running their own LinkedIn Ads who want to manage the account at speed with an AI that knows the platform.

## License

Source-available: MIT + [Commons Clause](https://commonsclause.com/) - see [LICENSE](LICENSE). Use it, fork it, build on it, run it for your own and your clients' accounts. You just can't repackage and resell the skills themselves as a product. Attribution appreciated.

---

*Built by [Ivan Falco](https://www.linkedin.com/in/ivanfalco/) at [Frontal](https://frontal.so). Provided as-is. You are responsible for your own API usage, ad spend, and platform compliance.*
