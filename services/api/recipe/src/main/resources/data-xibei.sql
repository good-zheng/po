-- 由 seed/recipes-xibei.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 西北菜，共 15 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 羊肉泡馍 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('羊肉泡馍', '西安的头牌。死面饦饦馍烙到八成熟，亲手掰成黄豆大的粒，配羊骨羊肉吊出的奶汤同煮，粉丝木耳吸饱汤汁，糖蒜和辣子酱摆在手边。', NULL, 90, 150, 240, 3, 4, '西北菜', '泡馍,主食,西安名吃,汤饭', 1, TRUE, 296, 620, 34, 22, 68, '馍是和死面烙的，不放酵母，烙到八成熟晾凉才掰得开；掰得越匀越入味；煮时用滚汤快煮，别在锅里久熬成一糊。', '醇厚鲜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '羊肉', '500', 'g', TRUE, 1, '/api/ingredients/yangrou.jpg'),
  (@r, '羊骨', '1000', 'g', TRUE, 2, '/api/ingredients/yangrou.jpg'),
  (@r, '中筋面粉', '300', 'g', TRUE, 3, '/api/ingredients/mianfen.jpg'),
  (@r, '红薯粉条', '80', 'g', FALSE, 4, '/api/ingredients/hongshufen.jpg'),
  (@r, '水发木耳', '50', 'g', FALSE, 5, '/api/ingredients/muer.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '2', '根', TRUE, 7, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '20', 'g', FALSE, 8, '/api/ingredients/dasuan.jpg'),
  (@r, '花椒', '15', '粒', TRUE, 9, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '3', '个', FALSE, 10, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '段', FALSE, 11, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '3', '片', FALSE, 12, '/api/ingredients/xiangye.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 13, '/api/ingredients/liaojiu.jpg'),
  (@r, '香菜', '20', 'g', FALSE, 14, '/api/ingredients/xiangcai.jpg'),
  (@r, '辣椒油', '15', 'ml', FALSE, 15, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '盐', '8', 'g', TRUE, 16, '/api/ingredients/yan.jpg'),
  (@r, '清水', '2500', 'ml', TRUE, 17, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '面粉加盐和清水揉成硬面团，醒20分钟后擀成厚饼，无油干烙至两面起焦花、八成熟，晾凉掰成黄豆大的碎粒', 60),
  (@r, 2, '羊骨和羊肉冷水下锅，加姜葱料酒，大火烧开撇净浮沫', 18),
  (@r, 3, '下花椒八角桂皮香叶，转微火加盖煮2小时至骨肉将离、汤色奶白', 125),
  (@r, 4, '羊肉捞出晾凉切片，原汤过滤留净', 12),
  (@r, 5, '取一碗装馍粒、肉片和泡软的粉条木耳，浇一勺滚沸羊肉汤', 4),
  (@r, 6, '旺火煮3分钟让馍吸汤，重浇一次汤，撒葱花香菜', 5),
  (@r, 7, '配辣椒酱、糖蒜和香菜末上桌，从边上一圈圈吃', 3);

-- ========== 2. 手抓羊肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('手抓羊肉', '宁夏甘肃的待客头道。滩羊后腿整块冷水下锅，只放姜葱花椒撇沫，煮到骨肉将离即捞，切条上桌，蘸椒盐或蒜泥酱油，吃的是羊肉本味。', NULL, 15, 90, 105, 1, 4, '西北菜', '羊肉,凉菜,宴客,西北硬菜', 1, TRUE, 119, 480, 38, 33, 3, '冷水下锅、微火慢煮才汤清肉嫩；盐起锅前放，早放肉柴；好滩羊不膻，香料越多越坏事。', '原汁咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '羊肉', '800', 'g', TRUE, 1, '/api/ingredients/yangrou.jpg'),
  (@r, '羊骨', '500', 'g', FALSE, 2, '/api/ingredients/yangrou.jpg'),
  (@r, '白萝卜', '1', '根', FALSE, 3, '/api/ingredients/bailuobo.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '2', '根', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '花椒', '20', '粒', TRUE, 6, '/api/ingredients/huajiao.jpg'),
  (@r, '香叶', '2', '片', FALSE, 7, '/api/ingredients/xiangye.jpg'),
  (@r, '料酒', '30', 'ml', FALSE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 9, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '15', 'ml', FALSE, 11, '/api/ingredients/xiangcu.jpg'),
  (@r, '盐', '8', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '清水', '2500', 'ml', TRUE, 13, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '羊肉整块冷水下锅，加羊骨、姜片、葱段和花椒，大火烧开', 15),
  (@r, 2, '撇净浮沫，转微火保持汤面只冒虾眼泡，煮60分钟', 65),
  (@r, 3, '下白萝卜块同煮20分钟至肉能插透筷子', 22),
  (@r, 4, '加盐调味再煮5分钟，捞出肉晾至不烫手', 8),
  (@r, 5, '逆纹切条装盘，浇一勺原汤', 6),
  (@r, 6, '大蒜捣泥，加生抽和少许香醋调成蘸汁，配椒盐同上桌', 5);

-- ========== 3. 大盘鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('大盘鸡', '从沙湾来的新疆名菜。鸡块炒糖色后配土豆青椒焖一大盘，酱香浓、辣味冲，最后拌一把宽面裹满汤汁，是西北馆子的排面。', NULL, 30, 45, 75, 2, 4, '西北菜', '大盘鸡,宴客,下饭菜,新疆名菜', 1, TRUE, 265, 640, 36, 26, 55, '土豆后放才不散不糊；干辣椒和花椒要先炝出香；宽面另煮铺底或蘸汁，别下进锅里糊了汤。', '酱香微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '三黄鸡', '1', '只(约1000g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '土豆', '400', 'g', TRUE, 2, '/api/ingredients/tudou.jpg'),
  (@r, '青辣椒', '2', '个', TRUE, 3, '/api/ingredients/qinglajiao.jpg'),
  (@r, '红辣椒', '1', '个', TRUE, 4, '/api/ingredients/honglajiao.jpg'),
  (@r, '洋葱', '1', '个', TRUE, 5, '/api/ingredients/yangcong.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '大葱', '1', '根', FALSE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '干辣椒', '15', 'g', TRUE, 9, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '15', '粒', TRUE, 10, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '2', '个', FALSE, 11, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '段', FALSE, 12, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '2', '片', FALSE, 13, '/api/ingredients/xiangye.jpg'),
  (@r, '冰糖', '15', 'g', TRUE, 14, '/api/ingredients/bingtang.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 15, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '15', 'ml', TRUE, 16, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 17, '/api/ingredients/liaojiu.jpg'),
  (@r, '中筋面粉', '300', 'g', FALSE, 18, '/api/ingredients/mianfen.jpg'),
  (@r, '盐', '6', 'g', TRUE, 19, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '50', 'ml', TRUE, 20, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '900', 'ml', TRUE, 21, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡斩大块冲净沥干，土豆滚刀块，青红椒和洋葱切块，姜蒜切好', 18),
  (@r, 2, '面粉加盐和温水揉软，醒30分钟后擀厚片切宽条，抖长备用', 35),
  (@r, 3, '热锅下油，冰糖炒出糖色，鸡块下锅煸至表皮金黄收紧', 8),
  (@r, 4, '下干辣椒、花椒、八角桂皮香叶和姜蒜葱爆香', 4),
  (@r, 5, '烹料酒加生抽老抽翻匀，添清水没过鸡块，大火烧开', 5),
  (@r, 6, '转中小火加盖焖20分钟', 22),
  (@r, 7, '下土豆块再焖15分钟至土豆绵软', 17),
  (@r, 8, '下青红椒和洋葱块，大火收至汤汁浓稠裹住鸡块', 5),
  (@r, 9, '宽面另锅煮熟铺在盘底，鸡块连汤倒扣上去，整盘上桌', 8);

-- ========== 4. 兰州牛肉面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('兰州牛肉面', '清汤牛肉面的规矩是一清二白三红四绿五黄：汤见底、萝卜薄、辣子红、蒜苗绿、面条黄亮。牛肉整块同煮，晾凉切片，汤要清而不寡。', NULL, 40, 180, 220, 3, 4, '西北菜', '面食,汤面,早餐,兰州名吃', 1, TRUE, 243, 520, 30, 16, 60, '汤全程微沸不能大滚，滚则浑；牛肉煮好晾凉再切才不散；白萝卜片单独焯软再入碗，才不会把汤弄味。', '清汤鲜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '新鲜黄牛肉', '800', 'g', TRUE, 1, '/api/ingredients/niurou.jpg'),
  (@r, '细面条', '400', 'g', TRUE, 2, '/api/ingredients/ximiantiao.jpg'),
  (@r, '白萝卜', '1', '根', TRUE, 3, '/api/ingredients/bailuobo.jpg'),
  (@r, '大蒜叶', '50', 'g', TRUE, 4, '/api/ingredients/qingsuan.jpg'),
  (@r, '香菜', '20', 'g', TRUE, 5, '/api/ingredients/xiangcai.jpg'),
  (@r, '生姜', '40', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '2', '根', TRUE, 7, '/api/ingredients/dacong.jpg'),
  (@r, '花椒', '20', '粒', TRUE, 8, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '2', '个', FALSE, 9, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '段', FALSE, 10, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '2', '片', FALSE, 11, '/api/ingredients/xiangye.jpg'),
  (@r, '草果', '2', '个', FALSE, 12, '/api/ingredients/caoguo.jpg'),
  (@r, '生抽', '30', 'ml', FALSE, 13, '/api/ingredients/shengchou.jpg'),
  (@r, '食用碱', '2', 'g', FALSE, 14, '/api/ingredients/dianfen.jpg'),
  (@r, '辣椒油', '30', 'ml', TRUE, 15, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '盐', '8', 'g', TRUE, 16, '/api/ingredients/yan.jpg'),
  (@r, '清水', '3000', 'ml', TRUE, 17, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肉整块冷水下锅，加姜葱，大火烧开撇净浮沫', 20),
  (@r, 2, '香料装料包下锅，转微火加盖煮2小时至肉能用筷子插透', 125),
  (@r, 3, '肉留汤里浸凉，捞出逆纹切薄片；原汤过滤，保持微沸', 20),
  (@r, 4, '白萝卜切薄圆片，下清水焯至透明，捞出铺碗底', 8),
  (@r, 5, '水烧开加少许食用碱，下面条煮至刚断生，捞起入碗', 6),
  (@r, 6, '撒蒜苗末和香菜末，摆牛肉片和萝卜片', 4),
  (@r, 7, '浇滚沸牛肉汤，淋一勺辣椒油，端碗先喝一口汤', 4);

-- ========== 5. 腊汁肉夹馍 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('腊汁肉夹馍', '西安人的快餐。猪前肘在老腊汁里炖到酥烂，捞出来剁碎夹进白吉馍，肉汁浸透馍心，外皮焦壳还顶着铁圈虎背菊花心的印子。', NULL, 40, 150, 190, 3, 6, '西北菜', '小吃,面食,肉夹馍,西安名吃', 1, TRUE, 144, 560, 28, 30, 42, '肉要带皮带肥，炖到勺背一压就散；馍是半发面，烙完再烤出硬壳；剁肉时浇一勺原汤，别放青椒香菜，那是外地的做法。', '酱香肥润');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪前肘', '1000', 'g', TRUE, 1, '/api/ingredients/zhuqianzhou.jpg'),
  (@r, '中筋面粉', '400', 'g', TRUE, 2, '/api/ingredients/mianfen.jpg'),
  (@r, '酵母', '5', 'g', TRUE, 3, '/api/ingredients/mianfen.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '2', '根', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '冰糖', '25', 'g', TRUE, 6, '/api/ingredients/bingtang.jpg'),
  (@r, '生抽', '50', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '25', 'ml', TRUE, 8, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '八角', '3', '个', TRUE, 10, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '段', TRUE, 11, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '3', '片', FALSE, 12, '/api/ingredients/xiangye.jpg'),
  (@r, '花椒', '15', '粒', FALSE, 13, '/api/ingredients/huajiao.jpg'),
  (@r, '丁香', '2', '粒', FALSE, 14, '/api/ingredients/dingxiang.jpg'),
  (@r, '盐', '5', 'g', TRUE, 15, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 16, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 17, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪前肘冷水下锅加姜葱料酒焯去血沫，捞出冲净', 15),
  (@r, 2, '热锅下油炒冰糖成糖色，下肉翻匀上色', 6),
  (@r, 3, '加生抽老抽和香料包，添清水没过肉，大火烧开转小火加盖炖2小时至酥烂', 125),
  (@r, 4, '酵母用温水化开，加进面粉和少许盐揉软，醒20分钟成半发面', 25),
  (@r, 5, '面团分剂子擀成碗状饼坯，无油小锅烙至两面起焦花', 18),
  (@r, 6, '烙过的馍入烤箱或干锅小火烤至外壳发硬发脆', 8),
  (@r, 7, '肉捞出剁碎，边剁边浇两勺原汤至湿润', 8),
  (@r, 8, '馍从侧面剖开不切断，塞满肉馅，压实后立刻吃', 4);

-- ========== 6. 油泼面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('油泼面', '陕西面的魂全在一勺滚油。宽面捞进碗里，堆辣椒面、蒜末和葱花，热油泼下去辣香冲鼻，再沿碗边淋一圈香醋，拌匀后根根挂红。', NULL, 40, 10, 50, 1, 2, '西北菜', '面食,快手菜,素面,西安家常', 1, TRUE, 258, 540, 14, 20, 74, '辣椒面要用秦椒，油烧到八成热分两次泼，才香而不糊；醋顺着碗边淋，遇热挥发才留下酸去掉生味。', '香辣酸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '300', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '小白菜心', '200', 'g', TRUE, 2, '/api/ingredients/baicai.jpg'),
  (@r, '辣椒面', '25', 'g', TRUE, 3, '/api/ingredients/lajiaofen.jpg'),
  (@r, '大蒜', '25', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '20', 'g', TRUE, 5, '/api/ingredients/xiaocong.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '25', 'ml', TRUE, 7, '/api/ingredients/xiangcu.jpg'),
  (@r, '盐', '5', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '80', 'ml', TRUE, 9, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '150', 'ml', TRUE, 10, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '面粉加盐和温水揉成软面团，盖住醒30分钟', 32),
  (@r, 2, '面团分剂子抹油再醒20分钟，擀开后用手指在中间压一道痕', 22),
  (@r, 3, '两手捏住面片轻轻扯长扯宽，抖出裤带面', 6),
  (@r, 4, '宽水烧开下面，用筷子轻推，煮至断生，半路点一次凉水', 6),
  (@r, 5, '下青菜同烫十秒，面和菜一起捞入大碗', 2),
  (@r, 6, '面上堆辣椒面、蒜末、葱花和盐，浇生抽', 4),
  (@r, 7, '另锅把油烧至冒青烟，分两次泼在辣椒面上，趁响沿碗边淋香醋，拌匀', 3);

-- ========== 7. 麻酱凉皮 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('麻酱凉皮', '洗面洗出的凉皮薄透带筋，切宽条配黄瓜丝，浇油泄的芝麻酱、蒜水和辣椒油，酸辣麻香裹着滑溜的皮子，是陕西夏天的街头味道。', NULL, 60, 20, 300, 2, 3, '西北菜', '凉菜,小吃,夏季,西安名吃', 1, TRUE, 129, 400, 10, 16, 52, '面浆沉淀一夜才透亮，摊皮要薄，入锅烫到起泡即起；面筋蒸熟撕块同拌；芝麻酱先加油泄开再加水，直接加水会结块。', '麻酱酸辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '400', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '黄瓜', '1', '根', TRUE, 2, '/api/ingredients/huanggua.jpg'),
  (@r, '芝麻酱', '40', 'g', TRUE, 3, '/api/ingredients/zhimajiang.jpg'),
  (@r, '大蒜', '25', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '陈醋', '35', 'ml', TRUE, 6, '/api/ingredients/xiangcu.jpg'),
  (@r, '辣椒油', '25', 'ml', TRUE, 7, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '白糖', '8', 'g', FALSE, 8, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '4', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '香菜', '15', 'g', FALSE, 10, '/api/ingredients/xiangcai.jpg'),
  (@r, '食用油', '15', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '200', 'ml', TRUE, 12, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '面粉加少许盐和对成的200ml清水揉软，盖住醒30分钟', 32),
  (@r, 2, '盆里加水反复抓洗面团，直到水变清，面筋剩一小块', 15),
  (@r, 3, '洗面水过筛静置沉淀至少2小时（隔夜更好），倒掉上层清水', 120),
  (@r, 4, '面筋加一点酵母发小半小时，上锅蒸20分钟成蜂窝块，切块', 55),
  (@r, 5, '平盘刷薄油舀一勺面浆摊平，浮在沸水锅上加盖蒸2分钟至起泡', 4),
  (@r, 6, '连盘投入冷水，揭下凉皮抹薄油防粘，叠起切宽条', 10),
  (@r, 7, '芝麻酱加油泄开，再加生抽陈醋白糖清水和蒜泥调成料汁', 6),
  (@r, 8, '凉皮装碗，码黄瓜丝和面筋，浇料汁与辣椒油，撒香菜拌匀', 4);

-- ========== 8. 岐山臊子面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('岐山臊子面', '讲究薄筋光、酸辣香：猪肉臊子炒出油，配胡萝卜木耳豆腐的漂菜，酸汤冲开，面只挑一线，一碗见底不剩汤。', NULL, 30, 25, 55, 2, 4, '西北菜', '面食,汤面,酸汤,陕西名吃', 1, TRUE, 254, 480, 20, 16, 62, '臊子提前一天炒好，泡在醋里更出味；醋要下锅烹出酸香，别起锅才放；面少汤宽，岐山规矩是只挑一线面。', '酸辣鲜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪瘦肉', '250', 'g', TRUE, 1, '/api/ingredients/zhushourou.jpg'),
  (@r, '细面条', '400', 'g', TRUE, 2, '/api/ingredients/ximiantiao.jpg'),
  (@r, '豆腐', '150', 'g', TRUE, 3, '/api/ingredients/doufu.jpg'),
  (@r, '胡萝卜', '1', '根', TRUE, 4, '/api/ingredients/huluobo.jpg'),
  (@r, '土豆', '1', '个', FALSE, 5, '/api/ingredients/tudou.jpg'),
  (@r, '水发木耳', '50', 'g', TRUE, 6, '/api/ingredients/muer.jpg'),
  (@r, '大蒜叶', '50', 'g', TRUE, 7, '/api/ingredients/qingsuan.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 9, '/api/ingredients/dacong.jpg'),
  (@r, '干辣椒', '10', 'g', TRUE, 10, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '10', '粒', FALSE, 11, '/api/ingredients/huajiao.jpg'),
  (@r, '陈醋', '50', 'ml', TRUE, 12, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 13, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '5', 'g', TRUE, 14, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 15, '/api/ingredients/shiyongyou.jpg'),
  (@r, '高汤', '1200', 'ml', TRUE, 16, '/api/ingredients/gaotang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '瘦肉切小丁加少许盐抓匀，胡萝卜土豆木耳豆腐切同样大的丁，蒜苗切小段', 15),
  (@r, 2, '热锅下油，花椒炸香捞出，下肉丁煸炒至发白出油', 5),
  (@r, 3, '下干辣椒段和姜葱末炒香，烹入一半陈醋激出酸香', 3),
  (@r, 4, '加生抽和少许水，小火煨10分钟成臊子', 12),
  (@r, 5, '高汤烧开，下臊子和胡萝卜土豆木耳豆腐丁煮3分钟，补盐和剩下的醋', 6),
  (@r, 6, '另锅煮熟面条，捞入碗中只放一线面', 6),
  (@r, 7, '浇酸汤和漂菜，撒蒜苗段，辣子油按口味点几滴', 3);

-- ========== 9. 新疆手抓饭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('新疆手抓饭', '羊腿肉、黄萝卜和洋葱在清油里炒到软甜，铺上大米焖一锅。米粒油亮分明、裹着肉香，抓一把就着羊肉吃，是新疆待客的硬饭。', NULL, 25, 50, 75, 2, 4, '西北菜', '主食,米饭,宴客,新疆名菜', 1, TRUE, 275, 660, 28, 22, 88, '萝卜切粗条才焖得出甜；米铺在菜上不能翻动，沿锅边淋水；焖好后翻匀扣盘，配一碟生菜丝和皮牙子解腻。', '油润肉香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '羊肉', '500', 'g', TRUE, 1, '/api/ingredients/yangrou.jpg'),
  (@r, '大米', '400', 'g', TRUE, 2, '/api/ingredients/dami.jpg'),
  (@r, '胡萝卜', '300', 'g', TRUE, 3, '/api/ingredients/huluobo.jpg'),
  (@r, '洋葱', '2', '个', TRUE, 4, '/api/ingredients/yangcong.jpg'),
  (@r, '红枣', '6', '颗', FALSE, 5, '/api/ingredients/hongzao.jpg'),
  (@r, '生姜', '20', 'g', FALSE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '花椒', '10', '粒', FALSE, 7, '/api/ingredients/huajiao.jpg'),
  (@r, '盐', '6', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '80', 'ml', TRUE, 9, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '500', 'ml', TRUE, 10, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '羊肉切条，胡萝卜切粗条，洋葱切粗丝，大米洗净盐水泡20分钟', 22),
  (@r, 2, '锅烧热下油，花椒炸香捞出，下羊肉条煸至表面收紧出油', 8),
  (@r, 3, '下洋葱丝炒至透明发甜，再下胡萝卜条炒软', 8),
  (@r, 4, '加盐和少许姜末翻匀，添清水没过菜，烧开焖5分钟', 8),
  (@r, 5, '把泡好的米沥干平铺在菜上，不要翻动，沿锅边淋下清水', 5),
  (@r, 6, '水开后转小火加盖焖25分钟至米熟汤干', 26),
  (@r, 7, '放入红枣再焖5分钟，关火焖10分钟', 15),
  (@r, 8, '揭盖把米和肉菜从底向上翻匀，扣盘堆成小山上桌', 6);

-- ========== 10. 洋芋擦擦 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('洋芋擦擦', '陕北家常。土豆擦成粗条裹一层面粉蒸熟，再配葱花干辣椒和肉末炒到表面起焦壳，土豆的香里带一点焦香，一碗能当一顿饭。', NULL, 30, 20, 50, 1, 3, '西北菜', '素菜,主食,家常,陕北小吃', 1, TRUE, 244, 380, 9, 14, 54, '土豆条裹粉要薄，多了会结块；蒸好摊凉再炒，一锅别压太厚才出焦壳；起锅前沿锅边点几滴醋提香。', '干香微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '土豆', '600', 'g', TRUE, 1, '/api/ingredients/tudou.jpg'),
  (@r, '中筋面粉', '80', 'g', TRUE, 2, '/api/ingredients/mianfen.jpg'),
  (@r, '猪肉末', '80', 'g', FALSE, 3, '/api/ingredients/zhuroumo.jpg'),
  (@r, '大葱', '1', '根', TRUE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '15', 'g', FALSE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '干辣椒', '8', 'g', TRUE, 6, '/api/ingredients/ganlajiao.jpg'),
  (@r, '胡萝卜', '1', '根', FALSE, 7, '/api/ingredients/huluobo.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '8', 'ml', FALSE, 9, '/api/ingredients/xiangcu.jpg'),
  (@r, '盐', '4', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '45', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '土豆去皮擦成粗条，清水冲去表面淀粉后沥干', 12),
  (@r, 2, '拌入面粉和少许盐，让每根都挂上薄粉', 5),
  (@r, 3, '铺上蒸笼中火蒸15分钟，取出摊凉抖散', 16),
  (@r, 4, '热锅下油，干辣椒段和葱花爆香，下肉末炒散炒酥', 5),
  (@r, 5, '下胡萝卜丝和蒸好的土豆条，大火翻炒至表面起焦壳', 8),
  (@r, 6, '淋生抽和醋，撒蒜末翻匀出锅', 3);

-- ========== 11. 黄焖羊肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('黄焖羊肉', '西北的冬炖。羊肉块先干煸出水汽再下油，配干辣椒花椒和香料焖一小时，汤浓肉烂，辣香钻进羊肉里，一点不膻。', NULL, 20, 75, 95, 2, 4, '西北菜', '炖菜,羊肉,冬季,下饭菜', 1, TRUE, 213, 590, 38, 40, 18, '羊肉先无油干煸出水汽，再下油炒才不腥；一次加足热水，中途不添冷水；土豆后下，炖化就糊了汤。', '浓辣鲜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '羊肉', '800', 'g', TRUE, 1, '/api/ingredients/yangrou.jpg'),
  (@r, '土豆', '300', 'g', TRUE, 2, '/api/ingredients/tudou.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '25', 'g', FALSE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '干辣椒', '15', 'g', TRUE, 6, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '15', '粒', TRUE, 7, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '2', '个', FALSE, 8, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '段', FALSE, 9, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '2', '片', FALSE, 10, '/api/ingredients/xiangye.jpg'),
  (@r, '冰糖', '12', 'g', FALSE, 11, '/api/ingredients/bingtang.jpg'),
  (@r, '生抽', '35', 'ml', TRUE, 12, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '12', 'ml', TRUE, 13, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 14, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '5', 'g', TRUE, 15, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 16, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '1200', 'ml', TRUE, 17, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '羊肉切块冲净；干辣椒切段，姜切片，葱切段，土豆滚刀块', 12),
  (@r, 2, '干锅下羊肉块中火煸炒，逼出水汽和羊油至表面微黄，盛出', 10),
  (@r, 3, '锅留底油，下花椒干辣椒、姜葱蒜和八角桂皮香叶爆香', 4),
  (@r, 4, '羊肉回锅，加冰糖生抽老抽料酒翻炒上色', 5),
  (@r, 5, '添热水没过羊肉，大火烧开转小火加盖焖50分钟', 55),
  (@r, 6, '下土豆块继续焖20分钟至肉烂土豆绵', 22),
  (@r, 7, '试咸淡补盐，开大火收至汤汁浓稠挂肉，撒葱段出锅', 6);

-- ========== 12. 椒麻鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('椒麻鸡', '新疆凉菜的头牌。三黄鸡白煮后浸冰水收紧皮，手撕成条，浇现泼的花椒油、原汤和大量皮牙子，麻香窜鼻，鸡皮脆韧挂汁。', NULL, 25, 35, 90, 2, 4, '西北菜', '凉菜,鸡肉,宴客,新疆名菜', 1, TRUE, 304, 380, 32, 22, 6, '煮鸡用虾眼水浸煮，关火再焖20分钟才嫩；过冰水皮才脆；花椒要现舂，热油分两次泼出麻香才够劲。', '麻香清爽');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '三黄鸡', '1', '只(约1200g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '洋葱', '2', '个', TRUE, 2, '/api/ingredients/yangcong.jpg'),
  (@r, '青辣椒', '2', '个', TRUE, 3, '/api/ingredients/qinglajiao.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '2', '根', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '花椒', '25', 'g', TRUE, 6, '/api/ingredients/huajiao.jpg'),
  (@r, '香菜', '20', 'g', TRUE, 7, '/api/ingredients/xiangcai.jpg'),
  (@r, '大蒜', '20', 'g', FALSE, 8, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '15', 'ml', FALSE, 10, '/api/ingredients/xiangcu.jpg'),
  (@r, '芝麻香油', '20', 'ml', TRUE, 11, '/api/ingredients/xiangyou.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 12, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '8', 'g', TRUE, 13, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '60', 'ml', TRUE, 14, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '2000', 'ml', TRUE, 15, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大锅水烧开，加姜葱料酒和几粒花椒，放入整鸡', 10),
  (@r, 2, '水再次烧开后转微火煮25分钟，关火加盖焖20分钟', 45),
  (@r, 3, '鸡捞出投入冰水浸凉15分钟，收干皮后手撕成条，骨头留汤里', 20),
  (@r, 4, '洋葱切丝，青椒切圈，香菜切段，蒜切末', 8),
  (@r, 5, '花椒舂碎加盐拌匀，热油分两次泼上去激出麻香', 4),
  (@r, 6, '加生抽、香醋、香油、白糖和两勺煮鸡原汤调成椒麻汁', 4),
  (@r, 7, '鸡条和皮牙子青椒拌匀，浇汁腌15分钟入味，装盘撒香菜', 18);

-- ========== 13. 牛奶鸡蛋醪糟 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('牛奶鸡蛋醪糟', '兰州夜市的甜暖。牛奶烧开下甜酒酿，蛋液拉出细丝，撒枸杞红枣和芝麻核桃，蛋花浮在奶白里，甜香带着一点酒气。', NULL, 5, 12, 17, 1, 2, '西北菜', '甜品,夜宵,暖身,兰州小吃', 1, TRUE, 115, 280, 11, 9, 38, '牛奶将开未开时下醪糟，久煮奶腥、酒气全跑；蛋液要细流下锅同时快速搅出丝；干料起锅前才撒，泡久就不脆了。', '奶甜酒香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '牛奶', '500', 'ml', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '甜酒酿', '120', 'g', TRUE, 2, '/api/ingredients/mijiu.jpg'),
  (@r, '鸡蛋', '2', '个', TRUE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '枸杞', '10', 'g', FALSE, 4, '/api/ingredients/gouqi.jpg'),
  (@r, '红枣', '4', '颗', FALSE, 5, '/api/ingredients/hongzao.jpg'),
  (@r, '白糖', '25', 'g', TRUE, 6, '/api/ingredients/baitang.jpg'),
  (@r, '熟芝麻', '8', 'g', FALSE, 7, '/api/ingredients/baizhima.jpg'),
  (@r, '核桃碎', '15', 'g', FALSE, 8, '/api/ingredients/hetaosui.jpg'),
  (@r, '清水', '100', 'ml', TRUE, 9, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '红枣去核切小条，鸡蛋打散成蛋液', 5),
  (@r, 2, '牛奶和清水倒小锅，中火烧至边缘起小泡', 5),
  (@r, 3, '下甜酒酿和白糖煮开，注意别让它扑锅', 3),
  (@r, 4, '转小火，蛋液细流淋入并快速搅出蛋丝', 2),
  (@r, 5, '立刻关火盛碗，撒枸杞、红枣条、芝麻和核桃碎', 2);

-- ========== 14. 兰州灰豆子 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('兰州灰豆子', '黄河边的早点甜汤。小红豆加一点蓬灰慢熬三小时，豆皮熬化在汤里成沙，加红枣和白糖，稠到挂勺，甜香里带一丝碱香。', NULL, 30, 240, 270, 2, 4, '西北菜', '甜品,早餐,豆类,兰州小吃', 1, TRUE, 122, 220, 8, 1, 44, '蓬灰（食用碱）只放一点点，多了发苦；全程小火不糊底，边熬边搅；熬到看不见豆皮、汤色发灰褐才算成。', '豆沙甜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '红豆', '300', 'g', TRUE, 1, '/api/ingredients/xuedou.jpg'),
  (@r, '红枣', '8', '颗', TRUE, 2, '/api/ingredients/hongzao.jpg'),
  (@r, '食用碱', '2', 'g', TRUE, 3, '/api/ingredients/dianfen.jpg'),
  (@r, '白糖', '80', 'g', TRUE, 4, '/api/ingredients/baitang.jpg'),
  (@r, '桂花糖', '15', 'ml', FALSE, 5, '/api/ingredients/guihuatang.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 6, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '红豆挑净洗净，加食用碱和清水泡2小时', 125),
  (@r, 2, '连泡豆水入锅，添足清水大火烧开', 8),
  (@r, 3, '转小火加盖熬2小时，中途常搅防糊底', 125),
  (@r, 4, '下红枣条继续熬40分钟至豆皮化开、汤色转灰褐', 45),
  (@r, 5, '加白糖熬化，试甜度调整', 8),
  (@r, 6, '熬到稠得挂勺、豆子起沙，盛碗可淋少许桂花糖', 8);

-- ========== 15. 葫芦头泡馍 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('葫芦头泡馍', '西安另一碗泡馍。猪大肠反复搓洗到不见腥，配猪骨熬出奶白汤，馍粒同煮，肠软汤浓，浮一层辣子油，糖蒜在边上候着。', NULL, 60, 180, 240, 3, 4, '西北菜', '泡馍,汤饭,小吃,西安名吃', 1, TRUE, 186, 640, 30, 34, 52, '肠要用盐和醋反复搓三遍、翻面去净油，才真不腥；汤要大火冲白；馍掰得比羊肉泡馍稍大一点，吸汤不糊。', '浓汤脂香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪肥肠', '600', 'g', TRUE, 1, '/api/ingredients/zhufeichang.jpg'),
  (@r, '猪筒骨', '500', 'g', TRUE, 2, '/api/ingredients/zhutonggu.jpg'),
  (@r, '带皮五花肉', '200', 'g', FALSE, 3, '/api/ingredients/wuhuarou.jpg'),
  (@r, '中筋面粉', '300', 'g', TRUE, 4, '/api/ingredients/mianfen.jpg'),
  (@r, '红薯粉条', '60', 'g', FALSE, 5, '/api/ingredients/hongshufen.jpg'),
  (@r, '水发木耳', '40', 'g', FALSE, 6, '/api/ingredients/muer.jpg'),
  (@r, '生姜', '40', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '2', '根', TRUE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '25', 'g', FALSE, 9, '/api/ingredients/dasuan.jpg'),
  (@r, '花椒', '20', '粒', TRUE, 10, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '3', '个', FALSE, 11, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '段', FALSE, 12, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '2', '片', FALSE, 13, '/api/ingredients/xiangye.jpg'),
  (@r, '料酒', '40', 'ml', TRUE, 14, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '25', 'ml', FALSE, 15, '/api/ingredients/shengchou.jpg'),
  (@r, '香菜', '20', 'g', FALSE, 16, '/api/ingredients/xiangcai.jpg'),
  (@r, '辣椒油', '20', 'ml', TRUE, 17, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '香醋', '20', 'ml', FALSE, 18, '/api/ingredients/xiangcu.jpg'),
  (@r, '盐', '8', 'g', TRUE, 19, '/api/ingredients/yan.jpg'),
  (@r, '清水', '2500', 'ml', TRUE, 20, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大肠加盐和香醋反复搓洗三遍，翻面刮净油脂，冲净后切段', 25),
  (@r, 2, '肠段冷水下锅加姜葱料酒焯透，捞出再冲一遍', 12),
  (@r, 3, '面粉加盐和清水揉硬面团，醒20分钟，烙成八成熟的死面饼，晾凉掰成稍大的馍粒', 55),
  (@r, 4, '猪骨、五花肉和肠段下大锅，添清水加姜葱，大火烧开撇沫', 20),
  (@r, 5, '下花椒八角桂皮香叶，转中火保持汤面翻滚煮2小时至汤色奶白、肠软', 125),
  (@r, 6, '捞出肠和肉切条，原汤过滤留净', 12),
  (@r, 7, '碗里装馍粒、粉条和木耳，浇一勺滚汤在旺火上煮3分钟，重浇一次汤', 6),
  (@r, 8, '摆肠条肉条，撒葱花香菜，点辣椒油，配糖蒜上桌', 4);
