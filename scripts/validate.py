import json
import pathlib
import sys
from urllib.parse import unquote, urlparse
from bs4 import BeautifulSoup

root = pathlib.Path(__file__).resolve().parents[1]
errors = []
warnings = []
pages = {}
for file in root.rglob('*.html'):
    if any(x in file.parts for x in ['dist', '.source']):
        continue
    path = '/' + str(file.relative_to(root)).removesuffix('index.html')
    pages[path] = BeautifulSoup(file.read_text(), 'html.parser')
for path, doc in pages.items():
    if path == '/404.html':
        continue
    if len(doc.select('h1')) != 1:
        errors.append([path, 'Expected one h1'])
    if not doc.select_one('main#main'):
        errors.append([path, 'Missing main landmark'])
    if not doc.title or not doc.select_one('meta[name=description]'):
        errors.append([path, 'Missing title/description'])
    for js in doc.select('script[type="application/ld+json"]'):
        try:
            json.loads(js.text)
        except ValueError:
            errors.append([path, 'Invalid JSON-LD'])
    for node in doc.select('[href],[src]'):
        attr = 'href' if node.has_attr('href') else 'src'
        value = node[attr]
        if value.startswith('https://strongwinds.ch'):
            value = value[len('https://strongwinds.ch'):]
        if value.startswith(('/', '#')) and not value.startswith('//'):
            parsed = urlparse(value)
            target = unquote(parsed.path) or path
            if target.endswith('.html') and target.removesuffix('.html') + '/' in pages:
                continue
            exists = target in pages or (root / target.lstrip('/')).is_file()
            if not exists:
                errors.append([path, 'Missing resource', target])
            if parsed.fragment and target in pages and not pages[target].find(id=parsed.fragment):
                errors.append([path, 'Missing anchor', target + '#' + parsed.fragment])
    for image in doc.select('img'):
        if not image.has_attr('alt'):
            errors.append([path, 'Missing image alt', image.get('src')])
    canonical = doc.select_one('link[rel=canonical]')
    canonical_path=path.replace('ai-agenten-fuer-schweizer-kmu','whatsapp-email-crm')
    if not canonical or canonical['href'] != 'https://strongwinds.ch' + canonical_path:
        errors.append([path, 'Canonical mismatch'])
    for alt in doc.select('link[rel=alternate][hreflang]'):
        if alt['hreflang'] == 'x-default':
            continue
        target = urlparse(alt['href']).path
        if target in pages:
            reciprocal = pages[target].select_one(f'link[hreflang="{doc.html["lang"]}"]')
            if not reciprocal or urlparse(reciprocal['href']).path != canonical_path:
                errors.append([path, 'Nonreciprocal hreflang', target])
    if len(doc.title.text) > 70:
        warnings.append([path, 'Long title', len(doc.title.text)])
    desc = doc.select_one('meta[name=description]')['content']
    if len(desc) > 180:
        warnings.append([path, 'Long description', len(desc)])
result = {'pages': len(pages)-1, 'errors': errors, 'warnings': warnings}
(root / 'validation.json').write_text(json.dumps(result, indent=2))
print(json.dumps({'pages': result['pages'], 'errors': len(errors), 'warnings': len(warnings), 'sample_errors': errors[:35]}, indent=2))
sys.exit(bool(errors))
