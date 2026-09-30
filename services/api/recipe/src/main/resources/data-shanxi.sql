-- 由 seed/recipes-shanxi.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 山西菜，共 15 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 大同刀削面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('大同刀削面', '山西面食的头一张名片。面团要和得偏硬、醒得足，用削刀贴着水面把面片一片片削进滚水，中间厚两边薄。卤子备肉臊和番茄鸡蛋两样，出锅沿碗边淋一勺老陈醋。', NULL, 90, 25, 115, 3, 4, '山西菜', '主食,面食,刀削面,山西名菜', 1, TRUE, 289, 620, 26, 18, 92, '面软了削不出形，水要一次加足；削之前刀面沾点水防粘；卤子宁淡勿咸，面汤本身带咸味。', '咸鲜微酸');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '500', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '清水', '200', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '食用碱', '2', 'g', FALSE, 3, '/api/ingredients/dianfen.jpg'),
  (@r, '盐', '4', 'g', TRUE, 4, '/api/ingredients/yan.jpg'),
  (@r, '猪肉末', '200', 'g', TRUE, 5, '/api/ingredients/zhuroumo.jpg'),
  (@r, '西红柿', '300', 'g', TRUE, 6, '/api/ingredients/xihongshi.jpg'),
  (@r, '鸡蛋', '2', '个', TRUE, 7, '/api/ingredients/jidan.jpg'),
  (@r, '水发木耳', '60', 'g', FALSE, 8, '/api/ingredients/muer.jpg'),
  (@r, '蒜薹', '50', 'g', FALSE, 9, '/api/ingredients/suantai.jpg'),
  (@r, '大葱', '1', '根', FALSE, 10, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 11, '/api/ingredients/shengjiang.jpg'),
  (@r, '陈醋', '30', 'ml', TRUE, 12, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '20', 'ml', FALSE, 13, '/api/ingredients/shengchou.jpg'),
  (@r, '辣椒油', '15', 'ml', FALSE, 14, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '淀粉', '15', 'g', FALSE, 15, '/api/ingredients/dianfen.jpg'),
  (@r, '食用油', '50', 'ml', TRUE, 16, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '面粉加盐，食用碱用少量温水化开后倒入，搅成絮状再揉成偏硬面团', 15),
  (@r, 2, '面团盖湿布醒30分钟，中间取出揉两次，直到表面光滑有韧性', 35),
  (@r, 3, '醒好的面揉成下宽上窄的柳叶形面坯，托在左臂上', 5),
  (@r, 4, '肉末用葱姜水打散下锅煸散出油，加生抽和少许清水熬成肉臊子盛出', 12),
  (@r, 5, '热锅炒散鸡蛋盛出，下西红柿炒出红汁，添水烧开后回鸡蛋和木耳，勾薄芡成卤', 15),
  (@r, 6, '大锅水烧至微沸，右手执削刀贴着水面把面片直直削进锅里', 8),
  (@r, 7, '面片全部浮起、中间只剩一点白芯时连汤捞出，分装四碗', 4),
  (@r, 8, '分别浇上肉臊和番茄蛋卤，淋陈醋与辣椒油，撒蒜薹和葱花', 3);

