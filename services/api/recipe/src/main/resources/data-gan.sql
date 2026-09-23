-- 由 seed/recipes-gan.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 江西菜，共 15 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 三杯鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('三杯鸡', '赣菜名扬四海的代表作，相传源自江西万载。一杯甜米酒、一杯猪油、一杯酱油，三杯入锅不见水，鸡块焖得油亮酥嫩，酒香钻进骨头里。', '/api/covers/gan-sanbeiji.jpg', 20, 30, 50, 2, 3, '江西菜', '经典,宴客,鸡肉,江西名菜', 1, TRUE, 223, 480, 32, 30, 8, '全程不加一滴水，靠米酒和酱油煨熟，火候宁小勿大；收汁收到锅里滋滋响、油亮裹身才算到位。', '咸鲜酒香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '土鸡', '半', '只(约800g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '甜米酒', '50', 'ml', TRUE, 2, '/api/ingredients/mijiu.jpg'),
  (@r, '猪油', '30', 'g', TRUE, 3, '/api/ingredients/zhuyou.jpg'),
  (@r, '酱油', '50', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '干红辣椒', '5', 'g', FALSE, 7, '/api/ingredients/ganlajiao.jpg'),
  (@r, '小葱', '3', '根', TRUE, 8, '/api/ingredients/xiaocong.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡斩成小块，姜切片、蒜拍碎', 12),
  (@r, 2, '热锅下猪油化开，下姜片、蒜瓣、干辣椒爆香', 2),
  (@r, 3, '下鸡块大火煸炒至表皮微黄收紧', 8),
  (@r, 4, '烹入酱油、甜米酒，烧开后转小火加盖焖15分钟', 15),
  (@r, 5, '开盖转大火收汁至浓稠裹身，撒葱花装盘', 5);

-- ========== 2. 藜蒿炒腊肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('藜蒿炒腊肉', '十大赣菜之一，鄱阳湖春天的限定美味。藜蒿脆嫩带野清香，腊肉咸香出油，一句“正月藜，二月蒿”唱的就是它的时令金贵。', '/api/covers/gan-lihao-larou.jpg', 15, 8, 23, 1, 3, '江西菜', '经典,时令,腊味,江西名菜', 1, TRUE, 253, 420, 18, 34, 8, '藜蒿叶全部掐掉只留杆，撕去老皮才脆嫩；下锅后大火快炒半分钟即起，炒久了发软失魂。', '咸鲜清香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '藜蒿', '300', 'g', TRUE, 1, '/api/ingredients/lihao.jpg'),
  (@r, '腊肉', '200', 'g', TRUE, 2, '/api/ingredients/larou.jpg'),
  (@r, '干红辣椒', '5', 'g', FALSE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '盐', '1', 'g', TRUE, 6, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '藜蒿掐成寸段，撕去老皮，洗净沥干', 8),
  (@r, 2, '腊肉上锅蒸15分钟，晾凉切薄片', 18),
  (@r, 3, '热锅下腊肉小火煸至透明出油', 4),
  (@r, 4, '下姜蒜末、干辣椒段爆香', 1),
  (@r, 5, '下藜蒿转大火快炒半分钟，尝味补少许盐即出锅', 1);

-- ========== 3. 余干辣椒炒肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('余干辣椒炒肉', '赣菜辣味的门面担当。余干枫树辣椒明清时是贡品，皮薄肉厚辣得温柔，与土猪肉同炒，一碗汤泡饭全靠它。', '/api/covers/gan-yugan-lajiaochaorou.jpg', 15, 8, 23, 1, 3, '江西菜', '经典,家常,下饭,江西名菜', 1, TRUE, 94, 520, 22, 42, 6, '辣椒要用刀拍裂再下锅，辣香才出得来；肥肉煸油、瘦肉后下，一锅两吃口感才对。', '香辣微甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮土猪肉', '350', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '余干辣椒', '150', 'g', TRUE, 2, '/api/ingredients/qinglajiao.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '豆豉', '8', 'g', TRUE, 4, '/api/ingredients/douchi.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '2', 'g', TRUE, 6, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪肉肥瘦分开切薄片，辣椒拍裂切段，蒜切粒', 10),
  (@r, 2, '热锅下肥肉片，小火煸出油脂至微卷', 5),
  (@r, 3, '下瘦肉片滑炒变色，加豆豉、蒜粒', 2),
  (@r, 4, '下辣椒段大火翻炒至起虎皮', 2),
  (@r, 5, '烹生抽、加盐翻炒均匀，连汁出锅', 1);

-- ========== 4. 鄱湖胖鱼头 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('鄱湖胖鱼头', '赣菜的宴席招牌。鄱阳湖的鳙鱼头大而肥美，配剁椒豆豉米酒旺火蒸透，鱼脑凝脂、鱼肉如蒜瓣，鲜辣里裹着湖水的清甜。', '/api/covers/gan-pohu-pangyutou.jpg', 20, 15, 35, 2, 4, '江西菜', '经典,宴客,河鲜,江西名菜', 1, TRUE, 154, 300, 26, 16, 6, '鱼头从鱼腹面剖开不断脊，趴盘而蒸受热匀；米酒去腥添香是赣做法的点睛之笔。', '鲜辣嫩滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鳙鱼头', '1', '个(约1200g)', TRUE, 1, '/api/ingredients/yongyutou.jpg'),
  (@r, '剁椒', '80', 'g', TRUE, 2, '/api/ingredients/duojiao.jpg'),
  (@r, '米酒', '30', 'ml', TRUE, 3, '/api/ingredients/mijiu.jpg'),
  (@r, '豆豉', '10', 'g', TRUE, 4, '/api/ingredients/douchi.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '蒸鱼豉油', '20', 'ml', TRUE, 7, '/api/ingredients/zhengyuchichou.jpg'),
  (@r, '小葱', '3', '根', TRUE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 9, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鱼头从腹面剖开不切断，展开铺盘，抹上米酒腌10分钟', 12),
  (@r, 2, '剁椒与豆豉、姜蒜末拌勻，厚铺鱼头上', 5),
  (@r, 3, '水开上锅，大火蒸12分钟，关火虚蒸2分钟', 14),
  (@r, 4, '倒去盘中腥水，淋蒸鱼豉油、撒葱花', 3),
  (@r, 5, '热油烧至冒烟浇下激香，趁热连盘上桌', 1);

-- ========== 5. 井冈山烟笋炒肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('井冈山烟笋炒肉', '井冈山八百里竹海的馈赠。鲜笋熏成烟笋，烟香混着笋香，与五花肉同炒，笋吸肉油、肉沾笋香，是赣西南山区的下饭担当。', '/api/covers/gan-jinggangshan-yansun.jpg', 40, 12, 52, 2, 3, '江西菜', '地方名菜,山珍,下饭', 1, TRUE, 262, 460, 20, 36, 10, '烟笋干硬，温水泡4小时再煮20分钟才软而不烂；炒时先下肥肉煸油，笋丝借猪油才润。', '烟香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '干烟笋', '150', 'g', TRUE, 1, '/api/ingredients/yansun.jpg'),
  (@r, '带皮五花肉', '250', 'g', TRUE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '大蒜叶', '50', 'g', TRUE, 3, '/api/ingredients/qingsuan.jpg'),
  (@r, '干红辣椒', '8', 'g', TRUE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '2', 'g', TRUE, 7, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '烟笋温水泡发4小时，撕成细丝，煮20分钟捞出挤干', 260),
  (@r, 2, '五花肉切薄片，蒜叶切段，姜切丝', 8),
  (@r, 3, '热锅下五花肉煸出油至微卷', 5),
  (@r, 4, '下姜丝、干辣椒段、烟笋丝中火炒2分钟', 2),
  (@r, 5, '烹生抽、加盐，下蒜叶大火炒匀出锅', 2);

-- ========== 6. 赣州小炒鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('赣州小炒鱼', '相传王阳明府中庖厨的即兴之作，醋香入馔的开山菜。鱼块滑嫩带醋香，辣椒姜蒜齐攻，酸甜咸辣一锅出，赣南人宴客的常客。', '/api/covers/gan-ganzhou-xiaochaoyu.jpg', 20, 10, 30, 2, 3, '江西菜', '经典,宴客,河鲜', 1, TRUE, 233, 360, 28, 20, 8, '鱼块拌薯粉（红薯粉）抓匀再滑炒，外滑里嫩；醋分两次放，炝锅一次起锅一次，醋香才有层次。', '醋香咸辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '草鱼', '1', '条(约800g)', TRUE, 1, '/api/ingredients/caoyu.jpg'),
  (@r, '红薯淀粉', '20', 'g', TRUE, 2, '/api/ingredients/dianfen.jpg'),
  (@r, '香醋', '20', 'ml', TRUE, 3, '/api/ingredients/xiangcu.jpg'),
  (@r, '米酒', '15', 'ml', TRUE, 4, '/api/ingredients/mijiu.jpg'),
  (@r, '红辣椒', '2', '根', TRUE, 5, '/api/ingredients/honglajiao.jpg'),
  (@r, '青辣椒', '2', '根', FALSE, 6, '/api/ingredients/qinglajiao.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 8, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '食用油', '50', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鱼治净取中段切3厘米块，加米酒、盐、红薯淀粉抓匀', 12),
  (@r, 2, '青红椒切菱形片，姜蒜切末', 5),
  (@r, 3, '热油下鱼块滑散，煎至两面定型盛出', 4),
  (@r, 4, '锅留底油，下姜蒜末、辣椒片爆香，烹入一半香醋炝锅', 2),
  (@r, 5, '倒回鱼块，加生抽和少许水，中火烧2分钟', 2),
  (@r, 6, '淋剩下的香醋，翻匀收汁出锅', 1);

-- ========== 7. 赣南荷包胙 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('赣南荷包胙', '南安府（大余）传了三百年的宴席大菜。方形五花肉裹米粉香料，荷叶包扎入钵慢蒸半日，肉酥烂不腻、荷叶清香沁入，解开就是满堂香。', '/api/covers/gan-gannan-hebaozuo.jpg', 60, 240, 300, 3, 6, '江西菜', '地方名菜,宴席,猪肉', 1, TRUE, 138, 680, 22, 54, 18, '肉先煮七成熟再切块拌粉，肥油逼出大半；荷叶扎紧不漏汽，蒸足4小时，筷子一戳到底才算成。', '软糯荷香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '1000', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '干荷叶', '4', '张', TRUE, 2, '/api/ingredients/ganye.jpg'),
  (@r, '粘米粉', '100', 'g', TRUE, 3, '/api/ingredients/zhanmifen.jpg'),
  (@r, '八角粉', '3', 'g', TRUE, 4, '/api/ingredients/bajiao.jpg'),
  (@r, '酱油', '40', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '甜酒酿', '30', 'g', TRUE, 6, '/api/ingredients/mijiu.jpg'),
  (@r, '白糖', '10', 'g', TRUE, 7, '/api/ingredients/baitang.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉整块煮至七成熟，捞出晾凉切5厘米见方的块', 40),
  (@r, 2, '肉块加酱油、酒酿、白糖、八角粉、姜末拌匀腌20分钟', 25),
  (@r, 3, '粘米粉干锅炒至微黄，拌入肉块让每面挂粉', 15),
  (@r, 4, '荷叶烫软，每张包两块肉扎紧，码入蒸钵', 20),
  (@r, 5, '上甑大火蒸4小时至肉酥烂，连荷叶装盘，桌上解开', 240);

-- ========== 8. 南昌瓦罐煨汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('南昌瓦罐煨汤', '南昌人从宋朝煨到今天的早餐魂。小瓦罐装料封盖，埋进大瓦缸的木炭火里煨足数小时，汤浓似乳、藕粉肉酥，一盅下肚全天踏实。', '/api/covers/gan-nanchang-waguan-tang.jpg', 20, 180, 200, 2, 4, '江西菜', '经典,汤品,养生,早餐', 1, TRUE, 237, 320, 22, 18, 16, '家用砂锅替代瓦缸也能煨出好汤，关键是小火加盖、绝不中途开盖；盐一定最后放，早放肉柴。', '浓香清润');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪排骨', '400', 'g', TRUE, 1, '/api/ingredients/zhupaigu.jpg'),
  (@r, '莲藕', '300', 'g', TRUE, 2, '/api/ingredients/ou.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '红枣', '5', '颗', FALSE, 4, '/api/ingredients/hongzao.jpg'),
  (@r, '盐', '4', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '清水', '1200', 'ml', TRUE, 6, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '排骨斩段冷水下锅焯水，洗净血沫', 12),
  (@r, 2, '莲藕去皮切滚刀块，姜拍裂', 8),
  (@r, 3, '小瓦罐（或砂锅）内放排骨、莲藕、姜、红枣，一次性加足清水', 5),
  (@r, 4, '加盖小火慢煨3小时，中途不开盖', 180),
  (@r, 5, '起锅前加盐调味，连罐上桌', 3);

-- ========== 9. 南昌拌粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('南昌拌粉', '南昌人过早的头牌。湿米粉烫得雪白弹滑，萝卜干花生米剁椒蒜末一拌，嗦一口咸辣冲鼻，再配一碗瓦罐汤，就是南昌的早晨。', '/api/covers/gan-nanchang-banfen.jpg', 10, 5, 15, 1, 2, '江西菜', '地方名菜,小吃,早餐,米粉', 1, TRUE, 173, 480, 12, 16, 70, '米粉烫十几秒就够，久烫软塌没嚼头；拌的顺序是先液体后干料，最后花生米保持脆响。', '咸辣爽口');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '江西湿米粉', '300', 'g', TRUE, 1, '/api/ingredients/ganmifen.jpg'),
  (@r, '萝卜干', '30', 'g', TRUE, 2, '/api/ingredients/luobogan.jpg'),
  (@r, '油炸花生米', '30', 'g', TRUE, 3, '/api/ingredients/huasheng.jpg'),
  (@r, '剁椒', '15', 'g', TRUE, 4, '/api/ingredients/duojiao.jpg'),
  (@r, '蒜末', '15', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '香油', '5', 'ml', TRUE, 7, '/api/ingredients/xiangyou.jpg'),
  (@r, '小葱', '2', '根', TRUE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '5', 'g', FALSE, 9, '/api/ingredients/xiangcai.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '萝卜干切细丁，葱、香菜切末', 5),
  (@r, 2, '碗中放生抽、香油、剁椒、蒜末调成底味', 2),
  (@r, 3, '水沸下米粉烫15秒，捞出沥爽', 1),
  (@r, 4, '米粉入碗颠拌均匀挂味', 2),
  (@r, 5, '撒萝卜干、花生米、葱花、香菜即成', 1);

-- ========== 10. 弋阳年糕 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('弋阳年糕', '“弋阳大禾谷，天下第一糕”。大禾谷米经三蒸两百锤捶打成年糕，久煮不糊、弹糯拉丝，配白菜肉丝一炒，是上饶人围炉的家常至味。', '/api/covers/gan-yiyang-niangao.jpg', 15, 10, 25, 1, 3, '江西菜', '地方名菜,主食,年糕', 1, TRUE, 147, 520, 14, 12, 88, '年糕切片先入开水煮软再炒，直接下锅容易外糊内硬；炒时勤翻动，年糕粘锅功力不小。', '软糯咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '弋阳年糕', '400', 'g', TRUE, 1, '/api/ingredients/niangao.jpg'),
  (@r, '大白菜', '200', 'g', TRUE, 2, '/api/ingredients/baicai.jpg'),
  (@r, '猪里脊丝', '100', 'g', TRUE, 3, '/api/ingredients/zhuliji.jpg'),
  (@r, '大蒜叶', '30', 'g', TRUE, 4, '/api/ingredients/qingsuan.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '3', 'g', TRUE, 6, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 7, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '年糕切3毫米薄片，入沸水煮2分钟至软，捞出过凉', 8),
  (@r, 2, '白菜切丝，里脊丝用少许生抽抓匀，蒜叶切段', 5),
  (@r, 3, '热油下肉丝滑炒变色，下白菜丝炒软', 3),
  (@r, 4, '下年糕片中火翻炒1分钟', 1),
  (@r, 5, '烹生抽、加盐，下蒜叶翻匀出锅', 2);

-- ========== 11. 泰和乌鸡汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('泰和乌鸡汤', '泰和白凤乌鸡是世界珍禽，绒羽雪白、骨乌肉黑。清炖只放姜枣，汤色澄黄油亮，滋补不燥，是江西人秋冬餐桌上的一盅温柔。', '/api/covers/gan-taihe-wuji-tang.jpg', 15, 100, 115, 1, 4, '江西菜', '地方名菜,汤品,养生,宴客', 1, TRUE, 101, 280, 30, 14, 6, '乌鸡焯水后炖，汤才清；姜片两三片足矣，多则夺了鸡的清鲜。', '清补鲜润');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '泰和乌骨鸡', '1', '只(约900g)', TRUE, 1, '/api/ingredients/wuguji.jpg'),
  (@r, '红枣', '8', '颗', TRUE, 2, '/api/ingredients/hongzao.jpg'),
  (@r, '枸杞', '5', 'g', TRUE, 3, '/api/ingredients/gouqi.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 5, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '4', 'g', TRUE, 6, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '乌鸡斩大件，冷水下锅加料酒焯水，洗净', 12),
  (@r, 2, '鸡块入砂锅，加姜片、红枣和足量开水', 5),
  (@r, 3, '大火烧开转小火，加盖炖80分钟', 80),
  (@r, 4, '撒枸杞再炖10分钟，加盐调味即成', 12);

-- ========== 12. 庐山石鱼炒蛋 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('庐山石鱼炒蛋', '庐山三石之一。石鱼长不盈寸、鲜香浓缩，与土鸡蛋同炒，蛋裹鱼鲜、鱼借蛋嫩，一盘山珍下饭一绝，去庐山必点的名馔。', '/api/covers/gan-lushan-shiyu-chaodan.jpg', 15, 5, 20, 1, 3, '江西菜', '地方名菜,山珍,鸡蛋', 1, TRUE, 269, 260, 20, 18, 4, '石鱼干温水泡5分钟即可，泡久了鲜味流失；油温五成热下蛋液，小火慢推才嫩。', '鲜香嫩滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '庐山石鱼', '30', 'g', TRUE, 1, '/api/ingredients/lushanshiyu.jpg'),
  (@r, '土鸡蛋', '5', '个', TRUE, 2, '/api/ingredients/jidan.jpg'),
  (@r, '小葱', '3', '根', TRUE, 3, '/api/ingredients/xiaocong.jpg'),
  (@r, '料酒', '5', 'ml', TRUE, 4, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '3', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 6, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '石鱼温水泡5分钟，洗净沥干', 6),
  (@r, 2, '鸡蛋打散，加料酒、盐、葱花和石鱼搅匀', 5),
  (@r, 3, '油烧至五成热，倒入蛋液', 1),
  (@r, 4, '中小火慢推，蛋液凝固至八成即关火', 2),
  (@r, 5, '利用余温焖十秒，装盘上桌', 1);

-- ========== 13. 九江茶饼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('九江茶饼', '浔阳江头的千年茶点，苏东坡都赞过的“香脆”。皮薄如纸、馅芯酥香，芝麻桂花的香气混着茶油香，配一盏庐山云雾茶刚刚好。', '/api/covers/gan-jiujiang-chabing.jpg', 40, 20, 60, 2, 8, '江西菜', '地方名菜,茶点,点心,小吃', 1, TRUE, 195, 320, 6, 14, 44, '面团掺茶油和面才酥，水油比例宁少勿多；烤到边缘微黄立刻出炉，放烤网上晾脆。', '香甜酥脆');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '250', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '茶油', '60', 'ml', TRUE, 2, '/api/ingredients/shiyongyou.jpg'),
  (@r, '白芝麻', '40', 'g', TRUE, 3, '/api/ingredients/baizhima.jpg'),
  (@r, '白糖', '80', 'g', TRUE, 4, '/api/ingredients/baitang.jpg'),
  (@r, '糖桂花', '15', 'g', TRUE, 5, '/api/ingredients/guihuatang.jpg'),
  (@r, '面粉(馅用)', '30', 'g', TRUE, 6, '/api/ingredients/mianfen.jpg'),
  (@r, '小苏打', '1', 'g', TRUE, 7, '/api/ingredients/dianfen.jpg'),
  (@r, '清水', '80', 'ml', TRUE, 8, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '面粉100g加茶油30ml搓成油酥面；剩余面粉加茶油、小苏打、清水和成水油面，醒20分钟', 30),
  (@r, 2, '白糖、糖桂花、面粉30g拌成馅', 5),
  (@r, 3, '水油面包油酥，擀开卷起分剂，逐个包馅压成圆饼', 15),
  (@r, 4, '饼面刷水，粘满白芝麻', 5),
  (@r, 5, '烤箱200度烤15分钟至边缘金黄，取出晾凉即酥', 20);

-- ========== 14. 南昌白糖糕 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('南昌白糖糕', '南昌街头巷尾的传统甜口小吃，糯食控的心头肉。糯米团搓条盘成玉环，入油锅炸得金黄鼓胀，趁热滚一层白糖，外脆里糯拉丝。', '/api/covers/gan-nanchang-baitanggao.jpg', 40, 15, 55, 2, 4, '江西菜', '地方名菜,小吃,甜点,糯米', 1, TRUE, 302, 420, 6, 14, 68, '面团里掺三分之一粘米粉，炸出来才不塌不粘牙；油温五成热下锅，小火慢炸才鼓得起空心。', '香甜软糯');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '糯米粉', '200', 'g', TRUE, 1, '/api/ingredients/nuomifen.jpg'),
  (@r, '粘米粉', '80', 'g', TRUE, 2, '/api/ingredients/zhanmifen.jpg'),
  (@r, '白糖', '40', 'g', TRUE, 3, '/api/ingredients/baitang.jpg'),
  (@r, '酵母', '2', 'g', TRUE, 4, '/api/ingredients/mianfen.jpg'),
  (@r, '温水', '180', 'ml', TRUE, 5, '/api/ingredients/qingshui.jpg'),
  (@r, '白砂糖粉', '60', 'g', TRUE, 6, '/api/ingredients/baitang.jpg'),
  (@r, '食用油', '500', 'ml', FALSE, 7, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '白糖入温水化开，加酵母，倒入两种米粉揉成光滑面团，醒发30分钟', 35),
  (@r, 2, '面团搓成细长条，盘成圆环状，收口捏紧', 10),
  (@r, 3, '油烧至五成热，逐个下糕坯小火慢炸，翻面炸至金黄鼓起', 8),
  (@r, 4, '捞出沥油，趁热滚满白砂糖粉', 3),
  (@r, 5, '稍晾即食，凉了回锅复炸半分钟依旧酥糯', 2);

-- ========== 15. 瑞金牛肉汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('瑞金牛肉汤', '红色故都瑞金的一张味觉名片。当天黄牛肉切薄片清水现煮，只放姜盐不加一物，汤清见底却鲜掉眉毛，蘸一碟辣椒酱就是一顿硬早餐。', '/api/covers/gan-ruijin-niuroutang.jpg', 15, 15, 30, 1, 4, '江西菜', '地方名菜,汤品,牛肉,早餐', 1, TRUE, 274, 280, 28, 14, 4, '牛肉逆纹切薄片，水微沸时下锅一烫就熟，久煮必老；汤里千万别加酱油，清才见鲜。', '清鲜原味');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '新鲜黄牛肉', '500', 'g', TRUE, 1, '/api/ingredients/niurou.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '盐', '5', 'g', TRUE, 3, '/api/ingredients/yan.jpg'),
  (@r, '小葱', '3', '根', TRUE, 4, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '10', 'g', TRUE, 5, '/api/ingredients/xiangcai.jpg'),
  (@r, '干辣椒面', '20', 'g', TRUE, 6, '/api/ingredients/lajiaofen.jpg'),
  (@r, '清水', '1000', 'ml', TRUE, 7, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肉逆纹切薄片，姜切丝，葱、香菜切末', 12),
  (@r, 2, '清水烧开，下姜丝', 2),
  (@r, 3, '牛肉片分散下锅，中火煮至刚变色（约1分钟）', 2),
  (@r, 4, '加盐调味，连汤舀入碗中', 1),
  (@r, 5, '撒葱花、香菜，配干辣椒面蘸碟趁烫吃', 1);
