-- 由 seed/recipes-guangxi.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 广西菜，共 15 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 柳州螺蛳粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('柳州螺蛳粉', '广西最出圈的一碗粉。汤用猪筒骨加螺蛳、香料熬足两小时，米粉配酸笋、腐竹、花生、木耳和青菜，辣油一浇，臭香扑鼻。', NULL, 60, 150, 210, 3, 4, '广西菜', '米粉,汤粉,小吃,柳州名小吃', 1, TRUE, 206, 580, 26, 22, 70, '螺蛳提前养一天吐沙，剪尾后和骨头同熬，汤才有河鲜味；酸笋一定要单独用油炒干水汽再下锅，直接扔进汤里会发涩；腐竹和花生现炸现放，泡久了不脆。', '鲜辣酸冲');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '米粉', '400', 'g', TRUE, 1, '/api/ingredients/ganmifen.jpg'),
  (@r, '螺蛳', '500', 'g', TRUE, 2, '/api/ingredients/tianluo.jpg'),
  (@r, '猪筒骨', '500', 'g', TRUE, 3, '/api/ingredients/zhutonggu.jpg'),
  (@r, '酸笋', '200', 'g', TRUE, 4, '/api/ingredients/yansun.jpg'),
  (@r, '腐竹', '60', 'g', TRUE, 5, '/api/ingredients/doufu.jpg'),
  (@r, '花生米', '50', 'g', FALSE, 6, '/api/ingredients/huasheng.jpg'),
  (@r, '木耳', '30', 'g', FALSE, 7, '/api/ingredients/muer.jpg'),
  (@r, '豆腐', '100', 'g', FALSE, 8, '/api/ingredients/doufu.jpg'),
  (@r, '小白菜心', '150', 'g', FALSE, 9, '/api/ingredients/baicai.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 10, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '25', 'g', FALSE, 11, '/api/ingredients/dasuan.jpg'),
  (@r, '干辣椒', '20', 'g', TRUE, 12, '/api/ingredients/ganlajiao.jpg'),
  (@r, '八角', '3', '个', FALSE, 13, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '4', 'g', FALSE, 14, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '3', '片', FALSE, 15, '/api/ingredients/xiangye.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 16, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 17, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '8', 'g', TRUE, 18, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '50', 'ml', TRUE, 19, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '2500', 'ml', TRUE, 20, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '螺蛳清水养一夜吐净泥沙，剪去尾部，搓洗干净', 65),
  (@r, 2, '猪筒骨焯水，和螺蛳、姜片、八角、桂皮、香叶一起下锅，大火烧开后转中火熬2小时', 125),
  (@r, 3, '捞出螺蛳和骨头，汤滤净保温做汤底', 6),
  (@r, 4, '酸笋切丝，下锅干炒去水汽，加少许油和水煮10分钟，盛出', 12),
  (@r, 5, '腐竹掰段油炸至起泡酥脆，花生米冷油慢炒至香脆，木耳泡发撕小朵', 12),
  (@r, 6, '另起一锅油，下干辣椒和蒜末熬出红油做辣油', 5),
  (@r, 7, '米粉温水泡软，沸水烫透入碗', 4),
  (@r, 8, '浇滚汤，摆酸笋、腐竹、花生、木耳、豆腐和烫熟的青菜，淋辣油，趁热拌开', 5);

-- ========== 2. 桂林米粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('桂林米粉', '桂林人的干拌粉。卤水用牛肉、五花肉和香料熬浓，米粉烫干装碗，浇卤水、加锅烧和酸萝卜，先干吃再冲汤，一根粉挂满卤香。', NULL, 40, 120, 160, 3, 4, '广西菜', '米粉,干拌,小吃,桂林名小吃', 1, TRUE, 313, 540, 28, 20, 62, '卤水要加冰糖和黄酒收稠，能挂在米粉上才算好；锅烧是五花肉整块卤后再炸，皮要起酥泡；干吃留两口卤水，吃完粉再冲骨汤，这是桂林本地的吃法。', '卤香咸甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '米粉', '400', 'g', TRUE, 1, '/api/ingredients/ganmifen.jpg'),
  (@r, '牛肉', '300', 'g', TRUE, 2, '/api/ingredients/niurou.jpg'),
  (@r, '五花肉', '250', 'g', TRUE, 3, '/api/ingredients/wuhuarou.jpg'),
  (@r, '卤水汁', '60', 'ml', TRUE, 4, '/api/ingredients/lushui.jpg'),
  (@r, '酸萝卜', '80', 'g', TRUE, 5, '/api/ingredients/suanluobo.jpg'),
  (@r, '花生米', '40', 'g', FALSE, 6, '/api/ingredients/huasheng.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '小葱', '2', '根', TRUE, 9, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '15', 'g', FALSE, 10, '/api/ingredients/xiangcai.jpg'),
  (@r, '八角', '3', '个', FALSE, 11, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '4', 'g', FALSE, 12, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '2', '片', FALSE, 13, '/api/ingredients/xiangye.jpg'),
  (@r, '冰糖', '20', 'g', TRUE, 14, '/api/ingredients/bingtang.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 15, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '15', 'ml', TRUE, 16, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 17, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '6', 'g', TRUE, 18, '/api/ingredients/yan.jpg'),
  (@r, '猪骨', '500', 'g', FALSE, 19, '/api/ingredients/zhutonggu.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 20, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肉和五花肉洗净，冷水下锅加料酒姜片焯透', 15),
  (@r, 2, '锅下清水、卤水汁、生抽、老抽、冰糖、葱姜和香料包，放入两种肉，中小火卤90分钟', 95),
  (@r, 3, '捞出五花肉，皮朝下煎炸到肉皮起酥泡，晾凉切薄片做锅烧', 12),
  (@r, 4, '牛肉晾凉逆纹切薄片，卤汁继续收浓到挂勺', 8),
  (@r, 5, '猪骨另熬一锅清汤保温，酸萝卜切丝，花生米炒脆', 20),
  (@r, 6, '米粉沸水烫透，甩干水入碗', 3),
  (@r, 7, '浇两勺浓卤水拌匀，铺锅烧、牛肉、酸萝卜、花生、葱花和香菜，先干吃，最后冲少许骨汤', 5);

-- ========== 3. 南宁老友粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('南宁老友粉', '南宁的「老友情」。酸笋、豆豉、蒜末和辣椒一起下锅爆香，肉片炒变色冲入汤，再烫米粉，一碗汤粉酸辣咸香、镬气十足。', NULL, 15, 15, 30, 1, 2, '广西菜', '米粉,汤粉,小吃,南宁名小吃', 1, TRUE, 108, 510, 22, 16, 68, '酸笋、豆豉、蒜和辣椒四样要先小火爆干香味，这是老友粉的灵魂，火小会出水；肉片上浆后滑炒到刚变色就掺汤；汤别熬太久，滚开下粉烫一下就起锅。', '酸辣浓郁');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '米粉', '300', 'g', TRUE, 1, '/api/ingredients/ganmifen.jpg'),
  (@r, '猪瘦肉', '150', 'g', TRUE, 2, '/api/ingredients/zhushourou.jpg'),
  (@r, '酸笋', '100', 'g', TRUE, 3, '/api/ingredients/yansun.jpg'),
  (@r, '豆豉', '15', 'g', TRUE, 4, '/api/ingredients/douchi.jpg'),
  (@r, '大蒜', '25', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '小米辣', '15', 'g', FALSE, 6, '/api/ingredients/xiaomila.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', FALSE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '西红柿', '80', 'g', FALSE, 9, '/api/ingredients/xihongshi.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 10, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 11, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '3', 'g', FALSE, 12, '/api/ingredients/baitang.jpg'),
  (@r, '淀粉', '5', 'g', FALSE, 13, '/api/ingredients/dianfen.jpg'),
  (@r, '高汤', '800', 'ml', TRUE, 14, '/api/ingredients/gaotang.jpg'),
  (@r, '食用油', '35', 'ml', TRUE, 15, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 16, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '瘦肉切薄片，用料酒、生抽和淀粉抓腌10分钟', 11),
  (@r, 2, '酸笋切丝，豆豉剁碎，蒜切末，姜切丝，葱切花，辣椒切圈', 8),
  (@r, 3, '锅下油，中小火先把酸笋、豆豉、蒜末、姜丝和辣椒爆干出香', 5),
  (@r, 4, '下肉片滑炒到刚变色，加西红柿炒出汁', 3),
  (@r, 5, '冲入高汤大火烧开，加生抽、白糖和盐调味', 4),
  (@r, 6, '下米粉烫1分钟入味，撒葱花出锅', 2);

-- ========== 4. 全州醋血鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('全州醋血鸭', '桂林全州的绝活。鸭肉炒香后加醋浆血，起锅前把鸭血醋汁淋回锅里挂匀，血裹肉呈酱紫，酸香压住膻味，配茄子一起焖。', NULL, 30, 40, 70, 3, 4, '广西菜', '焖炒,鸭肉,酸味,广西名菜', 1, TRUE, 280, 560, 42, 38, 14, '醋血要现调：新鲜鸭血加米醋搅匀，血和醋的比例约十比一；血浆一定要离火或小火时淋，火大就结成渣；鸭肉先煸出鸭油，成菜才不腻。', '酸香浓烈');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸭', '半', '只(约800g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '鲜鸭血', '200', 'ml', TRUE, 2, '/api/ingredients/yaxue.jpg'),
  (@r, '香醋', '60', 'ml', TRUE, 3, '/api/ingredients/xiangcu.jpg'),
  (@r, '茄子', '300', 'g', FALSE, 4, '/api/ingredients/qiezi.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '40', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '干辣椒', '15', 'g', FALSE, 7, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '3', 'g', FALSE, 8, '/api/ingredients/huajiao.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 11, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '6', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 13, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '400', 'ml', TRUE, 14, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸭宰杀时留血，鸭肉斩小块洗净沥干', 15),
  (@r, 2, '鸭血加香醋调稀成醋浆，搅匀备用', 4),
  (@r, 3, '茄子切滚刀块，姜蒜切片，干辣椒切节', 8),
  (@r, 4, '锅下油，鸭块中火煸到出鸭油、皮微黄，滗掉多余油', 10),
  (@r, 5, '下姜蒜辣椒花椒炒香，加料酒、生抽、白糖和清水，加盖焖20分钟', 23),
  (@r, 6, '下茄子再焖8分钟至软', 9),
  (@r, 7, '转小火，把醋浆分三次淋进锅里翻匀，成酱紫色后加盐出锅，切忌大火', 6);

-- ========== 5. 荔浦芋扣肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('荔浦芋扣肉', '广西宴客的头道硬菜。荔浦芋切片炸香，五花肉煮透扎孔、上色后炸出虎皮，肉芋相间码碗，拌入五香糖色汁蒸两小时，倒扣上桌，芋比肉还抢手。', NULL, 60, 150, 210, 3, 6, '广西菜', '蒸菜,扣肉,宴客,广西名菜', 1, TRUE, 88, 620, 24, 48, 26, '芋要挑荔浦芋（切面有紫红丝、粉到起沙），先炸后蒸不散；五花肉煮到筷子能插但别烂，皮上扎孔再抹糖色才起虎皮；蒸够2小时才糯，倒扣前先把汁滗出来。', '粉糯酱香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '五花肉', '600', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '芋头', '500', 'g', TRUE, 2, '/api/ingredients/tudou.jpg'),
  (@r, '五香粉', '5', 'g', TRUE, 3, '/api/ingredients/bajiao.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '蒜末', '20', 'g', FALSE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '冰糖', '20', 'g', TRUE, 7, '/api/ingredients/bingtang.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '20', 'ml', TRUE, 9, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 10, '/api/ingredients/liaojiu.jpg'),
  (@r, '蜂蜜', '15', 'g', FALSE, 11, '/api/ingredients/mayatang.jpg'),
  (@r, '盐', '5', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 13, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '200', 'ml', TRUE, 14, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉冷水下锅，加姜葱料酒煮30分钟至筷子能插透，捞出沥干', 35),
  (@r, 2, '肉皮用牙签扎满小孔，抹一层老抽和蜂蜜水，晾干10分钟', 12),
  (@r, 3, '芋头去皮切5毫米厚片，五成油温炸到表面结壳、边缘微黄', 8),
  (@r, 4, '肉皮朝下入热油锅炸出虎皮，起泡后立刻捞进冷水泡10分钟', 6),
  (@r, 5, '肉切成与芋片同厚的片，加五香粉、生抽、冰糖、盐和蒜末拌成料汁', 8),
  (@r, 6, '一片肉夹一片芋，皮朝下整齐码进碗里，剩下的料汁全部浇进去', 8),
  (@r, 7, '上锅大火蒸2小时，取出把汁滗进锅，扣盘后把汁勾薄再淋回肉面', 125);

-- ========== 6. 阳朔啤酒鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('阳朔啤酒鱼', '漓江边的名菜。鲜草鱼煎到两面微黄，加整瓶啤酒和西红柿、青椒同焖，汤汁收浓带麦香，鱼肉不腥、皮糯胶质重。', NULL, 20, 25, 45, 2, 4, '广西菜', '河鲜,焖烧,地方名菜,广西名菜', 1, TRUE, 137, 430, 40, 20, 14, '鱼一定要现杀，漓江一带用毛骨鱼，买不到就选草鱼或鲤鱼；先煎后焖，皮不破；啤酒一整瓶别减量，酒精挥发后只剩麦香；西红柿分两次放，一半早下熬进汤里，一半后下保形。', '麦香酸甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '草鱼', '1', '条(约900g)', TRUE, 1, '/api/ingredients/caoyu.jpg'),
  (@r, '啤酒', '500', 'ml', TRUE, 2, '/api/ingredients/pijiu.jpg'),
  (@r, '西红柿', '200', 'g', TRUE, 3, '/api/ingredients/xihongshi.jpg'),
  (@r, '青辣椒', '60', 'g', TRUE, 4, '/api/ingredients/qinglajiao.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '2', '根', FALSE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '料酒', '25', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', FALSE, 10, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '8', 'g', FALSE, 11, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '6', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '45', 'ml', TRUE, 13, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '草鱼宰净去黑膜，斩成宽条，用料酒和盐抹匀腌10分钟', 12),
  (@r, 2, '西红柿切块，青椒滚刀，姜蒜切片', 8),
  (@r, 3, '锅下宽油烧热，鱼条皮朝下煎到两面金黄定型，捞出', 8),
  (@r, 4, '锅留底油爆香姜蒜，下一半西红柿炒出红汁', 4),
  (@r, 5, '鱼回锅，倒入啤酒、生抽、老抽和白糖，大火烧开后转中火焖12分钟', 14),
  (@r, 6, '下青椒和剩下的西红柿，再焖5分钟', 6),
  (@r, 7, '大火收浓汤汁，撒葱花连锅上桌', 3);

-- ========== 7. 螺蛳鸭脚煲 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('螺蛳鸭脚煲', '南宁夜宵的顶流。鸭掌先炸到皮起皱，和螺蛳、酸笋、豆腐、土豆一起用香料汤煲到脱骨，汤浓味辣，一吮就骨肉分离。', NULL, 50, 90, 140, 3, 6, '广西菜', '火锅,夜宵,河鲜,南宁名菜', 1, TRUE, 89, 480, 30, 28, 26, '鸭掌炸后要泡冷水1小时，皮才起皱、吸汤；螺蛳提前吐沙剪尾，和骨头同熬做汤底；酸笋单独炒干再下煲；煲够1小时，鸭掌才糯到脱骨。', '香辣浓稠');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸭掌', '500', 'g', TRUE, 1, '/api/ingredients/jizhua.jpg'),
  (@r, '螺蛳', '400', 'g', TRUE, 2, '/api/ingredients/tianluo.jpg'),
  (@r, '猪骨', '500', 'g', TRUE, 3, '/api/ingredients/zhutonggu.jpg'),
  (@r, '酸笋', '150', 'g', TRUE, 4, '/api/ingredients/yansun.jpg'),
  (@r, '豆腐', '200', 'g', FALSE, 5, '/api/ingredients/doufu.jpg'),
  (@r, '土豆', '200', 'g', FALSE, 6, '/api/ingredients/tudou.jpg'),
  (@r, '腐竹', '50', 'g', FALSE, 7, '/api/ingredients/doufu.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 9, '/api/ingredients/dasuan.jpg'),
  (@r, '干辣椒', '20', 'g', TRUE, 10, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '5', 'g', FALSE, 11, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '2', '个', FALSE, 12, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '3', 'g', FALSE, 13, '/api/ingredients/guipi.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 14, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 15, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '15', 'ml', FALSE, 16, '/api/ingredients/laochou.jpg'),
  (@r, '盐', '7', 'g', TRUE, 17, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '400', 'ml', TRUE, 18, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '螺蛳吐净沙剪尾，和猪骨、姜片一起下锅熬1小时汤底，滤出螺蛳留用', 65),
  (@r, 2, '鸭掌剪去指甲焯水沥干，油温六成热炸到皮金黄起泡，捞进冷水泡1小时', 75),
  (@r, 3, '豆腐切块炸至硬壳，土豆滚刀块，酸笋切丝炒干水汽', 12),
  (@r, 4, '煲底放姜蒜、干辣椒、花椒、八角桂皮炒香，下酸笋和生抽老抽', 4),
  (@r, 5, '码入鸭掌、螺蛳、豆腐、土豆和腐竹，冲入骨汤没过食材', 6),
  (@r, 6, '大火烧开转小火煲60分钟至鸭掌软糯脱骨', 62),
  (@r, 7, '加盐调味，连煲上桌，配一碗米粉涮进去', 5);

-- ========== 8. 恭城油茶 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('恭城油茶', '桂林恭城的「饮料」。茶叶、姜、蒜用油炒过再舂碎，加水熬成苦香茶汤，配米花、花生和各式佐食，一碗配十样小点，是瑶家的待客礼。', NULL, 25, 20, 45, 2, 4, '广西菜', '饮品,油茶,瑶族,地方习俗', 1, TRUE, 187, 180, 5, 12, 14, '茶叶选老叶粗茶，嫩茶一熬就苦得发涩；先炒后舂再熬，三道水才能出味；米花一定要现炸，泡进汤里三秒就吃；第一碗最苦，喝到第二碗才回甘。', '苦香回甘');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '茶叶', '15', 'g', TRUE, 1, '/api/ingredients/lucha.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '米花', '40', 'g', TRUE, 4, '/api/ingredients/mihua.jpg'),
  (@r, '花生米', '40', 'g', TRUE, 5, '/api/ingredients/huasheng.jpg'),
  (@r, '猪油', '25', 'g', TRUE, 6, '/api/ingredients/zhuyou.jpg'),
  (@r, '小葱', '2', '根', FALSE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 8, '/api/ingredients/xiangcai.jpg'),
  (@r, '盐', '4', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '清水', '1200', 'ml', TRUE, 10, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '20', 'ml', FALSE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '茶叶用温水泡5分钟，姜切片，蒜去皮', 7),
  (@r, 2, '锅下猪油，姜片蒜瓣炒香，再下茶叶同炒2分钟', 4),
  (@r, 3, '倒进舂桶（或料理机）舂成粗末，让茶汁出味', 5),
  (@r, 4, '炒过的茶料入锅加清水，大火烧开熬8分钟', 10),
  (@r, 5, '滤出茶汤，再加水熬第二道，两次汤合并', 10),
  (@r, 6, '茶碗里放米花和炒花生，冲入滚油茶，撒葱花香菜和盐', 4),
  (@r, 7, '花生米冷油慢炒至香脆作佐食，米花另用热油炸至膨起', 8);

-- ========== 9. 玉林牛巴 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('玉林牛巴', '玉林的百年冷盘。黄牛肉加陈皮、五香和糖慢卤到汁干，晾凉后逆纹切薄片，色如琥珀、甜香带嚼劲，是广西人下酒和夹粉的东西。', NULL, 180, 120, 300, 3, 6, '广西菜', '卤味,冷盘,牛肉,广西名产', 1, TRUE, 230, 260, 38, 8, 10, '肉选后腿，去筋后再卤；腌渍2小时以上才入味；卤汁要收到能挂在肉上、锅底只剩油；切得越薄越好，逆着纹理切才不塞牙。', '甜香耐嚼');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '黄牛后腿肉', '800', 'g', TRUE, 1, '/api/ingredients/niurou.jpg'),
  (@r, '陈皮', '5', 'g', TRUE, 2, '/api/ingredients/luobogan.jpg'),
  (@r, '五香粉', '6', 'g', TRUE, 3, '/api/ingredients/bajiao.jpg'),
  (@r, '八角', '3', '个', FALSE, 4, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '4', 'g', FALSE, 5, '/api/ingredients/guipi.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '25', 'g', FALSE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '2', '根', FALSE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '冰糖', '40', 'g', TRUE, 9, '/api/ingredients/bingtang.jpg'),
  (@r, '生抽', '60', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '25', 'ml', TRUE, 11, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 12, '/api/ingredients/liaojiu.jpg'),
  (@r, '蜂蜜', '20', 'g', FALSE, 13, '/api/ingredients/mayatang.jpg'),
  (@r, '白酒', '15', 'ml', FALSE, 14, '/api/ingredients/baijiu.jpg'),
  (@r, '盐', '6', 'g', TRUE, 15, '/api/ingredients/yan.jpg'),
  (@r, '清水', '1000', 'ml', TRUE, 16, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肉剔去筋膜，加冰糖20克、生抽、五香粉和白酒抓匀，腌渍2小时', 125),
  (@r, 2, '锅里下清水、香料包、姜葱蒜和剩下的调料烧开煮20分钟出味', 22),
  (@r, 3, '牛肉连腌汁一起下锅，大火烧开转小火卤90分钟', 95),
  (@r, 4, '取出牛肉，卤汁继续熬到浓稠挂勺', 12),
  (@r, 5, '牛肉晾凉后逆纹切2毫米薄片', 10),
  (@r, 6, '肉片回锅裹匀浓汁，收干到表面发亮，摊开晾透装盘', 10);

-- ========== 10. 南宁卷筒粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('南宁卷筒粉', '南宁早餐的米皮卷。米浆在平底锅上摊成薄皮，铺肉末、木耳和胡萝卜，刮成筒状装盘，浇黄皮酱或番茄汁、撒葱花，一米皮卷两三口。', NULL, 30, 30, 60, 2, 4, '广西菜', '主食,早餐,米制品,南宁小吃', 1, TRUE, 124, 400, 14, 12, 60, '米浆要调得能挂勺又流得开，太稠摊不薄；锅要烧到微热再下浆，转一圈倒出多余的浆；馅炒得干一些，皮才不破；酱汁别省，卷筒粉全靠它提味。', '软滑酱香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '粘米粉', '150', 'g', TRUE, 1, '/api/ingredients/zhanmifen.jpg'),
  (@r, '淀粉', '30', 'g', TRUE, 2, '/api/ingredients/dianfen.jpg'),
  (@r, '猪肉末', '150', 'g', TRUE, 3, '/api/ingredients/zhuroumo.jpg'),
  (@r, '木耳', '25', 'g', TRUE, 4, '/api/ingredients/muer.jpg'),
  (@r, '胡萝卜', '80', 'g', FALSE, 5, '/api/ingredients/huluobo.jpg'),
  (@r, '大葱', '1', '根', FALSE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '小葱', '2', '根', TRUE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '番茄酱', '40', 'g', TRUE, 9, '/api/ingredients/honglajiao.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '15', 'g', TRUE, 11, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '4', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 13, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '300', 'ml', TRUE, 14, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '粘米粉、淀粉、少许盐和清水调成顺滑米浆，静置10分钟', 12),
  (@r, 2, '木耳泡发切细丝，胡萝卜切细丝，葱姜切末', 8),
  (@r, 3, '锅下油爆香姜葱，下肉末炒散，加木耳丝、胡萝卜丝和生抽盐炒干成馅', 6),
  (@r, 4, '平底不粘锅微热刷薄油，舀一勺米浆转匀成薄皮，小火烙20秒至起泡', 3),
  (@r, 5, '铺一小条馅，用刮板从一头卷成筒状，摆进盘里', 4),
  (@r, 6, '番茄酱、生抽、白糖和少许水煮开成酸甜汁，淋在卷筒粉上，撒葱花', 4);

-- ========== 11. 桂林田螺酿 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('桂林田螺酿', '桂林「酿」菜的代表。大田螺煮熟挑肉，和猪肉末、薄荷、紫苏剁在一起，再塞回螺壳，加汤焖入味，吸着吃，草本气顶着螺鲜。', NULL, 60, 25, 85, 3, 4, '广西菜', '河鲜,酿菜,地方名菜,桂林名菜', 1, TRUE, 152, 340, 32, 16, 10, '选拇指大的螺，太小挑不出肉；焯水加花椒和料酒去腥，螺盖一并揭掉；剁馅要带螺肉一起剁，口感才弹；塞馅留一点出头，好吸入口；焖够15分钟才进味。', '辛香鲜美');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '田螺', '800', 'g', TRUE, 1, '/api/ingredients/tianluo.jpg'),
  (@r, '猪肉末', '200', 'g', TRUE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '薄荷', '10', 'g', TRUE, 3, '/api/ingredients/xiangcai.jpg'),
  (@r, '紫苏叶', '15', 'g', TRUE, 4, '/api/ingredients/zisu.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '小米辣', '20', 'g', FALSE, 7, '/api/ingredients/xiaomila.jpg'),
  (@r, '小葱', '2', '根', FALSE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '花椒', '3', 'g', FALSE, 9, '/api/ingredients/huajiao.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 10, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 11, '/api/ingredients/shengchou.jpg'),
  (@r, '辣椒面', '5', 'g', FALSE, 12, '/api/ingredients/lajiaofen.jpg'),
  (@r, '淀粉', '10', 'g', FALSE, 13, '/api/ingredients/dianfen.jpg'),
  (@r, '盐', '6', 'g', TRUE, 14, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '35', 'ml', TRUE, 15, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '600', 'ml', TRUE, 16, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '田螺刷净外壳，冷水下锅加花椒、姜片和一半料酒，煮5分钟后捞出', 10),
  (@r, 2, '用竹签挑出螺肉，摘去尾部内脏和螺盖，洗净沥干', 15),
  (@r, 3, '螺肉加猪肉末、薄荷、紫苏、一半姜蒜和盐、淀粉一起剁成馅', 10),
  (@r, 4, '把馅塞回螺壳，压实并让馅略出头，摆进锅里', 12),
  (@r, 5, '锅下油爆香剩下的姜蒜和小米辣，加辣椒面炒出红油', 3),
  (@r, 6, '掺清水、生抽和剩下料酒烧开，下螺蛳，中火焖15分钟', 17),
  (@r, 7, '收汁到剩小半锅汤，撒葱花，连汤装深盘，吸着吃', 4);

-- ========== 12. 南宁酸嘢 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('南宁酸嘢', '广西街头的腌水果摊。萝卜、黄瓜、莴笋切厚片，用盐杀水后拌白糖、白醋和辣椒面，腌半小时就酸辣脆甜，边走边捏着吃。', NULL, 20, 0, 50, 1, 4, '广西菜', '凉菜,腌渍,素食,街头小吃', 1, TRUE, 288, 90, 3, 1, 20, '所有料一律切3毫米以上厚片，太薄一腌就软；盐杀水后一定要挤干，不然酸汁被稀释；糖醋比约一比一，辣椒面最后撒，久泡失色；腌半小时入味最脆，过夜就软了。', '酸甜辣脆');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '白萝卜', '250', 'g', TRUE, 1, '/api/ingredients/bailuobo.jpg'),
  (@r, '黄瓜', '200', 'g', TRUE, 2, '/api/ingredients/huanggua.jpg'),
  (@r, '莴笋', '200', 'g', TRUE, 3, '/api/ingredients/wosun.jpg'),
  (@r, '胡萝卜', '100', 'g', FALSE, 4, '/api/ingredients/huluobo.jpg'),
  (@r, '辣椒面', '8', 'g', TRUE, 5, '/api/ingredients/lajiaofen.jpg'),
  (@r, '白糖', '40', 'g', TRUE, 6, '/api/ingredients/baitang.jpg'),
  (@r, '白醋', '40', 'ml', TRUE, 7, '/api/ingredients/baicu.jpg'),
  (@r, '盐', '8', 'g', TRUE, 8, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '萝卜、黄瓜、莴笋、胡萝卜分别切3毫米厚片或粗条', 12),
  (@r, 2, '加5克盐拌匀腌15分钟，杀出的水倒掉，微微挤干', 16),
  (@r, 3, '白糖、白醋和剩下的盐和辣椒面调成酸甜辣汁', 3),
  (@r, 4, '蔬菜倒进无油容器，浇汁拌匀，腌30分钟以上', 32),
  (@r, 5, '装碟上桌，汁水一起淋上，捏着吃', 2);

-- ========== 13. 北海猪脚粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('北海猪脚粉', '北部湾的汤粉。猪蹄和猪骨加香料熬出白汤，米粉装碗，铺卤到发软的猪蹄块，配酸萝卜、香菜和一小碟黄酱，汤厚不腻。', NULL, 30, 180, 210, 2, 4, '广西菜', '米粉,汤粉,早餐,北海名小吃', 1, TRUE, 188, 600, 34, 26, 58, '猪蹄让摊主剁大块，熬汤前先焯两遍水；香料装袋，汤色才干净不浑；汤要熬足3小时，胶质溶出来才挂唇；黄酱是蘸碟关键，没有就用甜面酱加少许花生酱。', '醇厚胶香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '米粉', '400', 'g', TRUE, 1, '/api/ingredients/ganmifen.jpg'),
  (@r, '猪蹄', '800', 'g', TRUE, 2, '/api/ingredients/zhuqianzhou.jpg'),
  (@r, '猪骨', '500', 'g', TRUE, 3, '/api/ingredients/zhutonggu.jpg'),
  (@r, '酸萝卜', '80', 'g', FALSE, 4, '/api/ingredients/suanluobo.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '小葱', '2', '根', FALSE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '20', 'g', TRUE, 8, '/api/ingredients/xiangcai.jpg'),
  (@r, '八角', '3', '个', FALSE, 9, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '4', 'g', FALSE, 10, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '2', '片', FALSE, 11, '/api/ingredients/xiangye.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 12, '/api/ingredients/liaojiu.jpg'),
  (@r, '甜面酱', '30', 'g', FALSE, 13, '/api/ingredients/tianmianjiang.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 14, '/api/ingredients/shengchou.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 15, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '盐', '8', 'g', TRUE, 16, '/api/ingredients/yan.jpg'),
  (@r, '清水', '3000', 'ml', TRUE, 17, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪蹄剁块、猪骨洗净，各自冷水下锅焯水两遍，冲净', 20),
  (@r, 2, '汤锅注清水，下猪蹄猪骨、姜葱和香料袋，大火烧开后转中小火熬3小时', 185),
  (@r, 3, '汤色奶白后加生抽、白胡椒粉和盐调味，捞出猪蹄块保温', 6),
  (@r, 4, '酸萝卜切丝，香菜和葱花切末，甜面酱加少许凉开水调稀做蘸酱', 8),
  (@r, 5, '米粉烫热入碗，摆猪蹄块和酸萝卜', 3),
  (@r, 6, '浇滚汤，撒香菜葱花，配一碟甜面酱', 2);

-- ========== 14. 柳州牛杂煲 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('柳州牛杂煲', '广西人冬天的煲。牛肚牛肠和牛骨先卤后煲，配白萝卜同炖到透味，汤里加柱侯式的甜面酱与香料，一煲从汤吃到粉。', NULL, 60, 180, 240, 3, 6, '广西菜', '火锅,内脏,冬季,柳州小吃', 1, TRUE, 269, 420, 36, 20, 18, '内脏要盐醋反复搓洗，焯水后再卤，味才干净；牛肚和牛肠熟成时间不同，先肠后肚；白萝卜切厚块，后放避免煮散；煲够1小时，萝卜吸饱汤最好吃。', '酱香浓厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '牛肚', '400', 'g', TRUE, 1, '/api/ingredients/niudu.jpg'),
  (@r, '猪肥肠', '200', 'g', FALSE, 2, '/api/ingredients/zhufeichang.jpg'),
  (@r, '牛骨', '500', 'g', TRUE, 3, '/api/ingredients/niurou.jpg'),
  (@r, '白萝卜', '500', 'g', TRUE, 4, '/api/ingredients/bailuobo.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '干辣椒', '15', 'g', FALSE, 8, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '5', 'g', FALSE, 9, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '3', '个', TRUE, 10, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '4', 'g', FALSE, 11, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '3', '片', FALSE, 12, '/api/ingredients/xiangye.jpg'),
  (@r, '陈皮', '3', 'g', FALSE, 13, '/api/ingredients/luobogan.jpg'),
  (@r, '甜面酱', '40', 'g', TRUE, 14, '/api/ingredients/tianmianjiang.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 15, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '20', 'ml', TRUE, 16, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 17, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '7', 'g', TRUE, 18, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 19, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '2000', 'ml', TRUE, 20, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肚和肥肠用盐和面粉反复搓洗，冲净后冷水下锅加料酒焯10分钟，捞出切块', 20),
  (@r, 2, '牛骨焯净血沫，和姜葱、香料一起下锅熬2小时，滤出汤底', 125),
  (@r, 3, '锅下油，蒜瓣、干辣椒爆香，加甜面酱、生抽老抽炒出酱香', 4),
  (@r, 4, '下牛肚肥肠翻匀，掺骨汤，中火煲60分钟', 62),
  (@r, 5, '白萝卜切厚块下煲，再煲30分钟至萝卜透明', 32),
  (@r, 6, '加盐调味，连煲坐小火上，边加热边吃，最后可涮青菜和米粉', 8);

-- ========== 15. 拔丝芋头 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('拔丝芋头', '广西宴席上的甜菜。荔浦芋切块炸到外硬内粉，白糖熬成琥珀色糖浆裹匀，趁热夹起能拉出长丝，蘸凉开水定型后吃。', NULL, 20, 15, 35, 2, 4, '广西菜', '甜菜,宴客,素食,广西名菜', 1, TRUE, 248, 420, 5, 14, 70, '芋头先蒸10分钟再炸，内里才绵而不夹生；糖浆熬到浅琥珀色立刻下料，晚一秒就发苦；盆里抹薄油，装盘不粘；上桌配一碗凉开水，蘸着吃才不粘牙。', '焦甜绵软');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '芋头', '500', 'g', TRUE, 1, '/api/ingredients/tudou.jpg'),
  (@r, '白糖', '120', 'g', TRUE, 2, '/api/ingredients/baitang.jpg'),
  (@r, '淀粉', '30', 'g', FALSE, 3, '/api/ingredients/dianfen.jpg'),
  (@r, '生姜', '5', 'g', FALSE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '冰糖', '20', 'g', FALSE, 5, '/api/ingredients/bingtang.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 6, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '60', 'ml', TRUE, 7, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '芋头去皮切3厘米滚刀块，上锅蒸10分钟至七八分熟，晾凉', 15),
  (@r, 2, '表面薄薄拍一层淀粉', 4),
  (@r, 3, '六成油温下锅炸到外壳硬挺、表面金黄，捞出', 6),
  (@r, 4, '升高油温复炸30秒，外皮更脆', 1),
  (@r, 5, '锅留少许底油，加白糖和清水小火熬到浅琥珀色起小泡', 5),
  (@r, 6, '倒芋块快速翻匀，让糖浆裹满，盛进抹过油的盘里', 2),
  (@r, 7, '上桌配一碗凉开水，夹起蘸水拉丝吃', 2);
