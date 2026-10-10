-- 由 seed/recipes-hui.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 徽菜，共 15 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 臭鳜鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('臭鳜鱼', '徽州招牌头菜。鲜鳜鱼抹盐入缸腌发酵两三日，臭气钻进肉里反成全鲜。红烧后肉呈蒜瓣、吸足咸鲜汤汁，闻着臭吃着香。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-chouguiyu.jpg', 30, 35, 65, 3, 3, '徽菜', '经典,宴客,河鲜,徽菜名菜', 1, TRUE, 312, 330, 22, 24, 5, '发酵全凭温度，25℃左右腌两三天即成，天冷延长至一周；鱼肉紧实透出臭香才算好，烧时只推勺不翻鱼。', '臭鲜浓香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '桂鱼', '1', '条(约600g)', TRUE, 1, '/api/ingredients/guiyu.jpg'),
  (@r, '盐', '10', 'g', TRUE, 2, '/api/ingredients/yan.jpg'),
  (@r, '猪油', '25', 'g', TRUE, 3, '/api/ingredients/zhuyou.jpg'),
  (@r, '五花肉', '50', 'g', TRUE, 4, '/api/ingredients/wuhuarou.jpg'),
  (@r, '冬笋', '100', 'g', TRUE, 5, '/api/ingredients/dongsun.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '泡红椒', '30', 'g', TRUE, 8, '/api/ingredients/paohongjiao.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '黄酒', '20', 'ml', TRUE, 10, '/api/ingredients/huangjiu.jpg'),
  (@r, '淀粉', '10', 'g', TRUE, 11, '/api/ingredients/dianfen.jpg'),
  (@r, '清水', '300', 'ml', TRUE, 12, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鳜鱼两面各剞三四刀，擦干后里外抹匀盐', 8),
  (@r, 2, '入小缸压重石，25℃左右腌2至3天至肉质紧实透出臭香', 240),
  (@r, 3, '取出冲净沥干拍层薄淀粉，五花肉冬笋姜片蒜片切片', 8),
  (@r, 4, '热锅下猪油烧至六成热，中火煸五花肉片至出油金黄', 4),
  (@r, 5, '下泡红椒、姜蒜片大火爆香，再下笋片翻炒两分钟', 3),
  (@r, 6, '加生抽、黄酒和清水烧开，放入鳜鱼转小火加盖烧15分钟', 17),
  (@r, 7, '中途只推不翻面，汤剩三分之一时大火收浓，淋水淀粉出锅', 6);

-- ========== 2. 毛豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('毛豆腐', '相传朱元璋屯兵徽州，误食长了白毛的豆腐反觉鲜美，从此名扬四方。白毛豆腐煎得金黄，外皮酥香内里如腐乳绵软。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-maodoufu.jpg', 25, 15, 40, 2, 3, '徽菜', '经典,小吃,豆腐,徽州特色', 1, TRUE, 194, 310, 15, 24, 6, '发酵要阴凉潮湿，白毛长到寸许即成；煎好后加盖焖两分钟，内芯熔化才够绵嫩。', '咸辣香嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '豆腐', '1', '块(约400g)', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '猪油', '30', 'g', TRUE, 2, '/api/ingredients/zhuyou.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 3, '/api/ingredients/shiyongyou.jpg'),
  (@r, '辣椒粉', '10', 'g', TRUE, 4, '/api/ingredients/lajiaofen.jpg'),
  (@r, '盐', '3', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '熟芝麻', '5', 'g', FALSE, 6, '/api/ingredients/baizhima.jpg'),
  (@r, '大蒜', '15', 'g', FALSE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 8, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '豆腐用纱布包好压重石2小时去水，切成4厘米方块', 120),
  (@r, 2, '豆腐块摆上干净稻草，阴凉潮湿处发酵2至3天至白毛长到寸许', 240),
  (@r, 3, '毛豆腐轻轻冲洗浮毛，厨房纸吸干水分', 4),
  (@r, 4, '热锅下猪油和食用油烧至六成热，中火煎豆腐至两面金黄', 6),
  (@r, 5, '转小火加盖焖2分钟至内芯熔化', 2),
  (@r, 6, '出锅装盘，辣椒粉、盐、熟芝麻拌匀蘸食', 3);

-- ========== 3. 问政山笋 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('问政山笋', '歙县问政山笋是徽菜里的清雅担当，相传乾隆尝后赞胜却玉液仙餐。火腿同春笋煨足钟点，汤清笋酥，入口回甘，山鲜尽在一碗。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-wenzhengshansun.jpg', 20, 60, 80, 2, 4, '徽菜', '经典,宴客,山珍,徽菜名菜', 1, TRUE, 281, 120, 6, 8, 10, '春笋一定要焯水去涩；全程微火慢煨不搅动，汤面似开非开，笋才嫩酥不失形。', '清鲜咸香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '春笋', '500', 'g', TRUE, 1, '/api/ingredients/dongsun.jpg'),
  (@r, '火腿', '50', 'g', TRUE, 2, '/api/ingredients/huotui.jpg'),
  (@r, '干香菇', '30', 'g', TRUE, 3, '/api/ingredients/ganxianggu.jpg'),
  (@r, '猪油', '15', 'g', TRUE, 4, '/api/ingredients/zhuyou.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '黄酒', '15', 'ml', TRUE, 6, '/api/ingredients/huangjiu.jpg'),
  (@r, '盐', '3', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '清水', '600', 'ml', TRUE, 8, '/api/ingredients/qingshui.jpg'),
  (@r, '小葱', '2', '根', FALSE, 9, '/api/ingredients/xiaocong.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '春笋剥壳切去老根，先剖半再切成5厘米长薄片', 8),
  (@r, 2, '水烧开加盐，下笋片中火焯5分钟去涩，捞出沥干', 6),
  (@r, 3, '冬菇温水泡发1小时至软，挤干去蒂切片，火腿切薄片', 60),
  (@r, 4, '砂锅下猪油铺底火腿片和冬菇片，上面整齐码放笋片', 4),
  (@r, 5, '注入泡冬菇的水和清水没过料面，大火烧开后转微火煨1小时', 62),
  (@r, 6, '加黄酒尝味补盐，撒葱段连煲上桌', 3);

-- ========== 4. 胡氏一品锅 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('胡氏一品锅', '源自绩溪胡氏宗祠的合族大锅菜，因待客以一品之名传开。鸭块、五花肉、香干、笋片层层码放慢炖两小时，越炖越浓越吃越香。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-yipinguo.jpg', 45, 130, 175, 3, 6, '徽菜', '经典,宴客,汤羹,徽菜名菜', 1, TRUE, 257, 400, 26, 30, 4, '料要层层压实码放，汤只注八成满；小火炖足两小时中途不开盖，百味才融成一锅。', '咸鲜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '土鸭', '半', '只(约800g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '五花肉', '300', 'g', TRUE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '香干', '100', 'g', TRUE, 3, '/api/ingredients/xianggan.jpg'),
  (@r, '鹌鹑蛋', '100', 'g', TRUE, 4, '/api/ingredients/anchundan.jpg'),
  (@r, '冬笋', '150', 'g', TRUE, 5, '/api/ingredients/dongsun.jpg'),
  (@r, '木耳', '20', 'g', TRUE, 6, '/api/ingredients/muer.jpg'),
  (@r, '猪油', '25', 'g', TRUE, 7, '/api/ingredients/zhuyou.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 9, '/api/ingredients/dasuan.jpg'),
  (@r, '酱油', '20', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '黄酒', '20', 'ml', TRUE, 11, '/api/ingredients/huangjiu.jpg'),
  (@r, '清水', '1000', 'ml', TRUE, 12, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '土鸭斩块，与五花肉一起冷水下锅大火焯8分钟捞出洗净', 10),
  (@r, 2, '鹌鹑蛋下锅煮8分钟捞出剥壳，冬笋切片焯水3分钟去涩', 11),
  (@r, 3, '香干切条，木耳泡发后洗净，姜蒜拍松', 8),
  (@r, 4, '热锅下猪油五成热，中火煸鸭块和五花肉至表皮金黄，烹酱油黄酒', 6),
  (@r, 5, '锅底铺香干木耳，中码鸭肉笋片，上码鹌鹑蛋，层层压实注水八成满', 8),
  (@r, 6, '大火烧开转小火加盖炖2小时，中途不开盖', 120),
  (@r, 7, '开盖补盐，转中火滚10分钟至汤汁浓醇，连锅上桌边加热边吃', 10);

-- ========== 5. 李鸿章大杂烩 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('李鸿章大杂烩', '李鸿章府上应酬名菜，相传宴美国使团时仓促凑成一锅烩菜反获盛赞。海参虾仁火腿烩进浓鸡汤，软糯脆嫩并存，荤而不燥。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-dzahue.jpg', 30, 30, 60, 3, 4, '徽菜', '经典,宴客,海鲜,徽菜名菜', 1, TRUE, 153, 260, 29, 14, 3, '海参、鸡片先各自焯水定型；烩时推勺不划圈，薄芡分两次下，汤才清而裹味。', '咸鲜浓厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '海参', '300', 'g', TRUE, 1, '/api/ingredients/yuchi.jpg'),
  (@r, '鸡胸肉', '200', 'g', TRUE, 2, '/api/ingredients/jitui.jpg'),
  (@r, '河虾仁', '150', 'g', TRUE, 3, '/api/ingredients/hexiaren.jpg'),
  (@r, '火腿', '60', 'g', TRUE, 4, '/api/ingredients/huotui.jpg'),
  (@r, '鸡蛋', '2', '个', TRUE, 5, '/api/ingredients/jidan.jpg'),
  (@r, '水发木耳', '80', 'g', TRUE, 6, '/api/ingredients/muer.jpg'),
  (@r, '鸡清汤', '600', 'ml', TRUE, 7, '/api/ingredients/gaotang.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '黄酒', '15', 'ml', TRUE, 9, '/api/ingredients/huangjiu.jpg'),
  (@r, '盐', '3', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '水淀粉', '40', 'ml', TRUE, 11, '/api/ingredients/dianfen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '海参切4厘米长条，鸡胸肉切薄片，分别入开水中火汆2分钟捞出', 6),
  (@r, 2, '鸡蛋摊成两张薄蛋皮切菱形片，火腿切薄片', 5),
  (@r, 3, '砂锅下鸡清汤烧开，入海参、火腿、姜片，中火烩6分钟', 7),
  (@r, 4, '下鸡片、河虾仁转小火煮2分钟至刚熟', 3),
  (@r, 5, '加入木耳、蛋皮，烹黄酒加盐调味', 2),
  (@r, 6, '分两次淋水淀粉推勺勾薄芡，汤浓亮即盛盘', 3);

-- ========== 6. 徽州刀板香 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('徽州刀板香', '徽州咸肉雅号刀板香，腌三日风干七日，蒸时垫木板吸去浮油。肉色琥珀透光，肥肉不腻瘦肉不柴，薄切一盘便是地道下酒菜。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-daobanxiang.jpg', 40, 50, 90, 3, 6, '徽菜', '经典,卤味,宴客,徽州特色', 1, TRUE, 250, 280, 19, 22, 1, '腌三日风干七日急不得；蒸时垫木板吸油，晾至温热再逆纹切，片薄透光才正宗。', '咸香醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮土猪肉', '800', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '盐', '60', 'g', TRUE, 2, '/api/ingredients/yan.jpg'),
  (@r, '花椒', '5', 'g', TRUE, 3, '/api/ingredients/huajiao.jpg'),
  (@r, '香叶', '2', '片', TRUE, 4, '/api/ingredients/xiangye.jpg'),
  (@r, '白酒', '20', 'ml', TRUE, 5, '/api/ingredients/baijiu.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '盐与花椒、香叶入锅小火炒至微黄出香，倒出晾凉成花椒盐', 8),
  (@r, 2, '猪肉刮洗干净晾干，先抹白酒再把花椒盐通体搓揉一遍', 8),
  (@r, 3, '肉皮朝上放入小缸压重石，阴凉处腌3天每天上下翻面一次', 240),
  (@r, 4, '取出挂阴凉通风处风干7天，至外表干爽肥肉呈半透明', 240),
  (@r, 5, '切成长方块摆在木板上，入蒸锅大火蒸40分钟至油润透香', 42),
  (@r, 6, '晾至温热逆纹切薄片，码盘趁热食用', 5);

-- ========== 7. 黄山炖鸽 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('黄山炖鸽', '黄山一带的滋补头汤，当地人用山泉炖嫩鸽，只加姜与黄酒吊出本味。汤清如茶油，鸽肉酥烂离骨，一勺入口从喉咙暖到胃里。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-huangshandunge.jpg', 15, 140, 155, 2, 4, '徽菜', '经典,汤羹,滋补,徽州特色', 1, TRUE, 290, 190, 24, 9, 2, '全程微火，汤面只冒虾眼泡；炖足两小时肉自离骨，先下盐则肉柴汤浑。', '清鲜醇和');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '乳鸽', '2', '只(约600g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '枸杞', '10', 'g', TRUE, 3, '/api/ingredients/gouqi.jpg'),
  (@r, '黄酒', '20', 'ml', TRUE, 4, '/api/ingredients/huangjiu.jpg'),
  (@r, '盐', '3', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '清水', '1200', 'ml', TRUE, 6, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '乳鸽收拾干净斩去爪尖，冷水下锅加黄酒姜片，大火焯5分钟去血沫', 9),
  (@r, 2, '砂锅注入足量清水，下乳鸽、姜块，大火烧开撇净浮沫', 6),
  (@r, 3, '转微火加盖慢炖2小时至鸽肉酥烂离骨', 120),
  (@r, 4, '下枸杞再炖15分钟', 15),
  (@r, 5, '加黄酒和盐调味，连煲上桌', 3);

-- ========== 8. 茶叶熏鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('茶叶熏鸡', '徽州人把茶做进菜里的聪明菜。茶叶同米饭白糖入锅起烟，熏出枣红油亮外皮，烟香混着茶清香钻进骨缝，冷食热食两相宜。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-chayexunji.jpg', 25, 60, 85, 3, 6, '徽菜', '经典,卤味,宴客,徽州特色', 1, TRUE, 92, 250, 26, 15, 2, '熏只争五分钟：大火起烟即转中火，见皮色枣红立刻出锅，久熏发苦破皮。', '茶香熏鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '三黄鸡', '1', '只(约1000g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '茶叶', '15', 'g', TRUE, 2, '/api/ingredients/lucha.jpg'),
  (@r, '大米', '30', 'g', TRUE, 3, '/api/ingredients/dami.jpg'),
  (@r, '白糖', '30', 'g', TRUE, 4, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '25', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '花椒', '5', 'g', TRUE, 6, '/api/ingredients/huajiao.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '3', '根', TRUE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '香油', '10', 'ml', TRUE, 9, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '三黄鸡去爪洗净，冷水下锅没过，加姜葱花椒和盐，大火烧开撇沫', 10),
  (@r, 2, '转中火煮20分钟，关火加盖焖10分钟，捞出沥干汤汁', 30),
  (@r, 3, '厚底锅铺大米、茶叶、白糖，架上箅子，大火烧至冒出浓烟', 5),
  (@r, 4, '鸡皮朝上放箅子上，盖严锅盖转中火熏5分钟至表皮枣红', 6),
  (@r, 5, '立即出锅晾温，全身刷一层香油', 4),
  (@r, 6, '斩件码盘，原汁淋面', 4);

-- ========== 9. 火腿炖甲鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('火腿炖甲鱼', '徽菜高席炖菜，甲鱼裙边配徽州火腿同煨，不点一滴酱油。汤色醇厚油亮，裙边糯滑粘嘴，火腿咸香衬出龟肉清甜，最见火功。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-huotuijiayu.jpg', 20, 100, 120, 2, 4, '徽菜', '经典,宴客,汤羹,徽菜名菜', 1, TRUE, 298, 165, 22, 7, 2, '裙边必须烫净黑膜去腥；焯透后一次性加足开水，微火炖足一个半钟至软糯弹滑。', '咸鲜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '甲鱼裙边', '500', 'g', TRUE, 1, '/api/ingredients/jiayuqunbian.jpg'),
  (@r, '火腿', '80', 'g', TRUE, 2, '/api/ingredients/huotui.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '黄酒', '25', 'ml', TRUE, 4, '/api/ingredients/huangjiu.jpg'),
  (@r, '枸杞', '10', 'g', FALSE, 5, '/api/ingredients/gouqi.jpg'),
  (@r, '盐', '3', 'g', TRUE, 6, '/api/ingredients/yan.jpg'),
  (@r, '清水', '800', 'ml', TRUE, 7, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '裙边入开水中小火烫煮3分钟，捞出刮净两面黑膜，切方块', 8),
  (@r, 2, '裙边冷水下锅，加姜片和10ml黄酒，大火焯5分钟去腥洗净', 7),
  (@r, 3, '砂锅摆裙边块、火腿片、姜块，注入足量开水', 5),
  (@r, 4, '大火烧开转微火加盖炖1小时30分钟至裙边软糯', 90),
  (@r, 5, '下枸杞，补黄酒和盐再滚5分钟即成', 4);

-- ========== 10. 苞芦馃 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('苞芦馃', '徽州山民的玉米饼，苞芦粉沸水烫面作皮，包香干腊肉蒜叶馅煎制。外皮酥香带沙感，馅料咸香有嚼头，是山村旧岁月的待客点心。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-baoluguo.jpg', 40, 20, 60, 2, 4, '徽菜', '家常,小吃,粗粮,徽州特色', 1, TRUE, 185, 370, 11, 18, 40, '一定要沸水烫面才黏得住；馅要炒凉再包，煎后淋水加盖焖透，芯才不夹生。', '咸香粗粝');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '玉米面', '200', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '香干', '100', 'g', TRUE, 2, '/api/ingredients/xianggan.jpg'),
  (@r, '腊肉', '50', 'g', TRUE, 3, '/api/ingredients/larou.jpg'),
  (@r, '大蒜叶', '50', 'g', TRUE, 4, '/api/ingredients/qingsuan.jpg'),
  (@r, '猪油', '25', 'g', TRUE, 5, '/api/ingredients/zhuyou.jpg'),
  (@r, '干红辣椒', '3', 'g', FALSE, 6, '/api/ingredients/ganlajiao.jpg'),
  (@r, '盐', '2', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '清水', '150', 'ml', TRUE, 8, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '玉米面加盐，冲入沸水烫面，晾至温热揉成软面团盖布饧30分钟', 32),
  (@r, 2, '香干、腊肉、大蒜叶全部切成细末', 6),
  (@r, 3, '热锅下15g猪油五成热，中火煸腊肉末出油，下香干末辣椒末炒香，加蒜叶晾凉', 8),
  (@r, 4, '面团分4个剂子捏成碗状，各包入四分之一馅料，收口按扁成圆馃', 8),
  (@r, 5, '平底锅余下猪油烧至五成热，中火将馃煎至两面金黄起壳', 8),
  (@r, 6, '沿锅边淋20ml水，加盖小火焖3分钟至内芯熟透', 4);

-- ========== 11. 笋干老鸭煲 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('笋干老鸭煲', '徽州人把春笋晒成笋干留住山味，最金贵的吃法是炖老鸭。鸭油被干笋吸得饱满，汤鲜笋韧，一煲尽见徽州人家的山货家底。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-sunganyaobao.jpg', 45, 140, 185, 2, 6, '徽菜', '家常,汤羹,山珍,徽州特色', 1, TRUE, 99, 270, 22, 18, 3, '笋干泡透后一定要炒干水汽再下锅，吸油更足；煲汤一次加足开水，中途不添水。', '咸鲜笋香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '土鸭', '1', '只(约1200g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '笋干', '100', 'g', TRUE, 2, '/api/ingredients/yansun.jpg'),
  (@r, '火腿', '30', 'g', TRUE, 3, '/api/ingredients/huotui.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '黄酒', '20', 'ml', TRUE, 5, '/api/ingredients/huangjiu.jpg'),
  (@r, '盐', '4', 'g', TRUE, 6, '/api/ingredients/yan.jpg'),
  (@r, '枸杞', '10', 'g', FALSE, 7, '/api/ingredients/gouqi.jpg'),
  (@r, '清水', '1800', 'ml', TRUE, 8, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '笋干提前温水泡发4小时至回软，剪去老根切段', 240),
  (@r, 2, '土鸭洗净斩大块，冷水下锅加黄酒姜片，大火焯8分钟撇净血沫', 10),
  (@r, 3, '笋干段下空锅中小火煸2分钟炒干水汽', 4),
  (@r, 4, '鸭块与笋干一起入砂锅，放火腿片姜块，注入足量开水', 6),
  (@r, 5, '大火烧开转微火加盖煲2小时至鸭肉酥而不散', 120),
  (@r, 6, '下枸杞加盐调味，再滚5分钟连煲上桌', 6);

-- ========== 12. 黄山烧饼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('黄山烧饼', '又名梅城干馃，徽州茶商千里在途的干粮。薄酥皮裹梅干菜与肥肉丁，烤到焦香，凉了咬一口掉渣，咸中带甜越嚼越香。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-huangshanshaobing.jpg', 60, 25, 85, 3, 8, '徽菜', '小吃,干粮,徽菜名菜', 1, TRUE, 303, 250, 4, 14, 24, '馅要炒透晾凉再包；烤至酥壳硬透才存得住，放凉了再动才不会碎。', '干香咸甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '200', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '梅干菜', '50', 'g', TRUE, 2, '/api/ingredients/gandoujiao.jpg'),
  (@r, '五花肉', '80', 'g', TRUE, 3, '/api/ingredients/wuhuarou.jpg'),
  (@r, '猪油', '60', 'g', TRUE, 4, '/api/ingredients/zhuyou.jpg'),
  (@r, '白糖', '20', 'g', TRUE, 5, '/api/ingredients/baitang.jpg'),
  (@r, '白芝麻', '30', 'g', TRUE, 6, '/api/ingredients/baizhima.jpg'),
  (@r, '清水', '90', 'ml', TRUE, 7, '/api/ingredients/qingshui.jpg'),
  (@r, '盐', '2', 'g', TRUE, 8, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '面粉加35g猪油、90ml温水和2g盐，揉成软面团盖湿布饧40分钟', 42),
  (@r, 2, '梅干菜温水泡发1小时，反复淘净沙土挤干，切成细末', 60),
  (@r, 3, '五花肉切细丁；饼坯摆入烤盘刷水，撒上白芝麻', 6),
  (@r, 4, '热锅下10g猪油，中火炒香肉丁和干菜末，加白糖1g盐炒匀晾凉', 6),
  (@r, 5, '面团分8个剂子按扁，包入馅心收口，压成直径6厘米圆饼', 10),
  (@r, 6, '烤箱上下火200度预热，烤18分钟至表面焦黄酥壳硬', 18);

-- ========== 13. 冬笋炒腊肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('冬笋炒腊肉', '徽州冬日的一盘鲜：自家腌的腊肉对上肉厚的冬笋。笋片吸透腊猪油，咸香里带清甜脆嫩，一盘下肚山野的年气全在饭桌上。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-dongsunlarou.jpg', 15, 12, 27, 1, 3, '徽菜', '家常,时令,下饭,徽州特色', 1, TRUE, 92, 255, 12, 20, 5, '冬笋必焯水去涩；腊肉先蒸后煸至出油透明，转大火快炒才脆嫩不软塌。', '咸鲜脆嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '冬笋', '300', 'g', TRUE, 1, '/api/ingredients/dongsun.jpg'),
  (@r, '腊肉', '150', 'g', TRUE, 2, '/api/ingredients/larou.jpg'),
  (@r, '蒜苗', '50', 'g', TRUE, 3, '/api/ingredients/qingsuan.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '干红辣椒', '5', 'g', FALSE, 5, '/api/ingredients/ganlajiao.jpg'),
  (@r, '食用油', '10', 'ml', TRUE, 6, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '1', 'g', FALSE, 7, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '冬笋剥壳切去老根，斜刀切成薄片', 6),
  (@r, 2, '水烧开加盐，下笋片中火焯3分钟去涩捞出沥干', 4),
  (@r, 3, '腊肉温水洗净，上锅蒸20分钟取出切薄片', 22),
  (@r, 4, '热锅下油五成热，中火煸腊肉至卷边出油透明', 4),
  (@r, 5, '下姜片、辣椒段、笋片转大火翻炒2分钟', 2),
  (@r, 6, '撒蒜苗段炒至断生，尝味补盐出锅', 2);

-- ========== 14. 中和汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('中和汤', '徽州人家年三十的头一道汤，取中和二字，愿家道中和、岁岁平安。豆腐、冬笋、火腿、虾皮同烩一碗清汤，诸味调和，清鲜妥帖。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-zhonghetang.jpg', 15, 20, 35, 1, 4, '徽菜', '家常,汤羹,年节,徽州特色', 1, TRUE, 156, 120, 10, 6, 5, '豆腐下锅后用勺背轻推不可搅；小火养味、薄芡收住，汤才清鲜豆方完整。', '清鲜和醇');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '豆腐', '300', 'g', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '冬笋', '100', 'g', TRUE, 2, '/api/ingredients/dongsun.jpg'),
  (@r, '火腿', '40', 'g', TRUE, 3, '/api/ingredients/huotui.jpg'),
  (@r, '虾皮', '8', 'g', TRUE, 4, '/api/ingredients/xiapi.jpg'),
  (@r, '鸡清汤', '600', 'ml', TRUE, 5, '/api/ingredients/gaotang.jpg'),
  (@r, '盐', '2', 'g', TRUE, 6, '/api/ingredients/yan.jpg'),
  (@r, '水淀粉', '25', 'ml', TRUE, 7, '/api/ingredients/dianfen.jpg'),
  (@r, '白胡椒粉', '1', 'g', FALSE, 8, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '小葱', '2', '根', FALSE, 9, '/api/ingredients/xiaocong.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '豆腐切2厘米见方小丁，火腿切薄片，冬笋切薄片', 6),
  (@r, 2, '水烧开中火焯笋片2分钟去涩，捞出备用', 3),
  (@r, 3, '鸡清汤下锅烧沸，入火腿片、笋片、虾皮，中火煮5分钟出味', 5),
  (@r, 4, '下豆腐丁转小火煮3分钟，勺背轻推不搅碎', 4),
  (@r, 5, '淋水淀粉勾薄芡，加盐和胡椒粉调味', 3),
  (@r, 6, '盛碗撒葱花即成', 2);

-- ========== 15. 梅干菜烧排骨 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('梅干菜烧排骨', '徽州干菜一蒸三晒，腌出岁月的陈香。同排骨烧焖，干菜吃透肉油黑亮滋润，排骨酥软酱香浓郁，浓汤拌饭一碗不剩。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-meigancaipaigu.jpg', 20, 60, 80, 2, 4, '徽菜', '家常,下饭,肉类,徽州特色', 1, TRUE, 144, 290, 16, 22, 6, '干菜要反复淘净沙土、挤干再炒透；焖足四十五分钟，菜吃透肉油才黑亮回甜。', '咸甜浓香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪肋排', '500', 'g', TRUE, 1, '/api/ingredients/zhupaigu.jpg'),
  (@r, '梅干菜', '80', 'g', TRUE, 2, '/api/ingredients/gandoujiao.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '干红辣椒', '5', 'g', FALSE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '5', 'ml', TRUE, 6, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '8', 'g', TRUE, 7, '/api/ingredients/baitang.jpg'),
  (@r, '黄酒', '15', 'ml', TRUE, 8, '/api/ingredients/huangjiu.jpg'),
  (@r, '盐', '2', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '清水', '400', 'ml', TRUE, 10, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '梅干菜温水泡发1小时，反复淘净沙土挤干，切段', 60),
  (@r, 2, '肋排斩小段冷水下锅，加姜片黄酒，大火焯5分钟捞出洗净', 10),
  (@r, 3, '热锅下油五成热，中火煸肋排至表面微黄出油', 5),
  (@r, 4, '下梅干菜段和干辣椒转大火翻炒2分钟炒出干菜香', 3),
  (@r, 5, '加生抽、老抽、白糖和盐，注入开水，大火烧开', 3),
  (@r, 6, '转小火加盖焖烧45分钟至排骨酥软', 45),
  (@r, 7, '开盖大火收汁至汤浓裹肉油亮', 6);
