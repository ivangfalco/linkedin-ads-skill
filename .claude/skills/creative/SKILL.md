---
name: creative
description: |
  Generate single-image LinkedIn ad creatives consistently using OpenAI image generation, the user's branding, and a fixed workflow.
  MANDATORY TRIGGERS: creative, ad creative, generate creative, ad image, make an ad, design ad, creative generation, image ad, ad visual
---

# Creative Generation

Produce single-image LinkedIn ad creatives that look on-brand and follow what works on the platform. This skill needs no API - the user generates images in OpenAI (ChatGPT) and you guide the workflow. The finished image is pushed live with `linkedin-ads/scripts/create_image_ad.py`.

## Step 1: Set up image generation (first time only)

Ask the user if they have OpenAI image generation available:

> To generate creatives you'll use OpenAI's image model (GPT image). You need a ChatGPT account with image generation - the paid plan includes it. Open chatgpt.com, start a new chat, and confirm you can attach/generate images. Tell me when you're in.

If they prefer the API, they can use the OpenAI Images API instead - same prompts. No key is stored in this repo.

## Step 2: Capture branding (first time only)

Gather and save a short brand profile to reuse on every creative. Ask for:
- Brand colors (hex if they have them - primary + one accent)
- Logo (file or describe placement)
- Font feel (e.g. bold geometric sans, classic serif)
- Tone (e.g. sharp and technical, warm and plain-spoken)
- One or two example ads they like

Store the answers so you can reuse them without re-asking.

## Step 3: The creative workflow

Follow this every time. One idea per creative.

1. **Pick the one idea.** Get it from the copy. Use the `copywriting` skill to choose a headline formula and write the single headline that goes on the image. The headline is the creative.
2. **Choose the layout.** Default for B2B that performs: bold headline text on a solid background, logo small in a corner, one accent color on the key word. No stock photos, no feature lists, no clutter. Readable at thumbnail size.
3. **Write the image prompt.** Use this template, filling in branding and the headline:

   > A LinkedIn ad creative, 1200x1200. Solid [primary color] background. Large bold [font feel] headline text reading exactly: "[headline]". [Accent color] highlight on the word "[key word]". Small [brand] logo in the bottom-left corner. Clean, high-contrast, no other text, no photography, readable as a thumbnail.

4. **Generate 3 variations.** Different background/accent or headline emphasis - not minor tweaks. Single image only.
5. **Check it.** Headline spelled correctly and legible at small size? On brand? One message only? If not, regenerate.
6. **Check the copy** against the writing rules in `linkedin-ads/knowledge-base/copywriting.md` before it goes near an ad.
7. **Export** the chosen image (PNG/JPG) and save the path.
8. **Push it live (paused):**
   ```bash
   cd .claude/skills/linkedin-ads/scripts
   python create_image_ad.py --campaign-id <id> --image /path/to/creative.png \
       --headline "<headline>" --body "<body copy>" --url "<destination>" --name "<ad name>"
   ```

## Rules
- This skill covers single-image creative generation. For document, video, carousel, and thought-leader ads, use the creation scripts in the `linkedin-ads` skill (`create_document_ad.py`, `create_video_ad.py`, `create_carousel_ad.py`, `create_thought_leader_ad.py`).
- The headline carries the ad. Spend the effort there, in the copy.
- Three genuinely different concepts beat ten near-duplicates.
- Every line of text clears the writing check in copywriting.md.
- The ad is created PAUSED. The user reviews it in Campaign Manager before enabling.
