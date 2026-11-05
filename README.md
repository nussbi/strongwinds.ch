# strongwinds.ch

Source and tooling for **strongwinds.ch** — AI consulting & automation for Swiss freelancers and SMEs. Static site (hand-coded HTML/CSS/JS) deployed on **Cloudflare Pages**.

## Contents

```
.
└── scripts/
    └── add_sw_post.py         # Publish a trilingual (EN/DE/FR) blog post
```

## Blog publishing

`scripts/add_sw_post.py <post.json>` publishes a new post by cloning the newest clean post template and splicing in the new content:

- Updates `<title>`, meta description, `og:*`, canonical and `BlogPosting` JSON-LD.
- Rebuilds the `translations` object (EN/DE/FR) and the index card + `postN_*` keys.
- Appends the new post to `sitemap.xml` and repairs malformed `lastmod` values.
- Every `re.sub` splice uses a lambda replacement so `json.dumps` output is never mangled.

> The script expects the site tree at `/data/workspace/strongwinds-redesign` (blog posts, `blog/index.html`, `sitemap.xml`). Adjust `ROOT` for your environment.

## Deploy (Cloudflare Pages)

- Build command: *(none — static)*
- Output directory: `/` (repo root)
- Custom domain: `strongwinds.ch`

## Security

No secrets are committed. See [SECURITY.md](./SECURITY.md).
