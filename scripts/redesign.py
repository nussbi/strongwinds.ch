import html
import json
import pathlib
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

R = pathlib.Path(__file__).resolve().parents[1]
B = 'https://strongwinds.ch'
LANGS = ['en', 'de', 'fr', 'it']
FOLDERS = ['ai-agents', 'ki-agenten', 'agents-ia', 'agenti-ia']
GUIDE_SLUGS = [
    ['', 'what-is-an-ai-agent', 'openclaw', 'hermes', 'openclaw-vs-hermes', 'hosted-vs-local', 'security', 'getting-started'],
    ['', 'was-ist-ein-ki-agent', 'openclaw', 'hermes', 'openclaw-vs-hermes', 'gehostet-vs-lokal', 'sicherheit', 'erste-schritte'],
    ['', 'qu-est-ce-qu-un-agent-ia', 'openclaw', 'hermes', 'openclaw-vs-hermes', 'heberge-vs-local', 'securite', 'premiers-pas'],
    ['', 'cos-e-un-agente-ia', 'openclaw', 'hermes', 'openclaw-vs-hermes', 'ospitato-vs-locale', 'sicurezza', 'primi-passi']
]
S = R / '.source' / 'pages.json'
S.parent.mkdir(exist_ok=True)
if not S.exists():
    S.write_text(json.dumps({str(f.relative_to(R)): f.read_text() for f in R.rglob('*.html') if 'dist' not in f.parts}, ensure_ascii=False))
SOURCE = json.loads(S.read_text())
POSTS = sorted(p.split('/')[2] for p in SOURCE if p.startswith('blog/posts/') and p.endswith('/index.html'))
DUPLICATE = 'ai-agenten-fuer-schweizer-kmu'
UI = {
    'en': ['AI that works.\nFor the way you work.', 'AI agents for Swiss businesses', 'Less busywork. More room for what matters. I help freelancers and SMEs put AI agents to work — with OpenClaw, Hermes Agent, and workflows built around your business.', 'Explore AI agents', 'Free 30-minute conversation. No sales pressure.', 'Your tools. Better connected.', 'Illustrative workflow — no real customer data', 'Prepare a reply to this client enquiry using our approved documents.', 'Understand the request', 'Find the right context', 'Prepare a useful draft', 'You approve before sending', 'AI agent workflow', 'Human in the loop', 'Skip to content', 'Search articles', 'articles', 'No matching articles. Try another search.', 'Clear filters', 'Privacy', 'Cookie settings', 'Optional analytics stay off unless you agree. They help me understand how the website is used.', 'Allow analytics', 'No thanks', 'Independent AI consultant', 'Useful ideas.\nWithout the hype.', 'Browse all insights', 'Navigation', 'Get in touch', 'Based in Fuerteventura. Working with Swiss businesses.', 'Practical AI.\nNot another IT project.', 'Small steps.\nReal progress.', 'A human behind\nthe automation.', 'Email Christian'],
    'de': ['KI, die funktioniert.\nFür deinen Arbeitsalltag.', 'KI-Agenten für Schweizer Unternehmen', 'Weniger Routine. Mehr Zeit fürs Wesentliche. Ich helfe Selbständigen und KMU, KI-Agenten sinnvoll einzusetzen — mit OpenClaw, Hermes Agent und Abläufen, die zu deinem Unternehmen passen.', 'KI-Agenten entdecken', 'Kostenloses Gespräch von 30 Minuten. Ohne Verkaufsdruck.', 'Deine Tools. Besser verbunden.', 'Beispielablauf — keine echten Kundendaten', 'Bereite eine Antwort auf diese Kundenanfrage mit unseren freigegebenen Dokumenten vor.', 'Anfrage verstehen', 'Passenden Kontext finden', 'Einen hilfreichen Entwurf erstellen', 'Du gibst den Versand frei', 'Ablauf mit KI-Agent', 'Du behältst die Kontrolle', 'Zum Inhalt springen', 'Beiträge suchen', 'Beiträge', 'Keine passenden Beiträge. Versuche einen anderen Suchbegriff.', 'Filter zurücksetzen', 'Datenschutz', 'Cookie-Einstellungen', 'Optionale Analysedaten bleiben ohne deine Zustimmung ausgeschaltet. Sie helfen mir, die Nutzung der Website zu verstehen.', 'Analyse erlauben', 'Nein danke', 'Unabhängiger KI-Berater', 'Nützliche Ideen.\nOhne Hype.', 'Alle Beiträge ansehen', 'Navigation', 'Kontakt', 'Auf Fuerteventura zu Hause. Für Schweizer Unternehmen da.', 'Praktische KI.\nKein neues IT-Grossprojekt.', 'Kleine Schritte.\nSpürbarer Fortschritt.', 'Ein Mensch hinter\nder Automatisierung.', 'Christian eine E-Mail schreiben'],
    'fr': ['Une IA qui fonctionne.\nÀ votre façon.', 'Agents IA pour les entreprises suisses', 'Moins de tâches répétitives. Plus de temps pour l’essentiel. J’aide les indépendants et les PME à utiliser des agents IA — avec OpenClaw, Hermes Agent et des processus adaptés à leur activité.', 'Découvrir les agents IA', 'Un échange gratuit de 30 minutes. Sans pression commerciale.', 'Vos outils. Mieux connectés.', 'Exemple de processus — aucune donnée client réelle', 'Prépare une réponse à cette demande client à partir de nos documents approuvés.', 'Comprendre la demande', 'Trouver le bon contexte', 'Préparer un brouillon utile', 'Vous validez avant l’envoi', 'Processus avec agent IA', 'Vous gardez la main', 'Aller au contenu', 'Rechercher des articles', 'articles', 'Aucun article trouvé. Essayez une autre recherche.', 'Réinitialiser les filtres', 'Confidentialité', 'Préférences de cookies', 'Les statistiques facultatives restent désactivées sans votre accord. Elles m’aident à comprendre l’utilisation du site.', 'Autoriser les statistiques', 'Non merci', 'Consultant IA indépendant', 'Des idées utiles.\nSans battage médiatique.', 'Voir tous les articles', 'Navigation', 'Contact', 'Installé à Fuerteventura. Au service des entreprises suisses.', 'Une IA concrète.\nPas un grand projet informatique.', 'De petits pas.\nDe vrais progrès.', 'Une personne derrière\nl’automatisation.', 'Écrire à Christian'],
    'it': ['Un’IA che funziona.\nA modo tuo.', 'Agenti IA per le imprese svizzere', 'Meno attività ripetitive. Più tempo per ciò che conta. Aiuto indipendenti e PMI a usare gli agenti IA — con OpenClaw, Hermes Agent e processi adatti alla loro attività.', 'Scopri gli agenti IA', 'Conversazione gratuita di 30 minuti. Senza pressione commerciale.', 'I tuoi strumenti. Collegati meglio.', 'Esempio di processo — nessun dato cliente reale', 'Prepara una risposta a questa richiesta del cliente usando i nostri documenti approvati.', 'Capire la richiesta', 'Trovare il contesto giusto', 'Preparare una bozza utile', 'Approvi tu prima dell’invio', 'Processo con agente IA', 'Mantieni il controllo', 'Vai al contenuto', 'Cerca articoli', 'articoli', 'Nessun articolo trovato. Prova un’altra ricerca.', 'Rimuovi i filtri', 'Privacy', 'Preferenze cookie', 'Le statistiche facoltative restano disattivate senza il tuo consenso. Mi aiutano a capire come viene usato il sito.', 'Consenti le statistiche', 'No grazie', 'Consulente IA indipendente', 'Idee utili.\nSenza clamore.', 'Vedi tutti gli articoli', 'Navigazione', 'Contatti', 'A Fuerteventura. Al servizio delle imprese svizzere.', 'IA concreta.\nNon un grande progetto informatico.', 'Piccoli passi.\nProgressi concreti.', 'Una persona dietro\nl’automazione.', 'Scrivi a Christian']
}

