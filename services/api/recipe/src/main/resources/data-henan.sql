-- 由 seed/recipes-henan.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 河南菜，共 15 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 郑州羊肉烩面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('郑州羊肉烩面', '郑州的市饭。羊骨和羊肉熬出奶白汤，面是醒够后手工扯出的宽面片，锅里下粉丝、豆皮丝和木耳，出锅浇汤撒香菜，桌上配糖蒜和一勺辣椒油。', NULL, 70, 110, 180, 3, 4, '河南菜', '主食,面食,汤面,河南名吃', 1, TRUE, 165, 580, 32, 20, 68, '面要醒够才拉得开，扯成中间薄两边宽；汤必须熬到滚白再下面，清汤烩面不香。', '咸鲜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '400', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '温水', '200', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '盐', '5', 'g', TRUE, 3, '/api/ingredients/yan.jpg'),
  (@r, '羊肉', '300', 'g', TRUE, 4, '/api/ingredients/yangrou.jpg'),
  (@r, '羊骨', '500', 'g', TRUE, 5, '/api/ingredients/yangrou.jpg'),
  (@r, '清水', '2000', 'ml', TRUE, 6, '/api/ingredients/qingshui.jpg'),
  (@r, '粉丝', '80', 'g', TRUE, 7, '/api/ingredients/hongshufen.jpg'),
  (@r, '豆皮', '80', 'g', FALSE, 8, '/api/ingredients/doufu.jpg'),
  (@r, '水发木耳', '60', 'g', FALSE, 9, '/api/ingredients/muer.jpg'),
  (@r, '大葱', '1', '根', FALSE, 10, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '20', 'g', FALSE, 11, '/api/ingredients/shengjiang.jpg'),
  (@r, '香菜', '15', 'g', TRUE, 12, '/api/ingredients/xiangcai.jpg'),
  (@r, '料酒', '20', 'ml', FALSE, 13, '/api/ingredients/liaojiu.jpg'),
  (@r, '白胡椒粉', '3', 'g', TRUE, 14, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '辣椒油', '15', 'ml', FALSE, 15, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 16, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '面粉加盐和温水搅成絮状，揉成软面团抹油盖布醒30分钟', 35),
  (@r, 2, '羊骨和整块羊肉冷水下锅烧开撇沫，加葱姜料酒转微火熬90分钟成奶白汤', 100),
  (@r, 3, '捞出羊肉晾凉切片，汤过筛留清汤备用', 12),
  (@r, 4, '面团分剂子抹油再醒20分钟，取一团捏薄扯成中间薄两边宽的长面片', 25),
  (@r, 5, '滚汤下扯面，用筷子拨开煮至浮起', 5),
  (@r, 6, '下粉丝、豆皮丝和木耳同煮2分钟', 3),
  (@r, 7, '碗底放胡椒粉和香菜，捞面入碗浇羊汤，配糖蒜和辣椒油', 3);

-- ========== 2. 洛阳牛肉汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('洛阳牛肉汤', '洛阳人的早晨是一碗牛肉汤配饼丝。牛骨和整块牛肉清熬，肉切薄片放回碗里冲滚汤，撒葱花泼一勺辣子，汤清味厚不勾芡。', NULL, 90, 150, 240, 2, 4, '河南菜', '汤羹,牛肉,早餐,河南名吃', 1, TRUE, 216, 420, 36, 22, 18, '肉整块下锅、煮透后原汤浸泡才不柴；碗底不放酱油，颜色全靠牛骨汤。', '咸鲜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '黄牛后腿肉', '800', 'g', TRUE, 1, '/api/ingredients/niurou.jpg'),
  (@r, '牛骨', '500', 'g', TRUE, 2, '/api/ingredients/niurou.jpg'),
  (@r, '清水', '3000', 'ml', TRUE, 3, '/api/ingredients/qingshui.jpg'),
  (@r, '面粉', '200', 'g', FALSE, 4, '/api/ingredients/mianfen.jpg'),
  (@r, '生姜', '20', 'g', FALSE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', FALSE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '花椒', '3', 'g', FALSE, 7, '/api/ingredients/huajiao.jpg'),
  (@r, '盐', '8', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '3', 'g', TRUE, 9, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '香菜', '10', 'g', TRUE, 10, '/api/ingredients/xiangcai.jpg'),
  (@r, '蒜苗', '20', 'g', FALSE, 11, '/api/ingredients/qingsuan.jpg'),
  (@r, '食用油', '20', 'ml', FALSE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛骨和整块牛肉冷水浸泡1小时出血水', 60),
  (@r, 2, '冷水下锅烧开撇净浮沫，加葱姜花椒转微火熬2小时', 130),
  (@r, 3, '捞出牛肉晾凉切薄片，汤过筛留清汤', 15),
  (@r, 4, '面粉加盐和适量清水揉成硬面团，醒20分钟后擀薄切成细丝', 30),
  (@r, 5, '饼丝下平底锅少油烙至两面微黄', 8),
  (@r, 6, '碗底放盐和胡椒粉，铺肉片冲入滚汤，撒香菜蒜苗，配饼丝', 3);

-- ========== 3. 洛阳牡丹燕菜 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('洛阳牡丹燕菜', '洛阳水席的头菜。白萝卜切二细丝漂去辣味，拌薄粉上笼蒸松，再入酸辣鲜汤里回软，出锅时萝卜丝在汤中散开，形如牡丹。', NULL, 50, 30, 80, 3, 4, '河南菜', '汤菜,宴席菜,河南名菜,素菜', 1, TRUE, 148, 220, 10, 6, 32, '萝卜丝要漂两遍去生辣；拌粉只裹薄薄一层，多了结块；汤要滚着下，蒸好的燕菜不能泡久。', '酸辣鲜爽');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '白萝卜', '500', 'g', TRUE, 1, '/api/ingredients/bailuobo.jpg'),
  (@r, '淀粉', '60', 'g', TRUE, 2, '/api/ingredients/dianfen.jpg'),
  (@r, '鸡蛋', '2', '个', FALSE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '河虾仁', '80', 'g', FALSE, 4, '/api/ingredients/hexiaren.jpg'),
  (@r, '水发木耳', '40', 'g', FALSE, 5, '/api/ingredients/muer.jpg'),
  (@r, '香干', '50', 'g', FALSE, 6, '/api/ingredients/xianggan.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', FALSE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '白胡椒粒', '3', 'g', FALSE, 9, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '陈醋', '25', 'ml', TRUE, 10, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '20', 'ml', FALSE, 11, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '6', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '高汤', '800', 'ml', TRUE, 13, '/api/ingredients/gaotang.jpg'),
  (@r, '香油', '10', 'ml', FALSE, 14, '/api/ingredients/xiangyou.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 15, '/api/ingredients/xiangcai.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '白萝卜去皮切成二细丝，清水漂两遍后挤干', 20),
  (@r, 2, '萝卜丝拌上薄淀粉，上笼蒸8分钟后取出抖散晾凉', 15),
  (@r, 3, '虾仁用蛋清和少许淀粉上浆，木耳香干切细丝', 12),
  (@r, 4, '高汤烧开，下葱姜和白胡椒粒熬出味，捞去料渣', 10),
  (@r, 5, '汤里加醋、生抽和盐调成酸辣口，回萝卜丝稍煮', 6),
  (@r, 6, '另起小锅把虾仁滑熟，连木耳香干丝一起入汤', 5),
  (@r, 7, '盛碗淋香油，用香菜和蛋皮丝点缀，丝散如花即成', 4);

-- ========== 4. 河南胡辣汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('河南胡辣汤', '逍遥镇的早餐主角。面粉洗面出筋，汤里堆足胡椒和花椒，牛肉丝、粉条、海带丝、木耳一起熬稠，出锅前一勺醋和香油，配油饼吃。', NULL, 45, 35, 80, 2, 4, '河南菜', '汤羹,早餐,小吃,河南名吃', 1, TRUE, 252, 340, 16, 12, 44, '洗面水别倒，沉淀后当芡水用；胡椒和花椒要下足才配得上胡辣两个字；醋出锅前放，久煮酸味就跑光了。', '麻辣酸香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '200', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '牛肉', '150', 'g', TRUE, 3, '/api/ingredients/niurou.jpg'),
  (@r, '红薯粉条', '80', 'g', TRUE, 4, '/api/ingredients/hongshufen.jpg'),
  (@r, '海带丝', '50', 'g', FALSE, 5, '/api/ingredients/zicai.jpg'),
  (@r, '水发木耳', '50', 'g', FALSE, 6, '/api/ingredients/muer.jpg'),
  (@r, '豆皮', '60', 'g', FALSE, 7, '/api/ingredients/doufu.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', FALSE, 9, '/api/ingredients/dacong.jpg'),
  (@r, '白胡椒粉', '8', 'g', TRUE, 10, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '花椒粉', '4', 'g', TRUE, 11, '/api/ingredients/huajiaofen.jpg'),
  (@r, '陈醋', '20', 'ml', TRUE, 12, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '20', 'ml', FALSE, 13, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '6', 'g', TRUE, 14, '/api/ingredients/yan.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 15, '/api/ingredients/xiangcai.jpg'),
  (@r, '香油', '10', 'ml', FALSE, 16, '/api/ingredients/xiangyou.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 17, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '面粉加少量水和成软面团，醒20分钟后分次加水洗面，收下面筋和面水', 40),
  (@r, 2, '面筋上锅蒸10分钟切小片，粉条泡软剪段', 15),
  (@r, 3, '牛肉切丝，用生抽和少许水打上劲', 8),
  (@r, 4, '清水烧开，下姜丝、肉丝和面筋片煮开', 6),
  (@r, 5, '下海带丝、木耳丝和豆皮丝煮5分钟', 6),
  (@r, 6, '面水沉淀后倒去上层清水，缓缓搅进汤里熬稠', 8),
  (@r, 7, '加胡椒粉花椒粉和盐调味，淋香油和醋，撒香菜', 3);

-- ========== 5. 安阳三不粘 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('安阳三不粘', '安阳老店的甜菜，四样料全凭一双手炒。鸡蛋清、白糖、淀粉和水按比例调开，小油慢炒到金黄抱团，端上桌不粘盘、不粘筷、不粘牙。', NULL, 15, 25, 40, 3, 3, '河南菜', '甜点,热菜,河南名菜,宴席菜', 1, TRUE, 235, 380, 12, 20, 38, '全程小火、顺一个方向推炒，火大就散；油分次下，一次加多就成了炒蛋；炒到筷子挑起成团不滴落才算到位。', '甜香绵密');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸡蛋清', '6', '个', TRUE, 1, '/api/ingredients/jidanqing.jpg'),
  (@r, '白糖', '100', 'g', TRUE, 2, '/api/ingredients/baitang.jpg'),
  (@r, '淀粉', '60', 'g', TRUE, 3, '/api/ingredients/dianfen.jpg'),
  (@r, '清水', '100', 'ml', TRUE, 4, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '80', 'ml', TRUE, 5, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '1', 'g', FALSE, 6, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡蛋清加白糖搅至糖化，加清水和淀粉调成无颗粒的蛋浆', 10),
  (@r, 2, '不粘锅下少许油小火烧热，倒入蛋浆', 3),
  (@r, 3, '顺一个方向不停推炒，边炒边分次补油', 15),
  (@r, 4, '炒到蛋浆抱团、颜色金黄、挑起不滴落即可装盘', 4);

-- ========== 6. 开封炒凉粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('开封炒凉粉', '鼓楼夜市的招牌。红薯凉粉切厚块，下锅煎出硬壳还留着软心，加豆瓣酱、蒜水和辣椒翻匀，起锅前撒一把葱花，辣香冲鼻。', NULL, 25, 20, 45, 1, 3, '河南菜', '小吃,街头,河南名吃,夜市', 1, TRUE, 118, 300, 6, 12, 42, '凉粉切一指厚才炒得出壳而不碎；铲子少动，等底面结硬再翻；豆瓣酱本身咸，盐要收着放。', '咸香辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '淀粉', '100', 'g', TRUE, 1, '/api/ingredients/dianfen.jpg'),
  (@r, '清水', '1200', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '郫县豆瓣酱', '25', 'g', TRUE, 3, '/api/ingredients/pixianjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '大葱', '1', '根', FALSE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '辣椒油', '15', 'ml', FALSE, 7, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '生抽', '10', 'ml', FALSE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '淀粉加少许清水调开，其余清水烧开边倒边搅，熬至透明起大泡', 12),
  (@r, 2, '倒入抹过凉水的盆中晾凉凝固，切成一指厚的块', 90),
  (@r, 3, '大蒜捣泥加凉开水泡成蒜水，葱切花', 5),
  (@r, 4, '锅下油烧热，铺凉粉块煎至底面结硬再翻面', 8),
  (@r, 5, '下豆瓣酱和姜末炒香，淋蒜水和生抽翻匀', 4),
  (@r, 6, '起锅前撒葱花和辣椒油，连锅铲一起装盘', 2);

-- ========== 7. 卫辉蒸卤面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('卫辉蒸卤面', '河南人夏天的家常卤面。面条先蒸后拌汁再回笼，汤汁全被面吸干，豆角和五花肉的味道长在面上，出锅干香不坨。', NULL, 40, 45, 85, 2, 4, '河南菜', '主食,面食,蒸菜,家常', 1, TRUE, 165, 610, 22, 24, 76, '第一次蒸完要抖散晾凉再拌汁，不然结成一坨；汤汁宁少勿多，面吸不完就成汤面了。', '咸香干爽');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '400', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '清水', '180', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '盐', '4', 'g', TRUE, 3, '/api/ingredients/yan.jpg'),
  (@r, '五花肉', '200', 'g', TRUE, 4, '/api/ingredients/wuhuarou.jpg'),
  (@r, '干豆角', '100', 'g', TRUE, 5, '/api/ingredients/gandoujiao.jpg'),
  (@r, '绿豆芽', '150', 'g', FALSE, 6, '/api/ingredients/lvdouya.jpg'),
  (@r, '西红柿', '150', 'g', FALSE, 7, '/api/ingredients/xihongshi.jpg'),
  (@r, '大葱', '1', '根', FALSE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 9, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', FALSE, 11, '/api/ingredients/laochou.jpg'),
  (@r, '五香粉', '2', 'g', FALSE, 12, '/api/ingredients/bajiao.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 13, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '面粉加盐和清水和成偏硬面团，醒30分钟后擀薄切成粗面条', 40),
  (@r, 2, '面条上笼大火蒸15分钟，倒出抖散晾凉', 20),
  (@r, 3, '干豆角泡软切段，五花肉切片，豆芽和西红柿洗净', 12),
  (@r, 4, '热油煸肉片出油，下葱姜和老抽上色', 6),
  (@r, 5, '下豆角炒2分钟，加生抽和清水烧开后小火煮5分钟', 8),
  (@r, 6, '汤汁倒进面里拌匀，让面吃干汤汁', 6),
  (@r, 7, '面回笼再蒸15分钟，出锅前拌入豆芽和西红柿焖3分钟', 18);

-- ========== 8. 炸紫酥肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('炸紫酥肉', '郑州和洛阳年席上的老菜。五花肉加花椒闷煮到入味，晾透后拍粉下锅，炸出紫红硬壳，切条蘸花椒盐，肥而不腻。', NULL, 40, 60, 100, 2, 4, '河南菜', '炸物,冷盘,河南名菜,年节', 1, TRUE, 233, 640, 26, 54, 12, '煮肉的水里要放足花椒；煮好必须晾透，热着拍粉会脱壳；油温分两次，先养熟后炸脆。', '咸香酥');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '600', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '花椒', '6', 'g', TRUE, 2, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '2', '个', FALSE, 3, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '3', 'g', FALSE, 4, '/api/ingredients/guipi.jpg'),
  (@r, '生姜', '20', 'g', FALSE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', FALSE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '20', 'ml', FALSE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '6', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '生抽', '15', 'ml', FALSE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '面粉', '40', 'g', FALSE, 10, '/api/ingredients/mianfen.jpg'),
  (@r, '淀粉', '30', 'g', FALSE, 11, '/api/ingredients/dianfen.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 12, '/api/ingredients/qingshui.jpg'),
  (@r, '白胡椒粉', '3', 'g', FALSE, 13, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 14, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉整块冷水下锅，加花椒八角桂皮葱姜和料酒，烧开撇沫', 15),
  (@r, 2, '转微火煮40分钟至断生，原汤泡凉后取出沥干', 70),
  (@r, 3, '面粉和淀粉混匀，肉块表面拍上一层薄粉', 6),
  (@r, 4, '油烧五成热下肉，中火养煮至外壳微硬捞出', 12),
  (@r, 5, '油温升到七成热复炸至紫红发脆，倒出沥油', 5),
  (@r, 6, '晾到手温切厚条，蘸花椒盐装盘', 6);

-- ========== 9. 洛阳不翻汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('洛阳不翻汤', '老城十字街的夜市汤。面糊在热锅上摊成薄饼、只烙一面不翻身，切块垫进滚了虾皮紫菜的酸辣汤里，配一根烤面筋。', NULL, 30, 25, 55, 2, 4, '河南菜', '汤羹,小吃,夜市,河南名吃', 1, TRUE, 127, 260, 12, 8, 34, '面糊要稀到能挂住勺背，锅热再下才翻不动；紫菜虾皮最后放，久煮出腥。', '酸辣鲜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '淀粉', '100', 'g', TRUE, 1, '/api/ingredients/dianfen.jpg'),
  (@r, '鸡蛋', '2', '个', TRUE, 2, '/api/ingredients/jidan.jpg'),
  (@r, '清水', '300', 'ml', TRUE, 3, '/api/ingredients/qingshui.jpg'),
  (@r, '虾皮', '15', 'g', TRUE, 4, '/api/ingredients/xiapi.jpg'),
  (@r, '紫菜', '10', 'g', TRUE, 5, '/api/ingredients/zicai.jpg'),
  (@r, '水发木耳', '40', 'g', FALSE, 6, '/api/ingredients/muer.jpg'),
  (@r, '豆腐', '150', 'g', FALSE, 7, '/api/ingredients/doufu.jpg'),
  (@r, '红薯粉条', '60', 'g', FALSE, 8, '/api/ingredients/hongshufen.jpg'),
  (@r, '大葱', '1', '根', FALSE, 9, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 10, '/api/ingredients/shengjiang.jpg'),
  (@r, '白胡椒粉', '4', 'g', TRUE, 11, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '陈醋', '25', 'ml', TRUE, 12, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', FALSE, 13, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '5', 'g', TRUE, 14, '/api/ingredients/yan.jpg'),
  (@r, '香油', '8', 'ml', FALSE, 15, '/api/ingredients/xiangyou.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 16, '/api/ingredients/xiangcai.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 17, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '淀粉加鸡蛋和清水调成能挂勺的稀糊，静置10分钟', 12),
  (@r, 2, '热锅刷薄油，舀一勺糊转匀摊成薄饼，只烙一面至表面干透', 8),
  (@r, 3, '不翻饼取出切菱形块', 4),
  (@r, 4, '清水烧开，下虾皮紫菜姜丝和木耳煮5分钟', 6),
  (@r, 5, '加胡椒粉、醋、生抽和盐调成酸辣汤口', 3),
  (@r, 6, '下豆腐片和粉条煮2分钟', 3),
  (@r, 7, '碗底放不翻饼块，冲入滚汤，淋香油撒香菜', 2);

-- ========== 10. 蔡记蒸饺 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('蔡记蒸饺', '郑州老字号的发面蒸饺。皮要发到刚起小孔，馅是猪肉白菜分次打水打出来的，蒸好一咬一包汤，蘸陈醋蒜泥才够味。', NULL, 90, 15, 105, 3, 4, '河南菜', '主食,面点,蒸菜,河南名吃', 1, TRUE, 302, 480, 24, 18, 56, '半发面最好：全发面皮厚、死面皮硬；打水要分次顺一个方向；蒸够12分钟别中途开盖。', '咸鲜多汁');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '400', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '酵母', '4', 'g', TRUE, 2, '/api/ingredients/mianfen.jpg'),
  (@r, '温水', '220', 'ml', TRUE, 3, '/api/ingredients/qingshui.jpg'),
  (@r, '猪前腿肉馅', '300', 'g', TRUE, 4, '/api/ingredients/zhuroumo.jpg'),
  (@r, '大白菜', '300', 'g', TRUE, 5, '/api/ingredients/baicai.jpg'),
  (@r, '大葱', '1', '根', FALSE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '8', 'ml', FALSE, 9, '/api/ingredients/laochou.jpg'),
  (@r, '盐', '6', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 11, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '香油', '12', 'ml', FALSE, 12, '/api/ingredients/xiangyou.jpg'),
  (@r, '食用油', '20', 'ml', FALSE, 13, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '100', 'ml', FALSE, 14, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '酵母用温水化开倒入面粉，揉成软面团醒40分钟至刚起小孔', 45),
  (@r, 2, '大白菜切碎加盐杀水，挤干后拌香油', 15),
  (@r, 3, '肉馅分次打入清水、生抽老抽和姜末，顺一个方向搅上劲', 12),
  (@r, 4, '拌入白菜和葱花成馅', 5),
  (@r, 5, '面团搓条下剂子，擀成中间厚边薄的圆皮，包馅捏成月牙饺', 25),
  (@r, 6, '上笼大火蒸12分钟至表皮发亮', 12),
  (@r, 7, '配陈醋蒜泥端上桌', 2);

-- ========== 11. 南湾鱼头豆腐汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('南湾鱼头豆腐汤', '信阳靠大别山的水。南湾鳙鱼头先煎后炖，汤熬成奶白，点豆腐同煮，只放姜和盐，起锅撒一把香菜，是信阳炖菜的开场。', NULL, 20, 40, 60, 1, 4, '河南菜', '汤羹,河鲜,炖菜,信阳', 1, TRUE, 163, 360, 34, 20, 8, '鱼头一定要煎到皮微焦再冲滚水，汤才白；中途不添冷水；豆腐后下才不碎。', '清鲜奶白');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鳙鱼头', '800', 'g', TRUE, 1, '/api/ingredients/yongyutou.jpg'),
  (@r, '豆腐', '300', 'g', TRUE, 2, '/api/ingredients/doufu.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 3, '/api/ingredients/qingshui.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', FALSE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '20', 'ml', FALSE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '6', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 8, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 9, '/api/ingredients/xiangcai.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鱼头洗净劈开去鳃，用料酒和姜片抹匀腌10分钟', 12),
  (@r, 2, '热锅下油，鱼头两面煎至微黄', 6),
  (@r, 3, '冲入滚水大火煮10分钟，汤色转奶白', 10),
  (@r, 4, '转中火加盖炖15分钟', 15),
  (@r, 5, '下切块的豆腐再煮8分钟', 8),
  (@r, 6, '加盐和白胡椒粉调味，撒香菜葱花出锅', 3);

-- ========== 12. 信阳焖罐肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('信阳焖罐肉', '信阳人冬天的坛子菜。带皮五花肉干锅煸出油，加干豆角和花椒在陶罐里小火焖到肉色转深，肥的化口、瘦的不柴，舀汁拌饭最狠。', NULL, 30, 120, 150, 2, 4, '河南菜', '炖菜,冬日,信阳,下饭', 1, TRUE, 222, 720, 32, 60, 10, '肉下锅不放油，靠自身肥油煸香；焖够一个半小时才化；离火后连罐继续焖，味更进。', '咸香醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '700', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '干豆角', '150', 'g', TRUE, 2, '/api/ingredients/gandoujiao.jpg'),
  (@r, '生姜', '25', 'g', FALSE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', FALSE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '花椒', '4', 'g', TRUE, 5, '/api/ingredients/huajiao.jpg'),
  (@r, '干辣椒', '6', '个', FALSE, 6, '/api/ingredients/ganlajiao.jpg'),
  (@r, '料酒', '25', 'ml', FALSE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '12', 'ml', FALSE, 9, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '8', 'g', FALSE, 10, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '4', 'g', TRUE, 11, '/api/ingredients/yan.jpg'),
  (@r, '清水', '800', 'ml', TRUE, 12, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '20', 'ml', FALSE, 13, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉带皮切成麻将块，干豆角温水泡软切段', 12),
  (@r, 2, '净锅下肉块中小火煸出油，肉皮微焦后倒出多余油', 12),
  (@r, 3, '下花椒干辣椒和葱姜炒香，烹料酒', 4),
  (@r, 4, '加生抽老抽白糖和清水烧开', 5),
  (@r, 5, '转小火连肉带汤倒入陶罐，加盖焖90分钟', 90),
  (@r, 6, '下豆角再焖20分钟，收汁到油亮后连罐上桌', 22);

-- ========== 13. 红枣蒸南瓜 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('红枣蒸南瓜', '豫中一带的甜碗。老南瓜配新郑红枣和糯米，上笼蒸到筷子一插就透，只靠枣和糖提味，是年节里给老人孩子的一道软菜。', NULL, 25, 40, 65, 1, 4, '河南菜', '甜点,蒸菜,素菜,年节', 1, TRUE, 204, 240, 4, 2, 52, '南瓜挑面一点的，水南瓜蒸成一滩；糯米提前泡透才不夹生；蒸出的汁别倒，回浇一遍更甜。', '清甜绵软');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '老南瓜', '600', 'g', TRUE, 1, '/api/ingredients/nangua.jpg'),
  (@r, '红枣', '60', 'g', TRUE, 2, '/api/ingredients/hongzao.jpg'),
  (@r, '糯米', '80', 'g', TRUE, 3, '/api/ingredients/nuomi.jpg'),
  (@r, '白糖', '40', 'g', FALSE, 4, '/api/ingredients/baitang.jpg'),
  (@r, '清水', '200', 'ml', TRUE, 5, '/api/ingredients/qingshui.jpg'),
  (@r, '蜂蜜', '20', 'g', FALSE, 6, '/api/ingredients/mayatang.jpg'),
  (@r, '食用油', '10', 'ml', FALSE, 7, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '糯米提前浸泡2小时，红枣温水洗净', 120),
  (@r, 2, '南瓜去皮去瓤切厚片，盘底刷薄油摆好', 8),
  (@r, 3, '南瓜上撒白糖和沥干的糯米，嵌进红枣', 6),
  (@r, 4, '加清水上笼大火蒸35分钟，至筷子能插透南瓜', 35),
  (@r, 5, '取出淋蜂蜜，把蒸出的汁回浇一遍', 3);

-- ========== 14. 蒜泥捞面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('蒜泥捞面', '河南夏天的凉吃法。手擀面煮透后过两遍凉水，浇一勺蒜泥和芝麻酱调的卤，配黄瓜丝西红柿，一盆面四个人围着扒拉。', NULL, 45, 15, 60, 1, 4, '河南菜', '主食,面食,凉面,夏日', 1, TRUE, 253, 470, 14, 14, 72, '面要过凉到彻底凉透，表面才收紧不糊；蒜泥先用盐搓再泡水才不辣口；芝麻酱必须澥开再浇。', '蒜香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '400', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '清水', '190', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '盐', '4', 'g', TRUE, 3, '/api/ingredients/yan.jpg'),
  (@r, '鸡蛋', '2', '个', FALSE, 4, '/api/ingredients/jidan.jpg'),
  (@r, '大蒜', '40', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '芝麻酱', '40', 'g', TRUE, 6, '/api/ingredients/zhimajiang.jpg'),
  (@r, '黄瓜', '200', 'g', FALSE, 7, '/api/ingredients/huanggua.jpg'),
  (@r, '西红柿', '200', 'g', FALSE, 8, '/api/ingredients/xihongshi.jpg'),
  (@r, '陈醋', '25', 'ml', FALSE, 9, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '25', 'ml', FALSE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '香油', '15', 'ml', FALSE, 11, '/api/ingredients/xiangyou.jpg'),
  (@r, '辣椒油', '15', 'ml', FALSE, 12, '/api/ingredients/lajiaoyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '面粉加盐、鸡蛋和清水和成硬面团，醒30分钟后擀薄切成细面条', 35),
  (@r, 2, '大蒜加盐捣成泥，用凉开水泡开；芝麻酱分次加水澥成流动的稠汁', 10),
  (@r, 3, '黄瓜和西红柿切丝', 8),
  (@r, 4, '大锅水烧开下面，煮开两次点两回冷水，面熟捞出', 12),
  (@r, 5, '面条入凉开水过两遍，捞出沥干淋香油拌匀', 6),
  (@r, 6, '浇蒜泥水、芝麻酱、醋和生抽，配两样菜丝和辣椒油拌匀', 4);

-- ========== 15. 安阳皮渣 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('安阳皮渣', '晋豫交界的年下吃食。红薯粉加牛肉末和粉条熬成团，晾硬切块，先煎后烩，垫白菜或蒜苗同炖，是安阳人桌上的万能配菜。', NULL, 40, 40, 80, 2, 4, '河南菜', '杂粮,煎烩,年节,豫北', 1, TRUE, 113, 430, 16, 18, 54, '粉浆要熬到搅不动才成得了团；必须彻底晾硬再切，热切会散成一锅糊；煎出硬壳再烩才不烂。', '咸香筋道');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '淀粉', '200', 'g', TRUE, 1, '/api/ingredients/dianfen.jpg'),
  (@r, '清水', '700', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '牛肉末', '120', 'g', TRUE, 3, '/api/ingredients/niuroumo.jpg'),
  (@r, '红薯粉条', '80', 'g', TRUE, 4, '/api/ingredients/hongshufen.jpg'),
  (@r, '大葱', '1', '根', FALSE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '五香粉', '3', 'g', TRUE, 7, '/api/ingredients/bajiao.jpg'),
  (@r, '盐', '6', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '生抽', '20', 'ml', FALSE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 10, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '大白菜', '200', 'g', FALSE, 11, '/api/ingredients/baicai.jpg'),
  (@r, '食用油', '50', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '淀粉加部分清水调成稀浆，粉条泡软切碎', 10),
  (@r, 2, '剩余清水烧开，倒入粉浆不停搅，熬至成团能挂铲', 12),
  (@r, 3, '下牛肉末、粉条碎、葱姜末、五香粉和盐拌匀', 6),
  (@r, 4, '倒入抹油的方盘压平，彻底晾凉凝固', 120),
  (@r, 5, '切成厚块，下锅煎至两面结硬壳', 10),
  (@r, 6, '白菜切块垫砂锅底，码上皮渣，加生抽和少许水加盖烩10分钟', 12);
