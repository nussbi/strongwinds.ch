# strongwinds.ch

Responsive, four-language AI consultancy site for Swiss freelancers and SMEs. Violet/mint visual identity, custom SVG wind mark, static blog archive, OpenClaw and Hermes guides.

## Content preservation

- All **101 pre-existing blog routes** remain in the repository and the deployed site.
- `.source/pages.json` preserves the original HTML and translation dictionaries, before redesign.
- One exact duplicate (`ai-agenten-fuer-schweizer-kmu`) uses the canonical URL of `whatsapp-email-crm`; both source files and routes remain available. The index lists 100 distinct articles.
- Legacy `.html` links have explicit permanent redirects in `_redirects`.
- The migration checks article bodies in all four languages. German sharp-s is normalized to Swiss `ss` spelling.

## Local build and validation

Python dependencies: `pip install -r requirements.txt`

1. Edit authoritative content in `.source/pages.json` and/or design files.
2. `python scripts/redesign.py` renders the static pages and sitemap.
3. `python scripts/validate.py` checks routes, anchors, resources, JSON-LD, metadata, and reciprocal hreflang.
4. `python scripts/stage.py` copies only public runtime files to `dist`.

The original `scripts/add_sw_post.py` is a legacy pre-redesign publisher and should not be used with the generated pages.

## Adding articles

Use `python scripts/add_post.py post.json`, then run the build steps above. JSON fields: `slug`, ISO `date`, and `title`, `meta`, `body` dictionaries containing `en`, `de`, `fr`, and `it`. `body` contains HTML. Optional `tags`: an array of objects containing `slug`, `en`, `de`, `fr`, and `it`. The script refuses to overwrite an existing post.

## Cloudflare Pages

- GitHub repository: `nussbi/strongwinds.ch`, production branch `main`.
- Build command: `python3 scripts/stage.py`
- Output directory: `dist`
- Custom domain: `strongwinds.ch`
- Source snapshots, scripts, reports, and credentials are not deployed.

## Privacy and security

Google Tag Manager loads only after explicit analytics consent. No duplicate direct GA tag is loaded. Fonts are hosted locally. Contact links use the existing email, WhatsApp, and LinkedIn destinations. No backend or form submission service is introduced. Cloudflare Bot Fight Mode is retained; automated requests may receive a security challenge.

No credentials are stored in the repository. See `SECURITY.md`.