def e(v): return html.escape(str(v), quote=True)
def br(v): return '<br>'.join(e(x) for x in v.split('\n'))
def route(p, l): return '/' + (l+'/' if l!='en' else '') + (p.strip('/')+'/' if p.strip('/') else '')
def guide(l): return '/'+FOLDERS[LANGS.index(l)]+'/'
def soup(t): return BeautifulSoup(t, 'html.parser')
def dictionaries(t):
    m = re.search(r'const translations\s*=\s*(\{.*?\});', t, re.S)
    return json.loads(m.group(1)) if m else {}
def localized(t, l):
    doc=soup(t); ds=dictionaries(t); d=ds.get(l, ds.get('en', {}))
    for n in doc.select('[data-i18n],[data-i18n-html]'):
        k=n.get('data-i18n-html') or n.get('data-i18n')
        if k in d:
            n.clear(); n.append(soup(d[k]) if n.has_attr('data-i18n-html') else str(d[k]))
    if l=='de':doc=soup(str(doc).replace('ß','ss'))
    return doc,d
def clean(main, file, l):
    for n in main.select('[href],[src]'):
        attr='href' if n.has_attr('href') else 'src'; v=n[attr]
        if not v or v.startswith(('#','mailto:','tel:','data:')): continue
        if v.startswith(B): v=v[len(B):]
        if v.startswith(('https://','http://','//')):
            if n.get('target')=='_blank':n['rel']='noopener noreferrer'
            continue
        if 'assets/' in v:n[attr]='/assets/'+v.split('assets/',1)[1];continue
        p=urlparse(v); basename=p.path.rstrip('/').split('/')[-1].removesuffix('.html')
        if p.query.startswith('tag='): target=route('blog',l)+'?'+p.query
        elif basename in POSTS: target=route('blog/posts/'+basename,l)
        elif basename=='answering-reviews-with care':target=route('blog/posts/answering-reviews-calmly',l)
        elif basename in ['about','projects','blog']:target=route(basename,l)
        elif p.path in ['../','../../'] and file.startswith('blog/'):target=route('blog',l)
        elif p.path in ['./','/','index.html','../index.html','../../index.html']:target=route('',l)
        else:
            target=urljoin('/'+file.removesuffix('index.html'),v)
            for j,folder in enumerate(FOLDERS):
                if folder+'/' in p.path:
                    slug=p.path.split(folder+'/',1)[1].strip('/')
                    choices=GUIDE_SLUGS[j]
                    if slug not in choices and slug in GUIDE_SLUGS[0]:slug=choices[GUIDE_SLUGS[0].index(slug)]
                    target='/'+folder+'/'+(slug+'/' if slug else '');break
        for j,folder in enumerate(FOLDERS):
            prefix='/'+folder+'/'
            if target.startswith(prefix):
                slug=target[len(prefix):].strip('/').removesuffix('.html')
                if slug in GUIDE_SLUGS[0] and slug not in GUIDE_SLUGS[j]:target=prefix+GUIDE_SLUGS[j][GUIDE_SLUGS[0].index(slug)]+'/'
        if p.fragment and '#' not in target:target+='#'+p.fragment
        n[attr]=target
    for n in main.select('[style],[data-i18n],[data-i18n-html]'):
        for attr in ['style','data-i18n','data-i18n-html']:n.attrs.pop(attr,None)
    for n in main.select('.windlines,.ch-num'):n.decompose()
    for n in main.select('.feature-card h4'):n.name='h3'
    for n in main.select('.gl-item'):
        if n.find('dt'):n.parent.name='dl'
    for n in main.select('.about-client-logos[role]'):n['role']='group'
    for n in main.select('img'):
        n['loading']='lazy';n['decoding']='async'
        if 'christian' in n.get('src',''):n['width']='640';n['height']='640'
    for n in main.select('table'):
        if 'table-wrap' not in n.parent.get('class',[]):n.wrap(soup('<div class="table-wrap"></div>').div)
    main['id']='main';return str(main)

