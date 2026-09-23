-- 由 seed/recipes-chuan.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 川菜，共 25 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 回锅肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('回锅肉', '川菜之首，川人心中家的味道。二刀肉先煮后炒，肥肉片卷成灯盏窝，郫县豆瓣炒出红油，配蒜苗一炒，一盘不够下饭。', '/api/covers/chuan-huiguorou.jpg', 15, 15, 30, 2, 3, '川菜', '经典,家常,下饭,猪肉', 1, TRUE, 103, 560, 18, 48, 6, '肉煮到八成熟为宜，筷子能插透还带粉红；煸肉到微微卷曲出油就下豆瓣，煸过头肉会发柴。', '咸鲜微辣回甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '二刀肉', '500', 'g', TRUE, 1, '/api/ingredients/erdaorou.jpg'),
  (@r, '蒜苗', '100', 'g', TRUE, 2, '/api/ingredients/qingsuan.jpg'),
  (@r, '郫县豆瓣酱', '30', 'g', TRUE, 3, '/api/ingredients/pixianjiang.jpg'),
  (@r, '豆豉', '10', 'g', TRUE, 4, '/api/ingredients/douchi.jpg'),
  (@r, '甜面酱', '10', 'g', TRUE, 5, '/api/ingredients/tianmianjiang.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '白糖', '3', 'g', TRUE, 8, '/api/ingredients/baitang.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 9, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '整块肉冷水下锅，加姜片、料酒煮15分钟至八成熟，捞出晾凉', 18),
  (@r, 2, '肉切约2毫米薄片，蒜苗苗梗拍松切马耳朵段，叶另放', 8),
  (@r, 3, '热锅少油，下肉片中火煸炒至出油卷曲成灯盏窝', 5),
  (@r, 4, '下剁细的豆瓣、豆豉、甜面酱，小火炒出红油上色', 2),
  (@r, 5, '先下蒜苗梗炒半分钟，再下蒜苗叶，加糖翻匀出锅', 2);

-- ========== 2. 麻婆豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('麻婆豆腐', '成都百年名菜，陈麻婆创于同治年间。八字真言：麻、辣、烫、香、酥、嫩、鲜、活。牛肉臊子酥香，豆腐滚烫嫩滑，麻味收尾。', '/api/covers/chuan-mapo-doufu.jpg', 15, 15, 30, 2, 3, '川菜', '经典,家常,下饭,豆腐', 1, TRUE, 273, 340, 22, 24, 8, '豆腐用盐水焯过不易碎；勾芡分三次下，每次都等汤汁重新收拢，豆腐才挂得住汁、明油亮芡。', '麻辣烫嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '嫩豆腐', '400', 'g', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '牛肉末', '80', 'g', TRUE, 2, '/api/ingredients/niuroumo.jpg'),
  (@r, '郫县豆瓣酱', '25', 'g', TRUE, 3, '/api/ingredients/pixianjiang.jpg'),
  (@r, '豆豉', '10', 'g', TRUE, 4, '/api/ingredients/douchi.jpg'),
  (@r, '辣椒粉', '5', 'g', TRUE, 5, '/api/ingredients/lajiaofen.jpg'),
  (@r, '花椒粉', '3', 'g', TRUE, 6, '/api/ingredients/huajiaofen.jpg'),
  (@r, '蒜苗', '30', 'g', TRUE, 7, '/api/ingredients/qingsuan.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 9, '/api/ingredients/dasuan.jpg'),
  (@r, '水淀粉', '30', 'ml', TRUE, 10, '/api/ingredients/dianfen.jpg'),
  (@r, '高汤', '200', 'ml', TRUE, 11, '/api/ingredients/gaotang.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '豆腐切2厘米方块，入加盐的沸水中焯1分钟捞出泡温水', 5),
  (@r, 2, '热油下牛肉末中火煸至酥香金黄，盛出备用', 5),
  (@r, 3, '锅留油，下剁细的豆瓣、豆豉、姜蒜末、辣椒粉小火炒出红油', 3),
  (@r, 4, '加高汤烧开，下豆腐和牛肉末，小火烧3分钟', 3),
  (@r, 5, '分三次淋入水淀粉勾芡，轻推均匀，撒蒜苗段', 2),
  (@r, 6, '起锅装盘，撒上花椒粉即成', 1);

-- ========== 3. 宫保鸡丁 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('宫保鸡丁', '丁宝桢封太子少保得名，川菜走向世界的名片。鸡丁滑嫩、花生酥脆，糊辣荔枝口酸甜平衡，一把花椒垫出若有似无的麻。', '/api/covers/chuan-gongbao-jiding.jpg', 20, 8, 28, 2, 3, '川菜', '经典,宴客,下饭,鸡肉', 1, TRUE, 162, 480, 30, 28, 16, '碗汁提前调好，全程序一气呵成；干辣椒炝到棕红带糊边立刻下鸡丁，糊香味过了就发苦。', '糊辣荔枝味');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸡腿肉', '300', 'g', TRUE, 1, '/api/ingredients/jitui.jpg'),
  (@r, '油炸花生米', '80', 'g', TRUE, 2, '/api/ingredients/huasheng.jpg'),
  (@r, '干红辣椒', '10', 'g', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '3', 'g', TRUE, 4, '/api/ingredients/huajiao.jpg'),
  (@r, '大葱', '1', '根', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '白糖', '20', 'g', TRUE, 6, '/api/ingredients/baitang.jpg'),
  (@r, '香醋', '20', 'ml', TRUE, 7, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '料酒', '10', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '淀粉', '15', 'g', TRUE, 10, '/api/ingredients/dianfen.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 11, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '10', 'g', TRUE, 12, '/api/ingredients/dasuan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡腿肉切1.5厘米丁，加料酒、生抽、淀粉抓匀腌15分钟', 17),
  (@r, 2, '白糖、香醋、生抽、料酒、淀粉加两勺水调成碗汁；干辣椒剪段去籽，葱切马耳朵段', 5),
  (@r, 3, '热油下鸡丁滑散炒至变色盛出', 1),
  (@r, 4, '锅留底油，下花椒、干辣椒段小火炝出糊香味', 1),
  (@r, 5, '下鸡丁、姜蒜片、葱段大火翻炒，烹入碗汁快速颠匀', 1),
  (@r, 6, '下花生米翻匀，汁裹匀即出锅', 1);

-- ========== 4. 鱼香肉丝 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('鱼香肉丝', '不见鱼却有鱼味的川菜神来之笔。泡椒姜蒜炒出红油打底，酸甜咸辣一勺入魂，肉丝滑嫩配脆笋木耳，盖饭拌面两相宜。', '/api/covers/chuan-yuxiang-rousi.jpg', 20, 8, 28, 2, 3, '川菜', '经典,家常,下饭', 1, TRUE, 248, 400, 22, 24, 14, '泡椒是鱼香味的灵魂，一定要剁细炒出红油；碗汁里糖醋比例1比1，酸甜才平衡。', '鱼香味');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪里脊', '300', 'g', TRUE, 1, '/api/ingredients/zhuliji.jpg'),
  (@r, '水发木耳', '50', 'g', TRUE, 2, '/api/ingredients/muer.jpg'),
  (@r, '莴笋', '80', 'g', TRUE, 3, '/api/ingredients/wosun.jpg'),
  (@r, '泡红辣椒', '40', 'g', TRUE, 4, '/api/ingredients/paohongjiao.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '3', '根', TRUE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '白糖', '18', 'g', TRUE, 8, '/api/ingredients/baitang.jpg'),
  (@r, '香醋', '18', 'ml', TRUE, 9, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '淀粉', '15', 'g', TRUE, 11, '/api/ingredients/dianfen.jpg'),
  (@r, '食用油', '50', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '里脊切细丝，加料酒、盐、淀粉抓匀腌10分钟', 12),
  (@r, 2, '木耳、莴笋切丝，葱姜蒜、泡椒分别剁细', 8),
  (@r, 3, '白糖、香醋、生抽、淀粉加水调成鱼香碗汁', 3),
  (@r, 4, '热油下肉丝快速滑散至变色盛出', 1),
  (@r, 5, '锅留油，下泡椒茸、姜蒜末小火炒出红油', 2),
  (@r, 6, '下木耳丝、莴笋丝略炒，倒回肉丝，烹入碗汁大火翻匀', 2),
  (@r, 7, '撒葱花，汁亮起锅', 1);

-- ========== 5. 水煮牛肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('水煮牛肉', '自贡盐帮菜的旷世之作。牛肉片在红汤里汆得滑嫩，出口铺满辣椒花椒，一勺滚油浇下去刺啦一声，香气能掀翻屋顶。', '/api/covers/chuan-shuizhu-niurou.jpg', 25, 15, 40, 2, 4, '川菜', '经典,重辣,下饭,牛肉', 1, TRUE, 149, 480, 30, 32, 8, '牛肉逆纹切薄片，蛋清淀粉上浆冷藏半小时才滑嫩；最后浇的油要烧到冒烟，激香不全就逊色一半。', '麻辣烫鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '牛里脊', '300', 'g', TRUE, 1, '/api/ingredients/niurou.jpg'),
  (@r, '莴笋尖', '150', 'g', TRUE, 2, '/api/ingredients/wosun.jpg'),
  (@r, '芹菜', '80', 'g', TRUE, 3, '/api/ingredients/qincai.jpg'),
  (@r, '郫县豆瓣酱', '30', 'g', TRUE, 4, '/api/ingredients/pixianjiang.jpg'),
  (@r, '干红辣椒', '20', 'g', TRUE, 5, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '10', 'g', TRUE, 6, '/api/ingredients/huajiao.jpg'),
  (@r, '辣椒粉', '5', 'g', TRUE, 7, '/api/ingredients/lajiaofen.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 8, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 9, '/api/ingredients/shengjiang.jpg'),
  (@r, '鸡蛋清', '1', '个', TRUE, 10, '/api/ingredients/jidanqing.jpg'),
  (@r, '淀粉', '15', 'g', TRUE, 11, '/api/ingredients/dianfen.jpg'),
  (@r, '高汤', '500', 'ml', TRUE, 12, '/api/ingredients/gaotang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肉逆纹切薄片，加蛋清、盐、淀粉抓匀上浆，冷藏半小时', 35),
  (@r, 2, '莴笋尖、芹菜切段，入加盐沸水中焯断生，捞入汤碗垫底', 3),
  (@r, 3, '热油下剁细的豆瓣、姜蒜末炒出红油，加高汤烧开熬2分钟，打去料渣', 4),
  (@r, 4, '牛肉片逐片下锅，中火汆2分钟至熟，连汤倒入垫菜碗中', 3),
  (@r, 5, '面上撒辣椒粉、干辣椒段、花椒、蒜末', 2),
  (@r, 6, '菜油烧至冒烟，一勺浇下激香，撒葱花上桌', 1);

-- ========== 6. 夫妻肺片 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('夫妻肺片', '郭朝华夫妇推车卖出的百年凉菜。牛肉牛杂卤透切得飞薄，红油卤汁拌得红亮，麻香透牙，是四川凉菜的排面担当。', '/api/covers/chuan-fuqi-feipian.jpg', 30, 90, 120, 2, 4, '川菜', '经典,凉菜,下酒,牛肉', 1, TRUE, 207, 420, 34, 28, 8, '卤后的牛肉牛杂一定要晾透再切，热切会散；卤汁加红油的比例决定味道，卤汁3红油2最合口。', '麻辣鲜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '牛肉', '250', 'g', TRUE, 1, '/api/ingredients/niurou.jpg'),
  (@r, '牛肚', '150', 'g', TRUE, 2, '/api/ingredients/niudu.jpg'),
  (@r, '牛舌', '100', 'g', FALSE, 3, '/api/ingredients/niushe.jpg'),
  (@r, '八角', '2', '颗', TRUE, 4, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '段', TRUE, 5, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '3', '片', TRUE, 6, '/api/ingredients/xiangye.jpg'),
  (@r, '辣椒油', '50', 'ml', TRUE, 7, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '花椒粉', '3', 'g', TRUE, 8, '/api/ingredients/huajiaofen.jpg'),
  (@r, '卤水汁', '50', 'ml', TRUE, 9, '/api/ingredients/lushui.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '5', 'g', TRUE, 11, '/api/ingredients/baitang.jpg'),
  (@r, '熟花生碎', '30', 'g', TRUE, 12, '/api/ingredients/huasheng.jpg'),
  (@r, '熟芝麻', '10', 'g', TRUE, 13, '/api/ingredients/baizhima.jpg'),
  (@r, '芹菜', '30', 'g', FALSE, 14, '/api/ingredients/qincai.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 15, '/api/ingredients/xiangcai.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肉、牛肚、牛舌冷水下锅焯水，洗净', 15),
  (@r, 2, '换清水加八角、桂皮、香叶，小火卤1小时至熟', 60),
  (@r, 3, '捞出晾凉，切成长约8厘米的薄片', 15),
  (@r, 4, '辣椒油、卤水汁、生抽、白糖、花椒粉调成红油味汁', 5),
  (@r, 5, '肉片与味汁拌匀装盘，撒花生碎、芝麻、芹菜节、香菜即成', 5);

-- ========== 7. 口水鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('口水鸡', '郭沫若笔下让人流口水的鸡。白肉煮得皮爽肉嫩，红油姜蒜汁一淋，集麻辣鲜香嫩爽于一身，夏天没它饭桌不完整。', '/api/covers/chuan-koushuiji.jpg', 20, 25, 45, 2, 4, '川菜', '经典,凉菜,鸡肉,夏日', 1, TRUE, 106, 380, 32, 24, 8, '鸡煮15分钟关火焖10分钟，骨里带一丝红才嫩；冰水激过皮才爽滑，这一步不能省。', '麻辣香嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '三黄鸡', '半', '只(约700g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '辣椒油', '40', 'ml', TRUE, 2, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '芝麻酱', '15', 'g', TRUE, 3, '/api/ingredients/zhimajiang.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '10', 'ml', TRUE, 5, '/api/ingredients/xiangcu.jpg'),
  (@r, '白糖', '8', 'g', TRUE, 6, '/api/ingredients/baitang.jpg'),
  (@r, '花椒粉', '2', 'g', TRUE, 7, '/api/ingredients/huajiaofen.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 8, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 9, '/api/ingredients/shengjiang.jpg'),
  (@r, '熟花生碎', '20', 'g', TRUE, 10, '/api/ingredients/huasheng.jpg'),
  (@r, '熟芝麻', '5', 'g', TRUE, 11, '/api/ingredients/baizhima.jpg'),
  (@r, '小葱', '3', '根', TRUE, 12, '/api/ingredients/xiaocong.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡冷水下锅，加姜片、料酒，煮开后煮15分钟，关火加盖焖10分钟', 28),
  (@r, 2, '捞出立即入冰水浸凉，使鸡皮爽脆，沥干斩件装盘', 10),
  (@r, 3, '蒜捣成泥，与芝麻酱、辣椒油、生抽、香醋、白糖、花椒粉调匀成酱汁', 8),
  (@r, 4, '酱汁均匀淋在鸡块上', 2),
  (@r, 5, '撒花生碎、熟芝麻、葱花，静置5分钟入味上桌', 5);

-- ========== 8. 蒜泥白肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('蒜泥白肉', '成都竹林小餐的招牌。二刀肉煮得断生即起，刀工片成纸样透光的薄片，蒜泥红油一浇，肥而不腻、蒜香冲鼻。', '/api/covers/chuan-suanni-bairou.jpg', 20, 30, 50, 2, 4, '川菜', '经典,凉菜,下酒,猪肉', 1, TRUE, 245, 520, 20, 46, 6, '肉不要煮全熟，断生带一点点粉红最嫩；片肉时刀贴着走，片得越薄越见功夫。', '蒜香浓郁');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪后腿二刀肉', '500', 'g', TRUE, 1, '/api/ingredients/erdaorou.jpg'),
  (@r, '黄瓜', '1', '根', TRUE, 2, '/api/ingredients/huanggua.jpg'),
  (@r, '大蒜', '50', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '辣椒油', '30', 'ml', TRUE, 4, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '8', 'ml', TRUE, 6, '/api/ingredients/xiangcu.jpg'),
  (@r, '白糖', '5', 'g', TRUE, 7, '/api/ingredients/baitang.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '小葱', '2', '根', TRUE, 10, '/api/ingredients/xiaocong.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '整块肉冷水下锅，加姜、葱、料酒，中火煮20分钟至断生', 25),
  (@r, 2, '捞出晾凉（留汤），用滚刀法片成极薄的肉片', 15),
  (@r, 3, '黄瓜切细丝垫盘底，肉片码放其上', 8),
  (@r, 4, '蒜捣成蒜泥，加辣椒油、生抽、香醋、白糖和两勺煮肉汤调成蒜泥汁', 5),
  (@r, 5, '蒜泥汁浇在肉片上，撒葱花即成', 2);

-- ========== 9. 开水白菜 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('开水白菜', '看似清水煮白菜的国宴神作。鸡茸扫汤数遍，把高汤滤到清可见底，白菜心借汤成仙，至清至纯方见川菜深厚功力。', '/api/covers/chuan-kaishui-baicai.jpg', 60, 240, 300, 3, 4, '川菜', '经典,宴客,汤品,功夫菜', 1, TRUE, 240, 160, 18, 6, 8, '扫汤是全部功夫所在：鸡茸分次下、文火慢搅，蛋白质把浮油杂质全吸附走；白菜只取中心三寸嫩心。', '清鲜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '老母鸡', '1', '只(约1200g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '猪排骨', '300', 'g', TRUE, 2, '/api/ingredients/zhupaigu.jpg'),
  (@r, '火腿', '50', 'g', TRUE, 3, '/api/ingredients/huotui.jpg'),
  (@r, '鸡胸肉', '150', 'g', TRUE, 4, '/api/ingredients/jitui.jpg'),
  (@r, '黄芽白菜心', '2', '棵', TRUE, 5, '/api/ingredients/baicai.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '3', '根', TRUE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '盐', '3', 'g', TRUE, 8, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡、排骨、火腿焯水洗净，加葱姜和清水大火烧开转小火炖3小时成浓汤', 180),
  (@r, 2, '鸡胸肉剁成细茸，分两次下入汤中，文火慢搅，让鸡茸吸附杂质浮油，反复撇净滤清', 60),
  (@r, 3, '汤清如水后加盐调好味，即成开水（清汤）', 5),
  (@r, 4, '白菜心削成弓形，入沸水焯半分钟去生味，再入清汤中煨2分钟', 5),
  (@r, 5, '白菜心捞入汤碗，舀入滚烫清汤，即刻上桌', 3);

-- ========== 10. 樟茶鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('樟茶鸭', '清宫御膳房传入四川的名鸭。樟树叶与花茶熏出琥珀色，先蒸后炸，皮酥如纸、肉嫩带烟茶香，切块蘸椒盐边嚼边品。', '/api/covers/chuan-zhangchaya.jpg', 720, 100, 820, 3, 4, '川菜', '经典,宴客,鸭肉,功夫菜', 1, TRUE, 117, 520, 34, 36, 6, '腌足12小时味才透骨；熏时火要小、烟要浓，鸭皮上色到樟木色即止；炸前一定蒸透，外酥里嫩全在这顺序。', '烟熏茶香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '肥鸭', '1', '只(约1500g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '香樟树叶', '30', 'g', TRUE, 2, '/api/ingredients/zhangshuye.jpg'),
  (@r, '花茶', '20', 'g', TRUE, 3, '/api/ingredients/lucha.jpg'),
  (@r, '大米', '50', 'g', TRUE, 4, '/api/ingredients/dami.jpg'),
  (@r, '盐', '60', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '花椒', '5', 'g', TRUE, 6, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '2', '颗', TRUE, 7, '/api/ingredients/bajiao.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 9, '/api/ingredients/shengjiang.jpg'),
  (@r, '食用油', '1000', 'ml', FALSE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '花椒、八角入干锅与盐同炒至香，趁热擦遍鸭身内外，腌12小时', 730),
  (@r, 2, '樟树叶、花茶、大米铺熏锅底，架上鸭子，盖盖小火熏至鸭皮呈樟木色', 20),
  (@r, 3, '熏好的鸭上笼，大火蒸40分钟至熟透', 40),
  (@r, 4, '油烧至七成热，整鸭下锅炸至皮酥色金红，翻炸均匀', 8),
  (@r, 5, '捞出斩块装盘，随椒盐碟上桌', 5);

-- ========== 11. 东坡肘子 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('东坡肘子', '苏东坡家乡眉山的头牌。整肘炖到脱骨酥烂、肥而不腻，配红油蘸水一碟，肥皮的胶糯蘸上辣香，扒一口米饭赛神仙。', '/api/covers/chuan-dongpo-zhouzi.jpg', 20, 180, 200, 2, 6, '川菜', '经典,宴客,猪肉,眉山', 1, TRUE, 277, 680, 40, 52, 6, '肘子皮上的毛要燎净刮白，否则一股毛腥味；炖足3小时筷子一插到底才算到位，中途不添冷水。', '软糯咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪前肘', '1', '只(约1200g)', TRUE, 1, '/api/ingredients/zhuqianzhou.jpg'),
  (@r, '雪豆', '80', 'g', TRUE, 2, '/api/ingredients/xuedou.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '2', '根', TRUE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '40', 'ml', TRUE, 5, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '5', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '辣椒油', '20', 'ml', TRUE, 8, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '香醋', '10', 'ml', TRUE, 9, '/api/ingredients/xiangcu.jpg'),
  (@r, '蒜末', '15', 'g', TRUE, 10, '/api/ingredients/dasuan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '肘子明火燎净残毛，刮洗干净，冷水下锅焯水', 20),
  (@r, 2, '砂锅加足量开水，放肘子、姜块、葱段、料酒，小火炖2小时', 120),
  (@r, 3, '下泡发好的雪豆，继续炖1小时至肘子脱骨酥烂', 60),
  (@r, 4, '辣椒油、香醋、生抽、蒜末调成蘸水', 5),
  (@r, 5, '肘子连汤装盘，雪豆围边，蘸水一碟上桌', 5);

-- ========== 12. 干煸四季豆 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('干煸四季豆', '川菜干煸技法的教科书。四季豆煸到表皮起皱带虎皮纹，猪肉末酥香、芽菜咸鲜，一筷子下去干香扑鼻、越嚼越有味。', '/api/covers/chuan-ganbian-sijidou.jpg', 15, 12, 27, 2, 3, '川菜', '家常,下饭,素菜', 1, TRUE, 188, 320, 12, 24, 14, '四季豆务必煸到完全断生，生的有毒；宁可少油慢煸，不要大火炸焦。', '干香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '四季豆', '400', 'g', TRUE, 1, '/api/ingredients/sijidou.jpg'),
  (@r, '猪肉末', '80', 'g', TRUE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '碎米芽菜', '30', 'g', TRUE, 3, '/api/ingredients/yacai.jpg'),
  (@r, '干红辣椒', '8', 'g', TRUE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '2', 'g', TRUE, 5, '/api/ingredients/huajiao.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '2', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '60', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '四季豆撕去老筋，掰成两段，洗净沥干', 8),
  (@r, 2, '油烧至六成热，下四季豆中火煸炸至表皮起皱盛出', 6),
  (@r, 3, '锅留底油，下肉末煸至酥香出油', 3),
  (@r, 4, '下芽菜、干辣椒段、花椒、姜蒜末炒香', 2),
  (@r, 5, '倒回四季豆，烹生抽、加盐大火翻匀出锅', 2);

-- ========== 13. 豆瓣鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('豆瓣鱼', '川人办席必有的整鱼大菜。草鱼烧得肉嫩如蒜瓣，郫县豆瓣的红油汤汁浓稠挂身，酸甜带辣，最后汁舀在饭上才是正头。', '/api/covers/chuan-doubanyu.jpg', 20, 18, 38, 2, 4, '川菜', '经典,宴客,河鲜', 1, TRUE, 215, 420, 32, 22, 12, '鱼煎一下再烧，肉紧不散；收汁时不停把汁浇在鱼身上，颜色才红亮均匀。', '豆瓣咸辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '草鱼', '1', '条(约1000g)', TRUE, 1, '/api/ingredients/caoyu.jpg'),
  (@r, '郫县豆瓣酱', '40', 'g', TRUE, 2, '/api/ingredients/pixianjiang.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '3', '根', TRUE, 5, '/api/ingredients/xiaocong.jpg'),
  (@r, '白糖', '10', 'g', TRUE, 6, '/api/ingredients/baitang.jpg'),
  (@r, '香醋', '10', 'ml', TRUE, 7, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '水淀粉', '30', 'ml', TRUE, 10, '/api/ingredients/dianfen.jpg'),
  (@r, '食用油', '80', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '草鱼治净，两面打一字花刀，抹料酒、盐腌10分钟', 12),
  (@r, 2, '热油将鱼两面煎至定型微黄', 5),
  (@r, 3, '下剁细的豆瓣、姜蒜末炒出红油，加汤约500ml，下鱼', 3),
  (@r, 4, '加白糖、生抽，中火烧8分钟，其间反复把汁浇上鱼身', 8),
  (@r, 5, '鱼装盘，锅中汤汁勾水淀粉，淋醋收浓，浇鱼身撒葱花', 3);

-- ========== 14. 重庆辣子鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('重庆辣子鸡', '歌乐山林中餐馆的意外成名作。鸡丁炸得干香酥脆埋在辣椒堆里，吃鸡如寻宝，越翻越香，江湖气十足的一道重庆菜。', '/api/covers/chuan-chongqing-laziji.jpg', 20, 15, 35, 2, 3, '川菜', '经典,重辣,下酒,鸡肉', 1, TRUE, 156, 520, 30, 36, 10, '辣椒的量要夸张到盖过鸡丁才算正宗；鸡丁要炸两遍，第二遍高温逼出油才酥。', '香辣干酥');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸡腿', '2', '只', TRUE, 1, '/api/ingredients/jitui.jpg'),
  (@r, '干红辣椒', '100', 'g', TRUE, 2, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '10', 'g', TRUE, 3, '/api/ingredients/huajiao.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '大葱', '1', '根', TRUE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '5', 'g', TRUE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '熟芝麻', '10', 'g', TRUE, 10, '/api/ingredients/baizhima.jpg'),
  (@r, '食用油', '600', 'ml', FALSE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡腿去骨切1.5厘米丁，加料酒、生抽腌15分钟', 17),
  (@r, 2, '干辣椒剪段去籽，葱切段，姜蒜切片', 8),
  (@r, 3, '油烧至六成热，下鸡丁炸至微黄捞出，升油温复炸30秒至酥脆', 5),
  (@r, 4, '锅留底油，下姜蒜片、干辣椒段、花椒小火煸香', 2),
  (@r, 5, '下鸡丁大火翻炒，加白糖、葱段翻匀', 2),
  (@r, 6, '撒熟芝麻，颠匀出锅', 1);

-- ========== 15. 自贡冷吃兔 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('自贡冷吃兔', '盐都自贡的看家凉菜。兔丁煸到干香入味，辣椒花椒层层裹身，冷吃比热吃更妙，是自贡人车座底下都要囤一袋的乡愁。', '/api/covers/chuan-zigong-lengchitu.jpg', 20, 30, 50, 2, 4, '川菜', '地方名菜,凉菜,下酒,兔肉', 1, TRUE, 170, 380, 34, 22, 8, '兔丁要煸到边缘微焦才算到位，水分不干不香；出锅前那几滴醋是提香关键，吃不出酸只留香。', '麻辣干香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '兔肉', '500', 'g', TRUE, 1, '/api/ingredients/turou.jpg'),
  (@r, '干红辣椒', '40', 'g', TRUE, 2, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '8', 'g', TRUE, 3, '/api/ingredients/huajiao.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '八角', '1', '颗', TRUE, 6, '/api/ingredients/bajiao.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '5', 'g', TRUE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '香醋', '5', 'ml', TRUE, 10, '/api/ingredients/xiangcu.jpg'),
  (@r, '食用油', '80', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '兔肉切1.5厘米丁，加料酒、姜片、生抽腌20分钟', 22),
  (@r, 2, '干辣椒剪段，蒜切片', 5),
  (@r, 3, '油烧至五成热，下兔丁中火煸炒至水分收干、边缘微焦', 15),
  (@r, 4, '下干辣椒段、花椒、八角、蒜片，小火慢煸5分钟让辣麻入味', 5),
  (@r, 5, '加白糖、几滴香醋翻匀，晾凉后食用风味最佳', 3);

-- ========== 16. 乐山钵钵鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('乐山钵钵鸡', '乐山大佛脚下的市井绝味。签签上的鸡块素菜泡进藤椒红油汤汁里，麻辣中透着藤椒的清冽，泡得越久越有味，夏天一盆配啤酒。', '/api/covers/chuan-leshan-boboji.jpg', 40, 25, 65, 2, 4, '川菜', '地方名菜,凉菜,小吃,夏日', 1, TRUE, 307, 420, 30, 28, 10, '汤汁要用煮鸡的原汤打底，味道才有厚度；食材泡足半小时再吃，签签上的味道才透。', '麻辣藤椒香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '土鸡', '半', '只(约700g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '鸡爪', '4', '只', FALSE, 2, '/api/ingredients/jizhua.jpg'),
  (@r, '藕', '150', 'g', TRUE, 3, '/api/ingredients/ou.jpg'),
  (@r, '土豆', '150', 'g', TRUE, 4, '/api/ingredients/tudou.jpg'),
  (@r, '木耳', '50', 'g', FALSE, 5, '/api/ingredients/muer.jpg'),
  (@r, '辣椒油', '50', 'ml', TRUE, 6, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '藤椒油', '15', 'ml', TRUE, 7, '/api/ingredients/tengjiaoyou.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '10', 'g', TRUE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '熟芝麻', '15', 'g', TRUE, 10, '/api/ingredients/baizhima.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 11, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '3', '根', TRUE, 12, '/api/ingredients/xiaocong.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡与鸡爪冷水下锅，加姜、葱煮熟，捞汤留用', 25),
  (@r, 2, '鸡肉晾凉斩小块，鸡爪去骨，均用竹签串起', 15),
  (@r, 3, '藕、土豆切片、木耳撕小朵，焯熟串签', 10),
  (@r, 4, '煮鸡原汤200ml加辣椒油、藤椒油、生抽、白糖、芝麻调成汤汁', 8),
  (@r, 5, '所有签签泡入汤汁，静置30分钟入味即食', 30);

-- ========== 17. 乐山甜皮鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('乐山甜皮鸭', '乐山人的心头好，卤香里裹着蜜甜。老卤卤透的鸭子过油一炸，趁热刷上饴糖，皮甜脆如糖衣、肉细嫩含卤香，趁热咬第一口最妙。', '/api/covers/chuan-leshan-tianpiya.jpg', 30, 90, 120, 2, 4, '川菜', '地方名菜,卤味,鸭肉', 1, TRUE, 291, 560, 32, 40, 12, '卤水香料要足、火要小，卤到筷子能戳透；炸后趁热刷糖水，凉了皮回软就不脆了。', '甜香卤味');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '土鸭', '1', '只(约1200g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '八角', '3', '颗', TRUE, 2, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '段', TRUE, 3, '/api/ingredients/guipi.jpg'),
  (@r, '山奈', '3', 'g', TRUE, 4, '/api/ingredients/shannai.jpg'),
  (@r, '丁香', '2', 'g', TRUE, 5, '/api/ingredients/dingxiang.jpg'),
  (@r, '冰糖', '30', 'g', TRUE, 6, '/api/ingredients/bingtang.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 8, '/api/ingredients/laochou.jpg'),
  (@r, '麦芽糖', '40', 'g', TRUE, 9, '/api/ingredients/mayatang.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 10, '/api/ingredients/liaojiu.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 11, '/api/ingredients/shengjiang.jpg'),
  (@r, '食用油', '800', 'ml', FALSE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸭子治净焯水，放入加香料、姜、生抽、老抽、冰糖、料酒的卤水中，小火卤50分钟', 60),
  (@r, 2, '捞出晾至表皮收干', 20),
  (@r, 3, '油烧至七成热，淋炸至鸭皮金红酥脆', 6),
  (@r, 4, '麦芽糖加少许热水化开，趁热均匀刷在鸭皮上', 5),
  (@r, 5, '晾至糖皮微脆，斩块装盘', 5);

-- ========== 18. 宜宾燃面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('宜宾燃面', '叙府街头的重油之王。面条甩得滴水不留，香油猪油裹身根根分明，油重无水似可燃，故名燃面，芽菜花生一拌满口生香。', '/api/covers/chuan-yibin-ranmian.jpg', 10, 6, 16, 1, 2, '川菜', '地方名菜,主食,小吃', 1, TRUE, 303, 620, 16, 34, 66, '面煮至断生就捞，甩水越干越好，这是燃面的命门；香油趁热拌入，面凉了就坨。', '咸鲜油香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '碱水面', '200', 'g', TRUE, 1, '/api/ingredients/jianshuimian.jpg'),
  (@r, '碎米芽菜', '30', 'g', TRUE, 2, '/api/ingredients/yacai.jpg'),
  (@r, '熟花生碎', '30', 'g', TRUE, 3, '/api/ingredients/huasheng.jpg'),
  (@r, '辣椒油', '15', 'ml', TRUE, 4, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '香油', '20', 'ml', TRUE, 5, '/api/ingredients/xiangyou.jpg'),
  (@r, '猪油', '10', 'g', TRUE, 6, '/api/ingredients/zhuyou.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '3', 'ml', TRUE, 8, '/api/ingredients/xiangcu.jpg'),
  (@r, '小葱', '2', '根', TRUE, 9, '/api/ingredients/xiaocong.jpg'),
  (@r, '核桃碎', '10', 'g', FALSE, 10, '/api/ingredients/hetaosui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '芽菜取出发碟，花生碾碎，葱切花', 5),
  (@r, 2, '水开下面，煮至断生（约两分半钟）捞出', 3),
  (@r, 3, '竹漏勺反复颠甩，把面甩到几乎不带水', 2),
  (@r, 4, '趁热加香油、猪油抖散拌匀，使面条根条分明', 2),
  (@r, 5, '加芽菜、花生碎、辣椒油、生抽、醋拌匀，撒葱花上桌', 2);

-- ========== 19. 担担面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('担担面', '小贩挑担叫卖百年而成的成都名片。细面滑韧，脆臊酥香干爽，芝麻酱红油打底的汤汁浓而不澥，一两面一碗，回味勾人再来。', '/api/covers/chuan-dandanmian.jpg', 20, 15, 35, 2, 2, '川菜', '经典,主食,小吃', 1, TRUE, 142, 640, 22, 32, 68, '脆臊要煸到肉末完全吐油、颗颗分明才酥；碗底调料用化开的芝麻酱打底，汁才挂在面上。', '咸鲜香辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '细面条', '200', 'g', TRUE, 1, '/api/ingredients/ximiantiao.jpg'),
  (@r, '猪肉末', '100', 'g', TRUE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '碎米芽菜', '30', 'g', TRUE, 3, '/api/ingredients/yacai.jpg'),
  (@r, '芝麻酱', '20', 'g', TRUE, 4, '/api/ingredients/zhimajiang.jpg'),
  (@r, '辣椒油', '15', 'ml', TRUE, 5, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '5', 'ml', TRUE, 7, '/api/ingredients/xiangcu.jpg'),
  (@r, '花椒粉', '2', 'g', TRUE, 8, '/api/ingredients/huajiaofen.jpg'),
  (@r, '料酒', '10', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '小葱', '2', '根', TRUE, 10, '/api/ingredients/xiaocong.jpg'),
  (@r, '豌豆尖', '60', 'g', FALSE, 11, '/api/ingredients/wandoujian.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '热锅少油，下猪肉末中火煸至吐油酥香，加料酒、少许生抽炒匀，再下芽菜炒干，成脆臊', 10),
  (@r, 2, '芝麻酱用生抽、香醋、辣椒油、花椒粉和少许温水澥开，分装碗底', 5),
  (@r, 3, '水开下面煮熟，豌豆尖烫熟', 4),
  (@r, 4, '面捞入碗中，浇一勺面汤', 1),
  (@r, 5, '铺上脆臊、豌豆尖，撒葱花即成', 1);

-- ========== 20. 钟水饺 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('钟水饺', '光绪年间荔枝巷钟少伯家的绝活。全猪肉馅的饺子弹嫩多汁，红油加复制酱油纯甜咸口，不放一颗蒜以外的辛香料，简到极致。', '/api/covers/chuan-zhongshuijiao.jpg', 40, 10, 50, 2, 3, '川菜', '经典,小吃,主食', 1, TRUE, 220, 520, 22, 24, 52, '馅要顺一个方向搅打上劲并分次打入清水，饺子才嫩；复制酱油是甜咸魂，可用生抽加红糖小火熬浓替代。', '咸甜微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪前腿肉馅', '300', 'g', TRUE, 1, '/api/ingredients/zhuroumo.jpg'),
  (@r, '饺子皮', '40', '张', TRUE, 2, '/api/ingredients/jiaozipi.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '鸡蛋', '1', '个', TRUE, 4, '/api/ingredients/jidan.jpg'),
  (@r, '辣椒油', '30', 'ml', TRUE, 5, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '复制酱油', '30', 'ml', TRUE, 6, '/api/ingredients/laochou.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '8', 'g', TRUE, 8, '/api/ingredients/baitang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 9, '/api/ingredients/dasuan.jpg'),
  (@r, '香油', '10', 'ml', TRUE, 10, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '肉馅加姜末、鸡蛋、盐、香油和60ml清水，顺一个方向搅打上劲', 15),
  (@r, 2, '包成月牙饺，捏紧封口', 15),
  (@r, 3, '碗中放蒜末、辣椒油、复制酱油、生抽、白糖、香油调成味汁', 5),
  (@r, 4, '水开下饺，点两次凉水，煮至浮起皮透', 8),
  (@r, 5, '捞入味汁碗中翻拌挂汁，撒葱花即成', 2);

-- ========== 21. 龙抄手 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('龙抄手', '成都协和前的老字号，浓抄手的清汤代表。皮薄如绢、馅嫩如脂，一口咬开汤水四溢，清汤撒虾皮榨菜，鲜得舌头打颤。', '/api/covers/chuan-longchaoshou.jpg', 40, 10, 50, 2, 3, '川菜', '经典,小吃,汤食', 1, TRUE, 265, 480, 24, 20, 52, '抄手皮要买最薄的，馅心加蛋液和清水打足才嫩；煮抄手水宽火旺，才不粘不破。', '清鲜嫩滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪后腿肉馅', '300', 'g', TRUE, 1, '/api/ingredients/zhuroumo.jpg'),
  (@r, '抄手皮', '40', '张', TRUE, 2, '/api/ingredients/jiaozipi.jpg'),
  (@r, '鸡蛋', '1', '个', TRUE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '鸡清汤', '800', 'ml', TRUE, 5, '/api/ingredients/gaotang.jpg'),
  (@r, '虾皮', '5', 'g', TRUE, 6, '/api/ingredients/xiapi.jpg'),
  (@r, '榨菜粒', '15', 'g', TRUE, 7, '/api/ingredients/zhacai.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '香油', '10', 'ml', TRUE, 9, '/api/ingredients/xiangyou.jpg'),
  (@r, '小葱', '2', '根', TRUE, 10, '/api/ingredients/xiaocong.jpg'),
  (@r, '紫菜', '3', 'g', FALSE, 11, '/api/ingredients/zicai.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '肉馅加姜末、鸡蛋、盐、香油和80ml清水，顺一个方向搅打上劲', 15),
  (@r, 2, '取抄手皮包入馅心，对折再两角相捏成抄手', 20),
  (@r, 3, '鸡清汤烧开，加生抽调味，撒虾皮、榨菜粒、紫菜', 8),
  (@r, 4, '另锅宽水烧开下抄手，点两次水煮至浮起', 6),
  (@r, 5, '抄手捞入汤碗，淋香油，撒葱花上桌', 2);

-- ========== 22. 重庆酸辣粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('重庆酸辣粉', '山城街头的麻辣宵夜之王。红薯粉滑得打转，酸辣冲鼻，花生黄豆脆响，一碗下肚额头发汗，酸辣开胃的魔力全在那一勺保宁醋。', '/api/covers/chuan-cq-suanlafen.jpg', 15, 8, 23, 1, 2, '川菜', '地方名菜,小吃,主食,夏日', 1, TRUE, 310, 420, 10, 16, 62, '红薯粉提前泡软才透心；醋和辣椒油先入碗用热汤一激，酸香才激得出来。', '酸辣开胃');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '红薯粉条', '150', 'g', TRUE, 1, '/api/ingredients/hongshufen.jpg'),
  (@r, '油炸花生米', '30', 'g', TRUE, 2, '/api/ingredients/huasheng.jpg'),
  (@r, '榨菜粒', '20', 'g', TRUE, 3, '/api/ingredients/zhacai.jpg'),
  (@r, '黄豆', '20', 'g', TRUE, 4, '/api/ingredients/huangdou.jpg'),
  (@r, '辣椒油', '20', 'ml', TRUE, 5, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '保宁醋', '20', 'ml', TRUE, 6, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '白胡椒粉', '3', 'g', TRUE, 8, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '花椒粉', '2', 'g', TRUE, 9, '/api/ingredients/huajiaofen.jpg'),
  (@r, '高汤', '600', 'ml', TRUE, 10, '/api/ingredients/gaotang.jpg'),
  (@r, '小葱', '2', '根', TRUE, 11, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 12, '/api/ingredients/xiangcai.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '红薯粉提前温水泡软；黄豆干锅炒脆或炸至酥', 20),
  (@r, 2, '碗底放辣椒油、醋、生抽、白胡椒粉、花椒粉', 3),
  (@r, 3, '高汤烧开冲入碗中，激出酸辣香气', 2),
  (@r, 4, '粉条入沸水烫2分钟至透亮，捞入碗中', 3),
  (@r, 5, '撒花生、黄豆、榨菜粒、葱花、香菜即成', 2);

-- ========== 23. 富顺豆花 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('富顺豆花', '自贡富顺的一县之魂。胆水点的豆花绵而不散、窖水回甜，蘸水是灵魂：糍粑海椒配藿香木香，一碗豆花饭吃出川南人的踏实。', '/api/covers/chuan-fushun-douhua.jpg', 30, 30, 60, 2, 4, '川菜', '地方名菜,素菜,小吃', 1, TRUE, 297, 300, 24, 14, 22, '点豆花要一手搅浆一手点卤，卤水宁少勿多，豆花才绵嫩；糍粑海椒蒸熟舂茸，比生辣椒面香十倍。', '豆香蘸辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '黄豆', '300', 'g', TRUE, 1, '/api/ingredients/huangdou.jpg'),
  (@r, '胆水(卤水)', '10', 'ml', TRUE, 2, '/api/ingredients/lushui.jpg'),
  (@r, '干红辣椒', '30', 'g', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '郫县豆瓣酱', '15', 'g', TRUE, 4, '/api/ingredients/pixianjiang.jpg'),
  (@r, '花椒粉', '2', 'g', TRUE, 5, '/api/ingredients/huajiaofen.jpg'),
  (@r, '藿香叶', '5', '片', FALSE, 6, '/api/ingredients/huoxiangye.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '香油', '10', 'ml', TRUE, 9, '/api/ingredients/xiangyou.jpg'),
  (@r, '小葱', '2', '根', TRUE, 10, '/api/ingredients/xiaocong.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '黄豆泡发8小时，磨浆滤渣', 20),
  (@r, 2, '豆浆入锅烧开，撇沫后转小火', 10),
  (@r, 3, '一手轻搅豆浆，一手缓缓淋入胆水，见豆花凝结即停，静置5分钟', 8),
  (@r, 4, '干辣椒蒸熟，与豆瓣、蒜末舂成糍粑海椒，加花椒粉、生抽、香油、藿香碎调成蘸水', 10),
  (@r, 5, '豆花连窖水舀入碗，配蘸水与甑子饭同上', 5);

-- ========== 24. 简阳羊肉汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('简阳羊肉汤', '资阳简阳的冬至仪式。大耳羊与羊骨同熬通宵，汤白如奶、浓而不膻，羊肉切片回锅一烫，蘸干海椒面，喝汤吃肉从头暖到脚。', '/api/covers/chuan-jianyang-yangroutang.jpg', 30, 180, 210, 2, 6, '川菜', '地方名菜,汤品,羊肉,冬日', 1, TRUE, 110, 420, 36, 28, 4, '羊骨砸开再熬，骨髓才出、汤才奶白；大火滚煮是白汤的关键，小火煮出来是清汤。', '奶白浓鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '简阳大耳羊腿肉', '800', 'g', TRUE, 1, '/api/ingredients/yangrou.jpg'),
  (@r, '羊骨', '500', 'g', TRUE, 2, '/api/ingredients/yangrou.jpg'),
  (@r, '生姜', '40', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '2', '根', TRUE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '白胡椒粉', '3', 'g', TRUE, 5, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '花椒', '3', 'g', TRUE, 6, '/api/ingredients/huajiao.jpg'),
  (@r, '盐', '6', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '干辣椒面', '20', 'g', TRUE, 8, '/api/ingredients/lajiaofen.jpg'),
  (@r, '香菜', '15', 'g', FALSE, 9, '/api/ingredients/xiangcai.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '羊骨砸破，与羊肉同冷水下锅焯水，洗净', 20),
  (@r, 2, '大锅加足量开水，放羊骨、姜块、葱、花椒，大火滚煮2小时至汤白如奶', 120),
  (@r, 3, '羊肉捞出晾凉切薄片', 15),
  (@r, 4, '羊肉片入滚汤中烫热，连汤舀入大碗', 5),
  (@r, 5, '加盐、白胡椒粉调味，配干辣椒面蘸碟，撒香菜上桌', 5);

-- ========== 25. 毛血旺 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('毛血旺', '重庆磁器口码头边发明的一锅江湖。鸭血嫩滑、毛肚脆爽，红汤翻滚着厚厚的辣椒，是最生猛的重庆性格，越麻越辣越想吃。', '/api/covers/chuan-maoxuewang.jpg', 25, 15, 40, 2, 4, '川菜', '地方名菜,重辣,下饭,火锅', 1, TRUE, 247, 460, 30, 30, 10, '鸭血下锅后少搅动，保持块形完整；毛肚烫十几秒就够，久烫如嚼橡皮。', '麻辣浓郁');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸭血', '300', 'g', TRUE, 1, '/api/ingredients/yaxue.jpg'),
  (@r, '毛肚', '150', 'g', TRUE, 2, '/api/ingredients/niudu.jpg'),
  (@r, '午餐肉', '100', 'g', FALSE, 3, '/api/ingredients/wucanrou.jpg'),
  (@r, '黄豆芽', '150', 'g', TRUE, 4, '/api/ingredients/huangdouya.jpg'),
  (@r, '莴笋', '100', 'g', TRUE, 5, '/api/ingredients/wosun.jpg'),
  (@r, '鳝鱼片', '100', 'g', FALSE, 6, '/api/ingredients/shanyupian.jpg'),
  (@r, '郫县豆瓣酱', '30', 'g', TRUE, 7, '/api/ingredients/pixianjiang.jpg'),
  (@r, '干红辣椒', '20', 'g', TRUE, 8, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '10', 'g', TRUE, 9, '/api/ingredients/huajiao.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 10, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 11, '/api/ingredients/shengjiang.jpg'),
  (@r, '高汤', '600', 'ml', TRUE, 12, '/api/ingredients/gaotang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸭血切厚片，毛肚切梳子片，午餐肉切片，莴笋切片', 12),
  (@r, 2, '豆芽、莴笋焯断生，捞入深盆垫底', 3),
  (@r, 3, '热油下豆瓣、姜蒜末炒出红油，加高汤烧开熬2分钟', 4),
  (@r, 4, '依次下鸭血、午餐肉、鳝片煮3分钟，最后下毛肚烫15秒', 4),
  (@r, 5, '连汤倒入盆中，撒干辣椒段、花椒、蒜末', 2),
  (@r, 6, '滚油浇下激香，撒葱花上桌', 1);
