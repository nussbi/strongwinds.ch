#!/usr/bin/env python3
"""add_sw_post.py <post.json> - publish a trilingual blog post on strongwinds.ch.

Recreated 2026-10-15 after the original script was lost with the scratch dir.
Implements the strongwinds-blog-post skill:
  * copies blog/posts/ki-angebote.html (newest, clean template)
  * replaces <title>, meta description, og:title/og:description/og:url,
    canonical, JSON-LD (headline/description/datePublished/dateModified/
    mainEntityOfPage), the .blog-meta date, the <h1>, the three chips, the
    static post body, the three related-post links and the whole
    translations object (en/de/fr; the legacy "it" block is left as-is)
  * NO facturio.ch crosslink is injected; the facturio_crosslink key is
    dropped from en/de/fr (owner decision 2026-10-15)
  * adds the index card at the top of .cards.blog-grid plus postN_date/
    postN_title/postN_desc keys and any new tag_* keys in the index
    translations (existing tag keys must carry matching text)
  * appends the new post (and any drifted posts) to sitemap.xml

Pitfalls respected: every re.sub splice uses a lambda replacement so
json.dumps output is never mangled; tag slugs use underscores.
"""
import json
import os
import re
import sys

ROOT = "/data/workspace/strongwinds-redesign"
BLOG = os.path.join(ROOT, "blog")
POSTS_DIR = os.path.join(BLOG, "posts")
INDEX = os.path.join(BLOG, "index.html")
SITEMAP = os.path.join(ROOT, "sitemap.xml")
TEMPLATE = os.path.join(POSTS_DIR, "ki-angebote.html")
TEMPLATE_SLUG = "ki-angebote"
BASE = "https://strongwinds.ch"
LANGS = ("en", "de", "fr")


def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)


def next_post_number(index_html):
    nums = [int(x) for x in re.findall(r"post(\d+)_title", index_html)]
    return max(nums) + 1