HD=dictionaries(SOURCE['index.html'])
SERVICES = {
    'en': ['AI agent setup','OpenClaw or Hermes Agent, configured around your tools and tested with real tasks. Clear permissions, practical training, and human approval where it matters.','Workflow automation','Connect email, documents, and everyday tools. Simplify repetitive hand-offs without losing control of the important decisions.','Advice & training','Choose a useful starting point and learn by doing. Clear answers, practical guidance, and no unnecessary jargon.'],
    'de': ['KI-Agenten einrichten','OpenClaw oder Hermes Agent, passend zu deinen Tools eingerichtet und mit echten Aufgaben getestet. Klare Zugriffsrechte, praktische Schulung und deine Freigabe an den entscheidenden Stellen.','Abläufe automatisieren','E-Mails, Dokumente und tägliche Tools verbinden. Wiederkehrende Übergaben vereinfachen, ohne die Kontrolle über wichtige Entscheidungen zu verlieren.','Beratung & Schulung','Einen sinnvollen Einstieg finden und direkt ausprobieren. Klare Antworten, praktische Begleitung und kein unnötiges Fachchinesisch.'],
    'fr': ['Configuration d’agents IA','OpenClaw ou Hermes Agent, configuré autour de vos outils et testé avec des tâches réelles. Des droits d’accès clairs, une formation pratique et votre validation aux étapes importantes.','Automatisation des processus','Relier vos e-mails, vos documents et vos outils du quotidien. Simplifier les tâches répétitives sans perdre la maîtrise des décisions importantes.','Conseil & formation','Choisir un point de départ utile et apprendre par la pratique. Des réponses claires, un accompagnement concret et pas de jargon inutile.'],
    'it': ['Configurazione di agenti IA','OpenClaw o Hermes Agent, configurato intorno ai tuoi strumenti e testato con attività reali. Permessi chiari, formazione pratica e la tua approvazione nei momenti importanti.','Automazione dei processi','Collegare e-mail, documenti e strumenti quotidiani. Semplificare i passaggi ripetitivi senza perdere il controllo delle decisioni importanti.','Consulenza & formazione','Scegliere un punto di partenza utile e imparare facendo. Risposte chiare, supporto pratico e niente gergo superfluo.']
}
for lang in LANGS:
    for n,i in [(1,0),(3,2),(4,4)]:
        HD[lang]['card'+str(n)+'_title']=SERVICES[lang][i]
        HD[lang]['card'+str(n)+'_text']=SERVICES[lang][i+1]
HD['de']['step3_text']='Ich richte die passenden Werkzeuge gemeinsam mit dir ein und schule dein Team ohne Druck.'
HD['fr'].update({'contact_a':'Parlons de','contact_b':'votre quotidien.','contact_text':'30 minutes. Sans pression commerciale. Un échange concret sur les tâches dont l’IA pourrait vous décharger.','step1_text':'Nous commençons par un échange sur les tâches qui prennent du temps dans votre semaine.','step2_text':'J’analyse les points de friction et, si nécessaire, j’échange brièvement avec votre équipe.','step3_text':'Nous mettons en place les bons outils ensemble et formons votre équipe sans pression.'})
pages={}; groups={}; records=[]
def brand(l):return f'<a class="brand" href="{route("",l)}"><img src="/assets/logo-mark.svg" alt="" width="38" height="38"><span>strongwinds<span class="dot">.ch</span></span></a>'
def labels(l):
    d=HD[l];return [(d['nav_solutions'],route('',l)+'#solutions'),(d['nav_guide'],guide(l)),(d['nav_about'],route('about',l)),(d['nav_blog'],route('blog',l)),(d['nav_projects'],route('projects',l))]