-- ========== 2. 太原过油肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('太原过油肉', '山西宴席上桌的第一道热炒。猪里脊上浆后宽油旺火快滑，配木耳蒜薹，出锅前沿锅边烹入老陈醋，醋香先冲后回，肉片薄而亮。', NULL, 25, 12, 37, 2, 3, '山西菜', '热炒,宴席菜,山西名菜', 1, TRUE, 111, 480, 34, 30, 16, '油温不到六成肉片就下锅，浆会脱；醋分两次放，中途烹一半、出锅前补一半，才留得住醋香。', '咸鲜带醋香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪里脊', '300', 'g', TRUE, 1, '/api/ingredients/zhuliji.jpg'),
  (@r, '鸡蛋清', '1', '个', TRUE, 2, '/api/ingredients/jidanqing.jpg'),
  (@r, '淀粉', '40', 'g', TRUE, 3, '/api/ingredients/dianfen.jpg'),
  (@r, '水发木耳', '80', 'g', TRUE, 4, '/api/ingredients/muer.jpg'),
  (@r, '蒜薹', '60', 'g', TRUE, 5, '/api/ingredients/suantai.jpg'),
  (@r, '大葱', '1', '根', FALSE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '陈醋', '25', 'ml', TRUE, 8, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '5', 'ml', FALSE, 10, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '3', 'g', FALSE, 11, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '4', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '料酒', '15', 'ml', FALSE, 13, '/api/ingredients/liaojiu.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 14, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '里脊剔去筋膜，顶刀切成三分厚的薄片', 10),
  (@r, 2, '肉片加盐、料酒、蛋清和淀粉抓到发黏，最后封一层生油静置', 8),
  (@r, 3, '木耳泡发后撕小朵，蒜薹切段，葱姜切末', 5),
  (@r, 4, '锅中放足量油烧至六成热，下肉片快速划散，一变色立刻倒出沥油', 3),
  (@r, 5, '锅留底油爆香葱姜，下蒜薹和木耳大火翻炒', 2),
  (@r, 6, '沿锅边烹入一半陈醋，回肉片，加生抽老抽和白糖翻匀', 2),
  (@r, 7, '关火前再补剩余陈醋，兜两下装盘', 1);

-- ========== 3. 山西糖醋丸子 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('山西糖醋丸子', '年节席面上孩子最先抢的一道。猪肉牛肉两样肉末搅打上劲，挤成小丸子炸到外壳发脆，再丢进滚烫的糖醋汁里翻匀，酸甜挂得住、咬开还有肉汁。', NULL, 30, 20, 50, 2, 4, '山西菜', '炸物,酸甜,宴席菜,家常', 1, TRUE, 138, 560, 28, 34, 36, '糖醋比例按醋两份糖一份半起步，出锅前补一点醋提香；丸子复炸一次才脆得久。', '酸甜咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪肉末', '300', 'g', TRUE, 1, '/api/ingredients/zhuroumo.jpg'),
  (@r, '牛肉末', '150', 'g', FALSE, 2, '/api/ingredients/niuroumo.jpg'),
  (@r, '鸡蛋', '1', '个', TRUE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '淀粉', '60', 'g', TRUE, 4, '/api/ingredients/dianfen.jpg'),
  (@r, '大葱', '1', '根', FALSE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '陈醋', '60', 'ml', TRUE, 7, '/api/ingredients/xiangcu.jpg'),
  (@r, '白糖', '80', 'g', TRUE, 8, '/api/ingredients/baitang.jpg'),
  (@r, '生抽', '20', 'ml', FALSE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '5', 'ml', FALSE, 10, '/api/ingredients/laochou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 11, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 12, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '清水', '120', 'ml', FALSE, 13, '/api/ingredients/qingshui.jpg'),
  (@r, '白芝麻', '10', 'g', FALSE, 14, '/api/ingredients/baizhima.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 15, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '两样肉末加盐、胡椒粉、蛋清和葱姜末，顺一个方向搅至上劲', 10),
  (@r, 2, '手心沾水，把肉馅挤成核桃大的丸子逐个摆好', 8),
  (@r, 3, '油烧五成热下丸子，定型前别搅动，浮起后炸至浅黄捞出', 6),
  (@r, 4, '油温升到七成热复炸30秒，外壳发脆倒出沥油', 2),
  (@r, 5, '锅留少许底油，下醋、糖、生抽老抽和清水熬至冒大泡转小泡', 4),
  (@r, 6, '倒丸子快速颠锅挂汁，撒芝麻装盘', 2);

-- ========== 4. 平遥牛肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('平遥牛肉', '晋商老号的做法：牛肉只腌盐不腌酱，靠花椒八角提香，老汤慢煮到纤维松而不断，晾凉后逆纹切薄片，干吃下酒都成。', NULL, 40, 220, 260, 2, 6, '山西菜', '卤味,冷盘,山西名菜,下酒', 1, TRUE, 233, 320, 46, 12, 4, '腌够一夜才入味；煮好后别急着捞，在原汤里泡到自然凉，肉才不柴；一定要逆着纹路切。', '咸香回甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '黄牛后腿肉', '1000', 'g', TRUE, 1, '/api/ingredients/niurou.jpg'),
  (@r, '粗盐', '40', 'g', TRUE, 2, '/api/ingredients/yan.jpg'),
  (@r, '花椒', '5', 'g', FALSE, 3, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '3', '个', FALSE, 4, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '5', 'g', FALSE, 5, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '3', '片', FALSE, 6, '/api/ingredients/xiangye.jpg'),
  (@r, '生姜', '20', 'g', FALSE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', FALSE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '30', 'ml', FALSE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '老抽', '15', 'ml', FALSE, 10, '/api/ingredients/laochou.jpg'),
  (@r, '盐', '6', 'g', TRUE, 11, '/api/ingredients/yan.jpg'),
  (@r, '清水', '2000', 'ml', TRUE, 12, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肉顺着纹路切成大块，用竹签扎出密孔便于入味', 10),
  (@r, 2, '粗盐与花椒在干锅里炒至微黄，放凉后反复擦揉肉块表面', 12),
  (@r, 3, '肉块入缸压实，盖好腌一夜，中途翻动一次', 12),
  (@r, 4, '腌好的肉冷水下锅，加料酒烧开撇净血沫后捞出冲洗', 12),
  (@r, 5, '另起清水，下葱姜、八角桂皮香叶和老抽，放肉烧开', 10),
  (@r, 6, '转微火加盖煮2小时至筷子能插透', 125),
  (@r, 7, '加盐再煮20分钟，关火连汤泡至自然凉透', 40),
  (@r, 8, '捞出沥干，逆纹切薄片装盘', 8);

-- ========== 5. 莜面栲栳栳 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('莜面栲栳栳', '晋北燕麦面的看家活。烫好的莜面在掌心推成薄卷，一个个立在笼屉里蒸，蘸酸汤或配羊肉臊子卤，讲究的是面热、卤滚、蒜醋到位。', NULL, 50, 25, 75, 3, 4, '山西菜', '主食,杂粮面点,蒸菜,晋北', 1, TRUE, 218, 470, 22, 14, 66, '莜面必须用滚水烫，凉水和不开；推卷时手沾冷水防粘；蒸的时间别省，欠火发黏。', '咸鲜酸香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '莜面', '300', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '开水', '260', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '盐', '3', 'g', TRUE, 3, '/api/ingredients/yan.jpg'),
  (@r, '羊肉', '150', 'g', TRUE, 4, '/api/ingredients/yangrou.jpg'),
  (@r, '西红柿', '200', 'g', TRUE, 5, '/api/ingredients/xihongshi.jpg'),
  (@r, '土豆', '150', 'g', FALSE, 6, '/api/ingredients/tudou.jpg'),
  (@r, '洋葱', '50', 'g', FALSE, 7, '/api/ingredients/yangcong.jpg'),
  (@r, '大葱', '1', '根', FALSE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 9, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 10, '/api/ingredients/dasuan.jpg'),
  (@r, '陈醋', '30', 'ml', TRUE, 11, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', FALSE, 12, '/api/ingredients/shengchou.jpg'),
  (@r, '辣椒油', '10', 'ml', FALSE, 13, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 14, '/api/ingredients/xiangcai.jpg'),
  (@r, '高汤', '400', 'ml', FALSE, 15, '/api/ingredients/gaotang.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 16, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '莜面加盐，滚水分次倒入边倒边搅成絮状', 6),
  (@r, 2, '稍凉后揉成光滑面团，盖湿布醒10分钟', 12),
  (@r, 3, '取指甲大一团面在掌心推成薄卷，立着码进笼屉', 25),
  (@r, 4, '上汽后大火蒸12分钟至面卷定型', 12),
  (@r, 5, '羊肉切小丁煸炒出油，下葱姜洋葱和土豆丁翻炒', 10),
  (@r, 6, '加西红柿炒出汁，添高汤烧开后转中火炖15分钟成卤', 18),
  (@r, 7, '大蒜捣成泥加凉开水和陈醋调成蒜醋汁', 4),
  (@r, 8, '面卷扣盘，浇羊肉卤，配蒜醋汁和辣椒油，撒香菜', 4);

-- ========== 6. 浑源凉粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('浑源凉粉', '大同浑源县的夏天靠它。土豆淀粉熬成凝冻，切出细条，浇蒜水陈醋和油泼辣子，顶上撒一把炸黄豆和豆腐干，酸辣凉滑，一碗下去暑气全消。', NULL, 30, 15, 45, 2, 4, '山西菜', '凉拌,小吃,夏日,晋北', 1, TRUE, 137, 260, 8, 12, 32, '淀粉和水按一比十，火上一边倒一边搅，熬到起大泡才凝得住；晾透再切，热切就碎。', '酸辣清凉');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '淀粉', '100', 'g', TRUE, 1, '/api/ingredients/dianfen.jpg'),
  (@r, '清水', '1300', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '香干', '100', 'g', FALSE, 3, '/api/ingredients/xianggan.jpg'),
  (@r, '炒黄豆', '50', 'g', FALSE, 4, '/api/ingredients/huangdou.jpg'),
  (@r, '辣椒油', '25', 'ml', TRUE, 5, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '陈醋', '30', 'ml', TRUE, 6, '/api/ingredients/xiangcu.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '15', 'ml', FALSE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '5', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '白糖', '3', 'g', FALSE, 10, '/api/ingredients/baitang.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 11, '/api/ingredients/xiangcai.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '淀粉用100毫升清水调开至无颗粒', 4),
  (@r, 2, '其余清水烧开，转小火边倒淀粉浆边搅，熬至透明起大泡', 12),
  (@r, 3, '倒入抹过凉水的盆中摊平，室温晾凉后静置凝固', 90),
  (@r, 4, '凝固的凉粉扣出，切成细条码碗', 8),
  (@r, 5, '大蒜捣泥加少许凉开水泡成蒜水', 4),
  (@r, 6, '凉粉上浇蒜水、陈醋、生抽和盐糖，挖一勺辣椒油', 3),
  (@r, 7, '撒香干丁、炸黄豆和香菜，吃前拌匀', 3);

-- ========== 7. 大同羊杂割 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('大同羊杂割', '晋北冬天的早市顶流。羊骨熬出白汤，羊肚羊肺羊肝切丝回锅，滚汤冲进口粉丝的碗里，重胡椒重辣子，配一个烤饼才算齐整。', NULL, 40, 100, 140, 2, 4, '山西菜', '汤羹,羊杂,冬日,晋北', 1, TRUE, 88, 380, 28, 22, 18, '羊杂要反复焯洗去，粉丝先用热水泡软；胡椒粉下锅前放，冲汤时香气才出来。', '咸鲜辛辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '羊杂', '400', 'g', TRUE, 1, '/api/ingredients/shuzhudu.jpg'),
  (@r, '羊骨', '500', 'g', TRUE, 2, '/api/ingredients/yangrou.jpg'),
  (@r, '清水', '2000', 'ml', TRUE, 3, '/api/ingredients/qingshui.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', FALSE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '20', 'ml', FALSE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '粉丝', '60', 'g', TRUE, 7, '/api/ingredients/hongshufen.jpg'),
  (@r, '盐', '6', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '3', 'g', TRUE, 9, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '花椒粉', '2', 'g', FALSE, 10, '/api/ingredients/huajiaofen.jpg'),
  (@r, '香菜', '10', 'g', TRUE, 11, '/api/ingredients/xiangcai.jpg'),
  (@r, '蒜苗', '20', 'g', FALSE, 12, '/api/ingredients/qingsuan.jpg'),
  (@r, '辣椒油', '15', 'ml', FALSE, 13, '/api/ingredients/lajiaoyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '羊骨冷水下锅烧开撇沫，加姜片转微火熬90分钟成白汤', 100),
  (@r, 2, '羊杂加料酒单独焯水两次，冲净后切细丝', 15),
  (@r, 3, '粉丝用热水泡软，香菜蒜苗切末', 6),
  (@r, 4, '汤锅烧滚，下羊杂丝煮2分钟至透', 3),
  (@r, 5, '碗底放粉丝和盐、胡椒粉、花椒粉，冲入滚汤', 3),
  (@r, 6, '捞羊杂铺面，撒香菜蒜苗，淋辣椒油', 2);

-- ========== 8. 忻州蒸肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('忻州蒸肉', '忻州人待客的一道蒸菜，名字里有肉其实一半是土豆。五花肉片和厚土豆块拌上五香粉与玉米面，笼里蒸到油渗进面、面吸住肉香。', NULL, 40, 60, 100, 2, 4, '山西菜', '蒸菜,杂粮,家常,晋北', 1, TRUE, 130, 640, 26, 40, 44, '玉米面别放多，多了发干；土豆切厚块才耐蒸；蒸够一小时肥肉才化，中途别开盖。', '五香醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '400', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '土豆', '400', 'g', TRUE, 2, '/api/ingredients/tudou.jpg'),
  (@r, '玉米面', '80', 'g', TRUE, 3, '/api/ingredients/mianfen.jpg'),
  (@r, '面粉', '60', 'g', FALSE, 4, '/api/ingredients/mianfen.jpg'),
  (@r, '鸡蛋', '1', '个', FALSE, 5, '/api/ingredients/jidan.jpg'),
  (@r, '老抽', '10', 'ml', FALSE, 6, '/api/ingredients/laochou.jpg'),
  (@r, '生抽', '15', 'ml', FALSE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '五香粉', '3', 'g', TRUE, 8, '/api/ingredients/bajiao.jpg'),
  (@r, '盐', '5', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 10, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', FALSE, 11, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '15', 'ml', FALSE, 12, '/api/ingredients/liaojiu.jpg'),
  (@r, '清水', '150', 'ml', FALSE, 13, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '20', 'ml', FALSE, 14, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉带皮切成一指厚的片，加生抽老抽料酒和五香粉拌匀腌20分钟', 25),
  (@r, 2, '土豆去皮切厚块，与腌肉和剩余汁水拌在一起', 8),
  (@r, 3, '玉米面和面粉加盐、鸡蛋和清水调成能挂住的稠糊', 8),
  (@r, 4, '肉和土豆逐个裹上糊，皮朝下码进抹油的盆里', 10),
  (@r, 5, '上汽后大火蒸60分钟，中途不开盖', 60),
  (@r, 6, '取出扣在盘中，撒葱花淋少许热油', 3);

-- ========== 9. 太原什锦火锅 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('太原什锦火锅', '山西人过年桌上那只紫铜锅。排骨垫底，丸子、炸皮、白菜、木耳、粉丝一层层码整齐，浇高汤点炭慢煨，边吃边下，汤越滚越鲜。', NULL, 40, 45, 85, 2, 6, '山西菜', '火锅,宴席菜,冬日,家常', 1, TRUE, 145, 520, 34, 30, 26, '料要分层码，耐煮的垫底、易烂的浮面；汤一次添到八分满，中途只续开水；蘸料用韭菜花加腐乳。', '咸鲜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪排骨', '300', 'g', TRUE, 1, '/api/ingredients/zhupaigu.jpg'),
  (@r, '五花肉', '150', 'g', FALSE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '猪肉丸', '150', 'g', TRUE, 3, '/api/ingredients/zhuroumo.jpg'),
  (@r, '炸猪皮', '80', 'g', FALSE, 4, '/api/ingredients/wuhuarou.jpg'),
  (@r, '大白菜', '400', 'g', TRUE, 5, '/api/ingredients/baicai.jpg'),
  (@r, '水发木耳', '60', 'g', FALSE, 6, '/api/ingredients/muer.jpg'),
  (@r, '粉丝', '60', 'g', TRUE, 7, '/api/ingredients/hongshufen.jpg'),
  (@r, '干香菇', '30', 'g', FALSE, 8, '/api/ingredients/ganxianggu.jpg'),
  (@r, '胡萝卜', '100', 'g', FALSE, 9, '/api/ingredients/huluobo.jpg'),
  (@r, '鸡蛋', '2', '个', FALSE, 10, '/api/ingredients/jidan.jpg'),
  (@r, '大葱', '1', '根', FALSE, 11, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '20', 'g', FALSE, 12, '/api/ingredients/shengjiang.jpg'),
  (@r, '老抽', '10', 'ml', FALSE, 13, '/api/ingredients/laochou.jpg'),
  (@r, '生抽', '25', 'ml', FALSE, 14, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '6', 'g', TRUE, 15, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '3', 'g', FALSE, 16, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '高汤', '1500', 'ml', TRUE, 17, '/api/ingredients/gaotang.jpg'),
  (@r, '食用油', '30', 'ml', FALSE, 18, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '排骨斩段焯水，五花肉切厚片，干香菇温水泡发', 18),
  (@r, 2, '炸猪皮泡软切块，粉丝泡软剪段，大白菜帮叶分开', 12),
  (@r, 3, '鸡蛋摊成蛋皮切菱形片，胡萝卜切花片', 8),
  (@r, 4, '热油下葱姜，排骨和五花肉片翻炒至微黄，加生抽老抽上色', 8),
  (@r, 5, '火锅底层铺白菜帮，码上排骨、肉片、香菇和木耳', 8),
  (@r, 6, '中层摆肉丸、炸皮和胡萝卜，上面覆白菜叶和蛋皮', 6),
  (@r, 7, '冲入热高汤至八分满，加盐和胡椒粉，点炭烧开', 15),
  (@r, 8, '汤滚后再下粉丝，边煨边吃，只续开水', 10);

-- ========== 10. 山西大烩菜 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('山西大烩菜', '冬天最实在的一锅乱炖。白菜、土豆、粉条、豆腐和肉片同烩，勾一点酱油上色，烩到汤汁收浓、粉条吸干味，配馒头或泡饭都对。', NULL, 25, 30, 55, 1, 4, '山西菜', '炖菜,家常,冬日,下饭', 1, TRUE, 174, 460, 22, 22, 46, '粉条后放才不糊汤；白菜帮先炒软再合锅；喜欢酸口可以沿锅边烹一勺醋。', '咸鲜家常');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大白菜', '500', 'g', TRUE, 1, '/api/ingredients/baicai.jpg'),
  (@r, '带皮五花肉', '200', 'g', TRUE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '土豆', '300', 'g', TRUE, 3, '/api/ingredients/tudou.jpg'),
  (@r, '红薯粉条', '100', 'g', TRUE, 4, '/api/ingredients/hongshufen.jpg'),
  (@r, '豆腐', '200', 'g', TRUE, 5, '/api/ingredients/doufu.jpg'),
  (@r, '猪肉丸', '100', 'g', FALSE, 6, '/api/ingredients/zhuroumo.jpg'),
  (@r, '干香菇', '20', 'g', FALSE, 7, '/api/ingredients/ganxianggu.jpg'),
  (@r, '水发木耳', '50', 'g', FALSE, 8, '/api/ingredients/muer.jpg'),
  (@r, '大葱', '1', '根', FALSE, 9, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 10, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 11, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', FALSE, 12, '/api/ingredients/laochou.jpg'),
  (@r, '盐', '5', 'g', TRUE, 13, '/api/ingredients/yan.jpg'),
  (@r, '五香粉', '2', 'g', FALSE, 14, '/api/ingredients/bajiao.jpg'),
  (@r, '清水', '800', 'ml', TRUE, 15, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 16, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '粉条温水泡软剪段，香菇泡发切条，白菜帮叶分开切块', 12),
  (@r, 2, '豆腐切厚片，下锅煎至两面微黄盛出', 8),
  (@r, 3, '五花肉切片，下锅煸出油，加葱姜和五香粉炒香', 6),
  (@r, 4, '下白菜帮和土豆块炒至白菜变软', 6),
  (@r, 5, '加生抽老抽和香菇木耳，添清水烧开', 5),
  (@r, 6, '转中火加盖烩15分钟至土豆将熟', 15),
  (@r, 7, '下粉条、豆腐和肉丸再烩8分钟，汤汁收浓后补盐', 8),
  (@r, 8, '撒葱花连锅端上桌', 2);

-- ========== 11. 土豆擦尖 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('土豆擦尖', '晋中把土豆变成主食的做法：蒸熟的土豆压泥和进面粉，用擦床擦成两头尖的短条，煮到滑亮，浇西红柿肉末卤，是夏天的一碗凉快饭。', NULL, 50, 25, 75, 3, 3, '山西菜', '主食,面食,家常,晋中', 1, TRUE, 148, 430, 15, 12, 68, '土豆泥必须放凉再和面，热面和成黏糊；擦的时候一次少放，条才均匀。', '咸鲜微酸');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '土豆', '500', 'g', TRUE, 1, '/api/ingredients/tudou.jpg'),
  (@r, '面粉', '150', 'g', TRUE, 2, '/api/ingredients/mianfen.jpg'),
  (@r, '鸡蛋', '1', '个', FALSE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '盐', '4', 'g', TRUE, 4, '/api/ingredients/yan.jpg'),
  (@r, '猪肉末', '150', 'g', TRUE, 5, '/api/ingredients/zhuroumo.jpg'),
  (@r, '西红柿', '250', 'g', TRUE, 6, '/api/ingredients/xihongshi.jpg'),
  (@r, '蒜薹', '50', 'g', FALSE, 7, '/api/ingredients/suantai.jpg'),
  (@r, '大葱', '1', '根', FALSE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 9, '/api/ingredients/shengjiang.jpg'),
  (@r, '陈醋', '20', 'ml', FALSE, 10, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', FALSE, 11, '/api/ingredients/shengchou.jpg'),
  (@r, '淀粉', '10', 'g', FALSE, 12, '/api/ingredients/dianfen.jpg'),
  (@r, '清水', '800', 'ml', FALSE, 13, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 14, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '土豆去皮蒸熟，压成细泥放凉', 25),
  (@r, 2, '土豆泥加面粉、鸡蛋和盐揉成软面团', 8),
  (@r, 3, '面团分次上擦床，擦成两头尖的短条，撒干面粉防粘', 15),
  (@r, 4, '肉末炒散，下葱姜和西红柿炒出红汁', 8),
  (@r, 5, '添清水烧开，加生抽和少许盐熬成卤，勾薄芡', 10),
  (@r, 6, '另一锅水烧开，下擦尖煮2分钟至全部浮起捞出', 4),
  (@r, 7, '浇卤，撒蒜薹，沿碗边淋陈醋', 2);

-- ========== 12. 太原剔尖 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('太原剔尖', '和软面、摔出筋，用筷子贴着锅边一根根剔进滚水，条两头薄中间厚，比削面更滑。卤是打好的四合头荤卤，一碗面配一碟蒜和醋。', NULL, 60, 25, 85, 3, 4, '山西菜', '主食,面食,山西名菜', 1, TRUE, 209, 540, 22, 16, 80, '面要和到能用筷子挑起不断、抖得动；剔时左手托板右手双筷，手腕要活；卤要留汤，不然挂不住面。', '咸鲜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '400', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '鸡蛋', '2', '个', TRUE, 2, '/api/ingredients/jidan.jpg'),
  (@r, '温水', '220', 'ml', TRUE, 3, '/api/ingredients/qingshui.jpg'),
  (@r, '盐', '3', 'g', TRUE, 4, '/api/ingredients/yan.jpg'),
  (@r, '食用碱', '1', 'g', FALSE, 5, '/api/ingredients/dianfen.jpg'),
  (@r, '猪肉末', '150', 'g', TRUE, 6, '/api/ingredients/zhuroumo.jpg'),
  (@r, '干香菇', '20', 'g', FALSE, 7, '/api/ingredients/ganxianggu.jpg'),
  (@r, '水发木耳', '60', 'g', FALSE, 8, '/api/ingredients/muer.jpg'),
  (@r, '胡萝卜', '100', 'g', FALSE, 9, '/api/ingredients/huluobo.jpg'),
  (@r, '蒜薹', '60', 'g', FALSE, 10, '/api/ingredients/suantai.jpg'),
  (@r, '大葱', '1', '根', FALSE, 11, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 12, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 13, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '8', 'ml', FALSE, 14, '/api/ingredients/laochou.jpg'),
  (@r, '陈醋', '20', 'ml', FALSE, 15, '/api/ingredients/xiangcu.jpg'),
  (@r, '淀粉', '15', 'g', FALSE, 16, '/api/ingredients/dianfen.jpg'),
  (@r, '高汤', '300', 'ml', FALSE, 17, '/api/ingredients/gaotang.jpg'),
  (@r, '食用油', '50', 'ml', TRUE, 18, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '面粉加盐、鸡蛋和温水搅成软面团，加少许碱水反复摔打至起筋', 20),
  (@r, 2, '盖湿布醒20分钟，再摔打一次至面团光滑有弹性', 22),
  (@r, 3, '干香菇泡发切丝，木耳胡萝卜切丝，蒜薹切段', 10),
  (@r, 4, '肉末炒散，下葱姜和丝料翻炒，加生抽老抽和高汤烧开', 10),
  (@r, 5, '转小火煮5分钟，勾薄芡成带汤的卤', 6),
  (@r, 6, '面团置于托板上，右手双筷贴着滚锅边把面一根根剔进水里', 8),
  (@r, 7, '面全部浮起、无白芯后捞出装碗', 4),
  (@r, 8, '浇卤，配陈醋蒜瓣和辣椒油拌匀', 2);

-- ========== 13. 高平烧大葱 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('高平烧大葱', '晋城高平的待客硬菜，看着是一盘葱，吃起来比肉香。葱白去皮切段裹糊炸定型，再和肉末一起用糖醋汁烧到软透，甜里带酸。', NULL, 25, 20, 45, 2, 4, '山西菜', '热炒,素菜荤做,晋城', 1, TRUE, 294, 340, 14, 22, 24, '选本地的大葱，葱白要够长够粗；炸只到微黄，炸深了发苦；烧的时候小火，葱才烂得透。', '甜酸微咸');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大葱', '400', 'g', TRUE, 1, '/api/ingredients/dacong.jpg'),
  (@r, '猪肉末', '100', 'g', TRUE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '鸡蛋', '2', '个', TRUE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '面粉', '60', 'g', TRUE, 4, '/api/ingredients/mianfen.jpg'),
  (@r, '淀粉', '30', 'g', FALSE, 5, '/api/ingredients/dianfen.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '8', 'ml', FALSE, 7, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '15', 'g', TRUE, 8, '/api/ingredients/baitang.jpg'),
  (@r, '陈醋', '12', 'ml', FALSE, 9, '/api/ingredients/xiangcu.jpg'),
  (@r, '盐', '4', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 11, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 12, '/api/ingredients/shengjiang.jpg'),
  (@r, '清水', '150', 'ml', FALSE, 13, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 14, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大葱去外皮只留葱白，切10厘米段后一剖为四', 10),
  (@r, 2, '鸡蛋、面粉、淀粉加少许清水和盐调成稠糊', 6),
  (@r, 3, '葱段裹匀糊，油烧六成热下锅炸至微黄定型捞出', 8),
  (@r, 4, '肉末加姜末炒散，下生抽翻匀', 4),
  (@r, 5, '下葱段，添清水、白糖和老抽，小火加盖烧5分钟', 7),
  (@r, 6, '转大火收汁，出锅前烹陈醋，撒胡椒粉装盘', 3);

-- ========== 14. 糖醋黄河鲤鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('糖醋黄河鲤鱼', '沿黄河一带的席面大菜。鲤鱼剞花刀后炸到鱼鳍支起、外皮硬挺，趁热浇上翻滚的糖醋汁，吱啦一声上桌，讲究形不散、汁红亮。', NULL, 30, 20, 50, 3, 4, '山西菜', '河鲜,宴席菜,酸甜,造型菜', 1, TRUE, 138, 520, 42, 26, 28, '花刀要剞到鱼骨，炸时才翻得开；油温七成一次下锅别翻动；汁熬到挂勺、浇下去立刻吱啦作响才算到位。', '酸甜鲜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鲤鱼', '750', 'g', TRUE, 1, '/api/ingredients/caoyu.jpg'),
  (@r, '淀粉', '80', 'g', TRUE, 2, '/api/ingredients/dianfen.jpg'),
  (@r, '鸡蛋', '1', '个', FALSE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '陈醋', '60', 'ml', TRUE, 4, '/api/ingredients/xiangcu.jpg'),
  (@r, '白糖', '70', 'g', TRUE, 5, '/api/ingredients/baitang.jpg'),
  (@r, '生抽', '20', 'ml', FALSE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '8', 'ml', FALSE, 7, '/api/ingredients/laochou.jpg'),
  (@r, '盐', '5', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '大葱', '1', '根', FALSE, 10, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 11, '/api/ingredients/shengjiang.jpg'),
  (@r, '青豆', '30', 'g', FALSE, 12, '/api/ingredients/wandoujian.jpg'),
  (@r, '清水', '120', 'ml', FALSE, 13, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 14, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鲤鱼去鳞鳃和内脏，两面坡刀剞花刀至骨，间隔一指', 12),
  (@r, 2, '用盐、料酒和葱姜里外抹匀，腌20分钟', 22),
  (@r, 3, '拣去葱姜，刀口和鱼身内外拍干淀粉', 6),
  (@r, 4, '油烧七成热，手提鱼尾先炸鱼头，再整条下锅，不断浇热油使花刀翻开', 8),
  (@r, 5, '炸至硬挺金黄后翻面，熟透捞出摆盘', 6),
  (@r, 6, '锅留底油下葱姜末，加清水、白糖、陈醋和生抽熬至浓稠挂勺', 5),
  (@r, 7, '淋一勺热油使汁红亮，趁热浇在鱼身上，点缀青豆', 2);

-- ========== 15. 太谷饼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('太谷饼', '晋商带出门的干粮，也是晋中人的早点。软面按成厚饼，刷蜂蜜水沾满芝麻，烤到外皮一按就回弹，晾一夜之后绵软耐嚼，配砖茶正好。', NULL, 50, 20, 70, 2, 8, '山西菜', '点心,烘焙,山西名产,干粮', 1, TRUE, 198, 300, 5, 12, 42, '面和得偏软，硬了烤出来发板；蜂蜜水别刷厚，否则芝麻掉；烤好回潮一夜才绵。', '甜香绵软');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '300', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '白糖', '100', 'g', TRUE, 2, '/api/ingredients/baitang.jpg'),
  (@r, '食用油', '80', 'ml', TRUE, 3, '/api/ingredients/shiyongyou.jpg'),
  (@r, '温水', '120', 'ml', TRUE, 4, '/api/ingredients/qingshui.jpg'),
  (@r, '鸡蛋', '1', '个', TRUE, 5, '/api/ingredients/jidan.jpg'),
  (@r, '麦芽糖', '20', 'g', FALSE, 6, '/api/ingredients/mayatang.jpg'),
  (@r, '白芝麻', '40', 'g', TRUE, 7, '/api/ingredients/baizhima.jpg'),
  (@r, '小苏打', '2', 'g', FALSE, 8, '/api/ingredients/dianfen.jpg'),
  (@r, '盐', '2', 'g', FALSE, 9, '/api/ingredients/yan.jpg'),
  (@r, '蜂蜜', '20', 'g', FALSE, 10, '/api/ingredients/mayatang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '白糖、油、温水、鸡蛋和麦芽糖搅至糖半化', 6),
  (@r, 2, '加面粉、小苏打和盐揉成软面团，盖布醒30分钟', 38),
  (@r, 3, '面团分八份剂子，按成两厘米厚的圆饼', 8),
  (@r, 4, '饼面刷蜂蜜水，撒白芝麻轻压粘牢', 6),
  (@r, 5, '炉温180度烤18分钟，至表面金黄、按下去能回弹', 20),
  (@r, 6, '晾凉后装罐回潮一夜再吃', 12);
