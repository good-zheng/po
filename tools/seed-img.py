"""把 vibe_images/ 里的 ImageGen 源图压成 jar 内静态图。

产物落 api-bootstrap 的 static/covers 与 static/ingredients。食材源图按约定用
`ing-<slug>_<ts>.png` 命名，去掉 ing- 前缀即产物名；其余源图一律当封面处理。
（新菜系的封面不落 jar 而走 COS，见 tools/cos-upload.py 与 tools/README-covers.md。）
幂等：目标 jpg 已存在则跳过，换图要先删掉旧 jpg。

    py tools/seed-img.py                  # 默认只收 ing-*.png 食材源图
    py tools/seed-img.py 'xiang-*.png'    # 补旧批次封面时显式给通配
"""
import argparse
import glob, io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(REPO, 'services/api/api-bootstrap/src/main/resources/static') + '/'
SRC = os.path.join(REPO, 'vibe_images') + '/'
COVERS = STATIC + 'covers/'
INGREDIENTS = STATIC + 'ingredients/'
ING_PREFIX = 'ing-'


def convert(pattern):
    os.makedirs(COVERS, exist_ok=True)
    os.makedirs(INGREDIENTS, exist_ok=True)
    n = 0
    for p in sorted(glob.glob(SRC + pattern)):
        slug = os.path.basename(p).split('_')[0]
        if slug.startswith(ING_PREFIX):
            dst, name = INGREDIENTS, slug[len(ING_PREFIX):]
        else:
            dst, name = COVERS, slug
        out = dst + name + '.jpg'
        if os.path.exists(out):
            print('  跳过（已存在）：' + out)
            continue
        Image.open(p).convert('RGB').save(out, 'JPEG', quality=85)
        print('  写出：' + out)
        n += 1
    return n


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='vibe_images 源图 → static 产物 jpg')
    ap.add_argument('pattern', nargs='?', default='ing-*.png',
                    help="vibe_images 下的文件名通配，默认只处理食材源图——"
                         "新菜系封面走 COS，别烘进 jar（旧批次封面已在 static/covers 里）")
    a = ap.parse_args()
    print('新增 %d 张' % convert(a.pattern))
    for d in (COVERS, INGREDIENTS):
        print(d, len(os.listdir(d)), 'files')