def header(l,alt,current):
    u=UI[l]; nav=''.join(f'<a href="{p}"'+(' aria-current="page"' if p==current else '')+f'>{e(t)}</a>' for t,p in labels(l))
    langs=''.join(f'<a href="{alt[k]}" lang="{k}" hreflang="{k}" aria-label="{k.upper()} — {name}"'+(' aria-current="true"' if k==l else '')+f'>{k.upper()}</a>' for k,name in zip(LANGS,['English','Deutsch','Français','Italiano']))
    return f'<a class="skip-link" href="#main">{e(u[14])}</a><header class="topbar"><div class="topbar-inner">{brand(l)}<nav class="nav" id="main-nav" aria-label="{e(u[27])}">{nav}</nav><button class="nav-toggle" type="button" aria-label="{e(u[27])}" aria-expanded="false" aria-controls="main-nav">☰</button><nav class="language-links" aria-label="Language">{langs}</nav><a class="button header-contact" href="{route("",l)}#contact">{e(HD[l]['hero_cta'])} ↗</a></div></header>'
def footer(l):
    u=UI[l];links=''.join(f'<a href="{p}">{e(t)}</a>' for t,p in labels(l))
    return f'<footer class="site-footer"><div class="container"><div class="footer-grid"><div>{brand(l)}<p>{e(u[1])}.<br>{e(u[29])}</p></div><div><h3>{e(u[27])}</h3><nav>{links}</nav></div><div><h3>{e(u[28])}</h3><nav><a href="mailto:christian@strongwinds.ch">Email</a><a href="https://wa.me/41762558277">WhatsApp</a><a href="https://www.linkedin.com/in/nussbi">LinkedIn</a></nav></div><div><h3>{e(u[19])}</h3><nav><a href="{route("privacy",l)}">{e(u[19])}</a><button type="button" data-cookie-settings>{e(u[20])}</button></nav></div></div><div class="footer-bottom"><span>© 2026 strongwinds.ch · Christian Nussbaumer</span><span>OpenClaw · Hermes Agent · AI automation</span></div></div></footer><aside id="cookie-panel" class="cookie-panel" hidden aria-label="{e(u[20])}"><p>{e(u[21])} <a href="{route("privacy",l)}">{e(u[19])}</a></p><div class="actions"><button class="button secondary" type="button" data-consent="no">{e(u[23])}</button><button class="button" type="button" data-consent="yes">{e(u[22])}</button></div></aside>'
def contact(l):
    d=HD[l];u=UI[l]
    return f'<section class="contact-section" id="contact"><div class="container"><div class="contact-box"><div class="contact-grid"><div><p class="eyebrow">{e(u[28])}</p><h2>{e(d["contact_a"])}<br>{e(d["contact_b"])}</h2><p>{e(d["contact_text"])}</p></div><div><a class="button white" href="mailto:christian@strongwinds.ch?subject=AI%20consultation">{e(u[33])} ↗</a><a class="contact-email" href="https://wa.me/41762558277">WhatsApp · +41 76 255 82 77</a></div></div></div></div></section>'
