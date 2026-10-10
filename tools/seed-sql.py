"""从 seed/*.json 生成可导入 MySQL 的 data-*.sql 种子文件。"""
import hashlib
import io
import json
import os
import sys

from batches import BATCHES as FILES

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(REPO, 'services/api/recipe/src/main/resources/seed') + '/'
OUT = os.path.join(REPO, 'services/api/recipe/src/main/resources') + '/'
COVERS = os.path.join(REPO, 'services/api/api-bootstrap/src/main/resources/static/covers') + '/'
# 新菜系封面不落 jar 静态目录，由 tools/cos-upload.py 传腾讯云 COS，库里存公网绝对地址
VIBE = os.path.join(REPO, 'vibe_images') + '/'
COS_REGION = os.environ.get('COS_REGION', 'ap-shanghai')
COS_BUCKET = os.environ.get('COS_BUCKET', '7072-prod-d7g3zal0655a67232-1496875399')
COS_KEY_PREFIX = os.environ.get('COS_KEY_PREFIX', 'po')
COS_COVERS = 'https://%s.cos.%s.myqcloud.com/%s/covers' % (COS_BUCKET, COS_REGION, COS_KEY_PREFIX)

# (seed 文件名, 输出 sql, 封面来源: static = static/covers/, cos = COS 桶) 见 tools/batches.py


def cover_url(slug, source):
    """返回入库用的封面地址。static 分支缺文件直接失败；cos 分支缺源图先落 NULL，
    等 ImageGen 补齐后跑 tools/cos-upload.py 再导入 data-covers-backfill.sql 回填。"""
    if source == 'static':
        if not os.path.exists(COVERS + slug + '.jpg'):
            raise SystemExit('missing cover: ' + COVERS + slug + '.jpg')
        return '/api/covers/%s.jpg' % slug
    if not os.path.isdir(VIBE) or not any(f.startswith(slug + '_') for f in os.listdir(VIBE)):
        print('  ! 封面源图未生成，先写 NULL：' + slug)
        return None
    return '%s/%s.jpg' % (COS_COVERS, slug)


def esc(v):
    if v is None:
        return 'NULL'
    s = str(v).replace('\\', '\\\\').replace("'", "\\'")
    return "'" + s + "'"


def likes(title):
    return 88 + int(hashlib.md5(title.encode('utf-8')).hexdigest(), 16) % 233


def num(v):
    if v is None:
        return 'NULL'
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


def main():
    mapping = json.load(open(SEED + 'ingredient-images.json', encoding='utf-8'))
    total = 0
    backfill = []
    for src, dst, source in FILES:
        data = json.load(open(SEED + src, encoding='utf-8'))
        region = data['region']
        lines = [
            '-- 由 seed/%s 生成，请勿手改；重新生成：python tools/seed-sql.py' % src,
            '-- %s，共 %d 道。author_id = 1，likes 为标题哈希的确定性伪随机值。' % (region, len(data['recipes'])),
            '',
        ]
        for i, r in enumerate(data['recipes'], 1):
            slug = r['cover']['slug']
            cover = cover_url(slug, source)
            if source == 'cos' and cover:
                backfill.append(
                    "UPDATE recipe SET cover_image_url = %s WHERE title = %s AND category = %s"
                    " AND cover_image_url IS NULL;" % (esc(cover), esc(r['title']), esc(region)))
            lines.append('-- ========== %d. %s ==========' % (i, r['title']))
            lines.append(
                'INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time,'
                ' total_time, difficulty, servings, category, tags, author_id, is_public, likes_count,'
                ' calories, protein, fat, carbs, tips, flavor_profile) VALUES ('
                + ', '.join([
                    esc(r['title']), esc(r['description']),
                    esc(cover),
                    num(r['prepTime']), num(r['cookTime']), num(r['totalTime']),
                    num(r['difficulty']), num(r['servings']),
                    esc(region), esc(r['tags']), '1', 'TRUE', str(likes(r['title'])),
                    num(r['calories']), num(r['protein']), num(r['fat']), num(r['carbs']),
                    esc(r['tips']), esc(r['flavorProfile']),
                ]) + ');')
            lines.append('SET @r = LAST_INSERT_ID();')
            rows = []
            for j, (name, amount, unit, essential) in enumerate(r['ingredients'], 1):
                if name not in mapping:
                    raise SystemExit('ingredient not in mapping: ' + name)
                rows.append('(@r, %s, %s, %s, %s, %d, %s)' % (
                    esc(name), esc(amount), esc(unit),
                    'TRUE' if essential else 'FALSE', j, esc(mapping[name])))
            lines.append(
                'INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential,'
                ' sort_order, image_url) VALUES\n  ' + ',\n  '.join(rows) + ';')
            rows = []
            for j, (content, duration) in enumerate(r['steps'], 1):
                rows.append('(@r, %d, %s, %s)' % (j, esc(content), num(duration)))
            lines.append(
                'INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES\n  '
                + ',\n  '.join(rows) + ';')
            lines.append('')
            total += 1
        with open(OUT + dst, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines))
        print('%s -> %s (%d recipes)' % (src, dst, len(data['recipes'])))
    print('total recipes:', total)
    with open(OUT + 'data-covers-backfill.sql', 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join([
            '-- 由 tools/seed-sql.py 生成，请勿手改；重新生成：py tools/seed-sql.py',
            '-- COS 封面回填：只补 cover_image_url 仍为 NULL 的行，重复执行安全。',
            '-- 补图流程：ImageGen 生成源图 -> py tools/cos-upload.py -> py tools/seed-sql.py -> 导入本文件',
            '',
        ] + backfill) + '\n')
    print('covers backfill updates:', len(backfill))


if __name__ == '__main__':
    main()
