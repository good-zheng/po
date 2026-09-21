-- 湖南菜谱种子数据（10道经典湘菜）
-- 使用 author_id = 1（admin 用户）

SET @now = NOW();

-- ========== 1. 剁椒鱼头 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile, created_at, updated_at)
VALUES ('剁椒鱼头', '湖南经典名菜，以鲜辣剁椒蒸制胖头鱼，鱼肉嫩滑、辣香浓郁，是湘菜的代表作之一。', NULL, 20, 15, 35, 2, 4, '湘菜', '下饭,经典,蒸菜,辣', 1, TRUE, 128, 320.0, 28.5, 18.2, 5.0, '鱼头要新鲜，蒸的时间不宜过长，否则肉质变老', '鲜辣', @now, @now);
SET @r1 = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order) VALUES
(@r1, '胖头鱼鱼头', 1.0, '个', TRUE, 1),
(@r1, '剁椒', 150.0, 'g', TRUE, 2),
(@r1, '蒜末', 30.0, 'g', TRUE, 3),
(@r1, '姜末', 15.0, 'g', TRUE, 4),
(@r1, '葱花', 20.0, 'g', FALSE, 5),
(@r1, '料酒', 15.0, 'ml', TRUE, 6),
(@r1, '蒸鱼豉油', 20.0, 'ml', TRUE, 7),
(@r1, '食用油', 30.0, 'ml', FALSE, 8);
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
(@r1, 1, '鱼头从中间劈开，去除鱼鳃和黑膜，用料酒和姜片腌制10分钟去腥', 10),
(@r1, 2, '盘底铺姜片，放上鱼头，均匀铺满剁椒和蒜末', 5),
(@r1, 3, '大火蒸12-15分钟，关火焖2分钟', 15),
(@r1, 4, '出锅撒葱花，淋蒸鱼豉油，浇上烧热的油激香', 3);

-- ========== 2. 小炒黄牛肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile, created_at, updated_at)
VALUES ('小炒黄牛肉', '湘菜经典小炒，选用新鲜黄牛肉搭配小米辣快炒，肉质鲜嫩、辣味十足，下饭神器。', NULL, 15, 10, 25, 2, 3, '湘菜', '下饭,小炒,辣,快手菜', 1, TRUE, 96, 450.0, 32.0, 25.0, 8.0, '牛肉要逆纹切薄片，腌制后大火快炒，时间不超过30秒', '香辣', @now, @now);
SET @r2 = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order) VALUES
(@r2, '黄牛肉', 300.0, 'g', TRUE, 1),
(@r2, '小米辣', 50.0, 'g', TRUE, 2),
(@r2, '青蒜苗', 80.0, 'g', TRUE, 3),
(@r2, '姜丝', 10.0, 'g', FALSE, 4),
(@r2, '生抽', 15.0, 'ml', TRUE, 5),
(@r2, '蚝油', 10.0, 'ml', TRUE, 6),
(@r2, '淀粉', 10.0, 'g', TRUE, 7),
(@r2, '食用油', 30.0, 'ml', FALSE, 8);
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
(@r2, 1, '牛肉逆纹切薄片，加生抽、淀粉、少许油抓匀腌制10分钟', 10),
(@r2, 2, '小米辣切段，青蒜苗切段备用', 5),
(@r2, 3, '锅热油，大火快炒牛肉片至变色，约30秒盛出', 1),
(@r2, 4, '锅中留底油，爆香姜丝和小米辣，加入青蒜苗翻炒', 2),
(@r2, 5, '倒回牛肉，加蚝油翻炒均匀出锅', 1);

