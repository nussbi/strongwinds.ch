import pathlib
import re

root = pathlib.Path(__file__).resolve().parents[1]
PRIVACY = {
    'en': ('Optional analytics', 'Analytics', 'This website does not load Google Tag Manager or optional analytics scripts. No analytics consent popup is used. Cookies stored by an earlier version can be removed in your browser settings.'),
    'de': ('Optionale Analyse', 'Analyse', 'Diese Website lädt weder Google Tag Manager noch optionale Analyseskripte. Es gibt kein Analyse-Einwilligungsfenster. Cookies aus einer früheren Version kannst du in deinen Browsereinstellungen entfernen.'),
    'fr': ('Statistiques facultatives', 'Statistiques', 'Ce site ne charge ni Google Tag Manager ni scripts de statistiques facultatifs. Aucune fenêtre de consentement aux statistiques n’est utilisée. Les cookies enregistrés par une version précédente peuvent être supprimés dans les paramètres de votre navigateur.'),
    'it': ('Statistiche facoltative', 'Statistiche', 'Questo sito non carica Google Tag Manager né script di statistiche facoltativi. Non viene mostrata alcuna finestra di consenso alle statistiche. Puoi eliminare i cookie salvati da una versione precedente nelle impostazioni del browser.'),
}


def clean(content, language):
    content = content.replace('src="/site.js"', 'src="/site.js?v=no-analytics-20261108"')
    content = re.sub(r'<button\b[^>]*\bdata-cookie-settings[^>]*>.*?</button>', '', content, flags=re.S)
    content = re.sub(r'<aside\b[^>]*\bid="cookie-panel"[^>]*>.*?</aside>', '', content, flags=re.S)
    old_heading, heading, body = PRIVACY[language]
    content = re.sub(r'<h2>' + re.escape(old_heading) + r'</h2><p>.*?</p>', '<h2>' + heading + '</h2><p>' + body + '</p>', content, flags=re.S)
    return content


if __name__ == '__main__':
    generator = root / 'scripts' / 'redesign.py'
    source = generator.read_text()
    source = source.replace('src="/site.js"', 'src="/site.js?v=no-analytics-20261108"')
    source = source.replace('<button type="button" data-cookie-settings>{e(u[20])}</button>', '')
    source = re.sub(r'<aside id="cookie-panel".*?</aside>', '', source)
    for old_heading, heading, body in PRIVACY.values():
        pattern = "'" + re.escape(old_heading) + "','[^']*'"
        source = re.sub(pattern, lambda match: repr(heading) + ',' + repr(body), source)
    generator.write_text(source)
    javascript = root / 'site.js'
    source = javascript.read_text()
    if '  const panel =' in source:
        source = source[:source.index('  const panel =')] + '})();\n'
    javascript.write_text(source)
    changed = 0
    for file in root.rglob('*.html'):
        if any(part in {'.source', 'dist', '.git', 'node_modules'} for part in file.relative_to(root).parts):
            continue
        content = file.read_text()
        language = re.search(r'<html[^>]*lang="(en|de|fr|it)"', content).group(1)
        updated = clean(content, language)
        if updated != content:
            file.write_text(updated)
            changed += 1
        assert 'id="cookie-panel"' not in updated
        assert 'data-cookie-settings' not in updated
        assert 'googletagmanager.com' not in updated
    print(f'Removed analytics UI from {changed} pages.')