def render(p,l,title,desc,main,alt,kind='WebPage',extra=None):
    if l=='de':title=title.replace('ß','ss');desc=desc.replace('ß','ss');main=main.replace('ß','ss')
    canonical=p
    if '/blog/posts/'+DUPLICATE+'/' in p:
        canonical=p.replace(DUPLICATE,'whatsapp-email-crm')
        alt={k:v.replace(DUPLICATE,'whatsapp-email-crm') for k,v in alt.items()}
    if len(title)>70:
        title=title.removesuffix(' | strongwinds.ch')
        if len(title)>70:title=title[:67].rsplit(' ',1)[0]+'…'
    if len(desc)>170:desc=desc[:167].rsplit(' ',1)[0]+'…'
    url=B+canonical;web={'@type':kind,'@id':url+'#page','url':url,'name':title,'description':desc,'inLanguage':l,'isPartOf':{'@id':B+'/#website'}}
    if extra:web.update(extra)
    graph={'@context':'https://schema.org','@graph':[{'@type':'ProfessionalService','@id':B+'/#business','name':'strongwinds.ch','url':B+'/','logo':B+'/assets/wordmark.svg','email':'christian@strongwinds.ch','telephone':'+41 76 255 82 77','areaServed':{'@type':'Country','name':'Switzerland'},'address':{'@type':'PostalAddress','addressLocality':'Corralejo','addressCountry':'ES'},'founder':{'@id':B+'/#christian'}},{'@type':'Person','@id':B+'/#christian','name':'Christian Nussbaumer','url':B+'/about/','image':B+'/assets/christian.jpg','sameAs':['https://www.linkedin.com/in/nussbi']},{'@type':'WebSite','@id':B+'/#website','url':B+'/','name':'strongwinds.ch'},web]}
    if canonical!=route('',l):
        crumbs=[{'@type':'ListItem','position':1,'name':{'en':'Home','de':'Startseite','fr':'Accueil','it':'Home'}[l],'item':B+route('',l)}]
        if '/blog/posts/' in canonical:crumbs.append({'@type':'ListItem','position':2,'name':HD[l]['nav_blog'],'item':B+route('blog',l)})
        elif canonical.startswith(guide(l)) and canonical!=guide(l):crumbs.append({'@type':'ListItem','position':2,'name':HD[l]['nav_guide'],'item':B+guide(l)})
        crumbs.append({'@type':'ListItem','position':len(crumbs)+1,'name':extra.get('headline',title) if extra else title,'item':url})
        graph['@graph'].append({'@type':'BreadcrumbList','itemListElement':crumbs})
    js=json.dumps(graph,ensure_ascii=False).replace('</','<\\/')
    alternates=''.join(f'<link rel="alternate" hreflang="{k}" href="{B+alt[k]}">' for k in LANGS)+f'<link rel="alternate" hreflang="x-default" href="{B+alt["en"]}">'
    pages[p]=f'<!doctype html><html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(desc)}"><meta name="theme-color" content="#6750ce"><link rel="canonical" href="{url}">{alternates}<meta property="og:type" content="{"article" if kind=="BlogPosting" else "website"}"><meta property="og:site_name" content="strongwinds.ch"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:locale" content="{dict(en="en_GB",de="de_CH",fr="fr_CH",it="it_CH")[l]}"><meta property="og:image" content="{B}/assets/social-card.png"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{B}/assets/social-card.png"><link rel="icon" type="image/svg+xml" href="/assets/favicon.svg"><link rel="stylesheet" href="/styles.css"><script type="application/ld+json">{js}</script><script defer src="/site.js"></script></head><body>{header(l,alt,p)}{main}{footer(l)}</body></html>'
    groups[p]=alt
def post(slug,l):
    f='blog/posts/'+slug+'/index.html';doc,d=localized(SOURCE[f],l);title=d.get('post_title',doc.h1.get_text(' ',strip=True));meta=doc.select_one('meta[name=description]');desc=d.get('meta_description',meta.get('content',title) if meta else title);date=''
    for js in doc.select('script[type="application/ld+json"]'):
        match=re.search(r'"datePublished"\s*:\s*"([^"]+)"',js.text)
        if match:date=match.group(1)
    if not date:
        original_meta=soup(SOURCE[f]).select_one('.blog-meta')
        match=re.search(r'[A-Z][a-z]+ \d{1,2}, \d{4}',original_meta.get_text() if original_meta else '')
        if match:date=datetime.strptime(match.group(0),'%B %d, %Y').date().isoformat()
    if not re.match(r'^\d{4}-\d{2}-\d{2}',date):raise ValueError('Missing source publication date: '+slug)
    chips=doc.select_one('.post-header .chip-row')
    tags=[(k.removeprefix('tag_'),v) for k,v in d.items() if k.startswith('tag_')]
    if chips and tags:
        chips.clear()
        for key,value in tags:chips.append(soup(f'<a href="{route("blog",l)}?tag={e(key)}">{e(value)}</a>'))
    return doc,d,title,desc,date
def cards(l,limit=None):
    entries=[]
    for slug in POSTS:
        if slug==DUPLICATE:continue
        doc,d,title,desc,date=post(slug,l);tags=doc.select('.post-header .chip-row a');chips=''.join(f'<a href="{route("blog",l)}?{e(urlparse(x.get("href","")).query)}">{e(x.get_text(" ",strip=True))}</a>' for x in tags);keys=' '.join(urlparse(x.get('href','')).query.removeprefix('tag=') for x in tags)
        entries.append((date,slug,f'<article class="blog-grid-card" data-tags="{e(keys)}"><time class="blog-meta" datetime="{date[:10]}">{date[:10]}</time><h3><a href="{route("blog/posts/"+slug,l)}">{e(title)}</a></h3><p>{e(desc)}</p><div class="chip-row">{chips}</div></article>'))
    return ''.join(x[2] for x in sorted(entries,reverse=True)[:limit])