-- ========== 3. 农家小炒肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile, created_at, updated_at)
VALUES ('农家小炒肉', '湖南农家经典家常菜，五花肉配青椒爆炒，肥而不腻、香辣开胃，被誉为湘菜之魂。', NULL, 10, 15, 25, 1, 3, '湘菜', '下饭,家常,辣,快手菜', 1, TRUE, 210, 520.0, 22.0, 38.0, 6.0, '五花肉要先煸出油脂，这样吃起来不腻且更香', '咸辣', @now, @now);
SET @r3 = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order) VALUES
(@r3, '五花肉', 300.0, 'g', TRUE, 1),
(@r3, '青椒', 200.0, 'g', TRUE, 2),
(@r3, '红椒', 50.0, 'g', FALSE, 3),
(@r3, '蒜片', 20.0, 'g', TRUE, 4),
(@r3, '豆豉', 15.0, 'g', TRUE, 5),
(@r3, '生抽', 15.0, 'ml', TRUE, 6),
(@r3, '老抽', 5.0, 'ml', FALSE, 7);
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
(@r3, 1, '五花肉切薄片，青红椒切滚刀块', 5),
(@r3, 2, '锅中不放油，中火将五花肉片煸炒至出油微焦', 5),
(@r3, 3, '推到一边，放入蒜片和豆豉爆香', 2),
(@r3, 4, '加入青红椒大火翻炒至断生，淋入生抽、老抽调味', 3);

-- ========== 4. 辣椒炒肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile, created_at, updated_at)
VALUES ('辣椒炒肉', '湖南人餐桌上的灵魂菜，螺丝椒配前腿肉，简单到极致却美味到极致，每个湖南人的家乡味。', NULL, 10, 10, 20, 1, 2, '湘菜', '下饭,家常,辣,快手菜', 1, TRUE, 320, 480.0, 25.0, 32.0, 5.0, '辣椒要用螺丝椒或线椒，猪油炒更香', '香辣', @now, @now);
SET @r4 = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order) VALUES
(@r4, '前腿猪肉', 200.0, 'g', TRUE, 1),
(@r4, '螺丝椒', 250.0, 'g', TRUE, 2),
(@r4, '蒜末', 15.0, 'g', TRUE, 3),
(@r4, '生抽', 10.0, 'ml', TRUE, 4),
(@r4, '猪油', 30.0, 'g', TRUE, 5),
(@r4, '盐', 3.0, 'g', FALSE, 6);
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
(@r4, 1, '猪肉肥瘦分开切薄片，螺丝椒拍扁切段', 5),
(@r4, 2, '锅烧热不放油，将螺丝椒干煸至虎皮状盛出', 3),
(@r4, 3, '锅中加猪油，先煸肥肉出油，再下瘦肉炒至变色', 3),
(@r4, 4, '加入蒜末和煸好的辣椒，淋生抽翻炒均匀出锅', 2);

-- ========== 5. 毛氏红烧肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile, created_at, updated_at)
VALUES ('毛氏红烧肉', '因毛主席喜爱而闻名的湘菜名品，五花肉红烧至软糯，色泽红亮、肥而不腻、入口即化。', NULL, 15, 90, 105, 3, 6, '湘菜', '经典,红烧,宴客,炖煮', 1, TRUE, 185, 680.0, 20.0, 52.0, 15.0, '全程小火慢炖，不要急于翻动，炖够时间才会软糯入味', '咸甜', @now, @now);
SET @r5 = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order) VALUES
(@r5, '带皮五花肉', 600.0, 'g', TRUE, 1),
(@r5, '冰糖', 40.0, 'g', TRUE, 2),
(@r5, '干辣椒', 8.0, '个', TRUE, 3),
(@r5, '八角', 2.0, '个', TRUE, 4),
(@r5, '桂皮', 1.0, '块', FALSE, 5),
(@r5, '香叶', 3.0, '片', FALSE, 6),
(@r5, '生抽', 30.0, 'ml', TRUE, 7),
(@r5, '老抽', 15.0, 'ml', TRUE, 8),
(@r5, '料酒', 30.0, 'ml', TRUE, 9),
(@r5, '葱段', 30.0, 'g', FALSE, 10);
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
(@r5, 1, '五花肉切3厘米方块，冷水下锅焯水去血沫，捞出沥干', 10),
(@r5, 2, '锅中少油，小火将冰糖炒至琥珀色起泡', 5),
(@r5, 3, '放入肉块翻炒上色，加入干辣椒、八角、桂皮、香叶', 5),
(@r5, 4, '淋料酒、加生抽老抽，加开水没过肉面', 5),
(@r5, 5, '大火烧开后转小火，盖盖慢炖60-80分钟至软糯', 80),
(@r5, 6, '大火收汁至浓稠，汤汁裹满肉块即可', 5);

