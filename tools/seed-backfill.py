"""为旧种子（data-hunan.sql 等）已入库的食材行回填 image_url。

名字优先查 seed/ingredient-images.json，查不到用下方 EXTRA 手工映射。
输出：services/api/recipe/src/main/resources/data-ingredient-backfill.sql
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SEED = 'D:/pro/po/services/api/recipe/src/main/resources/seed/'
OUT = 'D:/pro/po/services/api/recipe/src/main/resources/'
IMG_DIR = 'D:/pro/po/services/api/api-bootstrap/src/main/resources/static/ingredients/'

# 2026-09-22 库中 image_url 为 NULL 的全部食材名（旧 11 道菜）
DB_NAMES = [
    '五花肉', '八角', '冰糖', '剁椒', '前腿猪肉', '土豆片', '外婆菜（腌菜）',
    '姜丝', '姜末', '姜片', '姜蒜', '小米辣', '带皮五花肉', '干辣椒', '料酒',
    '桂皮', '淀粉', '湖南圆米粉', '牛蛙', '猪油', '猪筒骨', '猪肉末', '猪肉片',
    '猪肋排', '生抽', '白胡椒粉', '盐', '红椒', '老抽', '花椒', '葱段', '葱花',
    '蒜末', '蒜片', '藕片', '蚝油', '螺丝椒', '豆豉', '郫县豆瓣酱', '酸豆角',
    '青椒', '青蒜苗', '食用油', '香叶', '黄牛肉',
]

# 名字 → 图片 slug（ingredient-images.json 未覆盖的旧名）
EXTRA = {
    '前腿猪肉': 'erdaorou',
    '土豆片': 'tudou',
    '外婆菜（腌菜）': 'zhacai',
    '姜丝': 'shengjiang',
    '姜末': 'shengjiang',
    '姜片': 'shengjiang',
    '姜蒜': 'shengjiang',
    '湖南圆米粉': 'ganmifen',
    '牛蛙': 'niuwa',
    '猪肉片': 'zhushourou',
    '红椒': 'honglajiao',
    '葱段': 'dacong',
    '葱花': 'xiaocong',
    '蒜片': 'dasuan',
    '藕片': 'ou',
    '青椒': 'qinglajiao',
    '螺丝椒': 'qinglajiao',
    '青蒜苗': 'qingsuan',
    '黄牛肉': 'niurou',
}


# 旧 11 道菜（recipe id 1-11）的封面 slug
COVERS_DIR = 'D:/pro/po/services/api/api-bootstrap/src/main/resources/static/covers/'
DB_COVERS = {
    1: ('红烧肉', 'classic-hongshaorou'),
    2: ('剁椒鱼头', 'classic-duojiao-yutou'),
    3: ('小炒黄牛肉', 'classic-xiaochao-huangniurou'),
    4: ('农家小炒肉', 'classic-nongjia-xiaochaorou'),
    5: ('辣椒炒肉', 'classic-lajiao-chaorou'),
    6: ('毛氏红烧肉', 'classic-maoshi-hongshaorou'),
    7: ('酸豆角炒肉末', 'classic-suandoujiao-roumo'),
    8: ('湘西外婆菜', 'classic-waipocai'),
    9: ('干锅牛蛙', 'classic-ganguo-niuwa'),
    10: ('剁椒蒸排骨', 'classic-duojiao-zhengpaigu'),
    11: ('湖南米粉', 'classic-hunan-mifen'),
}


def esc(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")


def main():
    mapping = json.load(open(SEED + 'ingredient-images.json', encoding='utf-8'))
    lines = [
        '-- 旧菜谱食材图片回填（由 tools/seed-backfill.py 生成）',
        "-- 幂等：只更新 image_url IS NULL 的行",
        '',
    ]
    for name in DB_NAMES:
        if name in mapping:
            path = mapping[name]
        elif name in EXTRA:
            path = '/api/ingredients/%s.jpg' % EXTRA[name]
        else:
            raise SystemExit('no image mapping for: ' + name)
        slug = path.rsplit('/', 1)[1]
        if not os.path.exists(IMG_DIR + slug):
            raise SystemExit('image file missing: ' + IMG_DIR + slug)
        lines.append(
            "UPDATE recipe_ingredient SET image_url = '%s' WHERE name = '%s' AND image_url IS NULL;"
            % (path, name))
    with open(OUT + 'data-ingredient-backfill.sql', 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')
    print('wrote %d updates' % len(DB_NAMES))

    cover_lines = [
        '-- 旧菜谱封面回填（由 tools/seed-backfill.py 生成）',
        '-- 幂等：只更新 cover_image_url IS NULL 的行，按 id 定位并核对标题',
        '',
    ]
    for rid, (title, slug) in DB_COVERS.items():
        if not os.path.exists(COVERS_DIR + slug + '.jpg'):
            raise SystemExit('cover file missing: ' + slug)
        cover_lines.append(
            "UPDATE recipe SET cover_image_url = '/api/covers/%s.jpg' WHERE id = %d"
            " AND title = '%s' AND cover_image_url IS NULL;" % (slug, rid, esc(title)))
    with open(OUT + 'data-cover-backfill.sql', 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(cover_lines) + '\n')
    print('wrote %d cover updates' % len(DB_COVERS))


if __name__ == '__main__':
    main()
