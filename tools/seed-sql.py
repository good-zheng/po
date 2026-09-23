"""从 seed/*.json 生成可导入 MySQL 的 data-*.sql 种子文件。"""
import hashlib
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SEED = 'D:/pro/po/services/api/recipe/src/main/resources/seed/'
OUT = 'D:/pro/po/services/api/recipe/src/main/resources/'
COVERS = 'D:/pro/po/services/api/api-bootstrap/src/main/resources/static/covers/'

FILES = [
    ('recipes-xiang-a.json', 'data-xiang-a.sql'),
    ('recipes-xiang-b.json', 'data-xiang-b.sql'),
    ('recipes-chuan.json', 'data-chuan.sql'),
    ('recipes-gan.json', 'data-gan.sql'),
]


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
    for src, dst in FILES:
        data = json.load(open(SEED + src, encoding='utf-8'))
        region = data['region']
        lines = [
            '-- 由 seed/%s 生成，请勿手改；重新生成：python tools/seed-sql.py' % src,
            '-- %s，共 %d 道。author_id = 1，likes 为标题哈希的确定性伪随机值。' % (region, len(data['recipes'])),
            '',
        ]
        for i, r in enumerate(data['recipes'], 1):
            slug = r['cover']['slug']
            cover_path = COVERS + slug + '.jpg'
            if not os.path.exists(cover_path):
                raise SystemExit('missing cover: ' + cover_path)
            lines.append('-- ========== %d. %s ==========' % (i, r['title']))
            lines.append(
                'INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time,'
                ' total_time, difficulty, servings, category, tags, author_id, is_public, likes_count,'
                ' calories, protein, fat, carbs, tips, flavor_profile) VALUES ('
                + ', '.join([
                    esc(r['title']), esc(r['description']),
                    esc('/api/covers/%s.jpg' % slug),
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


if __name__ == '__main__':
    main()
