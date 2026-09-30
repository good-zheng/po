-- 由 seed/recipes-dongbei.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 东北菜，共 15 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 猪肉炖粉条 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('猪肉炖粉条', '东北炖菜的底子。带皮五花肉切厚片煸出油，加八角桂皮慢炖，再下红薯粉条把汤汁吸得一滴不剩。肉片软烂带酱香，粉条筋道烫嘴，配米饭最实在。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/dongbei-zhuroudunfentiao.jpg', 20, 50, 70, 2, 4, '东北菜', '炖菜,下饭菜,家常,东北四大炖', 1, TRUE, 164, 520, 24, 32, 30, '粉条提前温水泡软，下锅后别盖盖久煮，否则糊成一坨；汤要一次加足，中途添热水不添冷水。', '咸鲜酱香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '500', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '红薯粉条', '150', 'g', TRUE, 2, '/api/ingredients/hongshufen.jpg'),
  (@r, '大白菜', '300', 'g', FALSE, 3, '/api/ingredients/baicai.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '15', 'g', FALSE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 8, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '冰糖', '10', 'g', FALSE, 10, '/api/ingredients/bingtang.jpg'),
  (@r, '八角', '3', '个', TRUE, 11, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '小段', FALSE, 12, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '2', '片', FALSE, 13, '/api/ingredients/xiangye.jpg'),
  (@r, '盐', '3', 'g', TRUE, 14, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 15, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '900', 'ml', TRUE, 16, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '粉条温水泡20分钟至软，五花肉切薄厚均匀的片，白菜切块，姜葱蒜切好', 22),
  (@r, 2, '冷锅下油，五花肉片中小火煸至两面金黄、猪油渗出', 6),
  (@r, 3, '下八角桂皮香叶姜葱蒜爆香，沿锅边烹料酒', 3),
  (@r, 4, '加生抽老抽冰糖翻炒上色，肉片裹匀酱色', 3),
  (@r, 5, '添清水没过肉，大火烧开转小火加盖炖30分钟', 32),
  (@r, 6, '下白菜块和泡软的粉条，继续敞盖炖12分钟至粉条透明', 13),
  (@r, 7, '试咸淡补盐，大火收至汤汁浓稠裹住粉条即可出锅', 4);

-- ========== 2. 酸菜白肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('酸菜白肉', '东北冬天的看家菜。整块五花白煮切片，东北酸菜丝攥干后炒香，回锅同炖半小时，酸味把猪油的腻全化开。肉片蘸蒜酱，酸香带劲。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/dongbei-suancaibairou.jpg', 25, 55, 80, 2, 4, '东北菜', '炖菜,冬季,家常,东北四大炖', 1, TRUE, 308, 460, 25, 33, 9, '酸菜别攥太干，留一点酸味；白肉煮到筷子能插透就捞出晾凉再切，热切会散。蘸料用蒜末加生抽和香油现调。', '酸鲜开胃');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '600', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '酸菜', '500', 'g', TRUE, 2, '/api/ingredients/baicai.jpg'),
  (@r, '红薯粉条', '100', 'g', FALSE, 3, '/api/ingredients/hongshufen.jpg'),
  (@r, '大葱', '1', '根', TRUE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '花椒', '15', '粒', FALSE, 7, '/api/ingredients/huajiao.jpg'),
  (@r, '香叶', '2', '片', FALSE, 8, '/api/ingredients/xiangye.jpg'),
  (@r, '料酒', '25', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 11, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '芝麻香油', '10', 'ml', TRUE, 12, '/api/ingredients/xiangyou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 13, '/api/ingredients/yan.jpg'),
  (@r, '清水', '1200', 'ml', TRUE, 14, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉整块冷水下锅，加姜葱料酒花椒香叶，大火烧开撇净浮沫', 12),
  (@r, 2, '转小火煮30分钟至筷子能插透，捞出晾凉切薄片', 32),
  (@r, 3, '酸菜切成细丝，清水漂一遍后攥去多余水分', 10),
  (@r, 4, '锅留少许猪油，下酸菜丝中火炒5分钟至酸香出来', 6),
  (@r, 5, '倒入煮肉的白汤烧开，下酸菜和粉条同炖20分钟', 22),
  (@r, 6, '肉片铺回锅里烫热，加盐和白胡椒粉调味', 4),
  (@r, 7, '连锅端上桌，另配一碗蒜末加生抽和香油的蘸汁', 3);

-- ========== 3. 小鸡炖蘑菇 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('小鸡炖蘑菇', '东北四大炖里最讲究的一条。小笨鸡斩块炒香，配大兴安岭榛蘑慢炖，菌香钻进鸡肉纤维，再下粉条收汁。鸡要炖到骨肉将离不烂，汤色琥珀。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/dongbei-xiaojidunmugu.jpg', 25, 60, 85, 2, 4, '东北菜', '炖菜,宴客,菌菇,东北四大炖', 1, TRUE, 245, 480, 34, 28, 16, '干榛蘑温水泡开，泡出的水沉砂后倒回锅里，菌香全靠它；三黄鸡或小公鸡都行，炖够时间才出味，别用饲料大肉鸡。', '鲜香醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '三黄鸡', '1', '只(约1000g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '榛蘑', '60', 'g', TRUE, 2, '/api/ingredients/ganxianggu.jpg'),
  (@r, '红薯粉条', '100', 'g', FALSE, 3, '/api/ingredients/hongshufen.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '20', 'g', FALSE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 9, '/api/ingredients/laochou.jpg'),
  (@r, '冰糖', '8', 'g', FALSE, 10, '/api/ingredients/bingtang.jpg'),
  (@r, '八角', '2', '个', FALSE, 11, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '小段', FALSE, 12, '/api/ingredients/guipi.jpg'),
  (@r, '盐', '4', 'g', TRUE, 13, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 14, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '1000', 'ml', TRUE, 15, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '榛蘑温水泡30分钟，挤干，泡菇水静置留用；鸡斩块冲净血水', 32),
  (@r, 2, '鸡块冷水下锅，加姜片料酒焯至浮沫出净，捞出沥干', 10),
  (@r, 3, '热锅下油，放冰糖炒出糖色，鸡块下锅翻炒至上色', 5),
  (@r, 4, '下姜葱蒜、八角桂皮爆香，烹料酒加生抽老抽翻匀', 3),
  (@r, 5, '倒入榛蘑和沉过底的泡菇水，添清水没过鸡肉', 4),
  (@r, 6, '大火烧开转小火加盖炖40分钟至鸡肉将烂', 42),
  (@r, 7, '下泡软的粉条再炖10分钟，试咸淡补盐，大火收浓汤汁', 12);

-- ========== 4. 锅包肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('锅包肉', '哈尔滨传来的老菜。猪里脊拍粉挂糊炸到壳脆，回锅裹糖醋急汁，酸甜冲鼻、外酥里嫩，咬下去咔嚓一声。正宗做法不放番茄酱，全凭糖醋和葱姜蒜丝提香。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/dongbei-guobaorou.jpg', 30, 15, 45, 3, 3, '东北菜', '炸物,酸甜,宴客,哈尔滨名菜', 1, TRUE, 250, 430, 26, 24, 27, '淀粉要用土豆淀粉，温水泡成糊才挂得住；必须复炸一次才脆；汁提前调好，下锅颠三两下就出，久了壳就软。', '酸甜酥脆');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪里脊', '350', 'g', TRUE, 1, '/api/ingredients/zhuliji.jpg'),
  (@r, '淀粉', '120', 'g', TRUE, 2, '/api/ingredients/dianfen.jpg'),
  (@r, '白糖', '80', 'g', TRUE, 3, '/api/ingredients/baitang.jpg'),
  (@r, '白醋', '50', 'ml', TRUE, 4, '/api/ingredients/baicu.jpg'),
  (@r, '生抽', '10', 'ml', FALSE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '大蒜', '25', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '半', '根', TRUE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '香菜', '20', 'g', FALSE, 9, '/api/ingredients/xiangcai.jpg'),
  (@r, '盐', '3', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '800', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '60', 'ml', TRUE, 12, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '里脊切3毫米厚大片，加盐和少许清水抓匀腌10分钟', 12),
  (@r, 2, '淀粉加温水调成非牛顿状的糊，抓进肉片裹匀挂住', 8),
  (@r, 3, '姜葱蒜切细丝，香菜切段，白糖白醋生抽清水调成急汁', 8),
  (@r, 4, '油烧六成热，肉片一片片下锅，中火炸至定型浮起捞出', 5),
  (@r, 5, '油温升到八成热复炸40秒至外壳金黄酥脆，沥油', 2),
  (@r, 6, '锅留底油，下姜葱蒜丝爆香，倒入急汁烧沸起泡', 3),
  (@r, 7, '肉片回锅快速颠匀裹汁，撒香菜段立刻出锅装盘', 2);

-- ========== 5. 地三鲜 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('地三鲜', '茄子、土豆、青椒三样地里长的鲜物，过油后回锅酱烧。东北饭馆的试金石：三样都要软糯入味，盘底却不见一堆油汤。', NULL, 15, 15, 30, 2, 3, '东北菜', '素菜,下饭菜,家常,过油', 1, TRUE, 196, 280, 5, 20, 22, '茄子切滚刀块先拍层薄淀粉再下锅，吸油少一半；三样分别过油，最后回锅只颠不炒，否则茄子全碎。', '咸鲜微甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '茄子', '2', '根(约400g)', TRUE, 1, '/api/ingredients/qiezi.jpg'),
  (@r, '土豆', '2', '个(约300g)', TRUE, 2, '/api/ingredients/tudou.jpg'),
  (@r, '青辣椒', '2', '个', TRUE, 3, '/api/ingredients/qinglajiao.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '大葱', '半', '根', FALSE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '8', 'ml', FALSE, 7, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '10', 'g', TRUE, 8, '/api/ingredients/baitang.jpg'),
  (@r, '淀粉', '20', 'g', TRUE, 9, '/api/ingredients/dianfen.jpg'),
  (@r, '盐', '3', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '500', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '120', 'ml', TRUE, 12, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '茄子土豆滚刀块，青椒掰块，蒜切末，淀粉对水调成水淀粉', 12),
  (@r, 2, '茄子块拍一层薄淀粉，土豆块冲去表面淀粉沥干', 5),
  (@r, 3, '油烧六成热下土豆，中火炸至边缘起壳金黄捞出', 5),
  (@r, 4, '下茄子炸至外脆内软，最后下青椒片十秒捞起控油', 3),
  (@r, 5, '锅留底油爆香蒜末葱段，加生抽老抽白糖和清水烧开', 3),
  (@r, 6, '三样回锅，转大火快速颠匀，淋水淀粉收浓挂汁', 2),
  (@r, 7, '见盘底只剩亮汁不见油，装盘撒剩余蒜末', 1);

-- ========== 6. 东北乱炖 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('东北乱炖', '一锅收尽园子里的菜：排骨、豆角、土豆、茄子、南瓜、白菜同炖，食材各让一分味，汤浑菜烂却甜丝丝。东北人夏天的家常顶流。', NULL, 25, 45, 70, 1, 4, '东北菜', '炖菜,家常,时蔬,一锅出', 1, TRUE, 119, 430, 22, 22, 33, '按耐煮程度下锅：豆角土豆先走，茄子南瓜后下，白菜最后；盐起锅前放，早放蔬菜出水冲淡汤味。', '咸鲜回甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '排骨', '400', 'g', TRUE, 1, '/api/ingredients/zhupaigu.jpg'),
  (@r, '四季豆', '250', 'g', TRUE, 2, '/api/ingredients/sijidou.jpg'),
  (@r, '土豆', '2', '个', TRUE, 3, '/api/ingredients/tudou.jpg'),
  (@r, '茄子', '1', '根', TRUE, 4, '/api/ingredients/qiezi.jpg'),
  (@r, '老南瓜', '300', 'g', TRUE, 5, '/api/ingredients/nangua.jpg'),
  (@r, '大白菜', '300', 'g', FALSE, 6, '/api/ingredients/baicai.jpg'),
  (@r, '西红柿', '1', '个', FALSE, 7, '/api/ingredients/xihongshi.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 9, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '15', 'g', FALSE, 10, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 11, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', FALSE, 12, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 13, '/api/ingredients/liaojiu.jpg'),
  (@r, '八角', '2', '个', FALSE, 14, '/api/ingredients/bajiao.jpg'),
  (@r, '盐', '5', 'g', TRUE, 15, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 16, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '1100', 'ml', TRUE, 17, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '排骨冷水下锅焯去血沫；豆角折段，土豆茄子南瓜滚刀块，白菜切块', 20),
  (@r, 2, '热锅下油，放八角和葱姜爆香，排骨煸至表面微黄', 5),
  (@r, 3, '烹料酒加生抽老抽翻匀，添清水没过排骨，大火烧开', 4),
  (@r, 4, '下豆角和土豆，转小火加盖炖20分钟', 22),
  (@r, 5, '下茄子南瓜和西红柿，继续炖15分钟至汤汁变浑', 16),
  (@r, 6, '下白菜块炖5分钟，加盐调味，撒蒜末即可连锅上桌', 7);

-- ========== 7. 尖椒干豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('尖椒干豆腐', '东北人待客必点的一道小炒。干豆腐薄到能透字，切丝焯水后配尖椒大火爆炒，勾一层薄芡挂在豆皮上，咸香带辣，一盘不够下饭。', NULL, 12, 8, 20, 1, 3, '东北菜', '快手菜,素菜,下饭菜,小炒', 1, TRUE, 283, 190, 13, 12, 9, '干豆腐焯水加一点食用碱，口感立刻回软；起锅前淋花椒油，是东北馆子那口香味的来处。', '咸鲜微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '干豆腐', '250', 'g', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '青辣椒', '3', '个', TRUE, 2, '/api/ingredients/qinglajiao.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '大葱', '半', '根', FALSE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '料酒', '10', 'ml', FALSE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '白糖', '3', 'g', FALSE, 7, '/api/ingredients/baitang.jpg'),
  (@r, '淀粉', '10', 'g', TRUE, 8, '/api/ingredients/dianfen.jpg'),
  (@r, '花椒', '10', '粒', FALSE, 9, '/api/ingredients/huajiao.jpg'),
  (@r, '盐', '2', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '35', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg'),
  (@r, '高汤', '120', 'ml', TRUE, 12, '/api/ingredients/gaotang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '干豆腐切细丝，青椒斜刀切片，蒜切片，淀粉对高汤调成碗汁', 10),
  (@r, 2, '水烧开加几滴油和一点食用碱，干豆腐丝焯30秒捞出沥干', 2),
  (@r, 3, '热锅下油，花椒炸香捞出，爆香葱蒜和青椒片', 3),
  (@r, 4, '下干豆腐丝大火快炒，烹料酒加生抽白糖', 2),
  (@r, 5, '淋碗汁翻匀收至挂住，试咸淡补盐出锅', 2);

-- ========== 8. 溜肉段 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('溜肉段', '东北宴席的硬热菜。猪瘦肉挂硬糊炸两遍，配青椒木耳咸鲜芡汁急溜，外壳酥韧、内里软嫩，一盘上桌最先见底。', NULL, 25, 15, 40, 3, 3, '东北菜', '炸物,宴客,下饭菜,辽菜经典', 1, TRUE, 140, 390, 27, 22, 22, '肉段要切麻将块大小，糊调成挂旗的稠度；溜汁必须提前对好，一次下锅十秒裹匀，久炒则糊壳脱落。', '咸鲜芡香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪瘦肉', '350', 'g', TRUE, 1, '/api/ingredients/zhushourou.jpg'),
  (@r, '淀粉', '100', 'g', TRUE, 2, '/api/ingredients/dianfen.jpg'),
  (@r, '青辣椒', '2', '个', TRUE, 3, '/api/ingredients/qinglajiao.jpg'),
  (@r, '水发木耳', '50', 'g', FALSE, 4, '/api/ingredients/muer.jpg'),
  (@r, '鸡蛋', '1', '个', FALSE, 5, '/api/ingredients/jidan.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '半', '根', TRUE, 7, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 8, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '5', 'ml', FALSE, 10, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 11, '/api/ingredients/liaojiu.jpg'),
  (@r, '白糖', '8', 'g', FALSE, 12, '/api/ingredients/baitang.jpg'),
  (@r, '香醋', '5', 'ml', FALSE, 13, '/api/ingredients/xiangcu.jpg'),
  (@r, '盐', '4', 'g', TRUE, 14, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '800', 'ml', TRUE, 15, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '100', 'ml', TRUE, 16, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '瘦肉切麻将块，加盐料酒姜片腌10分钟', 12),
  (@r, 2, '淀粉加温水揉成稠糊，抓入肉块挂匀，可加少许鸡蛋', 6),
  (@r, 3, '对碗汁：生抽老抽白糖香醋清水和淀粉调匀', 4),
  (@r, 4, '油烧五成热，肉段逐个下锅炸至定型微黄捞出', 5),
  (@r, 5, '油温升七成热复炸至外壳硬脆，下青椒木耳同捞沥油', 2),
  (@r, 6, '锅留底油爆香葱蒜，倒入碗汁烧沸起泡', 3),
  (@r, 7, '肉段回锅大火快颠十秒裹匀芡汁，立刻出锅', 1);

-- ========== 9. 白菜炖豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('白菜炖豆腐', '东北腊月最寻常的一锅。大白菜帮炖到透明，豆腐吸满汤，加一把粉条和几粒虾皮吊鲜，热乎乎端上桌，配馒头正好。', NULL, 12, 25, 37, 1, 3, '东北菜', '炖菜,素多,冬季,家常', 1, TRUE, 213, 210, 12, 10, 18, '白菜帮和叶分开下锅，帮先炖软；豆腐先用淡盐水泡十分钟不易碎；白胡椒粉起锅前放才够味。', '清淡鲜甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大白菜', '500', 'g', TRUE, 1, '/api/ingredients/baicai.jpg'),
  (@r, '豆腐', '1', '盒(约400g)', TRUE, 2, '/api/ingredients/doufu.jpg'),
  (@r, '红薯粉条', '60', 'g', FALSE, 3, '/api/ingredients/hongshufen.jpg'),
  (@r, '虾皮', '10', 'g', FALSE, 4, '/api/ingredients/xiapi.jpg'),
  (@r, '大葱', '半', '根', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '10', 'g', FALSE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 9, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '盐', '4', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '猪油', '25', 'g', TRUE, 11, '/api/ingredients/zhuyou.jpg'),
  (@r, '清水', '700', 'ml', TRUE, 12, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '白菜帮叶分开切块，豆腐切厚片淡盐水泡10分钟，粉条泡软', 12),
  (@r, 2, '热锅下猪油，爆香葱姜蒜，先下白菜帮炒至微微塌软', 4),
  (@r, 3, '加生抽翻匀，添清水烧开，下豆腐和粉条', 4),
  (@r, 4, '转中小火加盖炖15分钟至白菜透明、豆腐起孔', 16),
  (@r, 5, '下白菜叶再炖5分钟，加盐和白胡椒粉，撒虾皮出锅', 6);

-- ========== 10. 排骨炖豆角 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('排骨炖豆角', '东北炖菜的顶梁柱。黑猪排骨和油豆角同炖四十分钟，豆角炖到起皱发面、吸尽肉汁，土豆绵到边缘化在汤里，是夏天院子现摘的味道。', NULL, 20, 45, 65, 2, 4, '东北菜', '炖菜,下饭菜,夏季,东北四大炖', 1, TRUE, 96, 490, 28, 28, 25, '豆角一定要炖透，半生易中毒；油豆角、架豆王最耐炖；土豆后下，早下会化掉。', '咸鲜肉香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪排骨', '600', 'g', TRUE, 1, '/api/ingredients/zhupaigu.jpg'),
  (@r, '四季豆', '400', 'g', TRUE, 2, '/api/ingredients/sijidou.jpg'),
  (@r, '土豆', '2', '个', TRUE, 3, '/api/ingredients/tudou.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '15', 'g', FALSE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '12', 'ml', TRUE, 8, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '冰糖', '8', 'g', FALSE, 10, '/api/ingredients/bingtang.jpg'),
  (@r, '八角', '2', '个', FALSE, 11, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '小段', FALSE, 12, '/api/ingredients/guipi.jpg'),
  (@r, '盐', '4', 'g', TRUE, 13, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 14, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '1000', 'ml', TRUE, 15, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '排骨冷水下锅加姜葱料酒焯净血沫，捞出沥干；豆角去筋折段', 15),
  (@r, 2, '热锅下油，放冰糖八角桂皮炒香，排骨煸至表面金黄', 6),
  (@r, 3, '下姜葱蒜爆香，加生抽老抽翻炒上色', 3),
  (@r, 4, '添清水没过排骨，大火烧开转小火加盖炖20分钟', 22),
  (@r, 5, '下豆角段继续炖15分钟至豆角起皱软烂', 17),
  (@r, 6, '下滚刀土豆块再炖10分钟，试咸淡补盐', 11),
  (@r, 7, '大火收至汤汁浓稠挂在食材上，撒葱段出锅', 3);

-- ========== 11. 杀猪菜 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('杀猪菜', '东北年关的席。刚宰的猪现煮白肉、现灌血肠，配自家腌的酸菜一锅炖，酸香压住油腻，汤鲜肉厚。如今在家做，重点仍是酸菜要够酸、猪血要嫩。', NULL, 40, 60, 100, 3, 5, '东北菜', '炖菜,年菜,宴客,东北年俗', 1, TRUE, 217, 520, 30, 36, 11, '猪血切块后用八十度热水烫定型，滚水下锅就散；先煮肉、后下酸菜、临出锅烫血块，顺序错一样就老。', '酸香浓郁');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '400', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '猪骨', '500', 'g', TRUE, 2, '/api/ingredients/zhutonggu.jpg'),
  (@r, '酸菜', '600', 'g', TRUE, 3, '/api/ingredients/baicai.jpg'),
  (@r, '猪血', '300', 'g', TRUE, 4, '/api/ingredients/yaxue.jpg'),
  (@r, '红薯粉条', '120', 'g', FALSE, 5, '/api/ingredients/hongshufen.jpg'),
  (@r, '大葱', '1', '根', TRUE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 8, '/api/ingredients/dasuan.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '25', 'ml', FALSE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '花椒', '15', '粒', FALSE, 11, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '2', '个', FALSE, 12, '/api/ingredients/bajiao.jpg'),
  (@r, '香叶', '2', '片', FALSE, 13, '/api/ingredients/xiangye.jpg'),
  (@r, '盐', '5', 'g', TRUE, 14, '/api/ingredients/yan.jpg'),
  (@r, '猪油', '30', 'g', TRUE, 15, '/api/ingredients/zhuyou.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 16, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪骨和整块五花肉冷水下锅，加姜葱料酒花椒，烧开撇沫后小火煮40分钟', 45),
  (@r, 2, '肉煮至筷子插透捞出晾凉切薄片，原汤滤清留用', 12),
  (@r, 3, '酸菜切细丝漂洗攥干，猪血切厚块入八十度热水烫定型', 15),
  (@r, 4, '热锅下猪油，炒酸菜丝5分钟至酸香扑鼻', 6),
  (@r, 5, '倒入滤好的骨汤烧开，下酸菜和泡软的粉条炖20分钟', 22),
  (@r, 6, '肉片回锅烫热，下猪血块小火煨3分钟，加盐调味', 5),
  (@r, 7, '连锅上桌，配蒜泥生抽香油蘸汁', 3);

-- ========== 12. 雪衣豆沙 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('雪衣豆沙', '东北老菜里的甜功夫。红豆洗成沙、搓成小馅心，外面裹打发到能立筷子的蛋清糊，温油慢养着炸白，出锅撒白糖，形似雪堆、入口即化。', NULL, 60, 15, 75, 3, 4, '东北菜', '甜点,炸物,宴客,老菜', 1, TRUE, 209, 320, 8, 14, 41, '蛋清盆必须无油无水，筷子立住不倒才够硬；油温三四成热下锅，靠余温养大，油热就变焦黄，不白了。', '清甜绵密');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '红豆', '200', 'g', TRUE, 1, '/api/ingredients/xuedou.jpg'),
  (@r, '鸡蛋清', '4', '个', TRUE, 2, '/api/ingredients/jidanqing.jpg'),
  (@r, '白糖', '120', 'g', TRUE, 3, '/api/ingredients/baitang.jpg'),
  (@r, '猪油', '30', 'g', TRUE, 4, '/api/ingredients/zhuyou.jpg'),
  (@r, '糯米粉', '30', 'g', TRUE, 5, '/api/ingredients/nuomifen.jpg'),
  (@r, '淀粉', '20', 'g', FALSE, 6, '/api/ingredients/dianfen.jpg'),
  (@r, '熟芝麻', '10', 'g', FALSE, 7, '/api/ingredients/baizhima.jpg'),
  (@r, '桂花糖', '10', 'ml', FALSE, 8, '/api/ingredients/guihuatang.jpg'),
  (@r, '盐', '1', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '700', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '红豆泡一夜，蒸40分钟至烂，压成泥', 80),
  (@r, 2, '豆沙加白糖和猪油不粘锅里小火炒至能成团不粘手，晾凉搓成核桃大的馅心', 15),
  (@r, 3, '馅心表面拍一层面粉，冷藏20分钟定型', 22),
  (@r, 4, '蛋清加几滴白醋，用打蛋器甩到筷子立住不倒，拌入糯米粉和淀粉', 12),
  (@r, 5, '油烧至三四成热，馅心裹满蛋清糊逐朵下锅，小火养炸至膨白定型', 6),
  (@r, 6, '捞出升高油温回炸20秒使其挺括，沥油装盘', 2),
  (@r, 7, '撒白糖或糖桂花，配熟芝麻立即上桌，久放会塌', 2);

-- ========== 13. 酱骨架 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('酱骨架', '东北人啃骨头的快乐。猪筒骨焯净后用甜面酱和香料酱汤慢煨，酱色钻进骨缝，肉撕下来咸香带甜，最后拿手指捋一遍骨髓。配啤酒正好。', NULL, 20, 90, 110, 2, 4, '东北菜', '卤酱,硬菜,夜宵,下酒', 1, TRUE, 151, 440, 30, 30, 9, '甜面酱要先在油里炒出酱香再下汤，直接放有生酱味；酱好后原汤浸着凉透更入味，吃时回热。', '酱香咸甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪筒骨', '1200', 'g', TRUE, 1, '/api/ingredients/zhutonggu.jpg'),
  (@r, '甜面酱', '60', 'g', TRUE, 2, '/api/ingredients/tianmianjiang.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 3, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '20', 'ml', TRUE, 4, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 5, '/api/ingredients/liaojiu.jpg'),
  (@r, '冰糖', '25', 'g', TRUE, 6, '/api/ingredients/bingtang.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '30', 'g', FALSE, 9, '/api/ingredients/dasuan.jpg'),
  (@r, '八角', '3', '个', TRUE, 10, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '段', TRUE, 11, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '3', '片', FALSE, 12, '/api/ingredients/xiangye.jpg'),
  (@r, '花椒', '20', '粒', FALSE, 13, '/api/ingredients/huajiao.jpg'),
  (@r, '盐', '4', 'g', TRUE, 14, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 15, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '1800', 'ml', TRUE, 16, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '筒骨冷水下锅加姜葱料酒，大火烧开撇净浮沫，捞出冲净', 15),
  (@r, 2, '热锅下油，放甜面酱小火炒出酱香和红油', 4),
  (@r, 3, '下冰糖炒化，加生抽老抽和香料炒匀', 3),
  (@r, 4, '倒入清水和骨头，大火烧开转微火加盖煨75分钟', 78),
  (@r, 5, '中途翻两次面让酱色均匀，试咸淡补盐', 5),
  (@r, 6, '开盖大火收汁至汤浓挂骨，泡至凉透更入味', 12),
  (@r, 7, '剁段装盘，淋酱汤配蒜泥和葱段', 4);

-- ========== 14. 东北大拉皮 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('东北大拉皮', '夏天桌上的一盘凉。土豆淀粉摊出的拉皮透亮有韧性，切宽条配黄瓜丝、木耳、胡萝卜丝，浇芝麻酱蒜泥酸辣汁，拌匀后一根根挑起，滑溜带香。', NULL, 40, 10, 150, 2, 4, '东北菜', '凉菜,夏季,爽口,家常', 1, TRUE, 240, 260, 8, 12, 30, '自家摊拉皮：淀粉加水调浆，平盘薄薄一层烫至起泡，冰水冲凉才筋道；芝麻酱先加油泄开，直接加水会结块。', '麻酱酸辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大米凉粉', '400', 'g', TRUE, 1, '/api/ingredients/daliangfen.jpg'),
  (@r, '黄瓜', '1', '根', TRUE, 2, '/api/ingredients/huanggua.jpg'),
  (@r, '胡萝卜', '1', '根', TRUE, 3, '/api/ingredients/huluobo.jpg'),
  (@r, '水发木耳', '80', 'g', FALSE, 4, '/api/ingredients/muer.jpg'),
  (@r, '猪肉末', '80', 'g', FALSE, 5, '/api/ingredients/zhuroumo.jpg'),
  (@r, '芝麻酱', '40', 'g', TRUE, 6, '/api/ingredients/zhimajiang.jpg'),
  (@r, '陈醋', '30', 'ml', TRUE, 7, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '12', 'g', TRUE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 10, '/api/ingredients/dasuan.jpg'),
  (@r, '辣椒油', '20', 'ml', TRUE, 11, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '芝麻香油', '10', 'ml', FALSE, 12, '/api/ingredients/xiangyou.jpg'),
  (@r, '盐', '3', 'g', TRUE, 13, '/api/ingredients/yan.jpg'),
  (@r, '清水', '60', 'ml', TRUE, 14, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大米凉粉切宽条，冲凉开水后沥干拌少许香油防粘', 8),
  (@r, 2, '黄瓜胡萝卜切细丝，木耳焯水切丝，蒜捣成蒜泥', 12),
  (@r, 3, '芝麻酱分次加油泄开，再加生抽陈醋白糖清水和蒜泥调成麻酱汁', 8),
  (@r, 4, '肉末加生抽炒散炒香，晾凉备用', 5),
  (@r, 5, '拉皮垫底，码上各色丝和肉末，浇麻酱汁与辣椒油', 4),
  (@r, 6, '吃前拌匀，撒香菜段', 2);

-- ========== 15. 酸菜猪肉水饺 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('酸菜猪肉水饺', '东北饺子里最东北的一种。酸菜剁细攥水，拌进打足水的猪肉馅，酸味把肥肉的油香全提出来，煮好一口下去先吸汤再吃馅，配腊八蒜。', NULL, 60, 12, 72, 2, 4, '东北菜', '主食,饺子,年菜,家常', 1, TRUE, 131, 380, 16, 16, 42, '肉馅分次加葱姜水朝一个方向打上劲，再加酸菜，顺序别反；酸菜攥得越干馅越紧实；煮时点三次冷水，皮筋馅熟。', '酸鲜肉香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '饺子皮', '500', 'g', TRUE, 1, '/api/ingredients/jiaozipi.jpg'),
  (@r, '猪前腿肉馅', '400', 'g', TRUE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '酸菜', '350', 'g', TRUE, 3, '/api/ingredients/baicai.jpg'),
  (@r, '大葱', '1', '根', TRUE, 4, '/api/ingredients/dacong.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '8', 'ml', FALSE, 7, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '芝麻香油', '20', 'ml', TRUE, 9, '/api/ingredients/xiangyou.jpg'),
  (@r, '花椒粉', '2', 'g', FALSE, 10, '/api/ingredients/huajiaofen.jpg'),
  (@r, '盐', '5', 'g', TRUE, 11, '/api/ingredients/yan.jpg'),
  (@r, '清水', '120', 'ml', TRUE, 12, '/api/ingredients/qingshui.jpg'),
  (@r, '陈醋', '40', 'ml', FALSE, 13, '/api/ingredients/xiangcu.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '葱姜加清水泡10分钟成葱姜水；酸菜剁细再用纱布攥干水分', 20),
  (@r, 2, '肉馅加盐生抽老抽料酒和花椒粉，分三次打入葱姜水，朝一个方向搅上劲', 12),
  (@r, 3, '拌入酸菜末和葱花，最后淋香油封住，冷藏15分钟好包', 18),
  (@r, 4, '取皮放馅，对折捏出褶子收紧，摆盘', 20),
  (@r, 5, '宽水烧开下饺子，轻推防粘底，煮开后点半碗凉水', 6),
  (@r, 6, '重复点水三次至饺子鼓胀浮起，捞出沥水', 6),
  (@r, 7, '配陈醋和腊八蒜上桌', 2);