def home(l):
    d=HD[l];u=UI[l];flows=''.join(f'<div class="flow-step"><span class="flow-icon">{icon}</span><div>{e(u[i])}</div></div>' for icon,i in [('↳',8),('⌕',9),('✎',10)])
    services=''.join(f'<article class="service-card"><div class="service-icon">{icon}</div><h3>{e(d["card"+str(n)+"_title"])}</h3><p>{e(d["card"+str(n)+"_text"])}</p><a class="text-link" href="#contact">{e(d["hero_cta"])} →</a></article>' for n,icon in [(1,'✎'),(3,'⌕'),(4,'⇄')])
    process=''.join(f'<div class="process-step"><span class="step-number">0{n}</span><div><h3>{e(d.get("step"+str(n)+"_title",d.get("process"+str(n)+"_title","")))}</h3><p>{e(d.get("step"+str(n)+"_text",d.get("process"+str(n)+"_text","")))}</p></div></div>' for n in [1,2,3])
    headline=u[0].split('\n');h1=e(headline[0])+'<br><span class="accent">'+e(headline[1])+'</span>'
    about=d.get('about_p1',d.get('about_text1',''))
    return f'<main id="main"><section class="home-hero"><div class="container"><div class="hero-grid"><div class="hero-copy"><span class="pill">{e(u[1])}</span><h1>{h1}</h1><p>{e(u[2])}</p><div class="hero-actions"><a class="button" href="#contact">{e(d["hero_cta"])} ↗</a><a class="button secondary" href="{guide(l)}">{e(u[3])} →</a></div><p class="hero-note"><span>✓</span> {e(u[4])}</p></div><div class="agent-demo"><div class="demo-top"><span class="demo-dots"><i></i><i></i><i></i></span><b>{e(u[12])}</b><span class="demo-status">● {e(u[13])}</span></div><div class="demo-request"><div class="demo-label">{e(u[8])}</div>{e(u[7])}</div><div class="demo-flow">{flows}</div><div class="demo-result"><strong>✓ {e(u[10])}</strong><span>{e(u[11])}</span></div><p class="demo-caption">{e(u[6])}</p></div></div><div class="hero-foot"><span class="label">{e(u[5])}</span><div class="tool-names"><span>OpenClaw</span><span>Hermes Agent</span><span>Email</span><span>Documents</span><span>APIs</span></div></div></div></section><section class="section" id="solutions"><div class="container"><div class="section-head"><div><p class="eyebrow">{e(d["nav_solutions"])}</p><h2>{br(u[30])}</h2></div><p class="section-intro">{e(d["solutions_intro"])}</p></div><div class="service-grid">{services}</div></div></section><section class="section approach-section" id="how"><div class="container approach-grid"><div><p class="eyebrow">{e(d["nav_how"])}</p><h2>{br(u[31])}</h2><p class="approach-lead">{e(d.get("process_intro",d.get("how_intro","")))}</p><a class="text-link" href="{guide(l)}">{e(u[3])} →</a></div><div>{process}</div></div></section><section class="section"><div class="container founder-grid"><img class="founder-image" src="/assets/christian.jpg" alt="Christian Nussbaumer" width="640" height="640" loading="lazy"><div class="founder-copy"><p class="eyebrow">{e(d["nav_about"])}</p><h2>{br(u[32])}</h2><p>{e(about)}</p><a class="text-link" href="{route("about",l)}">{e(d["nav_about"])} →</a><span class="founder-name">Christian Nussbaumer<small>{e(u[24])}</small></span></div></div></section><section class="section"><div class="container"><div class="section-head"><div><p class="eyebrow">{e(d["nav_blog"])}</p><h2>{br(u[25])}</h2></div><a class="text-link" href="{route("blog",l)}">{e(u[26])} →</a></div><div class="blog-grid">{cards(l,3)}</div></div></section>{contact(l)}</main>'

