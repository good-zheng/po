-- 由 seed/recipes-lu.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 鲁菜，共 17 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 糖醋鲤鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('糖醋鲤鱼', '鲁菜头牌，老济南堂食必点，取黄河鲤鱼改牡丹花刀，炸成跃龙门之姿，趁热浇上糖醋芡汁，吱啦作响，外脆里嫩，酸甜冲鼻。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/lu-tangculiyu.jpg', 20, 25, 45, 3, 4, '鲁菜', '经典,宴客,河鲜,鲁菜名菜', 1, TRUE, 185, 500, 32, 25, 35, '剞刀要深至骨但不破皮，油温七成热时提着鱼尾下锅定型，芡汁要滚热，浇上去听那声吱啦才算成。', '酸甜咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鲤鱼', '1', '条(约750g)', TRUE, 1, '/api/ingredients/caoyu.jpg'),
  (@r, '面粉', '60', 'g', TRUE, 2, '/api/ingredients/mianfen.jpg'),
  (@r, '淀粉', '40', 'g', TRUE, 3, '/api/ingredients/dianfen.jpg'),
  (@r, '白糖', '60', 'g', TRUE, 4, '/api/ingredients/baitang.jpg'),
  (@r, '香醋', '50', 'ml', TRUE, 5, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '20', 'g', TRUE, 9, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '10', 'g', FALSE, 10, '/api/ingredients/dasuan.jpg'),
  (@r, '清水', '150', 'ml', TRUE, 11, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '60', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鲤鱼去鳞去鳃去内脏，两面剞牡丹花刀深至鱼骨', 8),
  (@r, 2, '里外抹料酒腌10分钟去腥，面粉淀粉加水调成厚糊挂匀鱼身', 10),
  (@r, 3, '油烧七成热，提鱼尾入锅，勺淋热油定型，中火炸至外壳金黄发硬', 8),
  (@r, 4, '升油温至八成热复炸1分钟，捞出摆盘', 2),
  (@r, 5, '锅留底油，下姜葱蒜末，加白糖、香醋、生抽、清水烧开', 3),
  (@r, 6, '水淀粉勾浓芡，趁滚热浇在鱼身上，吱声上桌', 2);

-- ========== 2. 油焖大虾 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('油焖大虾', '胶东待客头道海鲜菜。大虾以虾脑炼出红油，葱段姜丝焖入咸甜滋味，壳亮肉嫩，吮指连虾油都不放过。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/lu-youmendaxia.jpg', 15, 12, 27, 2, 3, '鲁菜', '经典,宴客,海鲜,鲁菜名菜', 1, TRUE, 149, 280, 30, 15, 5, '虾须虾枪剪净，背部开刀挑去沙线；按压虾头逼出虾油，汤汁才红亮焖香。', '咸鲜微甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大虾', '8', '只(约500g)', TRUE, 1, '/api/ingredients/hexiaren.jpg'),
  (@r, '大葱', '30', 'g', TRUE, 2, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '猪油', '30', 'g', TRUE, 4, '/api/ingredients/zhuyou.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 5, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '10', 'g', TRUE, 7, '/api/ingredients/baitang.jpg'),
  (@r, '香醋', '3', 'ml', FALSE, 8, '/api/ingredients/xiangcu.jpg'),
  (@r, '清水', '80', 'ml', TRUE, 9, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '剪去虾须虾枪虾脚，背部片开挑去沙线，姜切片葱切段', 8),
  (@r, 2, '热锅下猪油，大虾平铺，中火煎至一面变红', 3),
  (@r, 3, '翻转大虾，锅铲按压虾头逼出虾油，炒至油色红亮', 2),
  (@r, 4, '下姜片葱段炒香，烹料酒生抽，加清水白糖烧开', 2),
  (@r, 5, '加盖小火焖5分钟，开盖转中火收至汁浓裹身，点香醋出锅', 5);

-- ========== 3. 爆炒腰花 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('爆炒腰花', '鲁菜火功考题，爆字当先。猪腰剞麦穗花刀，旺火热油里十余秒成花卷，脆嫩无臊气，配木耳笋片，讲究一个快字。', NULL, 20, 4, 24, 3, 3, '鲁菜', '经典,快手,下饭,鲁菜名菜', 1, TRUE, 106, 180, 18, 9, 8, '臊筋片净是去腥根本，麦穗刀深而不透；全程大火一气呵成，腰花打卷即刻出锅。', '咸鲜脆嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪腰', '2', '个(约400g)', TRUE, 1, '/api/ingredients/zhuyao.jpg'),
  (@r, '水发木耳', '80', 'g', TRUE, 2, '/api/ingredients/muer.jpg'),
  (@r, '冬笋', '60', 'g', TRUE, 3, '/api/ingredients/dongsun.jpg'),
  (@r, '大葱', '15', 'g', TRUE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '10', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '料酒', '25', 'ml', TRUE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '12', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '淀粉', '10', 'g', TRUE, 9, '/api/ingredients/dianfen.jpg'),
  (@r, '清水', '30', 'ml', TRUE, 10, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '25', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '2', 'g', TRUE, 12, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪腰对半片开，片净白色臊筋，内侧剞十字花刀深而不透，切成麦穗块', 8),
  (@r, 2, '腰块加料酒浸泡10分钟去臊，捞出拍薄淀粉', 10),
  (@r, 3, '碗内放生抽、盐、淀粉和清水30ml兑成碗汁', 1),
  (@r, 4, '沸水快焯10余秒，腰花打卷即捞，沥干', 1),
  (@r, 5, '锅烧至冒烟下油，投腰花、木耳、笋片大火爆炒20秒', 1),
  (@r, 6, '泼入碗汁再爆10秒翻匀，下葱段装盘', 1);

-- ========== 4. 九转大肠 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('九转大肠', '济南堂菜魁首，俗传因九道工序、五味兼备得名。肥肠套叠煮透，炸红再煨，咸甜酸香辣层层盘绕，软嫩中带着韧。', NULL, 60, 60, 120, 3, 4, '鲁菜', '经典,宴客,鲁菜名菜', 1, TRUE, 172, 500, 22, 40, 10, '套肠要层层塞实不留空，煮透才能定型；收汁时香醋沿锅边分两次下，五味方有先后层次。', '五味兼备');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪肥肠', '750', 'g', TRUE, 1, '/api/ingredients/zhufeichang.jpg'),
  (@r, '面粉', '50', 'g', TRUE, 2, '/api/ingredients/mianfen.jpg'),
  (@r, '盐', '8', 'g', TRUE, 3, '/api/ingredients/yan.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 4, '/api/ingredients/liaojiu.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '30', 'g', TRUE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '白糖', '35', 'g', TRUE, 7, '/api/ingredients/baitang.jpg'),
  (@r, '香醋', '30', 'ml', TRUE, 8, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '清水', '120', 'ml', TRUE, 10, '/api/ingredients/qingshui.jpg'),
  (@r, '白胡椒粉', '2', 'g', TRUE, 11, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '肥肠加盐、面粉反复揉搓，翻面冲净黏液，重复三遍至无异味', 15),
  (@r, 2, '肠头沿肠身内翻塞入套叠成多层，沸水加葱姜料酒煮40分钟捞出', 45),
  (@r, 3, '切成五厘米长段，入六成热油炸至表皮红硬，捞出控油', 5),
  (@r, 4, '锅留底油，下姜葱，放大肠段，加生抽、清水、白糖，小火煨20分钟', 20),
  (@r, 5, '转大火收浓，沿锅边分两次下香醋，撒白胡椒粉翻匀', 3),
  (@r, 6, '大肠码入盘中，浇尽余汁，带姜丝上桌', 2);

-- ========== 5. 四喜丸子 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('四喜丸子', '鲁菜宴席四大名件，取福禄寿喜之意。四个拳头大的丸子先炸后煨，酱红油亮，筷子一夹即散，肉香浑厚，老人孩子都夹得动。', NULL, 30, 45, 75, 2, 4, '鲁菜', '经典,宴客,鲁菜名菜', 1, TRUE, 171, 320, 18, 25, 6, '肉馅三分肥七分瘦，搅打上劲才不散；高汤煨够半小时，丸子吸饱汤汁才绵软。', '咸鲜浓香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪前腿肉馅', '600', 'g', TRUE, 1, '/api/ingredients/zhuroumo.jpg'),
  (@r, '鸡蛋', '1', '个', TRUE, 2, '/api/ingredients/jidan.jpg'),
  (@r, '淀粉', '40', 'g', TRUE, 3, '/api/ingredients/dianfen.jpg'),
  (@r, '大葱', '40', 'g', TRUE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 7, '/api/ingredients/laochou.jpg'),
  (@r, '冰糖', '10', 'g', TRUE, 8, '/api/ingredients/bingtang.jpg'),
  (@r, '高汤', '300', 'ml', TRUE, 9, '/api/ingredients/gaotang.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 10, '/api/ingredients/liaojiu.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 12, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '肉馅加盐、鸡蛋、料酒朝一个方向搅打上劲，下淀粉和葱姜末拌匀', 10),
  (@r, 2, '手蘸水把肉馅团成四个拳头大的丸子，表面抹老抽上色', 8),
  (@r, 3, '油烧七成热，下丸子中火炸至表皮红硬，捞出控油', 8),
  (@r, 4, '砂锅底垫姜片，码入丸子，加高汤、生抽、冰糖，烧开转微火煨30分钟', 35),
  (@r, 5, '取出丸子摆盘，原汁大火烧开，水淀粉勾浓芡浇在丸子上', 4);

-- ========== 6. 德州扒鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('德州扒鸡', '德州名吃，相传曾是御用贡品。整鸡别翅盘腿入香料老汤，微火慢焖，热中一抖骨肉分离，五香透骨，烂而不散。', NULL, 30, 120, 150, 3, 4, '鲁菜', '经典,卤味,宴客,鲁菜名菜', 1, TRUE, 208, 300, 30, 18, 3, '焖鸡全程只用微火，汤面似开非开；出锅前连汤浸焖半小时，皮不破而味入骨。', '五香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '三黄鸡', '1', '只(约1000g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '生抽', '60', 'ml', TRUE, 2, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '20', 'ml', TRUE, 3, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '20', 'g', TRUE, 4, '/api/ingredients/baitang.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 5, '/api/ingredients/liaojiu.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '40', 'g', TRUE, 7, '/api/ingredients/dacong.jpg'),
  (@r, '八角', '5', 'g', TRUE, 8, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '3', 'g', TRUE, 9, '/api/ingredients/guipi.jpg'),
  (@r, '花椒', '2', 'g', TRUE, 10, '/api/ingredients/huajiao.jpg'),
  (@r, '丁香', '3', '粒', FALSE, 11, '/api/ingredients/dingxiang.jpg'),
  (@r, '清水', '800', 'ml', TRUE, 12, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡从颈部开口，两翅从口中别出，两腿交叉盘进腹腔定型', 10),
  (@r, 2, '表皮抹生抽和白糖腌20分钟，风干', 20),
  (@r, 3, '油烧七成热，手提鸡头淋炸至通体金红，捞出', 5),
  (@r, 4, '砂锅底铺姜葱与八角桂皮花椒，放鸡，倒入生抽老抽料酒清水烧开，转微火加盖焖110分钟', 115),
  (@r, 5, '连汤晾30分钟浸味，装盘浇原汁，拆食不掉骨肉', 30);

-- ========== 7. 把子肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('把子肉', '济南人下饭的硬菜，俗传与桃园结义有关。厚切五花肉用酱油甜面酱腌透，砂锅慢炖到肥肉颤而不散，咸甜酱香渗进肉纹。', NULL, 75, 70, 145, 2, 4, '鲁菜', '经典,下饭,卤味,鲁菜名菜', 1, TRUE, 310, 410, 18, 35, 5, '肉要切一指厚、巴掌宽才配称把子；炖足一小时再原汤泡半小时，肥油逼净、酱香入骨。', '酱香咸甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '800', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '甜面酱', '40', 'g', TRUE, 2, '/api/ingredients/tianmianjiang.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 3, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '15', 'ml', TRUE, 4, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '20', 'g', TRUE, 5, '/api/ingredients/baitang.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '30', 'g', TRUE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '八角', '4', 'g', TRUE, 9, '/api/ingredients/bajiao.jpg'),
  (@r, '清水', '300', 'ml', TRUE, 10, '/api/ingredients/qingshui.jpg'),
  (@r, '盐', '2', 'g', FALSE, 11, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉切成巴掌宽、一指厚的大片', 8),
  (@r, 2, '加生抽、甜面酱、料酒、白糖抓匀，腌1小时', 60),
  (@r, 3, '油烧四成热下肉片，中火煎至两面金黄、肥肉出油', 6),
  (@r, 4, '砂锅底铺姜片葱段八角，码入肉片，倒腌汁加清水烧开，转微火炖60分钟', 62),
  (@r, 5, '加盐调味，加盖再焖10分钟，连锅端上桌', 10);

-- ========== 8. 锅塌豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('锅塌豆腐', '济南传统锅塌菜，塌字写尽做法。豆腐拖蛋挂粉两面煎塌，再入高汤收塌入味，蛋香豆香相融，嫩到筷尖发颤。', NULL, 15, 20, 35, 1, 3, '鲁菜', '家常,经典,鲁菜名菜', 1, TRUE, 131, 310, 20, 18, 15, '豆腐片好必须拍干粉再拖蛋，蛋液才挂得住；焖时用中火收到见锅底，汤味全进豆腐里。', '咸鲜蛋香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '豆腐', '400', 'g', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '鸡蛋', '2', '个', TRUE, 2, '/api/ingredients/jidan.jpg'),
  (@r, '面粉', '30', 'g', TRUE, 3, '/api/ingredients/mianfen.jpg'),
  (@r, '高汤', '150', 'ml', TRUE, 4, '/api/ingredients/gaotang.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '料酒', '10', 'ml', TRUE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '大葱', '15', 'g', TRUE, 7, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '白糖', '3', 'g', TRUE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '2', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '豆腐切五毫米厚大片机干，鸡蛋加1g盐打散', 8),
  (@r, 2, '豆腐拍一层面粉，拖匀蛋液', 5),
  (@r, 3, '平底锅下油，中小火煎至两面金黄发塌，盛出', 8),
  (@r, 4, '锅留底油，下葱姜末炒香，豆腐回锅，加高汤、生抽、料酒、白糖，中火焖5分钟', 6),
  (@r, 5, '收到汤汁浓稠裹住豆腐，撒葱花出锅', 3);

-- ========== 9. 拔丝地瓜 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('拔丝地瓜', '鲁菜拔丝绝活，宴席上的压轴甜菜。红薯炸到外壳酥、内瓤沙，水炒糖浆熬成香油色，筷子一提金丝万缕，趁热蘸凉水吃。', NULL, 10, 20, 30, 3, 4, '鲁菜', '经典,甜品,宴客,鲁菜名菜', 1, TRUE, 204, 360, 1.5, 12, 60, '糖浆熬到大泡转小泡、色如香油，筷子蘸糖滴入凉水即刻变硬拉丝，才是下地瓜的时机。', '香甜脆硬');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '红薯', '500', 'g', TRUE, 1, '/api/ingredients/tudou.jpg'),
  (@r, '白糖', '150', 'g', TRUE, 2, '/api/ingredients/baitang.jpg'),
  (@r, '清水', '60', 'ml', TRUE, 3, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 4, '/api/ingredients/shiyongyou.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 5, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '红薯去皮切成滚刀块，拍去表面水分', 6),
  (@r, 2, '油烧五成热下红薯，中火炸6分钟至筷子能透，捞出', 6),
  (@r, 3, '升油温至八成热复炸1分钟，外壳硬挺金黄，捞出', 2),
  (@r, 4, '净锅下白糖和清水，小火慢熬至大泡转小泡、色如香油', 4),
  (@r, 5, '立刻倒红薯翻勺挂匀糖浆，盘抹薄香油，端凉开水一碗同上桌', 2);

-- ========== 10. 坛子肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('坛子肉', '济南老馆子的密封绝活。五花肉块炸后入小坛，加酱油香料封坛慢煨两小时，开坛香气冲屋，肉烂若凝脂，酱浓挂勺。', NULL, 30, 130, 160, 3, 4, '鲁菜', '经典,宴客,卤味,鲁菜名菜', 1, TRUE, 190, 430, 16, 38, 4, '坛口一定要封严，中途揭盖气走一半；微火养足两小时，肉才酥烂而块形不散。', '浓酱酥烂');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '700', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '酱油', '50', 'ml', TRUE, 2, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 3, '/api/ingredients/laochou.jpg'),
  (@r, '冰糖', '15', 'g', TRUE, 4, '/api/ingredients/bingtang.jpg'),
  (@r, '料酒', '25', 'ml', TRUE, 5, '/api/ingredients/liaojiu.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '30', 'g', TRUE, 7, '/api/ingredients/dacong.jpg'),
  (@r, '八角', '3', 'g', TRUE, 8, '/api/ingredients/bajiao.jpg'),
  (@r, '清水', '100', 'ml', TRUE, 9, '/api/ingredients/qingshui.jpg'),
  (@r, '盐', '2', 'g', FALSE, 10, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉切成麻将块大小，沸水焯5分钟去血沫，捞出控干', 8),
  (@r, 2, '抹老抽晾干，入六成热油炸至外壳红硬，捞出', 6),
  (@r, 3, '小坛底垫姜块、葱段、八角，码入肉块，倒酱油、料酒、冰糖、清水', 8),
  (@r, 4, '保鲜膜封严坛口加盖，微火煨120分钟', 120),
  (@r, 5, '开坛尝味补盐，整坛上桌，趁热分食', 3);

-- ========== 11. 单县羊肉汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('单县羊肉汤', '菏泽单县头道汤，名唱到京津。羊骨羊肉大火冲煮两小时，汤白如奶不见渣，碗底只撒盐葱，肉香一口醇到眉毛。', NULL, 75, 130, 205, 2, 6, '鲁菜', '经典,汤羹,冬令,鲁菜名菜', 1, TRUE, 277, 160, 14, 10, 2, '汤要白全靠火：全程大火滚冲，中途不添冷水；羊肉回锅前不腌不酱，原汁才正。', '咸鲜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '羊肉', '500', 'g', TRUE, 1, '/api/ingredients/yangrou.jpg'),
  (@r, '羊骨', '500', 'g', TRUE, 2, '/api/ingredients/yangrou.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '40', 'g', TRUE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '花椒', '5', 'g', TRUE, 5, '/api/ingredients/huajiao.jpg'),
  (@r, '白萝卜', '300', 'g', FALSE, 6, '/api/ingredients/bailuobo.jpg'),
  (@r, '盐', '6', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '2', 'g', TRUE, 8, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '香菜', '15', 'g', TRUE, 9, '/api/ingredients/xiangcai.jpg'),
  (@r, '小葱', '15', 'g', TRUE, 10, '/api/ingredients/xiaocong.jpg'),
  (@r, '清水', '3000', 'ml', TRUE, 11, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '羊骨砸断，羊肉切大块，一同冷水浸泡1小时去血', 60),
  (@r, 2, '沸水煮10分钟撇尽浮沫，捞出冲净', 10),
  (@r, 3, '桶内加清水，下肉骨、姜葱，花椒装料包投入，大火滚煮2小时，汤色乳白如奶，期间不断撇沫', 120),
  (@r, 4, '捞出羊肉晾凉切薄片，萝卜片下汤锅煮熟', 10),
  (@r, 5, '碗底放盐、胡椒粉、葱花香菜，铺肉片，冲入滚汤即成', 3);

-- ========== 12. 木须肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('木须肉', '北方人最熟的脸，鲁菜小炒经典。木须是鸡蛋的雅称，肉片鸡蛋黑木耳顶黄瓜同炒，鲜香脆嫩，一碗米饭不够。', NULL, 15, 10, 25, 1, 3, '鲁菜', '家常,快手,下饭', 1, TRUE, 143, 230, 16, 15, 7, '鸡蛋半凝固就盛出，黄瓜最后下锅；全程大火快炒，出锅前再淋香油。', '咸鲜清爽');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪里脊', '150', 'g', TRUE, 1, '/api/ingredients/zhuliji.jpg'),
  (@r, '鸡蛋', '3', '个', TRUE, 2, '/api/ingredients/jidan.jpg'),
  (@r, '水发木耳', '60', 'g', TRUE, 3, '/api/ingredients/muer.jpg'),
  (@r, '黄瓜', '1', '根', TRUE, 4, '/api/ingredients/huanggua.jpg'),
  (@r, '大葱', '10', 'g', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '10', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '5', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '12', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '料酒', '8', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '淀粉', '5', 'g', TRUE, 10, '/api/ingredients/dianfen.jpg'),
  (@r, '盐', '3', 'g', TRUE, 11, '/api/ingredients/yan.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 12, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '里脊切薄片，用料酒、淀粉、1g盐抓腌10分钟', 10),
  (@r, 2, '鸡蛋加1g盐打散，热油炒至半凝固盛出', 2),
  (@r, 3, '补油15ml，大火滑炒肉片至变色盛出', 2),
  (@r, 4, '下葱姜蒜爆香，先放木耳黄瓜片炒30秒断生', 1),
  (@r, 5, '肉片鸡蛋回锅，加生抽和余盐大火翻匀，淋香油出锅', 2);

-- ========== 13. 葱烧海参 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('葱烧海参', '胶东葱烧菜的扛鼎者，海参本无味，全靠葱油喂。大葱炸到焦香，海参入鸡汤煨透，浓芡亮汁裹身，葱香压过海腥。', NULL, 30, 20, 50, 3, 2, '鲁菜', '经典,宴客,海鲜,鲁菜名菜', 1, TRUE, 123, 150, 12, 8, 6, '葱段必须炸到焦黄发干才有葱油魂；海参先煨入味再勾芡，芡要分两次挂才亮。', '葱香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '海参', '500', 'g', TRUE, 1, '/api/ingredients/yuchi.jpg'),
  (@r, '大葱', '80', 'g', TRUE, 2, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '鸡清汤', '200', 'ml', TRUE, 4, '/api/ingredients/gaotang.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '5', 'ml', TRUE, 6, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '3', 'g', TRUE, 7, '/api/ingredients/baitang.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '淀粉', '10', 'g', TRUE, 9, '/api/ingredients/dianfen.jpg'),
  (@r, '猪油', '30', 'g', TRUE, 10, '/api/ingredients/zhuyou.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 11, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '水发海参切大条，沸水加姜葱料酒焯2分钟去腥，捞起沥干', 8),
  (@r, 2, '葱白切五厘米段拍松，三成热猪油慢炸至两面焦黄，盛出', 8),
  (@r, 3, '下海参略炒，倒鸡清汤、生抽、老抽、白糖，放葱段小火煨5分钟', 6),
  (@r, 4, '水淀粉分两次勾芡，汤汁浓亮紧裹海参，淋香油装盘', 3);

-- ========== 14. 糟溜鱼片 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('糟溜鱼片', '孔府传出的鲁菜雅味，糟香清雅。桂鱼片浆滑油至刚断生，入香糟卤调的白汁里一溜，嫩若豆腐，糟香绕舌三日。', NULL, 25, 10, 35, 3, 3, '鲁菜', '经典,河鲜,宴客,鲁菜名菜', 1, TRUE, 216, 180, 20, 7, 8, '滑油只能三四成热，鱼片白而刚卷就捞；糟卤下锅微开即勾芡，久沸糟香尽散。', '糟香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '桂鱼', '1', '条(约600g)', TRUE, 1, '/api/ingredients/guiyu.jpg'),
  (@r, '糟卤', '60', 'ml', TRUE, 2, '/api/ingredients/lushui.jpg'),
  (@r, '冬笋', '60', 'g', TRUE, 3, '/api/ingredients/dongsun.jpg'),
  (@r, '水发木耳', '30', 'g', FALSE, 4, '/api/ingredients/muer.jpg'),
  (@r, '鸡蛋清', '1', '个', TRUE, 5, '/api/ingredients/jidanqing.jpg'),
  (@r, '淀粉', '20', 'g', TRUE, 6, '/api/ingredients/dianfen.jpg'),
  (@r, '高汤', '200', 'ml', TRUE, 7, '/api/ingredients/gaotang.jpg'),
  (@r, '白糖', '6', 'g', TRUE, 8, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '3', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '料酒', '10', 'ml', TRUE, 10, '/api/ingredients/liaojiu.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '桂鱼去骨起两片肉，斜刀切厚片，漂净血水', 8),
  (@r, 2, '鱼片用1g盐、料酒抓至发黏，下蛋清和淀粉上浆', 8),
  (@r, 3, '三四成热油下滑开鱼片，肉色转白即捞，冬笋切薄片焯水', 3),
  (@r, 4, '锅下高汤、糟卤、白糖和余盐烧开，放笋片木耳', 2),
  (@r, 5, '鱼片回锅微开，水淀粉溜勾薄芡，淋明油出锅', 2);

-- ========== 15. 扒原壳鲍鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('扒原壳鲍鱼', '孔府扒菜看家手艺。鲜活鲍鱼煮熟取肉切片，回填原壳，鸡清汤小火慢扒勾芡，壳在原味也在鲜，一粒一味清醇。', NULL, 30, 15, 45, 3, 2, '鲁菜', '经典,宴客,海鲜,鲁菜名菜', 1, TRUE, 300, 130, 17, 3, 6, '鲍鱼煮过头就嚼不动，沸汤三分钟即捞；扒菜要锅体倾斜推芡，汁明芡亮方能成扒。', '咸鲜清醇');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鲜活鲍鱼', '6', '只', TRUE, 1, '/api/ingredients/baoyu.jpg'),
  (@r, '鸡清汤', '200', 'ml', TRUE, 2, '/api/ingredients/gaotang.jpg'),
  (@r, '火腿', '20', 'g', FALSE, 3, '/api/ingredients/huotui.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '15', 'g', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '8', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '2', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '白糖', '2', 'g', FALSE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '淀粉', '12', 'g', TRUE, 10, '/api/ingredients/dianfen.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 11, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鲍鱼刷净外壳，沸水加姜葱煮3分钟，取肉去内脏和边黑', 10),
  (@r, 2, '壳留用排入盘中，鲍鱼肉切薄片覆回壳内', 6),
  (@r, 3, '锅下鸡清汤、生抽、料酒、盐、白糖烧开，撇净浮沫', 3),
  (@r, 4, '倾锅推入水淀粉扒勾亮芡，淋在鲍鱼上，撒火腿末', 3);

-- ========== 16. 博山炸肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('博山炸肉', '淄博博山的年节硬菜，也是济青高速服务区的一绝。里脊切条腌足，裹红薯粉糊炸到外壳酥脆内里咸香，趁热撒椒盐。', NULL, 25, 15, 40, 2, 4, '鲁菜', '经典,小吃,鲁菜名菜', 1, TRUE, 180, 300, 20, 18, 12, '面糊调到手提成线不断；肉条必须复炸一次，外壳才咬得脆响、里面还留着汁。', '咸香酥脆');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪里脊', '400', 'g', TRUE, 1, '/api/ingredients/zhuliji.jpg'),
  (@r, '红薯淀粉', '80', 'g', TRUE, 2, '/api/ingredients/dianfen.jpg'),
  (@r, '鸡蛋', '1', '个', TRUE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '酱油', '15', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '料酒', '10', 'ml', TRUE, 5, '/api/ingredients/liaojiu.jpg'),
  (@r, '花椒', '3', 'g', TRUE, 6, '/api/ingredients/huajiao.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '15', 'g', TRUE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '盐', '3', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 10, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '里脊切一指粗肉条，加酱油、料酒、盐、姜葱末腌20分钟', 20),
  (@r, 2, '挑去姜葱，下鸡蛋和红薯淀粉，加清水60ml抓成糊，肉条挂匀', 6),
  (@r, 3, '油烧六成热，逐条下锅炸至浮起定型、外壳微黄，捞出', 5),
  (@r, 4, '油温升至八成热复炸至金黄酥脆，捞出控油', 2),
  (@r, 5, '花椒与盐2g干锅小火炒香，碾成椒盐，撒肉条上桌', 3);

-- ========== 17. 辣炒蛤蜊 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('辣炒蛤蜊', '胶东海边的灵魂下酒菜。蛤蜊吐净沙，旺火下干辣椒姜蒜爆炒，啤酒一烹盖子一焖，壳开口肉带卤汁，一盘鲜辣半天闲话。', NULL, 125, 8, 133, 1, 3, '鲁菜', '家常,海鲜,下饭,胶东名菜', 1, TRUE, 271, 105, 11, 4, 6, '吐沙必须用没过蛤蜊的淡盐水养足两小时；炒到刚开口就收火，开口后再焖肉就老缩了。', '香辣咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '蛤蜊', '700', 'g', TRUE, 1, '/api/ingredients/tianluo.jpg'),
  (@r, '干红辣椒', '8', 'g', TRUE, 2, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '2', 'g', TRUE, 3, '/api/ingredients/huajiao.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '大葱', '20', 'g', TRUE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '啤酒', '100', 'ml', TRUE, 7, '/api/ingredients/pijiu.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '2', 'g', FALSE, 9, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '25', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 11, '/api/ingredients/xiangcai.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '蛤蜊入没过身面的淡盐水养2小时吐净沙，刷洗外壳沥干', 120),
  (@r, 2, '干辣椒切段，姜蒜切片，葱切段', 5),
  (@r, 3, '热油下花椒、干辣椒、姜蒜，大火爆出香辣味', 1),
  (@r, 4, '倒蛤蜊烹啤酒，加盖大火焖2分钟至壳全开', 2),
  (@r, 5, '下葱段淋生抽翻匀，撒香菜出锅', 1);