def build_post_file(p):
    slug = p["slug"]
    dest = os.path.join(POSTS_DIR, slug + ".html")
    if os.path.exists(dest):
        fail("post already exists: %s" % dest)
    required = ("slug", "date", "title", "meta", "tags", "tag_keys",
                "related", "related_titles", "body")
    for k in required:
        if k not in p:
            fail("post JSON missing key: %s" % k)
    t = open(TEMPLATE, encoding="utf-8").read()

    t_title = re.search(r"<title>(.*?)</title>", t).group(1)
    t_meta = re.search(r'<meta name="description" id="meta-description" content="(.*?)"', t).group(1)
    t_date_iso = re.search(r'"datePublished": "([\d-]+)"', t).group(1)
    t_date_en = re.search(r'<div class="blog-meta"[^>]*>([A-Z][a-z]+ \d{1,2}, \d{4})</div>', t).group(1)
    t_chips = re.search(r'(?:<a href="\.\./\?tag=[a-z_0-9]+" data-i18n="tag_[a-z_0-9]+">[^<]+</a>){3}', t)
    if not t_chips:
        fail("could not locate the template chip row")

    # 1. rebuild the translations object (lambda replacement - CRITICAL)
    m = re.search(r"const translations = (\{.*?\});\s*function", t, re.S)
    if not m:
        fail("template translations object not found")
    tr = json.loads(m.group(1))
    for lang in LANGS:
        d = tr[lang]
        for k in list(d):
            if k.startswith("tag_") or k == "facturio_crosslink":
                del d[k]
        d["post_title"] = p["title"][lang]
        d["meta_description"] = p["meta"][lang]
        d["og_title"] = p["title"][lang]
        d["og_description"] = p["meta"][lang]
        d["post_content"] = p["body"][lang]
        for key, txt in zip(p["tag_keys"], p["tags"][lang]):
            d[key] = txt
        for i in range(3):
            d["rel%d_title" % (i + 1)] = p["related_titles"][lang][i]
    # legacy "it" block: keep Italian chrome keys, but overwrite the stale
    # template article with the EN values as a clean fallback (skill pitfall)
    if "it" in tr:
        d = tr["it"]
        for k in list(d):
            if k.startswith("tag_") or k == "facturio_crosslink":
                del d[k]
        d["post_title"] = p["title"]["en"]
        d["meta_description"] = p["meta"]["en"]
        d["og_title"] = p["title"]["en"]
        d["og_description"] = p["meta"]["en"]
        d["post_content"] = p["body"]["en"]
        for key, txt in zip(p["tag_keys"], p["tags"]["en"]):
            d[key] = txt
        for i in range(3):
            d["rel%d_title" % (i + 1)] = p["related_titles"]["en"][i]
    new_tr = json.dumps(tr, ensure_ascii=False)
    t = re.sub(r"const translations = \{.*?\};\s*(?=function)",
               lambda _: "const translations = " + new_tr + ";\n", t, flags=re.S)

    # 2. static post body (lambda replacement - CRITICAL)
    t = re.sub(r'(<div data-i18n-html="post_content">).*?(</div>)',
               lambda mm: mm.group(1) + "\n" + p["body"]["en"] + "\n" + mm.group(2),
               t, flags=re.S, count=1)

    # 3. head + static replacements
    t = t.replace(t_title, p["title"]["en"])
    t = t.replace(t_meta, p["meta"]["en"])
    t = t.replace("blog/posts/%s.html" % TEMPLATE_SLUG, "blog/posts/%s.html" % slug)
    t = t.replace(t_date_iso, p["date"]["iso"])
    t = t.replace(t_date_en, p["date"]["en"])
    chips = "".join('<a href="../?tag=%s" data-i18n="%s">%s</a>'
                    % (k[len("tag_"):], k, p["tags"]["en"][i])
                    for i, k in enumerate(p["tag_keys"]))
    t = t.replace(t_chips.group(0), chips)
    related_block = ('<ul class="related-list">\n'
                     + "\n".join('<li><a href="%s" data-i18n="rel%d_title">%s</a></li>'
                                 % (h, i + 1, p["related_titles"]["en"][i])
                                 for i, h in enumerate(p["related"]))
                     + "\n</ul>")
    t = re.sub(r'<ul class="related-list">.*?</ul>', lambda _: related_block,
               t, flags=re.S, count=1)

    # 4. sanity checks
    checks = {
        "canonical/og:url updated": "blog/posts/%s.html" % slug in t,
        "template slug gone": "blog/posts/%s.html" % TEMPLATE_SLUG not in t,
        "template title gone": t_title not in t,
        "no crosslink element": "crosslink-facturio" not in t
                                and 'data-i18n-html="facturio_crosslink"' not in t,
        "new chips present": chips in t,
        "template chips gone": "../?tag=offers" not in t,
        "new date present": p["date"]["en"] in t,
        "json-ld date updated": '"datePublished": "%s"' % p["date"]["iso"] in t,
    }
    for name, ok in checks.items():
        if not ok:
            fail("post check failed: %s" % name)
    m2 = re.search(r"const translations = (\{.*?\});\s*function", t, re.S)
    tr2 = json.loads(m2.group(1))
    for lang in LANGS:
        if tr2[lang]["post_title"] != p["title"][lang]:
            fail("translations %s post_title mismatch" % lang)
        if tr2[lang]["post_content"] != p["body"][lang]:
            fail("translations %s post_content mismatch" % lang)
        for key, txt in zip(p["tag_keys"], p["tags"][lang]):
            if tr2[lang].get(key) != txt:
                fail("translations %s %s mismatch" % (lang, key))
        if "facturio_crosslink" in tr2[lang]:
            fail("translations %s still has facturio_crosslink" % lang)
    if "it" in tr2:
        if tr2["it"].get("post_title") != p["title"]["en"]:
            fail("translations it post_title fallback mismatch")
        if tr2["it"].get("post_content") != p["body"]["en"]:
            fail("translations it post_content fallback mismatch")
        if "facturio_crosslink" in tr2["it"]:
            fail("translations it still has facturio_crosslink")
    open(dest, "w", encoding="utf-8").write(t)
    return dest


