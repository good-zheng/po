-- 由 seed/recipes-hubei.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 湖北菜，共 15 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 莲藕排骨汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('莲藕排骨汤', '湖北人煨汤的头一样。洪湖九孔藕粉糯，配猪肋排在砂罐里煨两小时，汤色微红、藕块拉丝，只下姜片和一撮盐，喝完汤再捞藕吃。', NULL, 15, 120, 135, 1, 4, '湖北菜', '汤羹,煨汤,家常,湖北名菜', 1, TRUE, 152, 430, 26, 24, 22, '煨汤要挑粉藕（表皮偏黄、七孔九孔那种），脆藕煸不糯；水一次加足中途不添；盐最后放，早放肉柴。', '清甜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '莲藕', '500', 'g', TRUE, 1, '/api/ingredients/ou.jpg'),
  (@r, '猪排骨', '500', 'g', TRUE, 2, '/api/ingredients/zhupaigu.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', FALSE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '20', 'ml', FALSE, 5, '/api/ingredients/liaojiu.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 6, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '盐', '5', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '清水', '2000', 'ml', TRUE, 8, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '排骨斩段冷水下锅，加姜片料酒烧开撇净血沫，捞出冲净', 15),
  (@r, 2, '莲藕去皮切滚刀块，立刻泡进清水里防黑', 10),
  (@r, 3, '砂罐一次添足清水，下排骨和姜片大火烧开', 10),
  (@r, 4, '转微火加盖煨60分钟', 62),
  (@r, 5, '下藕块继续煨45分钟至藕色转红、筷子能插透', 48),
  (@r, 6, '加盐和少许白胡椒粉调味，撒葱花端罐上桌', 4);

-- ========== 2. 清蒸武昌鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('清蒸武昌鱼', '「才饮长沙水，又食武昌鱼」。樊口鳊鱼两面剞刀，铺上火腿丝、香菇丝和冬笋丝旺火蒸十分钟，倒掉腥水再淋蒸鱼豉油与热油，肉细刺少。', NULL, 20, 15, 35, 2, 4, '湖北菜', '清蒸,河鲜,宴客,湖北名菜', 1, TRUE, 171, 260, 34, 10, 6, '鱼要现杀现蒸，蒸锅水大开再下鱼；七两到一斤的鱼蒸八到十分钟；蒸出的腥水一定要倒掉再淋豉油。', '清鲜本味');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鳊鱼', '1', '条(约700g)', TRUE, 1, '/api/ingredients/bianyu.jpg'),
  (@r, '火腿', '40', 'g', TRUE, 2, '/api/ingredients/huotui.jpg'),
  (@r, '干香菇', '20', 'g', FALSE, 3, '/api/ingredients/ganxianggu.jpg'),
  (@r, '冬笋', '80', 'g', FALSE, 4, '/api/ingredients/dongsun.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '小葱', '2', '根', TRUE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '料酒', '25', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '蒸鱼豉油', '30', 'ml', TRUE, 9, '/api/ingredients/zhengyuchichou.jpg'),
  (@r, '白糖', '3', 'g', FALSE, 10, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '4', 'g', TRUE, 11, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '25', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鱼去鳞鳃内脏洗净，两面各剞三刀，用盐和料酒里外抹匀腌10分钟', 12),
  (@r, 2, '火腿、冬笋、泡发的香菇和姜全部切细丝，小葱打结', 10),
  (@r, 3, '盘底垫姜片和葱结，鱼摆上，表面铺三色丝', 5),
  (@r, 4, '蒸锅水烧开后入鱼，旺火蒸8至10分钟', 10),
  (@r, 5, '取出拣去葱结，把盘里的腥水倒干净', 3),
  (@r, 6, '淋蒸鱼豉油和少许白糖，另起一勺滚油浇在鱼身上激香', 3);

-- ========== 3. 热干面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('热干面', '武汉的早晨从一碗面开始。碱面煮到八成熟摊凉拌油，吃前滚汤里烫十秒，浇油泄的芝麻酱、生抽和卤水，撒酸豆角萝卜丁与葱花，拌匀了根根挂酱。', NULL, 30, 10, 40, 2, 3, '湖北菜', '面食,早餐,小吃,武汉名吃', 1, TRUE, 151, 520, 16, 22, 62, '面煮到八成熟就要摊凉拌油扇凉，隔一夜再烫才筋道；芝麻酱必须用油泄，加水泄会泻汤发澥。', '麻酱咸香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '碱水面', '400', 'g', TRUE, 1, '/api/ingredients/jianshuimian.jpg'),
  (@r, '芝麻酱', '50', 'g', TRUE, 2, '/api/ingredients/zhimajiang.jpg'),
  (@r, '酸豆角', '50', 'g', TRUE, 3, '/api/ingredients/suandoujiao.jpg'),
  (@r, '萝卜干', '40', 'g', TRUE, 4, '/api/ingredients/luobogan.jpg'),
  (@r, '卤水汁', '20', 'ml', FALSE, 5, '/api/ingredients/lushui.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', FALSE, 7, '/api/ingredients/laochou.jpg'),
  (@r, '小葱', '20', 'g', TRUE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '辣椒油', '15', 'ml', FALSE, 9, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '芝麻香油', '15', 'ml', FALSE, 10, '/api/ingredients/xiangyou.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 11, '/api/ingredients/baitang.jpg'),
  (@r, '熟芝麻', '10', 'g', FALSE, 12, '/api/ingredients/baizhima.jpg'),
  (@r, '盐', '3', 'g', TRUE, 13, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '25', 'ml', TRUE, 14, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '芝麻酱分次加香油和少许凉开水，顺一个方向泄成能流动的稀酱', 8),
  (@r, 2, '酸豆角和萝卜干切小丁，小葱切葱花', 6),
  (@r, 3, '水烧开下碱面，煮到八成熟（芯刚软）立刻捞出', 4),
  (@r, 4, '面摊开淋食用油，边扇边挑散晾凉，防粘并收干表面水分', 8),
  (@r, 5, '吃前把面入滚水烫10秒捞起甩干装碗', 2),
  (@r, 6, '依次浇芝麻酱、生抽、老抽和卤水', 3),
  (@r, 7, '撒酸豆角、萝卜丁、葱花和熟芝麻，按口味点辣椒油，拌到根挂酱', 3);

-- ========== 4. 沔阳三蒸 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('沔阳三蒸', '沔阳「三蒸九扣」的头席。肉、菜分笼裹上炒过的粘米粉蒸，米粉吃透水、肉片糯而不腻，南瓜垫底吸足荤油，蒸笼一揭满屋粉香。', NULL, 40, 60, 100, 2, 4, '湖北菜', '蒸菜,米粉,宴客,湖北名菜', 1, TRUE, 275, 560, 26, 32, 40, '米粉要用炒至微黄的粘米粉，拌好后静置半小时让粉吃透肉汁；蒸中途洒两次高汤，粉才不会夹生。', '粉糯咸香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '400', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '粘米粉', '120', 'g', TRUE, 2, '/api/ingredients/zhanmifen.jpg'),
  (@r, '老南瓜', '400', 'g', TRUE, 3, '/api/ingredients/nangua.jpg'),
  (@r, '土豆', '200', 'g', FALSE, 4, '/api/ingredients/tudou.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '20', 'g', FALSE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '郫县豆瓣酱', '15', 'g', FALSE, 8, '/api/ingredients/pixianjiang.jpg'),
  (@r, '生抽', '35', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '15', 'ml', TRUE, 10, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '25', 'ml', TRUE, 11, '/api/ingredients/liaojiu.jpg'),
  (@r, '白糖', '10', 'g', FALSE, 12, '/api/ingredients/baitang.jpg'),
  (@r, '五香粉', '3', 'g', TRUE, 13, '/api/ingredients/bajiao.jpg'),
  (@r, '干荷叶', '2', '张', FALSE, 14, '/api/ingredients/ganye.jpg'),
  (@r, '高汤', '200', 'ml', TRUE, 15, '/api/ingredients/gaotang.jpg'),
  (@r, '盐', '4', 'g', TRUE, 16, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '干锅下粘米粉小火炒至微黄出香，盛出晾凉', 8),
  (@r, 2, '五花肉切薄片，南瓜和土豆切块，姜末葱花蒜末备好', 15),
  (@r, 3, '肉片加生抽老抽料酒白糖五香粉姜末和豆瓣酱抓匀，腌20分钟', 22),
  (@r, 4, '倒进米粉翻拌，让每片都裹上厚厚一层，再静置30分钟回水', 32),
  (@r, 5, '南瓜块和土豆块拌少许盐与米粉，垫在蒸笼底', 8),
  (@r, 6, '肉片皮朝下码在菜上，荷叶盖面，旺火上汽蒸50分钟', 52),
  (@r, 7, '中途开盖两次沿边洒高汤，让粉吃足水', 6),
  (@r, 8, '蒸到肉烂粉糯、南瓜成泥，扣入大盘撒葱花', 6);

-- ========== 5. 珍珠圆子 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('珍珠圆子', '泡透的糯米裹在肉丸外，蒸熟后颗颗晶莹如珍珠，咬开是打足水的嫩猪肉馅，底下垫南瓜吸汁，湖北年席上甜咸交界的那一口。', NULL, 40, 25, 245, 2, 4, '湖北菜', '蒸菜,丸子,年菜,湖北名菜', 1, TRUE, 298, 430, 22, 14, 55, '糯米要提前泡足3小时才蒸得透亮；肉馅分次打水朝一个方向搅上劲才嫩；米沥干再滚裹，裹匀不露馅。', '清鲜弹嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '糯米', '150', 'g', TRUE, 1, '/api/ingredients/nuomi.jpg'),
  (@r, '猪前腿肉馅', '300', 'g', TRUE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '老南瓜', '400', 'g', FALSE, 3, '/api/ingredients/nangua.jpg'),
  (@r, '鸡蛋', '1', '个', TRUE, 4, '/api/ingredients/jidan.jpg'),
  (@r, '淀粉', '25', 'g', TRUE, 5, '/api/ingredients/dianfen.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 7, '/api/ingredients/dacong.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 10, '/api/ingredients/baitang.jpg'),
  (@r, '高汤', '120', 'ml', FALSE, 11, '/api/ingredients/gaotang.jpg'),
  (@r, '盐', '4', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '清水', '400', 'ml', TRUE, 13, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '糯米淘净加清水泡3小时，捞出沥干至不沾手', 185),
  (@r, 2, '姜葱切末泡水成葱姜水；肉馅加盐生抽料酒和葱姜水，分三次打入并顺一个方向搅上劲', 15),
  (@r, 3, '拌入鸡蛋和淀粉继续搅到起胶，静置10分钟', 12),
  (@r, 4, '肉馅挤成核桃大的丸子，放进糯米里滚裹一层，手掌轻搓收口', 12),
  (@r, 5, '南瓜切厚片铺蒸盘，丸子上留空隙摆开', 8),
  (@r, 6, '上汽后中火蒸25分钟，至糯米透明、丸子鼓胀', 26),
  (@r, 7, '高汤加少许盐和淀粉勾薄芡淋面，撒葱花', 4);

-- ========== 6. 潜江油焖小龙虾 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('潜江油焖小龙虾', '潜江虾清水吐净再刷洗，剪头去虾线，高温炸红后配干辣椒花椒姜蒜焖烧，啤酒代水收汁。虾壳入味、虾肉弹甜，最后那盆红汤要拌一碗面。', NULL, 40, 25, 65, 2, 4, '湖北菜', '河鲜,辣,夜宵,潜江名菜', 1, TRUE, 107, 320, 30, 16, 8, '虾要刷净鳃和腹部、抽掉虾线；先高温炸一遍壳才红亮入味；焖的时间别长，超过十分钟虾肉就老。', '麻辣酱香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '小龙虾', '1500', 'g', TRUE, 1, '/api/ingredients/xiaolongxia.jpg'),
  (@r, '啤酒', '330', 'ml', TRUE, 2, '/api/ingredients/pijiu.jpg'),
  (@r, '干辣椒', '25', 'g', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '15', '粒', TRUE, 4, '/api/ingredients/huajiao.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '40', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '大葱', '1', '根', TRUE, 7, '/api/ingredients/dacong.jpg'),
  (@r, '香叶', '2', '片', FALSE, 8, '/api/ingredients/xiangye.jpg'),
  (@r, '八角', '2', '个', FALSE, 9, '/api/ingredients/bajiao.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '15', 'ml', TRUE, 11, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '15', 'g', FALSE, 12, '/api/ingredients/baitang.jpg'),
  (@r, '五香粉', '3', 'g', FALSE, 13, '/api/ingredients/bajiao.jpg'),
  (@r, '盐', '5', 'g', TRUE, 14, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '120', 'ml', TRUE, 15, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '300', 'ml', TRUE, 16, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '小龙虾刷净腹部和鳃，掐尾抽出虾线，剪去虾枪再冲两遍', 25),
  (@r, 2, '姜切片、蒜拍碎、葱切段、干辣椒切段', 8),
  (@r, 3, '宽油烧至八成热，虾下锅炸30秒至壳红硬立刻捞出', 3),
  (@r, 4, '锅留底油，小火炸香花椒干辣椒八角香叶', 4),
  (@r, 5, '下姜蒜葱段炒出香味，加生抽老抽白糖五香粉翻匀', 4),
  (@r, 6, '虾回锅颠匀，倒入啤酒和清水没过一半虾身', 4),
  (@r, 7, '加盖中火焖8分钟，中途翻一次让上层的虾也吃到汁', 9),
  (@r, 8, '开大火收至汤汁浓红挂壳，试咸淡补盐，装盆带汤上桌', 5);

-- ========== 7. 汪集鸡汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('汪集鸡汤', '新洲汪集用老井水煨土鸡，只下姜片和一撮枸杞，微火两小时。汤面浮一层黄亮鸡油，鸡肉捞出来蘸生抽吃，汤甜得能照见人。', NULL, 15, 150, 165, 1, 4, '湖北菜', '汤羹,煨汤,滋补,武汉名吃', 1, TRUE, 158, 380, 32, 24, 4, '整鸡下锅不斩块，肉才不柴；全程微沸、盖子留缝；盐起锅前放，早放汤浑肉老。', '原汁清甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '老母鸡', '1', '只(约1000g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', FALSE, 3, '/api/ingredients/dacong.jpg'),
  (@r, '枸杞', '15', 'g', FALSE, 4, '/api/ingredients/gouqi.jpg'),
  (@r, '红枣', '6', '颗', FALSE, 5, '/api/ingredients/hongzao.jpg'),
  (@r, '料酒', '20', 'ml', FALSE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '6', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '清水', '2500', 'ml', TRUE, 8, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡洗净去尾臊和肺，斩去爪尖，整只入冷水浸泡20分钟出血水', 22),
  (@r, 2, '冷水下锅加姜片和料酒，大火烧开撇净浮沫', 15),
  (@r, 3, '转微火，加盖留缝煨90分钟', 92),
  (@r, 4, '下红枣继续煨40分钟至鸡肉能用筷子插透', 42),
  (@r, 5, '撒枸杞煮5分钟，加盐调味', 6),
  (@r, 6, '连罐上桌，鸡肉另碟蘸生抽食用', 4);

-- ========== 8. 糍粑鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('糍粑鱼', '湖北的年菜。草鱼抹盐和花椒腌一天，挂通风处晾到表皮发黏，再煎到两面焦壳，配姜蒜干辣椒和糖醋汁烧透。外皮带韧、肉紧咸香，因口感像糍粑得名。', NULL, 40, 25, 65, 2, 4, '湖北菜', '河鲜,年菜,咸鲜,湖北年菜', 1, TRUE, 263, 340, 34, 18, 8, '腌后晾足两小时收干表皮，煎时不粘不碎；糖醋汁分次淋，让鱼慢慢吃透；火太大壳焦里还生。', '咸甜微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '草鱼', '1', '条(约800g)', TRUE, 1, '/api/ingredients/caoyu.jpg'),
  (@r, '盐', '12', 'g', TRUE, 2, '/api/ingredients/yan.jpg'),
  (@r, '花椒', '15', '粒', TRUE, 3, '/api/ingredients/huajiao.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '25', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '大葱', '1', '根', FALSE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '干辣椒', '15', 'g', TRUE, 7, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '20', 'ml', TRUE, 9, '/api/ingredients/xiangcu.jpg'),
  (@r, '白糖', '15', 'g', TRUE, 10, '/api/ingredients/baitang.jpg'),
  (@r, '料酒', '25', 'ml', TRUE, 11, '/api/ingredients/liaojiu.jpg'),
  (@r, '淀粉', '20', 'g', FALSE, 12, '/api/ingredients/dianfen.jpg'),
  (@r, '清水', '200', 'ml', TRUE, 13, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '80', 'ml', TRUE, 14, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鱼去头尾和骨，肉切成巴掌大的厚片，洗净沥干', 15),
  (@r, 2, '盐和花椒干锅小火炒香，放凉后里外抹匀鱼片，腌2小时以上（隔夜更香）', 130),
  (@r, 3, '取出用温水冲一下，厨房纸吸干，挂通风处晾2小时至表皮发黏', 125),
  (@r, 4, '干辣椒切段，姜切片，蒜拍碎，糖生抽香醋清水对成碗汁', 8),
  (@r, 5, '锅烧热下油，鱼片拍薄淀粉，中火煎至两面硬壳金黄，盛出', 10),
  (@r, 6, '锅留底油爆香姜蒜干辣椒，鱼片回锅，沿锅边烹料酒', 4),
  (@r, 7, '分三次淋入碗汁，小火烧到汁浓挂鱼，撒葱段出锅', 8);

-- ========== 9. 钟祥蟠龙菜 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('钟祥蟠龙菜', '嘉靖皇帝的「龙菜」。猪瘦肉剁茸拌蛋清淀粉，摊成蛋皮卷起蒸制定型，切片码盘，肉嫩如糕、蛋皮金黄起花，是钟祥宴席的头一道。', NULL, 60, 40, 100, 3, 4, '湖北菜', '蒸菜,宴客,刀工,湖北名菜', 1, TRUE, 136, 320, 28, 18, 8, '肉茸要朝一个方向搅到起胶，清水分次打进去才嫩；蒸好压重石定型再切，片才薄而不散。', '细嫩鲜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪瘦肉', '300', 'g', TRUE, 1, '/api/ingredients/zhushourou.jpg'),
  (@r, '五花肉', '100', 'g', TRUE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '鸡蛋', '4', '个', TRUE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '淀粉', '40', 'g', TRUE, 4, '/api/ingredients/dianfen.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '5', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '清水', '120', 'ml', TRUE, 11, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '25', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '瘦肉和五花肉剁成细茸，葱姜泡水留葱姜水', 25),
  (@r, 2, '肉茸加盐生抽料酒白糖和葱姜水，顺一个方向搅打上劲，分次打进清水', 15),
  (@r, 3, '拌入淀粉和4个蛋黄（蛋清单留），搅成稠滑馅', 8),
  (@r, 4, '蛋清加少许淀粉水摊成薄蛋皮，平铺案板', 10),
  (@r, 5, '馅抹在蛋皮上，从一头卷成紧实的长卷，用纱布或保鲜膜裹紧', 10),
  (@r, 6, '上锅中火蒸35分钟至定型', 36),
  (@r, 7, '取出压上重石晾凉，切薄片码盘', 25),
  (@r, 8, '回锅蒸10分钟，配生抽姜丝蘸食', 12);

-- ========== 10. 洪山菜薹炒腊肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('洪山菜薹炒腊肉', '洪山菜薹紫红脆甜，配自家熏的腊肉片大火爆炒。腊肉出油、菜薹吸香，只放一点干辣椒和蒜，是武汉冬天最金贵的一把菜。', NULL, 15, 10, 25, 1, 3, '湖北菜', '小炒,素菜,冬季,武汉名菜', 1, TRUE, 262, 260, 12, 20, 8, '菜薹要掐掉老皮、撕去茎上筋，只留嫩茎；先炒腊肉出油再下菜，大火快炒才脆不黑发。', '腊香脆甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '菜心', '400', 'g', TRUE, 1, '/api/ingredients/baicai.jpg'),
  (@r, '腊肉', '150', 'g', TRUE, 2, '/api/ingredients/larou.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '干辣椒', '8', 'g', TRUE, 5, '/api/ingredients/ganlajiao.jpg'),
  (@r, '料酒', '15', 'ml', FALSE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '10', 'ml', FALSE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '3', 'g', FALSE, 8, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '2', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '25', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '菜薹掐段，撕去茎上的老筋，洗净沥干；腊肉斜切薄片', 12),
  (@r, 2, '干辣椒切段，蒜拍碎', 4),
  (@r, 3, '热锅下油，腊肉片中火煸至透明出油、边缘微卷', 5),
  (@r, 4, '下干辣椒和蒜末爆香，烹料酒', 2),
  (@r, 5, '转大火下菜薹快速翻炒至变色断生', 3),
  (@r, 6, '加生抽白糖和盐翻匀，立刻出锅（久了出水就不脆）', 2);

-- ========== 11. 黄州东坡肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('黄州东坡肉', '苏轼在黄州写下「慢著火，少著水，火候足时它自美」，这块肉就是从那口锅里出来的：整方五花肉以酒代水配冰糖，砂锅微火焖两小时，酥烂不腻。', NULL, 20, 120, 140, 2, 4, '湖北菜', '红烧,猪肉,宴客,黄冈名菜', 1, TRUE, 105, 620, 28, 50, 10, '肉先冷水煮至五成熟再切方，定型不散；全程以酒代水、微火慢焖，中途别翻动；最后大火收汁上色。', '酱甜酥烂');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '800', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '黄酒', '250', 'ml', TRUE, 2, '/api/ingredients/huangjiu.jpg'),
  (@r, '生抽', '60', 'ml', TRUE, 3, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '25', 'ml', TRUE, 4, '/api/ingredients/laochou.jpg'),
  (@r, '冰糖', '40', 'g', TRUE, 5, '/api/ingredients/bingtang.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '2', '根', TRUE, 7, '/api/ingredients/dacong.jpg'),
  (@r, '盐', '3', 'g', FALSE, 8, '/api/ingredients/yan.jpg'),
  (@r, '清水', '200', 'ml', TRUE, 9, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '整块五花肉皮面朝下冷水下锅，煮至五成熟捞出，切成四方大块', 25),
  (@r, 2, '砂锅底铺姜片和葱段（防糊并垫香），肉皮朝下摆入', 8),
  (@r, 3, '冰糖加生抽老抽和清水调匀倒入，再淋黄酒', 5),
  (@r, 4, '大火烧开后转最小火，加盖慢焖90分钟', 92),
  (@r, 5, '肉翻面使上色均匀，继续焖20分钟至筷子能一插到底', 22),
  (@r, 6, '开盖转大火收浓汁至红亮挂肉，别搅碎肉块', 6),
  (@r, 7, '取出拆去葱姜，肉块皮朝上装盘，淋净汁', 4);

-- ========== 12. 武汉面窝 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('武汉面窝', '早点摊上的金黄圈。大米加黄豆泡透磨成稀浆，掺葱花和盐，倒进中间凸起的铁勺入油锅，炸到外焦里松——薄的那圈脆，厚的边沿软。', NULL, 40, 20, 300, 2, 4, '湖北菜', '早餐,炸物,小吃,武汉名吃', 1, TRUE, 137, 300, 8, 14, 34, '米和豆要泡足4小时，磨成的浆能挂勺却仍稀；油温五成下勺，浆一倒就脱模；中心薄处先上色，别炸过头发苦。', '豆香松脆');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大米', '300', 'g', TRUE, 1, '/api/ingredients/dami.jpg'),
  (@r, '黄豆', '100', 'g', TRUE, 2, '/api/ingredients/huangdou.jpg'),
  (@r, '大葱', '1', '根', TRUE, 3, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '酵母', '2', 'g', FALSE, 5, '/api/ingredients/mianfen.jpg'),
  (@r, '盐', '5', 'g', TRUE, 6, '/api/ingredients/yan.jpg'),
  (@r, '清水', '400', 'ml', TRUE, 7, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '800', 'ml', TRUE, 8, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大米和黄豆分别淘净，清水泡4小时以上至能用手指捻碎', 245),
  (@r, 2, '连部分泡米水一起磨成稀浆，稠度能挂勺又流动', 12),
  (@r, 3, '加酵母和盐拌匀，室温醒30分钟；葱切葱花拌进浆里', 32),
  (@r, 4, '面窝勺入油锅一起烧热，让勺子吃透油', 4),
  (@r, 5, '舀一勺浆倒入，晃平后下锅，中火炸至自动脱模浮起', 4),
  (@r, 6, '翻面炸至两面金黄硬壳，中心薄处起脆', 4),
  (@r, 7, '捞出立着沥油，稍晾后趁热吃', 2);

-- ========== 13. 鲜鱼糊汤粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('鲜鱼糊汤粉', '小鱼煮到化在汤里，过筛成糊，加姜末和白胡椒粉熬稠，下细米粉勾成糊状。一碗撒葱花，配一根油条蘸着吃，是武汉冬天的暖手早点。', NULL, 30, 40, 70, 2, 3, '湖北菜', '米粉,早餐,汤粉,武汉名吃', 1, TRUE, 229, 420, 22, 8, 62, '鱼要煮到骨肉分离、压散再过筛，汤才成糊；米粉下锅后要不断搅，糊底就毁了整锅；白胡椒粉下手要重才够味。', '胡椒鲜辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '草鱼', '400', 'g', TRUE, 1, '/api/ingredients/caoyu.jpg'),
  (@r, '干米粉', '150', 'g', TRUE, 2, '/api/ingredients/ganmifen.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '15', 'g', FALSE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '白胡椒粉', '5', 'g', TRUE, 6, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '料酒', '20', 'ml', FALSE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '15', 'ml', FALSE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '5', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '油条', '1', '根', FALSE, 10, '/api/ingredients/paisan.jpg'),
  (@r, '清水', '1200', 'ml', TRUE, 11, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '25', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '干米粉温水泡1小时至软，捞出沥干', 62),
  (@r, 2, '鱼洗净斩块，姜一半切片一半剁末', 12),
  (@r, 3, '热锅下油，鱼块煎至两面发白，加姜片和料酒', 5),
  (@r, 4, '冲入沸水，大火滚煮25分钟至鱼肉散烂、汤色发白', 26),
  (@r, 5, '用勺压散鱼块，连汤过筛，鱼骨鱼刺滤净，留成鱼糊汤', 10),
  (@r, 6, '糊汤回锅烧开，下姜末和泡好的米粉，中火边煮边搅至稠', 8),
  (@r, 7, '加盐、生抽和大量白胡椒粉调味，盛碗撒葱花，配油条蘸食', 4);

-- ========== 14. 土家油茶汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('土家油茶汤', '恩施土家族的待客茶。猪油下茶叶炒香，冲水煮出茶色后滤净，倒进盛着炒米、黄豆、花生和蒜苗的碗里，咸香带焦，一碗下肚从胃暖到背。', NULL, 20, 25, 45, 2, 4, '湖北菜', '饮品,汤羹,待客,恩施土家', 1, TRUE, 123, 380, 12, 26, 26, '茶叶必须下油锅炒过才出香、不带涩；大米要干锅炒到金黄爆花才叫炒米；料现放才脆，泡久了就绵了。', '咸香焦苦');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '茶叶', '10', 'g', TRUE, 1, '/api/ingredients/lucha.jpg'),
  (@r, '猪油', '40', 'g', TRUE, 2, '/api/ingredients/zhuyou.jpg'),
  (@r, '大米', '200', 'g', TRUE, 3, '/api/ingredients/dami.jpg'),
  (@r, '黄豆', '60', 'g', TRUE, 4, '/api/ingredients/huangdou.jpg'),
  (@r, '花生', '60', 'g', TRUE, 5, '/api/ingredients/huasheng.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜叶', '20', 'g', TRUE, 7, '/api/ingredients/qingsuan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 8, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '5', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '清水', '1000', 'ml', TRUE, 10, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '干锅下大米小火炒至金黄爆花，盛出成炒米', 10),
  (@r, 2, '黄豆和花生分别用油小火炒熟或炸酥，撒少许盐拌匀', 12),
  (@r, 3, '姜切末，蒜苗切小段，茶叶选粗老一点的', 6),
  (@r, 4, '锅下猪油烧化，茶叶下锅中小火炒至酥脆出香、颜色转深', 4),
  (@r, 5, '冲入沸水，加姜末煮5分钟熬出茶色', 6),
  (@r, 6, '滤净茶叶渣，茶汤回锅加盐烧沸', 4),
  (@r, 7, '碗里放炒米、黄豆、花生和蒜苗，冲入滚烫茶汤，立刻喝', 4);

-- ========== 15. 恩施炕土豆 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('恩施炕土豆', '「炕」是土家话里少油慢煎的意思。小土豆煮到刚熟，下猪油炕到表皮起一层金黄硬壳，撒辣椒面、蒜末和葱花，外脆里沙，是恩施夜市的一碗乡愁。', NULL, 20, 25, 45, 1, 3, '湖北菜', '小吃,素菜,夜宵,恩施名吃', 1, TRUE, 89, 320, 7, 18, 34, '土豆先煮到筷子刚插透，太熟一炕就散；全程中小火慢炕，别急着翻；出锅趁热撒料才粘得住。', '焦香麻辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '土豆', '600', 'g', TRUE, 1, '/api/ingredients/tudou.jpg'),
  (@r, '猪油', '40', 'g', TRUE, 2, '/api/ingredients/zhuyou.jpg'),
  (@r, '辣椒面', '12', 'g', TRUE, 3, '/api/ingredients/lajiaofen.jpg'),
  (@r, '花椒粉', '2', 'g', FALSE, 4, '/api/ingredients/huajiaofen.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '15', 'g', TRUE, 6, '/api/ingredients/xiaocong.jpg'),
  (@r, '生抽', '15', 'ml', FALSE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '3', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 9, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '80', 'ml', TRUE, 10, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '小土豆去皮或对半切开，冷水下锅加少许盐煮至筷子刚能插透，捞出沥干', 18),
  (@r, 2, '蒜切末、小葱切花，辣椒面和盐预混', 6),
  (@r, 3, '平底锅下猪油和食用油，中火烧化', 3),
  (@r, 4, '土豆平铺锅底，中小火慢炕至底面结金黄硬壳再翻面', 12),
  (@r, 5, '反复翻炕4至5次，让每面都起壳、内里绵沙', 10),
  (@r, 6, '淋生抽和少许水激一下，撒蒜末、葱花和辣椒花椒面，颠匀出锅', 3);