for l in LANGS:
    u=UI[l];d=HD[l]
    title={'en':'AI Agents & AI Consulting for Swiss SMEs','de':'KI-Agenten & KI-Beratung für Schweizer KMU','fr':'Agents IA & conseil IA pour les PME suisses','it':'Agenti IA & consulenza IA per le PMI svizzere'}[l]
    render(route('',l),l,title+' | strongwinds.ch',u[2],home(l),{k:route('',k) for k in LANGS})
    for name in ['about','projects']:
        f=name+'/index.html';doc,td=localized(SOURCE[f],l);main=doc.main
        if main.h1:main.h1.string='Christian Nussbaumer' if name=='about' else d['nav_projects'];main.h1['class']=[]
        for broken in main.select('a[href*="Christian-Nussbaumer-CV.pdf"]'):broken.decompose()
        main.append(soup(contact(l)));title=(d['nav_about']+' · Christian Nussbaumer' if name=='about' else d['nav_projects'])+' | strongwinds.ch'
        render(route(name,l),l,title,u[2],clean(main,f,l),{k:route(name,k) for k in LANGS},'AboutPage' if name=='about' else 'CollectionPage')
    main=f'<main id="main"><section class="blog-header"><div class="container"><p class="eyebrow">{e(d["nav_blog"])}</p><h1>{br(u[25])}</h1><p class="guide-lead">{e(d["solutions_intro"])}</p></div></section><section class="blog-list"><div class="container"><div class="blog-toolbar"><label for="blog-search">{e(u[15])}</label><input id="blog-search" type="search" placeholder="{e(u[15])}" autocomplete="off"><small><span id="blog-count" aria-live="polite">{len(POSTS)}</span> {e(u[16])}</small><a class="text-link" href="{route("blog",l)}">{e(u[18])}</a></div><p id="blog-empty" hidden>{e(u[17])}</p><div class="cards blog-grid">{cards(l)}</div></div></section></main>'
    render(route('blog',l),l,d['nav_blog']+' · '+u[1]+' | strongwinds.ch',u[2],main,{k:route('blog',k) for k in LANGS},'CollectionPage')
    for slug in POSTS:
        doc,td,title,desc,date=post(slug,l);main=doc.main;before=main.select_one('.post-body');body=before.get_text(' ',strip=True) if before else ''
        author=main.select_one('.post-author')
        if author:
            for a in author.select('a[href]'):
                if a.get('href','').endswith('about.html'):a['href']=route('about',l)
        output=clean(main,'blog/posts/'+slug+'/index.html',l);after=soup(output).select_one('.post-body')
        if before:assert body==after.get_text(' ',strip=True),(slug,l,'Blog body changed')
        records.append({'slug':slug,'language':l,'title':title,'body_unchanged':True})
        extra={'headline':title,'datePublished':date,'author':{'@id':B+'/#christian'},'publisher':{'@id':B+'/#business'},'mainEntityOfPage':B+route('blog/posts/'+slug,l),'image':B+'/assets/social-card.png'}
        render(route('blog/posts/'+slug,l),l,title+' | strongwinds.ch',desc,output,{k:route('blog/posts/'+slug,k) for k in LANGS},'BlogPosting',extra)
    privacy={
        'en':['This website is operated by Christian Nussbaumer, based in Corralejo, Spain, for businesses in Switzerland. For privacy enquiries: christian@strongwinds.ch.','Hosting','Cloudflare Pages hosts this site and processes connection and security data, including IP addresses, to deliver and protect it.','Optional analytics','Google Tag Manager is loaded only after you allow analytics. You can reopen cookie settings at any time. Declining analytics does not limit the site. Existing third-party cookies may need to be removed using your browser controls.','Getting in touch','Email, WhatsApp and LinkedIn open external services. Information you send is used to respond to your enquiry. Do not send confidential client data without first agreeing on a suitable process.','Your choices','Contact me to request access to, correction of, or deletion of personal data I hold about you, subject to applicable legal obligations.'],
        'de':['Diese Website wird von Christian Nussbaumer mit Sitz in Corralejo, Spanien, für Unternehmen in der Schweiz betrieben. Bei Datenschutzfragen: christian@strongwinds.ch.','Hosting','Cloudflare Pages hostet diese Website und verarbeitet Verbindungs- und Sicherheitsdaten, einschliesslich IP-Adressen, um sie bereitzustellen und zu schützen.','Optionale Analyse','Google Tag Manager wird erst nach deiner Zustimmung geladen. Du kannst die Cookie-Einstellungen jederzeit erneut öffnen. Eine Ablehnung schränkt die Website nicht ein. Bereits gesetzte Drittanbieter-Cookies musst du gegebenenfalls in deinem Browser entfernen.','Kontakt','E-Mail, WhatsApp und LinkedIn öffnen externe Dienste. Übermittelte Informationen dienen der Beantwortung deiner Anfrage. Sende keine vertraulichen Kundendaten, ohne zuvor einen geeigneten Ablauf zu vereinbaren.','Deine Möglichkeiten','Kontaktiere mich, um Auskunft, Berichtigung oder Löschung deiner bei mir gespeicherten Personendaten zu verlangen, soweit keine gesetzlichen Pflichten entgegenstehen.'],
        'fr':['Ce site est exploité par Christian Nussbaumer, installé à Corralejo, en Espagne, pour les entreprises suisses. Pour toute question : christian@strongwinds.ch.','Hébergement','Cloudflare Pages héberge ce site et traite les données de connexion et de sécurité, notamment les adresses IP, pour le fournir et le protéger.','Statistiques facultatives','Google Tag Manager est chargé uniquement après votre accord. Vous pouvez rouvrir les préférences de cookies à tout moment. Le refus ne limite pas le site. Les cookies tiers déjà enregistrés peuvent nécessiter une suppression dans votre navigateur.','Contact','L’e-mail, WhatsApp et LinkedIn ouvrent des services externes. Les informations envoyées servent à répondre à votre demande. Ne transmettez pas de données client confidentielles sans avoir convenu d’un processus approprié.','Vos choix','Contactez-moi pour demander l’accès, la rectification ou la suppression de vos données personnelles en ma possession, sous réserve des obligations légales applicables.'],
        'it':['Questo sito è gestito da Christian Nussbaumer, con sede a Corralejo, in Spagna, per le imprese svizzere. Per domande sulla privacy: christian@strongwinds.ch.','Hosting','Cloudflare Pages ospita il sito e tratta dati di connessione e sicurezza, inclusi gli indirizzi IP, per fornirlo e proteggerlo.','Statistiche facoltative','Google Tag Manager viene caricato solo dopo il tuo consenso. Puoi riaprire le preferenze cookie in qualsiasi momento. Il rifiuto non limita il sito. I cookie di terze parti già presenti potrebbero richiedere la rimozione tramite il browser.','Contatti','E-mail, WhatsApp e LinkedIn aprono servizi esterni. Le informazioni inviate vengono usate per rispondere alla richiesta. Non inviare dati riservati dei clienti senza aver concordato una procedura adatta.','Le tue scelte','Contattami per chiedere accesso, correzione o cancellazione dei dati personali che conservo, fatti salvi gli obblighi di legge applicabili.']
    }[l]
    main='<main id="main" class="privacy-page"><div class="container narrow"><h1>'+e(u[19])+'</h1><p>'+e(privacy[0])+'</p>'+''.join('<h2>'+e(privacy[i])+'</h2><p>'+e(privacy[i+1])+'</p>' for i in range(1,len(privacy),2))+'</div></main>'
    render(route('privacy',l),l,u[19]+' | strongwinds.ch',privacy[0],main,{k:route('privacy',k) for k in LANGS})