def update_index(p, n):
    t = open(INDEX, encoding="utf-8").read()
    slugs = " ".join(k[len("tag_"):] for k in p["tag_keys"])
    chips = "".join('<a href="?tag=%s" data-i18n="%s">%s</a>'
                    % (k[len("tag_"):], k, p["tags"]["en"][i])
                    for i, k in enumerate(p["tag_keys"]))
    card = ("\n<!-- %s -->\n"
            '<article class="solution-card blog-grid-card" data-tags="%s">\n'
            '<div class="blog-meta" data-i18n="post%d_date">%s</div>\n'
            '<h3><a href="posts/%s.html" data-i18n="post%d_title">%s</a></h3>\n'
            '<p data-i18n="post%d_desc">%s</p>\n'
            '<div class="chip-row">\n%s\n</div>\n'
            "</article>\n"
            % (p["date"]["en"], slugs, n, p["date"]["en"], p["slug"], n,
               p["title"]["en"], n, p["meta"]["en"], chips))
    anchor = '<div class="cards blog-grid">'
    if t.count(anchor) != 1:
        fail("index blog-grid anchor not unique")
    t = t.replace(anchor, anchor + card, 1)

    m = re.search(r"const translations = (\{.*?\});\s*function", t, re.S)
    tr = json.loads(m.group(1))
    for lang in LANGS:
        d = tr[lang]
        for i, k in enumerate(p["tag_keys"]):
            if k in d:
                if d[k] != p["tags"][lang][i]:
                    fail("index %s %s text mismatch: %r vs %r"
                         % (lang, k, d[k], p["tags"][lang][i]))
            else:
                d[k] = p["tags"][lang][i]
                print("  index %s: added new tag key %s" % (lang, k))
        d["post%d_date" % n] = p["date"][lang]
        d["post%d_title" % n] = p["title"][lang]
        d["post%d_desc" % n] = p["meta"][lang]
    new_tr = json.dumps(tr, ensure_ascii=False)
    t = re.sub(r"const translations = \{.*?\};\s*(?=function)",
               lambda _: "const translations = " + new_tr + ";\n", t, flags=re.S)
    open(INDEX, "w", encoding="utf-8").write(t)
    cnt = t.count('<article class="solution-card blog-grid-card"')
    print("  index: now %d cards" % cnt)


def update_sitemap(p):
    t = open(SITEMAP, encoding="utf-8").read()
    blocks = []
    added = []
    for f in sorted(os.listdir(POSTS_DIR)):
        if not f.endswith(".html"):
            continue
        stem = f[:-5]
        loc = "%s/blog/posts/%s" % (BASE, stem)
        if loc in t:
            continue
        src = open(os.path.join(POSTS_DIR, f), encoding="utf-8").read()
        dm = re.search(r'"datePublished": "([\d-]+)"', src)
        lastmod = dm.group(1) if dm else p["date"]["iso"]
        blocks.append("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n"
                      "    <changefreq>monthly</changefreq>\n"
                      "    <priority>0.6</priority>\n  </url>\n" % (loc, lastmod))
        added.append(stem)
    if blocks:
        t = t.replace("</urlset>", "".join(blocks) + "</urlset>")
    # repair the one malformed lastmod found on whatsapp-email-crm
    bad = re.search(r"(<loc>%s/blog/posts/whatsapp-email-crm</loc>\s*<lastmod>)([\d-]+)(</lastmod>)" % BASE, t)
    if bad and not re.match(r"\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$", bad.group(2)):
        src = open(os.path.join(POSTS_DIR, "whatsapp-email-crm.html"), encoding="utf-8").read()
        dm = re.search(r'"datePublished": "([\d-]+)"', src)
        if dm:
            t = t.replace("<lastmod>%s</lastmod>" % bad.group(2),
                          "<lastmod>%s</lastmod>" % dm.group(1), 1)
            print("  sitemap: repaired invalid lastmod %s for whatsapp-email-crm -> %s"
                  % (bad.group(2), dm.group(1)))
    open(SITEMAP, "w", encoding="utf-8").write(t)
    return added


def main():
    if len(sys.argv) != 2:
        print("usage: add_sw_post.py <post.json>")
        sys.exit(2)
    p = json.load(open(sys.argv[1], encoding="utf-8"))
    idx = open(INDEX, encoding="utf-8").read()
    n = p.get("n") or next_post_number(idx)
    print("publishing post %d: %s" % (n, p["slug"]))
    dest = build_post_file(p)
    print("  wrote %s" % dest)
    update_index(p, n)
    added = update_sitemap(p)
    print("  sitemap entries added: %s" % (", ".join(added) or "none"))
    print("DONE post %d -> %s" % (n, dest))


if __name__ == "__main__":
    main()
