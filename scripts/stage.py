import pathlib
import shutil
import errno
import time

root = pathlib.Path(__file__).resolve().parents[1]
dest = root / 'dist'
if dest.exists():
    for attempt in range(5):
        try:
            shutil.rmtree(dest)
            break
        except OSError as error:
            if error.errno != errno.ENOTEMPTY or attempt == 4:
                raise
            time.sleep(0.25 * (attempt + 1))
dest.mkdir()
for name in ['assets', 'ai-agents', 'ki-agenten', 'agents-ia', 'agenti-ia', 'about', 'projects', 'blog', 'privacy', 'de', 'fr', 'it']:
    shutil.copytree(root / name, dest / name)
for name in ['index.html', '404.html', 'favicon.ico', 'styles.css', 'site.js', 'sitemap.xml', 'robots.txt', '_headers', '_redirects']:
    shutil.copyfile(root / name, dest / name)
print('Staged static deployment in dist; source snapshots and tooling excluded.')
