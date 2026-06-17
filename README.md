# Ivan Falco's LinkedIn Ads Skills for Claude Code

**Run your LinkedIn Ads like an ads engineer - free.** This is a preview of the system my team uses to run LinkedIn Ads for B2B clients. It connects Claude Code to your ad account so you can report, build campaigns and ads, run bulk edits, and generate creatives and copy, all in plain English. Built from running $100k+/month in B2B LinkedIn ad spend.

> **Important:** this runs in **Claude Code on your own computer** - the `claude` CLI in your terminal, or the Claude Code desktop app (Local mode). It does **not** work in the Claude chat app (claude.ai / the Claude desktop chat), which can't run scripts on your machine. New to Claude Code? Install it: https://code.claude.com/docs

## Built by

**Ivan Falco** - I do ads engineering: I help B2B companies scale their paid motion with AI-native systems - ABM and ABM 1:1, syncing ad audiences with outbound, AI-native creative, and scaling accounts like an engineer. Head of Growth at [ColdIQ](https://coldiq.com).

This is the free, public version. The full system - the complete operating system, the creative production system, and hands-on management - is what we run for our clients (Series A/B B2B tech companies and agencies with $1M+ growth teams).

**Want a hand with your account?** I run a free LinkedIn Ads teardown. [Book a call](https://calendly.com/ivan-coldiq/call-with-ivan-falco-1) or find me on [LinkedIn](https://www.linkedin.com/in/ivanfalco/).

---

## What's inside

**Scripts (connect to your LinkedIn ad account):**
- `report.py` - clean HTML dashboard for the last 7, 30, and 90 days
- `create_campaign.py` - create campaigns, single or bulk
- `create_image_ad.py` - create single-image ads, single or bulk (always created paused)
- `bulk_edit.py` - pause/enable, rename, budget, bid, and audience exclusions across many campaigns at once
- `bulk_utm.py` - add UTM tracking to existing ads in bulk
- `list_campaigns.py` - list campaigns and their IDs

**Skills (no API needed):**
- **Creative generation** - your branding plus an OpenAI image-gen workflow to produce single-image creatives consistently
- **Copywriting** - six headline formulas, voice-of-customer sourcing, and the writing process
- **Anti-AI-slop** - a hard standard (the patterns readers recognize and distrust) so your copy reads human

**Knowledge:**
- How to run LinkedIn Ads: fundamentals, the full-funnel framework, structure, and a launch checklist

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

*Built by [Ivan Falco](https://www.linkedin.com/in/ivanfalco/) at [ColdIQ](https://coldiq.com). Provided as-is. You are responsible for your own API usage, ad spend, and platform compliance.*
