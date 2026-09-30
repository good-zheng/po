-- 由 seed/recipes-min.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 闽菜，共 17 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 佛跳墙 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('佛跳墙', '闽菜头牌，相传坛启荤香飘四邻，佛闻弃禅跳墙来。家常版以老母鸡、排骨吊汤，海参鲍鱼分层入坛，文火慢煨至汤色金浓。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/min-foitiaoqiang.jpg', 60, 180, 240, 3, 6, '闽菜', '经典,宴客,海鲜,闽菜名菜', 1, TRUE, 174, 350, 28, 20, 6, '各路料分别焯水、泡发到位再分层码入坛，高汤滤净才注入，全程微火煨，急火则汤浊失味。', '咸鲜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '老母鸡', '半', '只(约500g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '排骨', '300', 'g', TRUE, 2, '/api/ingredients/zhupaigu.jpg'),
  (@r, '鲜活鲍鱼', '6', '只', TRUE, 3, '/api/ingredients/baoyu.jpg'),
  (@r, '海参', '3', '只', TRUE, 4, '/api/ingredients/yuchi.jpg'),
  (@r, '干香菇', '8', '朵', TRUE, 5, '/api/ingredients/ganxianggu.jpg'),
  (@r, '冬笋', '150', 'g', FALSE, 6, '/api/ingredients/dongsun.jpg'),
  (@r, '高汤', '1500', 'ml', TRUE, 7, '/api/ingredients/gaotang.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '干荷叶', '1', '张', FALSE, 9, '/api/ingredients/ganye.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 10, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 11, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '3', 'g', TRUE, 12, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '老母鸡、排骨冷水下锅焯去血沫，捞出洗净', 15),
  (@r, 2, '干香菇、冬笋温水泡发，海参泡软切段焯水', 120),
  (@r, 3, '鲍鱼去壳刷净，与鸡块、排骨分层码入陶坛', 10),
  (@r, 4, '高汤加姜、料酒、生抽烧开，滤净注入坛中', 8),
  (@r, 5, '坛口盖荷叶封严，微火煨至汤色浓稠', 120);

-- ========== 2. 荔枝肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('荔枝肉', '福州宴席老菜，猪瘦肉剞十字花刀后炸成荔枝卷，外裹糖醋汁红亮酸甜，缀以荸荠，形似荔珠而得名。', NULL, 25, 12, 37, 2, 4, '闽菜', '经典,酸甜,猪肉,福州名菜', 1, TRUE, 133, 420, 26, 26, 20, '剞花刀要切透而不切断，炸时肉片自然卷成荔球；糖醋汁先调好再下锅，二次裹汁才亮。', '酸甜爽口');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪瘦肉', '400', 'g', TRUE, 1, '/api/ingredients/zhushourou.jpg'),
  (@r, '荸荠', '100', 'g', FALSE, 2, '/api/ingredients/ou.jpg'),
  (@r, '红薯淀粉', '80', 'g', TRUE, 3, '/api/ingredients/dianfen.jpg'),
  (@r, '白糖', '40', 'g', TRUE, 4, '/api/ingredients/baitang.jpg'),
  (@r, '香醋', '30', 'ml', TRUE, 5, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '番茄酱', '30', 'g', FALSE, 7, '/api/ingredients/honglajiao.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', TRUE, 9, '/api/ingredients/xiaocong.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪瘦肉切厚片，两面剞十字花刀再改方块', 10),
  (@r, 2, '加清水、生抽、姜汁抓腌10分钟，裹匀淀粉', 10),
  (@r, 3, '调糖醋汁：白糖、香醋、番茄酱、生抽搅匀', 3),
  (@r, 4, '油烧七成热下肉块，大火炸至卷起金黄捞出', 4),
  (@r, 5, '升温复炸至外壳酥脆，捞出沥油', 2),
  (@r, 6, '锅留底油下糖醋汁烧沸，倒肉块荸荠翻匀裹汁', 4);

-- ========== 3. 醉排骨 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('醉排骨', '福州老巷名味，猪肋排先炸后拌，以黄酒、蒜末、糖醋调成醉汁，趁热裹匀冷后入味，酒香酸甜而肉质外酥内嫩。', NULL, 30, 10, 40, 2, 4, '闽菜', '经典,宴客,排骨,福州名菜', 1, TRUE, 235, 450, 24, 34, 12, '醉汁要趁排骨刚出锅滚烫时拌，热才吸得进去；黄酒要用福建老酒，香气足而不发苦。', '酸甜酒香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪肋排', '500', 'g', TRUE, 1, '/api/ingredients/zhupaigu.jpg'),
  (@r, '黄酒', '40', 'ml', TRUE, 2, '/api/ingredients/huangjiu.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '白糖', '25', 'g', TRUE, 4, '/api/ingredients/baitang.jpg'),
  (@r, '香醋', '15', 'ml', TRUE, 5, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '鸡蛋', '1', '个', TRUE, 7, '/api/ingredients/jidan.jpg'),
  (@r, '红薯淀粉', '40', 'g', TRUE, 8, '/api/ingredients/dianfen.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 9, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', FALSE, 10, '/api/ingredients/xiaocong.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '排骨斩小块，加生抽、黄酒、姜片腌30分钟', 30),
  (@r, 2, '腌好的排骨裹蛋液和红薯淀粉', 6),
  (@r, 3, '油烧六成热下排骨，中火炸至表面定型', 4),
  (@r, 4, '升温七成热，大火复炸至金黄酥脆沥油', 3),
  (@r, 5, '蒜末加白糖、香醋、生抽与黄酒调成醉汁', 3),
  (@r, 6, '热排骨倒入醉汁盆，趁热翻拌裹匀晾凉', 3);

-- ========== 4. 姜母鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('姜母鸭', '闽南冬令进补名菜，老姜剁米用麻油炒香，与土鸭同焖，鸭肉酥烂汤汁带姜辣酒香，一锅热气驱寒。', NULL, 20, 50, 70, 2, 4, '闽菜', '经典,时令,鸭肉,闽菜名菜', 1, TRUE, 135, 400, 30, 26, 6, '老姜要剁碎炒至干香再下鸭，麻油全程不能糊；加黄酒焖要小火，火大姜苦而出不了香。', '姜香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '土鸭', '半', '只(约900g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '老姜', '150', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '芝麻香油', '50', 'ml', TRUE, 3, '/api/ingredients/xiangyou.jpg'),
  (@r, '黄酒', '80', 'ml', TRUE, 4, '/api/ingredients/huangjiu.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', FALSE, 6, '/api/ingredients/laochou.jpg'),
  (@r, '冰糖', '15', 'g', TRUE, 7, '/api/ingredients/bingtang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 8, '/api/ingredients/dasuan.jpg'),
  (@r, '高汤', '500', 'ml', TRUE, 9, '/api/ingredients/gaotang.jpg'),
  (@r, '盐', '2', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '小葱', '2', '根', FALSE, 11, '/api/ingredients/xiaocong.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '土鸭斩块焯去血沫，老姜去皮剁成姜米', 15),
  (@r, 2, '麻油下锅小火，入姜米炒至干香金黄', 5),
  (@r, 3, '下鸭块转中火煸至皮面收紧出油', 6),
  (@r, 4, '烹黄酒、生抽、老抽，加冰糖与高汤烧开', 5),
  (@r, 5, '转小火加盖焖至鸭肉酥烂', 40),
  (@r, 6, '开盖大火收至汤汁浓，撒葱花装盘', 4);

-- ========== 5. 海蛎煎 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('海蛎煎', '闽南街头灵魂小吃，海蛎拌入番薯粉浆，蛋液裹边煎至焦香，蘸甜辣酱外酥内糯，厦门泉州夜宵摊必点。', NULL, 15, 10, 25, 1, 2, '闽菜', '家常,小吃,海鲜,闽南名吃', 1, TRUE, 167, 320, 15, 18, 25, '粉浆要调得稀，下锅前才拌入海蛎和蒜苗；火要大煎才起泡边脆，翻面一次定形别乱铲。', '咸鲜软糯');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '海蛎', '200', 'g', TRUE, 1, '/api/ingredients/tianluo.jpg'),
  (@r, '红薯淀粉', '60', 'g', TRUE, 2, '/api/ingredients/dianfen.jpg'),
  (@r, '鸡蛋', '2', '个', TRUE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '青蒜苗', '30', 'g', TRUE, 4, '/api/ingredients/qingsuan.jpg'),
  (@r, '清水', '80', 'ml', TRUE, 5, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 6, '/api/ingredients/shiyongyou.jpg'),
  (@r, '生抽', '8', 'ml', FALSE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '1', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '辣椒油', '20', 'ml', FALSE, 9, '/api/ingredients/lajiaoyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '海蛎冲洗沥干，青蒜苗切段', 8),
  (@r, 2, '红薯淀粉加清水调稀浆，拌入海蛎蒜苗盐', 4),
  (@r, 3, '平底锅下油烧热，倒入浆料摊平', 2),
  (@r, 4, '淋蛋液铺面，中火煎至边缘起脆泡', 3),
  (@r, 5, '翻面再煎半分钟至两面金黄，配蘸汁上桌', 2);

-- ========== 6. 厦门沙茶面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('厦门沙茶面', '厦门华侨带回的南洋味，沙茶酱调出橙红汤头，配碱面与虾、贝、豆腐，汤浓带花生微辣，是厦门人的早午餐魂。', NULL, 20, 25, 45, 2, 2, '闽菜', '经典,小吃,面食,厦门名吃', 1, TRUE, 200, 480, 20, 20, 55, '沙茶酱先用油炒散再冲汤，炒过香气才化得开；汤要滚着下面，面断生即起否则糊汤。', '咸鲜微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '碱水面', '300', 'g', TRUE, 1, '/api/ingredients/jianshuimian.jpg'),
  (@r, '沙茶酱', '50', 'g', TRUE, 2, '/api/ingredients/zhimajiang.jpg'),
  (@r, '河虾仁', '100', 'g', FALSE, 3, '/api/ingredients/hexiaren.jpg'),
  (@r, '蛤蜊', '200', 'g', FALSE, 4, '/api/ingredients/tianluo.jpg'),
  (@r, '嫩豆腐', '150', 'g', FALSE, 5, '/api/ingredients/doufu.jpg'),
  (@r, '高汤', '800', 'ml', TRUE, 6, '/api/ingredients/gaotang.jpg'),
  (@r, '花生米', '30', 'g', FALSE, 7, '/api/ingredients/huasheng.jpg'),
  (@r, '大蒜', '10', 'g', TRUE, 8, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 9, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '小葱', '2', '根', TRUE, 11, '/api/ingredients/xiaocong.jpg'),
  (@r, '食用油', '15', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '虾仁开背，蛤蜊吐沙洗净，豆腐切块焯水', 20),
  (@r, 2, '锅下油，中火炒香姜蒜末与沙茶酱', 3),
  (@r, 3, '冲入高汤大火烧开，转小火熬出沙茶汤头', 12),
  (@r, 4, '另锅水沸下碱面，大火煮至断生捞入碗中', 3),
  (@r, 5, '汤中下虾仁蛤蜊煮至开口，连豆腐倒入面碗', 4),
  (@r, 6, '撒花生碎与葱花即成', 2);

-- ========== 7. 福州鱼丸 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('福州鱼丸', '福州没有鱼丸不成席，海鳗剔肉打浆做皮，包入猪肉馅，挤丸入温水定型，咬开爆汁皮弹馅香，是闽江边的手艺。', NULL, 45, 20, 65, 3, 4, '闽菜', '经典,海鲜,小吃,福州名菜', 1, TRUE, 201, 260, 18, 12, 18, '鱼肉要加盐水顺一个方向搅上劲才起胶做皮，水温八十度下丸养熟，沸水滚会冲破丸皮。', '咸鲜弹嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '海鳗', '400', 'g', TRUE, 1, '/api/ingredients/shanyupian.jpg'),
  (@r, '猪后腿肉馅', '150', 'g', TRUE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '清水', '200', 'ml', TRUE, 3, '/api/ingredients/qingshui.jpg'),
  (@r, '盐', '5', 'g', TRUE, 4, '/api/ingredients/yan.jpg'),
  (@r, '鸡蛋清', '1', '个', FALSE, 5, '/api/ingredients/jidanqing.jpg'),
  (@r, '红薯淀粉', '30', 'g', TRUE, 6, '/api/ingredients/dianfen.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', TRUE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '高汤', '600', 'ml', TRUE, 9, '/api/ingredients/gaotang.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 10, '/api/ingredients/xiangyou.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 11, '/api/ingredients/baihujiaofen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '海鳗去皮剔骨取净肉，绞成鱼肉泥', 15),
  (@r, 2, '鱼肉加盐水顺一个方向搅打至上劲成胶', 15),
  (@r, 3, '肉馅加生抽、姜末、葱花搅匀，团成小丸', 10),
  (@r, 4, '虎口挤鱼胶包肉馅成丸，入温水定型', 10),
  (@r, 5, '高汤烧开下鱼丸，小火养熟至浮起', 12),
  (@r, 6, '撒葱花淋香油，连汤盛入碗中', 2);

-- ========== 8. 太平燕 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('太平燕', '福州婚寿宴席必备的太平燕，番薯粉与猪瘦肉千锤打成薄燕皮，裹肉馅成燕，配鸭蛋入汤，取平安团圆之意。', NULL, 50, 20, 70, 3, 4, '闽菜', '宴客,汤羹,小吃,福州名菜', 1, TRUE, 252, 300, 20, 14, 24, '燕皮要用木槌把瘦肉和番薯粉锤成纸才弹韧，包馅留一指宽边捏出燕尾；汤必须清澈见底。', '清鲜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪瘦肉', '250', 'g', TRUE, 1, '/api/ingredients/zhushourou.jpg'),
  (@r, '红薯淀粉', '150', 'g', TRUE, 2, '/api/ingredients/dianfen.jpg'),
  (@r, '猪后腿肉馅', '150', 'g', TRUE, 3, '/api/ingredients/zhuroumo.jpg'),
  (@r, '鸭蛋', '3', '个', TRUE, 4, '/api/ingredients/jidan.jpg'),
  (@r, '高汤', '800', 'ml', TRUE, 5, '/api/ingredients/gaotang.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', TRUE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '3', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 10, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪瘦肉切薄片，与红薯淀粉铺案用木槌反复锤打', 20),
  (@r, 2, '锤成薄如纸的燕皮，切成方片', 15),
  (@r, 3, '肉馅加生抽、姜末搅上劲，包入燕皮捏成燕尾', 12),
  (@r, 4, '鸭蛋煮熟去壳，高汤烧沸下燕丸', 10),
  (@r, 5, '燕丸浮起煮2分钟，放入对半鸭蛋', 4),
  (@r, 6, '撒葱花淋香油即成', 2);

-- ========== 9. 闽南卤面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('闽南卤面', '漳州泉州年节必备，碱面入锅与卤汤同煮，勾出稠亮芡汁，配虾、蛋、卤肉与豆芽，浇上蒜蓉醋，一碗浓滑热香。', NULL, 25, 20, 45, 2, 4, '闽菜', '家常,宴客,汤面,闽南名吃', 1, TRUE, 301, 460, 22, 16, 58, '面要另锅煮散再入卤，边推边勾薄芡成琉璃芡才不糊底；起锅后淋蒜醋打蛋花提香。', '咸鲜浓滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '碱水面', '400', 'g', TRUE, 1, '/api/ingredients/jianshuimian.jpg'),
  (@r, '五花肉', '150', 'g', TRUE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '河虾仁', '80', 'g', FALSE, 3, '/api/ingredients/hexiaren.jpg'),
  (@r, '黄豆芽', '100', 'g', FALSE, 4, '/api/ingredients/huangdouya.jpg'),
  (@r, '鸡蛋', '2', '个', TRUE, 5, '/api/ingredients/jidan.jpg'),
  (@r, '高汤', '900', 'ml', TRUE, 6, '/api/ingredients/gaotang.jpg'),
  (@r, '水淀粉', '60', 'ml', TRUE, 7, '/api/ingredients/dianfen.jpg'),
  (@r, '干香菇', '6', '朵', TRUE, 8, '/api/ingredients/ganxianggu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 10, '/api/ingredients/dasuan.jpg'),
  (@r, '香醋', '10', 'ml', FALSE, 11, '/api/ingredients/xiangcu.jpg'),
  (@r, '盐', '2', 'g', TRUE, 12, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉切丝，干香菇泡发切丝，豆芽洗净', 15),
  (@r, 2, '锅下肉丝小火煸出油，下香菇丝蒜末炒香', 5),
  (@r, 3, '冲入高汤大火烧开，加盐与生抽调味', 6),
  (@r, 4, '另锅沸水煮碱面至八成熟，捞出沥干', 6),
  (@r, 5, '面入卤汤转小火推散，勾水淀粉成浓亮芡', 5),
  (@r, 6, '淋蛋花撒豆芽，浇蒜醋汁翻匀出锅', 3);

-- ========== 10. 建瓯板鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('建瓯板鸭', '建瓯板鸭已有千余年，冬季把麻鸭剖开压扁风干成板，吃时蒸透斩件，皮脆肉紧咸香带腊味，佐酒最宜。', NULL, 30, 60, 90, 2, 6, '闽菜', '经典,宴客,腊味,闽北名菜', 1, TRUE, 122, 380, 30, 28, 2, '板鸭先用温水泡半小时退咸，加姜片黄酒上锅蒸透才回软，斩件要顺肉纹横切而不散。', '咸香腊味');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '板鸭', '半', '只(约600g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '黄酒', '30', 'ml', TRUE, 3, '/api/ingredients/huangjiu.jpg'),
  (@r, '冰糖', '10', 'g', FALSE, 4, '/api/ingredients/bingtang.jpg'),
  (@r, '小葱', '3', '根', TRUE, 5, '/api/ingredients/xiaocong.jpg'),
  (@r, '清水', '1000', 'ml', TRUE, 6, '/api/ingredients/qingshui.jpg'),
  (@r, '辣椒油', '15', 'ml', FALSE, 7, '/api/ingredients/lajiaoyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '板鸭温水浸泡退咸，刷净沥干', 30),
  (@r, 2, '姜切片，与葱结、黄酒、冰糖码入盘中', 8),
  (@r, 3, '上锅大火隔水蒸至鸭肉回软', 60),
  (@r, 4, '取出晾凉，顺纹横切成板状件', 8),
  (@r, 5, '摆盘淋原汁，配辣椒油蘸食', 3);

-- ========== 11. 淡糟香螺片 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('淡糟香螺片', '闽菜刀工代表作，香螺肉剞上十字花刀汆成螺卷，以红糟、虾油、姜丝爆炒，脆嫩爽口、糟香清郁，极考火候。', NULL, 30, 10, 40, 3, 4, '闽菜', '经典,刀工,河鲜,闽菜名菜', 1, TRUE, 254, 180, 16, 6, 10, '螺片入沸水即捞、汆十秒便卷，久煮则老韧；红糟先用油炒出香再下锅，急火快炒才挂得住。', '糟香脆嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '香螺肉', '400', 'g', TRUE, 1, '/api/ingredients/tianluo.jpg'),
  (@r, '红糟', '30', 'g', TRUE, 2, '/api/ingredients/duojiao.jpg'),
  (@r, '虾油', '10', 'ml', TRUE, 3, '/api/ingredients/xiapi.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '20', 'g', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '10', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 8, '/api/ingredients/baitang.jpg'),
  (@r, '水淀粉', '30', 'ml', TRUE, 9, '/api/ingredients/dianfen.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '1', 'g', FALSE, 11, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '香螺肉去杂洗净，两面剞十字花刀后切薄片', 15),
  (@r, 2, '螺片入沸水大火汆十秒卷起即捞', 1),
  (@r, 3, '红糟加料酒、白糖、虾油调成糟汁', 4),
  (@r, 4, '锅下油，中火爆香姜蒜与葱段', 2),
  (@r, 5, '下糟汁炒出红香，倒入螺片大火翻匀', 2),
  (@r, 6, '勾水淀粉亮汁即出锅', 1);

-- ========== 12. 鸡汤汆海蚌 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('鸡汤汆海蚌', '闽侯一带的闽菜极品，以鸡清汤冲汆新鲜海蚌，蚌肉脆嫩汤清见底，全靠一手滚汤激熟的手上功夫。', NULL, 20, 20, 40, 3, 2, '闽菜', '经典,汤羹,河鲜,闽菜名菜', 1, TRUE, 197, 150, 16, 5, 6, '海蚌要片得薄，滚汤冲入即加盖焖十几秒；汤不够沸则蚌肉带腥而不脆。', '清鲜原味');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '海蚌肉', '300', 'g', TRUE, 1, '/api/ingredients/baoyu.jpg'),
  (@r, '鸡清汤', '600', 'ml', TRUE, 2, '/api/ingredients/gaotang.jpg'),
  (@r, '老母鸡', '200', 'g', TRUE, 3, '/api/ingredients/tuji.jpg'),
  (@r, '清水', '800', 'ml', TRUE, 4, '/api/ingredients/qingshui.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '料酒', '10', 'ml', FALSE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '2', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '1', 'g', FALSE, 8, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '小葱', '2', '根', TRUE, 9, '/api/ingredients/xiaocong.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '老母鸡焯水，加清水姜片小火吊出鸡清汤', 60),
  (@r, 2, '海蚌去壳取肉，片成薄片入冷水漂洗沥干', 15),
  (@r, 3, '蚌片入沸水大火汆五秒卷起，捞出装碗', 1),
  (@r, 4, '鸡清汤大火烧至沸滚，加盐调底味', 5),
  (@r, 5, '滚汤冲入蚌片碗，加盖焖十秒激熟', 1),
  (@r, 6, '撒葱花即可，汤面清亮不见渣', 1);

-- ========== 13. 红糟鳗鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('红糟鳗鱼', '福州人家年节味，海鳗切段用红糟、黄酒腌透，裹粉炸至外酥里嫩，红亮糟香带酸甜，冷吃热吃皆宜。', NULL, 30, 15, 45, 2, 4, '闽菜', '经典,河鲜,宴客,福州名菜', 1, TRUE, 112, 380, 26, 26, 12, '鳗段一定要用红糟加黄酒腌透两小时去腥上色；炸时先六成热定型，再升温逼油才酥。', '糟香咸甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '海鳗', '600', 'g', TRUE, 1, '/api/ingredients/shanyupian.jpg'),
  (@r, '红糟', '50', 'g', TRUE, 2, '/api/ingredients/duojiao.jpg'),
  (@r, '黄酒', '30', 'ml', TRUE, 3, '/api/ingredients/huangjiu.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '白糖', '10', 'g', TRUE, 6, '/api/ingredients/baitang.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '8', 'ml', FALSE, 8, '/api/ingredients/xiangcu.jpg'),
  (@r, '红薯淀粉', '40', 'g', TRUE, 9, '/api/ingredients/dianfen.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '海鳗宰杀去内脏，切成四厘米长的鳗段', 10),
  (@r, 2, '红糟加黄酒、姜蒜末、白糖、生抽调成糟浆', 8),
  (@r, 3, '鳗段入糟浆腌两小时入味上色', 120),
  (@r, 4, '腌好取出拍干，裹一层红薯淀粉', 8),
  (@r, 5, '油烧六成热，中火炸至定型浮起', 4),
  (@r, 6, '升七成热大火复炸至外壳酥脆，沥油装盘', 3);

-- ========== 14. 花生汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('花生汤', '闽南古早味甜汤，花生仁加小苏打慢炖至酥而不散，汤色乳白甜润，配油条是厦门人天亮前的早餐。', NULL, 20, 150, 170, 1, 4, '闽菜', '家常,甜品,早餐,闽南名吃', 1, TRUE, 244, 220, 9, 15, 14, '花生要泡透去皮，炖时只放小苏打不放糖，煮到酥烂才下冰糖，过早加糖怎么煮都不烂。', '甜润清香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '花生', '200', 'g', TRUE, 1, '/api/ingredients/huasheng.jpg'),
  (@r, '冰糖', '50', 'g', TRUE, 2, '/api/ingredients/bingtang.jpg'),
  (@r, '小苏打', '2', 'g', TRUE, 3, '/api/ingredients/dianfen.jpg'),
  (@r, '清水', '1200', 'ml', TRUE, 4, '/api/ingredients/qingshui.jpg'),
  (@r, '鸡蛋', '2', '个', FALSE, 5, '/api/ingredients/jidan.jpg'),
  (@r, '米酒', '10', 'ml', FALSE, 6, '/api/ingredients/mijiu.jpg'),
  (@r, '盐', '1', 'g', FALSE, 7, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '花生温水泡两小时，搓去红衣沥干', 120),
  (@r, 2, '花生入锅加清水和小苏打，大火烧开', 5),
  (@r, 3, '转微火加盖炖至花生酥烂', 150),
  (@r, 4, '下冰糖煮化，尝味至甜润', 6),
  (@r, 5, '可选窝入鸡蛋，盛碗撒几粒熟花生', 4);

-- ========== 15. 土笋冻 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('土笋冻', '闽南独有奇味，晋江沿海的沙虫熬煮出天然胶质，连虫带汤倒碗冷凝成冻，切块蘸芥末酱油，晶莹弹滑清鲜。', NULL, 30, 40, 70, 2, 6, '闽菜', '传统,小吃,海鲜,闽南名吃', 1, TRUE, 311, 130, 12, 3, 8, '沙虫靠反复揉搓挤净泥沙，长时间熬煮才释出胶质，趁热连虫带汤入碗，凉透自然凝成冻。', '清鲜弹滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '沙虫', '300', 'g', TRUE, 1, '/api/ingredients/niqiu.jpg'),
  (@r, '清水', '1200', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '酱油', '20', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '10', 'ml', FALSE, 5, '/api/ingredients/xiangcu.jpg'),
  (@r, '芥末酱', '3', 'g', FALSE, 6, '/api/ingredients/tengjiaoyou.jpg'),
  (@r, '大蒜', '10', 'g', FALSE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 8, '/api/ingredients/xiangcai.jpg'),
  (@r, '辣椒油', '5', 'ml', FALSE, 9, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '盐', '1', 'g', TRUE, 10, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '沙虫加水浸泡，逐条揉压挤去内脏泥沙漂净', 20),
  (@r, 2, '洗净沙虫入锅，加清水与姜片大火煮开', 10),
  (@r, 3, '转小火熬至汤起胶质、虫体软烂', 40),
  (@r, 4, '连虫带汤舀入小碗，加盐调底味', 5),
  (@r, 5, '放凉后冷藏至自然凝成冻', 240),
  (@r, 6, '取出切块，蘸芥末酱油食用', 4);

-- ========== 16. 沙县扁肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('沙县扁肉', '沙县小吃的灵魂，猪后腿肉用木槌敲成脆馅，薄皮裹成菱形小馄饨，滚水烫熟配清汤，皮薄馅脆带弹牙。', NULL, 40, 15, 55, 2, 4, '闽菜', '家常,小吃,面食,沙县名吃', 1, TRUE, 225, 280, 16, 12, 26, '肉馅要捶不要剁，加冰水摔打出胶质才脆弹；包时只捏两角留边，才成扁肉的菱形。', '咸鲜爽滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪后腿肉馅', '300', 'g', TRUE, 1, '/api/ingredients/zhuroumo.jpg'),
  (@r, '抄手皮', '1', '包(约200g)', TRUE, 2, '/api/ingredients/jiaozipi.jpg'),
  (@r, '清水', '30', 'ml', TRUE, 3, '/api/ingredients/qingshui.jpg'),
  (@r, '鸡蛋清', '1', '个', TRUE, 4, '/api/ingredients/jidanqing.jpg'),
  (@r, '高汤', '600', 'ml', TRUE, 5, '/api/ingredients/gaotang.jpg'),
  (@r, '小苏打', '1', 'g', FALSE, 6, '/api/ingredients/dianfen.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '3', '根', TRUE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 10, '/api/ingredients/xiangyou.jpg'),
  (@r, '白胡椒粉', '1', 'g', FALSE, 11, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '盐', '2', 'g', TRUE, 12, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪后腿肉用木槌反复敲打成胶状肉馅', 15),
  (@r, 2, '肉馅加清水、盐、蛋清、小苏打摔打上劲', 10),
  (@r, 3, '抄手皮抹馅，对折捏成菱形小扁肉', 20),
  (@r, 4, '沸水大火下扁肉，煮至皮透馅浮', 3),
  (@r, 5, '碗内加高汤、生抽、胡椒粉调汤底', 2),
  (@r, 6, '扁肉捞入汤碗，撒葱花淋香油', 2);

-- ========== 17. 泉州烧肉粽 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('泉州烧肉粽', '泉州端午的烧肉粽，糯米先炒酱油上色，包入五香猪肉、香菇、虾米与咸蛋黄，粽叶扎紧煮透，油润咸香弹糯。', NULL, 40, 120, 160, 2, 6, '闽菜', '时令,小吃,糯米,泉州名吃', 1, TRUE, 91, 430, 18, 22, 42, '糯米要泡足沥干，用葱酥和酱油先炒至均匀上色再包；煮时大火压足两小时才黏糯不透心。', '咸香油润');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '糯米', '600', 'g', TRUE, 1, '/api/ingredients/nuomi.jpg'),
  (@r, '五花肉', '300', 'g', TRUE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '干香菇', '8', '朵', TRUE, 3, '/api/ingredients/ganxianggu.jpg'),
  (@r, '咸蛋黄', '6', '个', TRUE, 4, '/api/ingredients/jidan.jpg'),
  (@r, '虾米', '50', 'g', TRUE, 5, '/api/ingredients/xiapi.jpg'),
  (@r, '板栗', '100', 'g', FALSE, 6, '/api/ingredients/huasheng.jpg'),
  (@r, '粽叶', '20', '张', TRUE, 7, '/api/ingredients/ganye.jpg'),
  (@r, '小葱', '3', '根', TRUE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 10, '/api/ingredients/laochou.jpg'),
  (@r, '五香粉', '3', 'g', TRUE, 11, '/api/ingredients/bajiao.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '糯米清水泡三小时至透，捞出沥干', 180),
  (@r, 2, '五花肉切块，加生抽、老抽、五香粉腌一小时', 60),
  (@r, 3, '干香菇泡发，虾米、板栗、咸蛋黄分别备好', 15),
  (@r, 4, '锅下油炒香葱花，倒入糯米加酱油炒至上色', 8),
  (@r, 5, '粽叶折漏斗，铺米码肉与蛋黄香菇，盖米扎紧', 15),
  (@r, 6, '入锅大火水煮至粽叶香透、糯米黏糯', 120);
