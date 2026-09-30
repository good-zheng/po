"""菜谱批次清单：seed-sql.py 与 cos-upload.py 共用，加批次只改这里。

每项 (seed 文件名, 输出 sql 文件名, 封面来源)：
  static = jar 内 static/covers/（旧批次，URL 为 /api/covers/<slug>.jpg）
  cos    = 腾讯云 COS po/covers/（新菜系，URL 为公网绝对地址）
"""
BATCHES = [
    ('recipes-xiang-a.json', 'data-xiang-a.sql', 'static'),
    ('recipes-xiang-b.json', 'data-xiang-b.sql', 'static'),
    ('recipes-chuan.json', 'data-chuan.sql', 'static'),
    ('recipes-gan.json', 'data-gan.sql', 'static'),
    ('recipes-yue.json', 'data-yue.sql', 'cos'),
    ('recipes-lu.json', 'data-lu.sql', 'cos'),
    ('recipes-min.json', 'data-min.sql', 'cos'),
    ('recipes-su.json', 'data-su.sql', 'cos'),
    ('recipes-zhe.json', 'data-zhe.sql', 'cos'),
    ('recipes-hui.json', 'data-hui.sql', 'cos'),
    ('recipes-dongbei.json', 'data-dongbei.sql', 'cos'),
    ('recipes-xibei.json', 'data-xibei.sql', 'cos'),
    ('recipes-hubei.json', 'data-hubei.sql', 'cos'),
    ('recipes-yunnan.json', 'data-yunnan.sql', 'cos'),
    ('recipes-guizhou.json', 'data-guizhou.sql', 'cos'),
    ('recipes-guangxi.json', 'data-guangxi.sql', 'cos'),
    ('recipes-shanxi.json', 'data-shanxi.sql', 'cos'),
    ('recipes-henan.json', 'data-henan.sql', 'cos'),
]