guide_sources={}
for l,folder in zip(LANGS,FOLDERS):
    for f in SOURCE:
        if f.startswith(folder+'/'):
            doc=soup(SOURCE[f]);canonical=doc.select_one('link[rel=canonical]');path='/'+f.removesuffix('index.html');alt={}
            for a in doc.select('link[rel=alternate][hreflang]'):
                if a['hreflang'] in LANGS:alt[a['hreflang']]=urlparse(a['href']).path
            number=GUIDE_SLUGS[LANGS.index(l)].index(f.split('/')[1] if f.count('/')>1 else '')
            alt={k:guide(k)+(GUIDE_SLUGS[LANGS.index(k)][number]+'/' if number else '') for k in LANGS}
            guide_sources[path]=(l,doc,f,alt)
for path,(l,doc,f,alt) in guide_sources.items():
    meta=doc.select_one('meta[name=description]');desc=meta['content'] if meta else doc.h1.get_text(' ',strip=True)
    note={'en':'Agent features depend on the installed version, model, and configuration. Local hosting does not automatically keep every request local. Limit permissions, protect credentials, and review outputs before taking action.','de':'Agentenfunktionen hängen von Version, Modell und Konfiguration ab. Lokales Hosting hält nicht automatisch jede Anfrage lokal. Begrenze Zugriffsrechte, schütze Zugangsdaten und prüfe Ergebnisse vor einer Aktion.','fr':'Les fonctionnalités dépendent de la version, du modèle et de la configuration. Un hébergement local ne garantit pas que toutes les requêtes restent locales. Limitez les droits, protégez les identifiants et vérifiez les résultats avant toute action.','it':'Le funzionalità dipendono da versione, modello e configurazione. L’hosting locale non garantisce che tutte le richieste restino locali. Limita i permessi, proteggi le credenziali e verifica i risultati prima di agire.'}[l]
    doc.main.append(soup(f'<div class="container"><aside class="callout"><p>{e(note)}</p><a class="text-link" href="https://docs.openclaw.ai/">OpenClaw docs ↗</a> · <a class="text-link" href="https://hermes-agent.nousresearch.com/docs/user-guide/security">Hermes security ↗</a></aside></div>'))
    render(path,l,doc.title.get_text(' ',strip=True).removesuffix(' | strongwinds.ch')+' | strongwinds.ch',desc,clean(doc.main,f,l),alt)
for path,text in pages.items():
    text=text.replace('<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">','<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48 64x64 128x128 256x256"><link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">')
    pages[path]=text
    file=R/path.strip('/')/'index.html' if path!='/' else R/'index.html';file.parent.mkdir(parents=True,exist_ok=True);file.write_text(text)
redirects=['/about.html /about/ 301','/projects.html /projects/ 301','/index.html / 301']+[f'/blog/posts/{s}.html /blog/posts/{s}/ 301' for s in POSTS]
R.joinpath('_redirects').write_text('\n'.join(redirects)+'\n')
R.joinpath('_headers').write_text('/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n/assets/*\n  Cache-Control: public, max-age=86400\n')
R.joinpath('robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://strongwinds.ch/sitemap.xml\n')
ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9');ET.register_namespace('xhtml','http://www.w3.org/1999/xhtml');root=ET.Element('{http://www.sitemaps.org/schemas/sitemap/0.9}urlset')
for path in sorted(pages):
    if '/blog/posts/'+DUPLICATE+'/' in path:continue
    entry=ET.SubElement(root,'{http://www.sitemaps.org/schemas/sitemap/0.9}url');ET.SubElement(entry,'{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text=B+path
    for k,p in groups[path].items():ET.SubElement(entry,'{http://www.w3.org/1999/xhtml}link',{'rel':'alternate','hreflang':k,'href':B+p})
ET.ElementTree(root).write(R/'sitemap.xml',encoding='utf-8',xml_declaration=True)
notfound=soup(pages['/']);notfound.title.string='Page not found | strongwinds.ch';notfound.main.replace_with(soup('<main id="main" class="not-found"><div class="container"><h1>Page not found</h1><p>The page may have moved. Find your article in the complete blog archive.</p><a class="button" href="/blog/">Browse all insights →</a></div></main>'));notfound.head.append(soup('<meta name="robots" content="noindex">'));R.joinpath('404.html').write_text(str(notfound))
R.joinpath('blog-preservation.json').write_text(json.dumps({'unique_posts':len(POSTS),'checks':records},ensure_ascii=False,indent=2))
print(f'Generated {len(pages)} pages. Preserved {len(POSTS)} posts in four languages.')