-- ========== 6. 酸豆角炒肉末 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile, created_at, updated_at)
VALUES ('酸豆角炒肉末', '湖南人的开胃神器，酸豆角的酸爽搭配肉末的鲜香，酸辣开胃，米饭杀手级别的存在。', NULL, 10, 10, 20, 1, 3, '湘菜', '下饭,家常,酸辣,快手菜', 1, TRUE, 175, 380.0, 18.0, 22.0, 12.0, '酸豆角要提前泡水去盐，炒之前干煸去水分更香', '酸辣', @now, @now);
SET @r6 = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order) VALUES
(@r6, '酸豆角', 200.0, 'g', TRUE, 1),
(@r6, '猪肉末', 150.0, 'g', TRUE, 2),
(@r6, '小米辣', 20.0, 'g', TRUE, 3),
(@r6, '蒜末', 15.0, 'g', TRUE, 4),
(@r6, '生抽', 10.0, 'ml', TRUE, 5),
(@r6, '食用油', 20.0, 'ml', FALSE, 6);
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
(@r6, 1, '酸豆角切小段，提前用清水泡10分钟去过多盐分', 10),
(@r6, 2, '锅中不放油，干煸酸豆角至水分收干，盛出', 3),
(@r6, 3, '锅中加油烧热，放入肉末炒散炒至微焦', 3),
(@r6, 4, '加入蒜末、小米辣爆香，倒回酸豆角翻炒', 2),
(@r6, 5, '淋入生抽调味，翻炒均匀出锅', 1);

-- ========== 7. 湘西外婆菜 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile, created_at, updated_at)
VALUES ('湘西外婆菜', '源自湘西的腌菜小炒，多种腌菜混合炒制，咸香酸辣，是湖南人最爱的下饭菜之一。', NULL, 10, 8, 18, 1, 3, '湘菜', '下饭,家常,快手菜,腌菜', 1, TRUE, 88, 220.0, 8.0, 12.0, 18.0, '各种腌菜咸度不同，炒之前先尝一下，酌情调整盐量', '咸辣', @now, @now);
SET @r7 = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order) VALUES
(@r7, '外婆菜（腌菜）', 200.0, 'g', TRUE, 1),
(@r7, '猪肉末', 100.0, 'g', FALSE, 2),
(@r7, '小米辣', 30.0, 'g', TRUE, 3),
(@r7, '蒜末', 15.0, 'g', TRUE, 4),
(@r7, '葱花', 10.0, 'g', FALSE, 5),
(@r7, '食用油', 20.0, 'ml', FALSE, 6);
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
(@r7, 1, '外婆菜取出切碎，小米辣切段', 5),
(@r7, 2, '锅中加油烧热，放入肉末炒至变色', 2),
(@r7, 3, '加入小米辣和蒜末爆香', 1),
(@r7, 4, '放入外婆菜大火翻炒2-3分钟至干香', 3),
(@r7, 5, '撒葱花翻炒均匀出锅', 1);

-- ========== 8. 干锅牛蛙 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile, created_at, updated_at)
VALUES ('干锅牛蛙', '湘菜馆必点硬菜，牛蛙肉质细嫩，搭配藕片、土豆等配菜，麻辣鲜香，越吃越上瘾。', NULL, 20, 25, 45, 3, 4, '湘菜', '下饭,硬菜,麻辣,干锅', 1, TRUE, 156, 520.0, 35.0, 28.0, 18.0, '牛蛙先炸至金黄再入锅，外酥里嫩口感最佳', '麻辣', @now, @now);
SET @r8 = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order) VALUES
(@r8, '牛蛙', 600.0, 'g', TRUE, 1),
(@r8, '藕片', 150.0, 'g', FALSE, 2),
(@r8, '土豆片', 150.0, 'g', FALSE, 3),
(@r8, '干辣椒', 30.0, 'g', TRUE, 4),
(@r8, '花椒', 10.0, 'g', TRUE, 5),
(@r8, '郫县豆瓣酱', 30.0, 'g', TRUE, 6),
(@r8, '姜蒜', 30.0, 'g', TRUE, 7),
(@r8, '料酒', 20.0, 'ml', TRUE, 8),
(@r8, '淀粉', 30.0, 'g', TRUE, 9),
(@r8, '食用油', 100.0, 'ml', FALSE, 10);
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
(@r8, 1, '牛蛙处理干净切块，加料酒、盐、淀粉腌制15分钟', 15),
(@r8, 2, '藕片、土豆片焯水备用', 5),
(@r8, 3, '油温七成热，将牛蛙炸至金黄捞出', 5),
(@r8, 4, '锅留底油，小火炒香豆瓣酱、干辣椒、花椒、姜蒜', 3),
(@r8, 5, '加入配菜翻炒，放入牛蛙，大火翻炒入味', 5),
(@r8, 6, '转入干锅，点上酒精灯保温，撒香菜即可', 2);

