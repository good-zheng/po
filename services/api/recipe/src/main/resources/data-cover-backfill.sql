-- 旧菜谱封面回填（由 tools/seed-backfill.py 生成）
-- 幂等：只更新 cover_image_url IS NULL 的行，按 id 定位并核对标题

UPDATE recipe SET cover_image_url = '/api/covers/classic-hongshaorou.jpg' WHERE id = 1 AND title = '红烧肉' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = '/api/covers/classic-duojiao-yutou.jpg' WHERE id = 2 AND title = '剁椒鱼头' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = '/api/covers/classic-xiaochao-huangniurou.jpg' WHERE id = 3 AND title = '小炒黄牛肉' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = '/api/covers/classic-nongjia-xiaochaorou.jpg' WHERE id = 4 AND title = '农家小炒肉' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = '/api/covers/classic-lajiao-chaorou.jpg' WHERE id = 5 AND title = '辣椒炒肉' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = '/api/covers/classic-maoshi-hongshaorou.jpg' WHERE id = 6 AND title = '毛氏红烧肉' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = '/api/covers/classic-suandoujiao-roumo.jpg' WHERE id = 7 AND title = '酸豆角炒肉末' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = '/api/covers/classic-waipocai.jpg' WHERE id = 8 AND title = '湘西外婆菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = '/api/covers/classic-ganguo-niuwa.jpg' WHERE id = 9 AND title = '干锅牛蛙' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = '/api/covers/classic-duojiao-zhengpaigu.jpg' WHERE id = 10 AND title = '剁椒蒸排骨' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = '/api/covers/classic-hunan-mifen.jpg' WHERE id = 11 AND title = '湖南米粉' AND cover_image_url IS NULL;
