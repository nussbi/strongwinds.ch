import json
import pathlib
import re
import sys
from bs4 import BeautifulSoup

root = pathlib.Path(__file__).resolve().parents[1]
post = json.loads(pathlib.Path(sys.argv[1]).read_text())
slug = post['slug']
if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
    raise ValueError('Use a lowercase hyphenated slug')
source = root / '.source' / 'pages.json'
pages = json.loads(source.read_text())
path = 'blog/posts/' + slug + '/index.html'
if path in pages:
    raise ValueError('Post already exists; update its source entry instead')
template = pages['blog/posts/ai-agents-reality-check/index.html']
match = re.search(r'const translations\s*=\s*(\{.*?\});', template, re.S)
translations = json.loads(match.group(1))
for lang in ['en', 'de', 'fr', 'it']:
    for key in ['title', 'meta', 'body']:
        if lang not in post[key]:
            raise ValueError('Missing ' + lang + ' in ' + key)
    translations[lang].update({'post_title': post['title'][lang], 'meta_description': post['meta'][lang], 'og_title': post['title'][lang], 'og_description': post['meta'][lang], 'post_content': post['body'][lang]})
    for key in list(translations[lang]):
        if key.startswith('tag_'):
            del translations[lang][key]
    for tag in post.get('tags', []):
        translations[lang]['tag_' + tag['slug']] = tag[lang]
template = template[:match.start(1)] + json.dumps(translations, ensure_ascii=False) + template[match.end(1):]
doc = BeautifulSoup(template, 'html.parser')
doc.title.string = post['title']['en']
doc.h1.string = post['title']['en']
doc.select_one('meta[name=description]')['content'] = post['meta']['en']
doc.select_one('link[rel=canonical]')['href'] = 'https://strongwinds.ch/blog/posts/' + slug + '/'
for script in doc.select('script[type="application/ld+json"]'):
    data = json.loads(script.text)
    data['headline'] = post['title']['en']
    data['description'] = post['meta']['en']
    data['datePublished'] = post['date']
    data['dateModified'] = post['date']
    script.string = json.dumps(data, ensure_ascii=False)
body = doc.select_one('[data-i18n-html=post_content]')
body.clear()
body.append(BeautifulSoup(post['body']['en'], 'html.parser'))
meta = doc.select_one('.blog-meta')
if meta:
    meta.string = post['date']
related = doc.select_one('.related-posts')
if related:
    related.decompose()
pages[path] = str(doc)
source.write_text(json.dumps(pages, ensure_ascii=False))
print('Added source post. Run redesign.py, validate.py, then stage.py.')