-- ========== 9. 剁椒蒸排骨 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile, created_at, updated_at)
VALUES ('剁椒蒸排骨', '简单易做的湖南家常菜，排骨鲜嫩多汁，剁椒的辣味渗入肉中，蒸菜健康又美味。', NULL, 15, 30, 45, 1, 4, '湘菜', '家常,蒸菜,辣,简单', 1, TRUE, 112, 420.0, 30.0, 26.0, 6.0, '排骨要提前浸泡去血水，拌入淀粉可以锁住肉汁', '鲜辣', @now, @now);
SET @r9 = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order) VALUES
(@r9, '猪肋排', 500.0, 'g', TRUE, 1),
(@r9, '剁椒', 80.0, 'g', TRUE, 2),
(@r9, '蒜末', 20.0, 'g', TRUE, 3),
(@r9, '姜末', 10.0, 'g', TRUE, 4),
(@r9, '生抽', 15.0, 'ml', TRUE, 5),
(@r9, '蚝油', 10.0, 'ml', FALSE, 6),
(@r9, '淀粉', 15.0, 'g', TRUE, 7),
(@r9, '葱花', 10.0, 'g', FALSE, 8);
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
(@r9, 1, '排骨冷水浸泡30分钟去血水，沥干', 30),
(@r9, 2, '排骨加生抽、蚝油、淀粉、姜末抓匀腌制15分钟', 15),
(@r9, 3, '铺入盘中，均匀撒上剁椒和蒜末', 3),
(@r9, 4, '大火蒸25-30分钟至排骨熟透', 30),
(@r9, 5, '出锅撒葱花即可', 1);

-- ========== 10. 湖南米粉（汤粉） ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile, created_at, updated_at)
VALUES ('湖南米粉', '湖南人的早餐灵魂，圆粉配猪骨高汤，加上酸豆角、剁椒等浇头，一碗热腾腾的米粉开启美好一天。', NULL, 30, 60, 90, 2, 4, '湘菜', '经典,早餐,汤粉,主食', 1, TRUE, 245, 550.0, 22.0, 18.0, 65.0, '汤底要小火慢熬至少1小时，米粉提前泡软口感更好', '鲜香', @now, @now);
SET @r10 = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order) VALUES
(@r10, '湖南圆米粉', 400.0, 'g', TRUE, 1),
(@r10, '猪筒骨', 500.0, 'g', TRUE, 2),
(@r10, '猪肉片', 200.0, 'g', TRUE, 3),
(@r10, '酸豆角', 80.0, 'g', FALSE, 4),
(@r10, '剁椒', 30.0, 'g', FALSE, 5),
(@r10, '葱花', 20.0, 'g', TRUE, 6),
(@r10, '姜片', 20.0, 'g', TRUE, 7),
(@r10, '料酒', 20.0, 'ml', TRUE, 8),
(@r10, '盐', 5.0, 'g', TRUE, 9),
(@r10, '白胡椒粉', 3.0, 'g', FALSE, 10);
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
(@r10, 1, '猪筒骨冷水下锅焯水，捞出洗净', 10),
(@r10, 2, '另起锅加足量水，放入筒骨、姜片、料酒，大火烧开后转小火熬1小时', 60),
(@r10, 3, '米粉提前用温水泡软；酸豆角切碎炒香备用', 15),
(@r10, 4, '汤熬好后加盐和白胡椒调味，放入肉片烫熟', 5),
(@r10, 5, '米粉入沸水烫30秒捞出放入碗中，浇上骨汤和肉片', 2),
(@r10, 6, '加上酸豆角、剁椒、葱花即可食用', 1);
