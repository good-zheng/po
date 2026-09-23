import glob, io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image

SRC = 'D:/pro/po/vibe_images/'
COVERS = 'D:/pro/po/services/api/api-bootstrap/src/main/resources/static/covers/'
INGREDIENTS = 'D:/pro/po/services/api/api-bootstrap/src/main/resources/static/ingredients/'


def convert(pattern, dst, strip_prefix=''):
    os.makedirs(dst, exist_ok=True)
    n = 0
    for p in sorted(glob.glob(SRC + pattern)):
        base = os.path.basename(p)
        slug = base.split('_')[0]
        if strip_prefix:
            slug = slug[len(strip_prefix):]
        out = dst + slug + '.jpg'
        if os.path.exists(out):
            continue
        im = Image.open(p).convert('RGB')
        im.save(out, 'JPEG', quality=85)
        n += 1
    return n


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if what in ('covers', 'all'):
        print('covers converted:', convert('xiang-*.png', COVERS) + convert('chuan-*.png', COVERS) + convert('gan-*.png', COVERS) + convert('classic-*.png', COVERS))
    if what in ('ingredients', 'all'):
        print('ingredients converted:', convert('ing-*.png', INGREDIENTS, 'ing-'))
    for d in (COVERS, INGREDIENTS):
        if os.path.isdir(d):
            print(d, len(os.listdir(d)), 'files')
