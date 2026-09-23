-- 由 seed/recipes-xiang-a.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 湘菜，共 33 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 东安子鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('东安子鸡', '湘菜首席名菜，源自永州东安县。嫩母鸡煮至七成熟斩条，与姜醋辣椒同炒，酸辣鲜香、鸡条细嫩，醋香是这道菜的灵魂。', '/api/covers/xiang-donganzi-ji.jpg', 25, 15, 40, 2, 4, '湘菜', '经典,宴客,酸辣,鸡肉', 1, TRUE, 216, 420, 32, 24, 6, '鸡只煮到七成熟，煮老了肉柴；醋分两次放，起锅前沿锅边再淋半勺，香气更足。', '酸辣鲜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '土鸡', '1', '只(约1200g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '干红辣椒', '8', '个', TRUE, 2, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生姜', '50', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '青辣椒', '2', '根', FALSE, 4, '/api/ingredients/qinglajiao.jpg'),
  (@r, '陈醋', '30', 'ml', TRUE, 5, '/api/ingredients/xiangcu.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '花椒', '2', 'g', TRUE, 7, '/api/ingredients/huajiao.jpg'),
  (@r, '小葱', '3', '根', FALSE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '食用油', '50', 'ml', TRUE, 9, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '3', 'g', TRUE, 10, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '整鸡冷水下锅，加姜片、料酒煮约15分钟至七成熟，捞出晾凉后斩成小条', 15),
  (@r, 2, '干辣椒切段，生姜切丝，青辣椒切斜片，葱切段', 5),
  (@r, 3, '锅烧热油，下花椒、干辣椒段、姜丝爆香', 1),
  (@r, 4, '下鸡条中火翻炒2分钟，沿锅边烹入料酒和一半的醋', 3),
  (@r, 5, '加青辣椒片翻炒，加少许煮鸡的汤，中小火焖2分钟', 3),
  (@r, 6, '大火收汁，出锅前淋入剩下的醋，撒葱段翻匀装盘', 1);

-- ========== 2. 腊味合蒸 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('腊味合蒸', '湖南年菜经典，腊肉、腊鱼、腊鸡三味同蒸，腊香交融、咸鲜油润，是湘菜蒸菜的代表。', '/api/covers/xiang-lawei-hezheng.jpg', 15, 60, 75, 1, 4, '湘菜', '经典,年菜,蒸菜,腊味', 1, TRUE, 316, 520, 30, 40, 4, '腊味先用温水洗净表面烟尘，蒸的时候垫姜片去腥；想要更润可加一勺鸡汤同蒸。', '腊香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '腊肉', '200', 'g', TRUE, 1, '/api/ingredients/larou.jpg'),
  (@r, '腊鱼', '150', 'g', TRUE, 2, '/api/ingredients/layu.jpg'),
  (@r, '腊鸡', '150', 'g', FALSE, 3, '/api/ingredients/laji.jpg'),
  (@r, '干红辣椒', '5', '个', TRUE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 6, '/api/ingredients/baitang.jpg'),
  (@r, '食用油', '15', 'ml', FALSE, 7, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '腊肉、腊鱼、腊鸡用温水刷洗干净，上锅蒸20分钟后取出', 20),
  (@r, 2, '三种腊味分别切成厚薄均匀的片', 8),
  (@r, 3, '取大碗，腊味相间码入碗中，铺上姜丝、干辣椒段，淋少许油和糖', 5),
  (@r, 4, '上锅大火蒸40分钟至腊味软亮出油，倒扣入盘中即可', 40);

-- ========== 3. 麻辣子鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('麻辣子鸡', '长沙传统名菜，嫩鸡斩丁配干辣椒花椒火爆，外焦里嫩、麻辣透香，是湘菜"麻辣"一路的代表作。', '/api/covers/xiang-mala-ziji.jpg', 15, 10, 25, 2, 3, '湘菜', '经典,下饭,麻辣,鸡肉', 1, TRUE, 124, 480, 28, 32, 6, '鸡丁要炸两次，第一次定型、第二次逼出油分，才能达到外焦里嫩。', '麻辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸡腿', '2', '只', TRUE, 1, '/api/ingredients/jitui.jpg'),
  (@r, '干红辣椒', '15', 'g', TRUE, 2, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '3', 'g', TRUE, 3, '/api/ingredients/huajiao.jpg'),
  (@r, '红辣椒', '1', '根', FALSE, 4, '/api/ingredients/honglajiao.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '陈醋', '10', 'ml', TRUE, 8, '/api/ingredients/xiangcu.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '淀粉', '20', 'g', TRUE, 10, '/api/ingredients/dianfen.jpg'),
  (@r, '食用油', '500', 'ml', FALSE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡腿去骨切1.5厘米丁，加料酒、生抽、淀粉抓匀腌15分钟', 15),
  (@r, 2, '干辣椒切段去籽，红椒切小片，蒜切片', 3),
  (@r, 3, '油烧至六成热，下鸡丁炸至微黄捞出；油温升到八成热复炸20秒至酥脆', 4),
  (@r, 4, '锅留底油，小火煸香干辣椒段和花椒，下蒜片、红椒片', 2),
  (@r, 5, '倒入鸡丁大火翻炒，烹入料酒、陈醋，加少许糖炒匀即可', 2);

-- ========== 4. 永州血鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('永州血鸭', '湘南名肴，麻鸭斩块爆炒，起锅前拌入用白醋防凝的鲜鸭血，酱红油亮、鸭肉紧实，血香独特。', '/api/covers/xiang-yongzhou-xueya.jpg', 25, 35, 60, 3, 4, '湘菜', '经典,地方名菜,鸭肉,下饭', 1, TRUE, 113, 560, 34, 38, 6, '鲜鸭血必须立刻与白醋混合搅散防凝，最后下锅翻匀即起，久炒会变渣。', '香辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸭', '1', '只(约1500g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '鲜鸭血', '100', 'ml', TRUE, 2, '/api/ingredients/yaxue.jpg'),
  (@r, '白醋', '10', 'ml', TRUE, 3, '/api/ingredients/baicu.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '干红辣椒', '10', 'g', TRUE, 6, '/api/ingredients/ganlajiao.jpg'),
  (@r, '青辣椒', '3', '根', FALSE, 7, '/api/ingredients/qinglajiao.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 10, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鲜鸭血与白醋混合搅散防凝备用', 2),
  (@r, 2, '鸭子斩小块，冷水下锅焯水后沥干', 8),
  (@r, 3, '锅中放油，下鸭块中火煸炒至水分收干、出油微黄', 10),
  (@r, 4, '下姜片、蒜粒、干辣椒爆香，烹料酒、加生抽和适量热水，焖15分钟', 15),
  (@r, 5, '大火收汁至浓稠，倒入鸭血快速翻匀，血裹匀鸭块立即出锅', 2);

-- ========== 5. 洪江血粑鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('洪江血粑鸭', '湘西洪江名菜，鸭块与糯米血粑同焖。血粑吸饱鸭汁油润咸香，鸭肉紧实入味，一菜两吃是它的妙处。', '/api/covers/xiang-hongjiang-xueba-ya.jpg', 20, 40, 60, 2, 4, '湘菜', '经典,地方名菜,鸭肉,下饭', 1, TRUE, 195, 640, 30, 36, 28, '血粑先用油炸定型再与鸭同焖，既不散又能吸汁；买不到血粑可用糯米血肠代替。', '咸香微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸭', '半只(约750g)', '', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '糯米血粑', '300', 'g', TRUE, 2, '/api/ingredients/nuomixueba.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '干红辣椒', '10', 'g', TRUE, 5, '/api/ingredients/ganlajiao.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 8, '/api/ingredients/baitang.jpg'),
  (@r, '食用油', '500', 'ml', FALSE, 9, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '血粑切成1.5厘米厚的片；鸭斩块焯水沥干', 8),
  (@r, 2, '油烧至六成热，下血粑片炸至外壳定型微黄，捞出沥油', 5),
  (@r, 3, '锅留底油，下鸭块煸炒至出油，加姜蒜、干辣椒爆香', 6),
  (@r, 4, '烹料酒、加生抽、糖和热水没过鸭块，中小火焖20分钟', 20),
  (@r, 5, '下炸好的血粑翻匀，继续焖5分钟，大火收汁装盘', 6);

-- ========== 6. 芷江鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('芷江鸭', '怀化芷江侗乡名菜，本地麻鸭配老姜米酒焖炒，鸭肉酥嫩、姜香浓郁，是湘西南待客的招牌菜。', '/api/covers/xiang-zhijiang-ya.jpg', 20, 40, 60, 2, 4, '湘菜', '经典,地方名菜,鸭肉,宴客', 1, TRUE, 116, 520, 32, 34, 4, '老姜用量要足，与鸭油同煸出香；米酒代替清水焖煮，去腥提鲜两不误。', '咸鲜香辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸭', '1', '只(约1500g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '生姜', '80', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '干红辣椒', '10', 'g', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '米酒', '100', 'ml', TRUE, 4, '/api/ingredients/mijiu.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '5', 'ml', FALSE, 6, '/api/ingredients/laochou.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '3', '根', FALSE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 9, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸭子斩块，冷水下锅焯水后沥干；老姜一半切片、一半切丝', 10),
  (@r, 2, '锅中放油，下鸭块大火煸炒10分钟至表面焦黄、出油', 10),
  (@r, 3, '下姜片、蒜粒、干辣椒炒香，加生抽、老抽上色', 3),
  (@r, 4, '倒入米酒和适量热水，没过鸭块，小火焖20分钟', 20),
  (@r, 5, '大火收汁，撒姜丝和葱段翻匀出锅', 3);

-- ========== 7. 长沙口味虾 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('长沙口味虾', '长沙夜宵之王。小龙虾配豆瓣酱、花椒、紫苏大火焖制，麻、辣、鲜、香层层递进，吮指才够味。', '/api/covers/xiang-kouwei-xia.jpg', 30, 25, 55, 2, 3, '湘菜', '夜宵,麻辣,小龙虾,宴客', 1, TRUE, 138, 380, 30, 18, 12, '小龙虾用刷子逐只刷净腹部，剪头去腮抽虾线；紫苏最后放，久煮香气会散。', '麻辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '小龙虾', '1000', 'g', TRUE, 1, '/api/ingredients/xiaolongxia.jpg'),
  (@r, '郫县豆瓣酱', '40', 'g', TRUE, 2, '/api/ingredients/pixianjiang.jpg'),
  (@r, '干红辣椒', '15', 'g', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '5', 'g', TRUE, 4, '/api/ingredients/huajiao.jpg'),
  (@r, '紫苏', '50', 'g', TRUE, 5, '/api/ingredients/zisu.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '50', 'g', TRUE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '啤酒', '330', 'ml', TRUE, 8, '/api/ingredients/pijiu.jpg'),
  (@r, '白糖', '8', 'g', FALSE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '小龙虾刷洗干净，剪去头部前端、抽出虾线', 20),
  (@r, 2, '姜切片、蒜拍碎、紫苏洗净摘叶备用', 5),
  (@r, 3, '锅中放油，下豆瓣酱小火炒出红油，加干辣椒、花椒、姜蒜爆香', 4),
  (@r, 4, '下小龙虾大火翻炒至变红，倒入啤酒，加生抽、糖，中火焖15分钟', 15),
  (@r, 5, '撒入紫苏叶翻匀，再煮2分钟关火，连汤汁浸泡10分钟更入味', 12);

-- ========== 8. 长沙臭豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('长沙臭豆腐', '火宫殿名小吃，黑豆腐胚炸至外酥里嫩，浇上蒜水辣汁，闻着臭吃着香，长沙街头的味道名片。', '/api/covers/xiang-chou-doufu.jpg', 10, 10, 20, 1, 2, '湘菜', '小吃,街头美食,油炸,素食', 1, TRUE, 228, 320, 14, 22, 16, '买市售黑色臭豆腐生胚最稳妥；炸到外壳鼓起变硬再翻面，浇汁前用筷子戳洞让汤汁渗入。', '酸辣咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '臭豆腐胚', '12', '块', TRUE, 1, '/api/ingredients/choudoufu.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 2, '/api/ingredients/dasuan.jpg'),
  (@r, '辣椒面', '10', 'g', TRUE, 3, '/api/ingredients/lajiaofen.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '陈醋', '10', 'ml', FALSE, 5, '/api/ingredients/xiangcu.jpg'),
  (@r, '香菜', '15', 'g', FALSE, 6, '/api/ingredients/xiangcai.jpg'),
  (@r, '榨菜', '20', 'g', FALSE, 7, '/api/ingredients/zhacai.jpg'),
  (@r, '食用油', '500', 'ml', FALSE, 8, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大蒜压成蒜泥，加少许温开水调成蒜水；榨菜切末', 3),
  (@r, 2, '辣椒面放入碗中，浇一勺热油激成辣椒油，加生抽、陈醋、蒜水调成料汁', 3),
  (@r, 3, '油烧至七成热，下臭豆腐胚炸至外壳变硬鼓起、捞出', 5),
  (@r, 4, '复炸30秒至外酥，捞出装盘，用筷子在每块上戳一个小洞', 1),
  (@r, 5, '浇上料汁，撒榨菜末和香菜即可', 1);

-- ========== 9. 糖油粑粑 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('糖油粑粑', '长沙传统甜味小吃，糯米饼在糖油里慢煮，外脆内糯、甜而不腻，"毛泽东也排队"的老口子记忆。', '/api/covers/xiang-tyou-baba.jpg', 15, 15, 30, 1, 2, '湘菜', '小吃,甜点,街头美食,素食', 1, TRUE, 101, 460, 6, 8, 92, '糖油用红糖加白糖更出琥珀色；粑粑下锅后用锅铲轻压，糖浆才能裹得均匀。', '香甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '糯米粉', '300', 'g', TRUE, 1, '/api/ingredients/nuomifen.jpg'),
  (@r, '红糖', '50', 'g', TRUE, 2, '/api/ingredients/hongtang.jpg'),
  (@r, '白糖', '30', 'g', TRUE, 3, '/api/ingredients/baitang.jpg'),
  (@r, '食用油', '150', 'ml', FALSE, 4, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '糯米粉加温水揉成光滑面团，分成小剂子，搓圆压成1厘米厚的饼', 10),
  (@r, 2, '锅中放油和糖，小火慢慢熬至糖融化起泡', 4),
  (@r, 3, '下糯米饼，中小火煎炸，不断翻面并淋糖油', 8),
  (@r, 4, '炸至两面金黄、糖浆浓稠裹匀，出锅趁热吃', 2);

-- ========== 10. 葱油粑粑 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('葱油粑粑', '长沙早餐摊的老味道，米浆调葱花入勺油炸，外壳金黄酥脆、内里软嫩，一口一个停不下来。', '/api/covers/xiang-congyou-baba.jpg', 120, 15, 135, 2, 3, '湘菜', '小吃,早餐,油炸,素食', 1, TRUE, 193, 350, 7, 12, 52, '米浆要提前磨好静置发酵2小时以上才有香气；圆勺先入油烫热再倒浆，粑粑才能完整脱模。', '咸香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大米', '300', 'g', TRUE, 1, '/api/ingredients/dami.jpg'),
  (@r, '糯米', '50', 'g', TRUE, 2, '/api/ingredients/nuomi.jpg'),
  (@r, '小葱', '50', 'g', TRUE, 3, '/api/ingredients/xiaocong.jpg'),
  (@r, '盐', '4', 'g', TRUE, 4, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '500', 'ml', FALSE, 5, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大米和糯米混合，加水浸泡4小时后打成细米浆', 10),
  (@r, 2, '米浆加盖静置发酵2小时，至表面起小泡', 120),
  (@r, 3, '拌入盐和葱花搅匀；圆勺入油锅中烫热', 3),
  (@r, 4, '勺内舀入一层米浆，连勺浸入七成热油中，定型后轻抖脱模', 4),
  (@r, 5, '炸至金黄浮起捞出，稍凉即食', 3);

-- ========== 11. 火宫殿姊妹团子 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('火宫殿姊妹团子', '长沙火宫殿传统名点，糯米皮一甜一咸成"姊妹"：糖馅流沙细嫩，肉馅鲜香多汁，蒸得晶莹透亮。', '/api/covers/xiang-zimei-tuanzi.jpg', 40, 15, 55, 2, 3, '湘菜', '小吃,点心,蒸点,糯米', 1, TRUE, 308, 420, 10, 10, 70, '糯米粉团要揉到不裂不粘手，包馅时收口捏紧；蒸的时候垫油纸防粘。', '香甜咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '糯米粉', '250', 'g', TRUE, 1, '/api/ingredients/nuomifen.jpg'),
  (@r, '粘米粉', '50', 'g', TRUE, 2, '/api/ingredients/zhanmifen.jpg'),
  (@r, '猪瘦肉', '150', 'g', TRUE, 3, '/api/ingredients/zhushourou.jpg'),
  (@r, '白糖', '60', 'g', TRUE, 4, '/api/ingredients/baitang.jpg'),
  (@r, '红枣', '30', 'g', TRUE, 5, '/api/ingredients/hongzao.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '香油', '8', 'ml', FALSE, 7, '/api/ingredients/xiangyou.jpg'),
  (@r, '桂花糖', '10', 'g', FALSE, 8, '/api/ingredients/guihuatang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '糯米粉与粘米粉混合，加温水和成软硬适中的粉团', 10),
  (@r, 2, '猪瘦肉剁成肉末，加生抽、香油搅打上劲成肉馅', 8),
  (@r, 3, '红枣去核切碎，与白糖、桂花糖拌匀成糖馅', 5),
  (@r, 4, '粉团分剂，一半包肉馅、一半包糖馅，收口搓圆', 10),
  (@r, 5, '垫油纸上锅，水开后蒸12分钟至皮色透亮', 12);

-- ========== 12. 蒜薹炒腊肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('蒜薹炒腊肉', '湖南家常下饭王。烟熏腊肉肥瘦透亮，配脆嫩蒜薹大火同炒，腊香裹着蒜香，一碗饭不够吃。', '/api/covers/xiang-suantai-laorou.jpg', 15, 10, 25, 1, 3, '湘菜', '家常,下饭,腊味,快手菜', 1, TRUE, 289, 480, 18, 40, 8, '腊肉先蒸或煮10分钟再切片，既去咸味又好切；蒜薹先干煸去生辣味更香。', '腊香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '腊肉', '250', 'g', TRUE, 1, '/api/ingredients/larou.jpg'),
  (@r, '蒜薹', '250', 'g', TRUE, 2, '/api/ingredients/suantai.jpg'),
  (@r, '干红辣椒', '5', '个', FALSE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生抽', '5', 'ml', FALSE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '食用油', '10', 'ml', FALSE, 5, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '腊肉上锅蒸10分钟，晾凉后切薄片；蒜薹掐段洗净', 12),
  (@r, 2, '锅烧热不放油，下蒜薹煸至表皮起皱，盛出', 3),
  (@r, 3, '锅中下腊肉片中火煸出油，加干辣椒段炒香', 3),
  (@r, 4, '倒入蒜薹大火翻炒，淋少许生抽调味即可', 2);

-- ========== 13. 干豆角炒腊肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('干豆角炒腊肉', '湖南乡下经典搭配，干豆角吸饱腊肉的油香，嚼起来干香有韧劲，越嚼越香的"外婆味道"。', '/api/covers/xiang-gandoujiao-laorou.jpg', 30, 12, 42, 1, 3, '湘菜', '家常,下饭,腊味,乡村风味', 1, TRUE, 208, 460, 16, 36, 12, '干豆角用温水泡发到回软即可，泡太久会失去干香；炒时借腊肉的油，不必另放油。', '腊香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '腊肉', '250', 'g', TRUE, 1, '/api/ingredients/larou.jpg'),
  (@r, '干豆角', '100', 'g', TRUE, 2, '/api/ingredients/gandoujiao.jpg'),
  (@r, '干红辣椒', '5', '个', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '5', 'ml', FALSE, 5, '/api/ingredients/shengchou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '干豆角温水泡发30分钟，洗净切段', 30),
  (@r, 2, '腊肉煮软切薄片，蒜切片', 8),
  (@r, 3, '锅热下腊肉煸出油，下蒜片、干辣椒爆香', 3),
  (@r, 4, '下干豆角中火翻炒3分钟，淋少许生抽和一勺水，炒干水汽即可', 4);

-- ========== 14. 萝卜干炒腊肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('萝卜干炒腊肉', '咸香的萝卜干遇上油润的腊肉，一脆一韧，是湖南人秋冬餐桌最落胃的一盘炒菜。', '/api/covers/xiang-luobogan-laorou.jpg', 20, 10, 30, 1, 3, '湘菜', '家常,下饭,腊味,快手菜', 1, TRUE, 274, 450, 16, 36, 10, '萝卜干本身很咸，泡水后先尝一下再决定要不要放盐。', '咸香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '萝卜干', '120', 'g', TRUE, 1, '/api/ingredients/luobogan.jpg'),
  (@r, '腊肉', '250', 'g', TRUE, 2, '/api/ingredients/larou.jpg'),
  (@r, '干红辣椒', '5', '个', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '青辣椒', '2', '根', FALSE, 5, '/api/ingredients/qinglajiao.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '萝卜干温水泡20分钟洗净，切成小丁；腊肉煮软切片', 20),
  (@r, 2, '锅热下腊肉煸炒出油，下蒜片、干辣椒段爆香', 3),
  (@r, 3, '下萝卜干丁大火翻炒2分钟', 2),
  (@r, 4, '加青辣椒片翻炒断生即可出锅', 2);

-- ========== 15. 湘西蕨菜炒腊肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湘西蕨菜炒腊肉', '山野蕨菜配湘西烟熏腊肉，蕨菜滑嫩带山气，腊肉烟香浓郁，是湘西待客的风味硬菜。', '/api/covers/xiang-juecai-laorou.jpg', 30, 10, 40, 1, 3, '湘菜', '家常,山珍,腊味,湘西', 1, TRUE, 269, 430, 15, 34, 9, '干蕨菜要泡发足够久并多换水，去掉涩味后再炒；鲜蕨菜必须焯水去原蕨苷。', '腊香微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '干蕨菜', '80', 'g', TRUE, 1, '/api/ingredients/juecai.jpg'),
  (@r, '腊肉', '250', 'g', TRUE, 2, '/api/ingredients/larou.jpg'),
  (@r, '干红辣椒', '6', '个', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '盐', '1', 'g', FALSE, 6, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '干蕨菜温水泡发4小时，多换几次水，切段', 30),
  (@r, 2, '腊肉煮软切片，姜蒜切片', 8),
  (@r, 3, '锅热下腊肉煸出油，下姜蒜片、干辣椒爆香', 3),
  (@r, 4, '下蕨菜大火翻炒3分钟，尝味后酌情加盐，炒匀出锅', 4);

-- ========== 16. 攸县香干炒肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('攸县香干炒肉', '株洲攸县名产香干，豆香浓郁有嚼劲，配土猪肉片大火快炒，是湘菜馆点单率最高的小炒之一。', '/api/covers/xiang-youxian-xianggan.jpg', 15, 10, 25, 1, 3, '湘菜', '家常,下饭,豆制品,快手菜', 1, TRUE, 254, 420, 26, 28, 8, '香干先煎至两面起泡再炒，豆香才足；五花肉煸出的油正是香干最好的伴侣。', '咸香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '香干', '300', 'g', TRUE, 1, '/api/ingredients/xianggan.jpg'),
  (@r, '五花肉', '150', 'g', TRUE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '青蒜苗', '50', 'g', TRUE, 3, '/api/ingredients/qingsuan.jpg'),
  (@r, '干红辣椒', '4', '个', FALSE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '食用油', '15', 'ml', FALSE, 7, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '香干切三角片，五花肉切薄片，青蒜苗切段', 8),
  (@r, 2, '锅放少许油，下香干片中火煎至两面金黄起泡，盛出', 4),
  (@r, 3, '下五花肉片煸出油，加蒜片、干辣椒段爆香', 3),
  (@r, 4, '倒回香干，加生抽大火翻炒，下蒜苗段炒断生即可', 3);

-- ========== 17. 擂辣椒皮蛋 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('擂辣椒皮蛋', '湘味经典凉菜。青辣椒烧出虎皮后与皮蛋同入擂钵，加蒜擂碎，煳香、辣香、蛋香浑然一体，下饭一绝。', '/api/covers/xiang-lei-jiaojiao-pidan.jpg', 5, 10, 15, 1, 2, '湘菜', '凉菜,下饭,素菜,快手菜', 1, TRUE, 242, 220, 10, 14, 10, '辣椒干烧或干烙至整只起虎皮再撕皮，煳香味才正；擂的时候加一小撮盐更出味。', '煳辣咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '青辣椒', '300', 'g', TRUE, 1, '/api/ingredients/qinglajiao.jpg'),
  (@r, '皮蛋', '2', '个', TRUE, 2, '/api/ingredients/pidan.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '芝麻香油', '5', 'ml', FALSE, 5, '/api/ingredients/xiangyou.jpg'),
  (@r, '盐', '2', 'g', TRUE, 6, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '青辣椒整只洗净，干锅（不放油）中小火烙至全身起虎皮发软', 8),
  (@r, 2, '烙好的辣椒撕去外皮，去蒂备用', 3),
  (@r, 3, '皮蛋剥壳切瓣，与辣椒、蒜瓣、盐一起放入擂钵（或用擀面杖在碗中代替）', 3),
  (@r, 4, '擂至辣椒起茸、皮蛋碎与蒜融合，加生抽、香油拌匀装盘', 2);

-- ========== 18. 家常红烧鳊鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('家常红烧鳊鱼', '洞庭湖区的家常烧鱼。鳊鱼肉厚刺少，煎香后加姜蒜辣椒红烧，酱汁浓郁，鱼肉细嫩入味。', '/api/covers/xiang-hongshaio-bianyu.jpg', 15, 20, 35, 2, 3, '湘菜', '家常,下饭,河鲜,宴客', 1, TRUE, 123, 380, 32, 20, 8, '煎鱼前把鱼身水分擦干，热锅凉油不破皮；烧的过程中用勺把汁不断浇到鱼背上。', '咸鲜微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鳊鱼', '1', '条(约750g)', TRUE, 1, '/api/ingredients/bianyu.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '干红辣椒', '6', '个', TRUE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '小葱', '3', '根', FALSE, 5, '/api/ingredients/xiaocong.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 7, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '食用油', '60', 'ml', FALSE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鳊鱼去鳞去鳃去内脏，两面打斜花刀，擦干水分，抹少许盐和料酒腌10分钟', 12),
  (@r, 2, '油烧至七成热，下鳊鱼中火煎至两面金黄定型', 6),
  (@r, 3, '下姜蒜片、干辣椒段爆香，烹料酒、加生抽老抽、糖和热水没过鱼身一半', 2),
  (@r, 4, '中火烧10分钟，期间不断把汤汁浇到鱼背上', 10),
  (@r, 5, '大火收汁至浓稠，撒葱花出锅', 3);

-- ========== 19. 紫苏炒田螺 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('紫苏炒田螺', '长沙夜宵摊的"唆螺"。田螺吐净泥沙剪尾，与紫苏、辣椒、姜蒜爆炒，一颗一颗唆着吃才过瘾。', '/api/covers/xiang-zisu-tianluo.jpg', 240, 20, 260, 2, 3, '湘菜', '夜宵,下酒,河鲜,小吃', 1, TRUE, 169, 260, 22, 10, 10, '田螺买回后清水养半天吐沙，滴几滴香油吐得更干净；剪掉螺尾更容易入味和吸食。', '香辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '田螺', '800', 'g', TRUE, 1, '/api/ingredients/tianluo.jpg'),
  (@r, '紫苏', '50', 'g', TRUE, 2, '/api/ingredients/zisu.jpg'),
  (@r, '干红辣椒', '15', 'g', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '啤酒', '200', 'ml', FALSE, 6, '/api/ingredients/pijiu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '3', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '40', 'ml', FALSE, 9, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '田螺清水养半天吐净泥沙，逐只刷净剪去螺尾', 240),
  (@r, 2, '姜切末、蒜切末、干辣椒剪段、紫苏摘叶洗净', 5),
  (@r, 3, '锅热油，下姜蒜末、干辣椒段爆香，倒入田螺大火翻炒', 3),
  (@r, 4, '加生抽、盐和啤酒，盖盖焖煮8分钟', 8),
  (@r, 5, '下紫苏叶大火翻炒2分钟至香气扑鼻，出锅', 2);

-- ========== 20. 酸辣鸡杂 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('酸辣鸡杂', '鸡胗鸡心脆嫩弹牙，配酸豆角、小米辣猛火爆炒，酸辣冲鼻，是湖南人"重口味"下饭菜的代表。', '/api/covers/xiang-suanla-jiza.jpg', 15, 8, 23, 1, 2, '湘菜', '家常,下饭,快手菜,酸辣', 1, TRUE, 167, 280, 24, 14, 8, '鸡杂切薄片后加料酒和淀粉抓洗去腥，全程大火快炒，一变色就下调料，久了会老。', '酸辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸡杂', '300', 'g', TRUE, 1, '/api/ingredients/jiza.jpg'),
  (@r, '酸豆角', '100', 'g', TRUE, 2, '/api/ingredients/suandoujiao.jpg'),
  (@r, '小米辣', '15', 'g', TRUE, 3, '/api/ingredients/xiaomila.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '陈醋', '5', 'ml', FALSE, 8, '/api/ingredients/xiangcu.jpg'),
  (@r, '淀粉', '10', 'g', TRUE, 9, '/api/ingredients/dianfen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡杂洗净切薄片，加料酒、淀粉抓匀腌10分钟；酸豆角切小段', 12),
  (@r, 2, '小米辣切圈，姜蒜切末', 3),
  (@r, 3, '锅烧热油，大火下鸡杂爆炒至变色断生', 2),
  (@r, 4, '下姜蒜末、小米辣、酸豆角大火翻炒2分钟', 2),
  (@r, 5, '淋生抽、几滴陈醋，翻匀立即出锅', 1);

-- ========== 21. 湘味爆炒猪肝 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湘味爆炒猪肝', '猪肝切得极薄，猛火快炒断生即起，嫩得像豆腐，配上青蒜辣椒的锅气，是检验火候的湘菜基本功。', '/api/covers/xiang-baochao-zhugan.jpg', 20, 5, 25, 2, 2, '湘菜', '家常,下饭,快手菜,爆炒', 1, TRUE, 316, 320, 26, 16, 8, '猪肝泡水去血水后要彻底沥干；滑油时五六成热下锅，变色就捞，全靠回锅那十几秒入味。', '咸香微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪肝', '300', 'g', TRUE, 1, '/api/ingredients/zhugan.jpg'),
  (@r, '青蒜苗', '50', 'g', TRUE, 2, '/api/ingredients/qingsuan.jpg'),
  (@r, '红辣椒', '1', '根', FALSE, 3, '/api/ingredients/honglajiao.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '淀粉', '15', 'g', TRUE, 8, '/api/ingredients/dianfen.jpg'),
  (@r, '白胡椒粉', '1', 'g', FALSE, 9, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '食用油', '300', 'ml', FALSE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪肝切2毫米薄片，清水浸泡20分钟去血水，捞出挤干', 20),
  (@r, 2, '猪肝加料酒、生抽、淀粉、白胡椒粉抓匀腌5分钟', 5),
  (@r, 3, '油烧至五成热，下猪肝快速滑散，变色立即捞出', 1),
  (@r, 4, '锅留底油，下姜蒜片、红辣椒片爆香', 1),
  (@r, 5, '倒回猪肝，下青蒜苗段，大火翻炒十几秒，调少许生抽即可', 1);

-- ========== 22. 酸辣腰花 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('酸辣腰花', '猪腰打上麦穗花刀，配泡椒姜蒜猛火爆炒，脆嫩无腥，酸辣汁裹着腰花，湘菜火候菜的看家本领。', '/api/covers/xiang-suanla-yaohua.jpg', 20, 5, 25, 3, 2, '湘菜', '家常,下饭,爆炒,酸辣', 1, TRUE, 213, 300, 24, 16, 8, '腰臊（白色筋膜）必须片干净才能去腥；花刀深浅一致，焯或炒的时候才会卷成漂亮的腰花。', '酸辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪腰', '2', '个', TRUE, 1, '/api/ingredients/zhuyao.jpg'),
  (@r, '泡红椒', '30', 'g', TRUE, 2, '/api/ingredients/paohongjiao.jpg'),
  (@r, '小米辣', '10', 'g', FALSE, 3, '/api/ingredients/xiaomila.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '青蒜苗', '30', 'g', FALSE, 6, '/api/ingredients/qingsuan.jpg'),
  (@r, '陈醋', '10', 'ml', TRUE, 7, '/api/ingredients/xiangcu.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '淀粉', '10', 'g', TRUE, 9, '/api/ingredients/dianfen.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪腰剖开片净腰臊，斜刀打十字花刀后切成小块', 10),
  (@r, 2, '腰花加料酒抓洗，再冲水沥干，拌少许淀粉备用', 8),
  (@r, 3, '泡红椒切碎、姜蒜切末、青蒜苗切段', 3),
  (@r, 4, '锅大火烧油至冒烟，下腰花爆炒10秒至打卷', 1),
  (@r, 5, '下泡椒末、姜蒜末、蒜苗炒香，烹陈醋和生抽，翻匀立即出锅', 1);

-- ========== 23. 虎皮青椒 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('虎皮青椒', '整只青椒干烙出虎皮斑，再用糖醋蒜香汁一焖，皮皱肉软、酸辣回甜，最下饭的素菜没有之一。', '/api/covers/xiang-hupi-qingjiao.jpg', 5, 10, 15, 1, 2, '湘菜', '家常,下饭,素菜,快手菜', 1, TRUE, 106, 160, 3, 9, 12, '青椒选皮薄肉厚的螺丝椒最好；烙的时候用锅铲压平，虎皮才均匀。', '酸辣回甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '青辣椒', '300', 'g', TRUE, 1, '/api/ingredients/qinglajiao.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 2, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 3, '/api/ingredients/shengchou.jpg'),
  (@r, '陈醋', '15', 'ml', TRUE, 4, '/api/ingredients/xiangcu.jpg'),
  (@r, '白糖', '10', 'g', TRUE, 5, '/api/ingredients/baitang.jpg'),
  (@r, '食用油', '15', 'ml', FALSE, 6, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '青椒洗净去柄，用刀背轻拍裂；蒜切末', 3),
  (@r, 2, '干锅小火将青椒烙至两面起虎皮斑、变软', 6),
  (@r, 3, '加少许油、蒜末炒香，烹入生抽、陈醋、白糖和小半碗水', 1),
  (@r, 4, '中火焖1分钟让虎皮吸汁，大火收浓即可', 2);

-- ========== 24. 湖南啤酒鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湖南啤酒鸭', '湘人家宴常客。鸭块煸出油，与姜蒜辣椒同炒后整瓶啤酒焖烧，酒香去腥、汤汁浓郁，越焖越香。', '/api/covers/xiang-pijiu-ya.jpg', 15, 50, 65, 2, 4, '湘菜', '家常,宴客,鸭肉,下饭', 1, TRUE, 106, 520, 30, 32, 10, '鸭子皮下的油要煸出来，成菜才不腻；啤酒要用整瓶，不额外加水。', '香辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸭', '半只(约800g)', '', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '啤酒', '500', 'ml', TRUE, 2, '/api/ingredients/pijiu.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '干红辣椒', '10', 'g', TRUE, 5, '/api/ingredients/ganlajiao.jpg'),
  (@r, '八角', '2', '个', FALSE, 6, '/api/ingredients/bajiao.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 8, '/api/ingredients/laochou.jpg'),
  (@r, '青蒜苗', '30', 'g', FALSE, 9, '/api/ingredients/qingsuan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸭子斩块，冷水下锅焯水后沥干', 10),
  (@r, 2, '锅不放油，下鸭块中火煸炒10分钟至出油微黄', 10),
  (@r, 3, '下姜片、蒜粒、干辣椒、八角爆香，加生抽、老抽炒上色', 3),
  (@r, 4, '倒入整瓶啤酒，大火烧开后转小火焖35分钟', 35),
  (@r, 5, '大火收汁，撒青蒜苗段翻匀出锅', 3);

-- ========== 25. 常德津市牛肉粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('常德津市牛肉粉', '常德米粉的头牌。牛腩炖到酥烂作码子，红油骨汤浇在烫熟的圆粉上，一碗管饱，"嗦粉"的至高形态。', '/api/covers/xiang-jinshi-nurou-fen.jpg', 20, 120, 140, 2, 2, '湘菜', '主食,米粉,牛肉,地方名吃', 1, TRUE, 182, 620, 30, 22, 72, '牛肉炖前先焯水，加香料小火炖足2小时才酥；米粉烫十几秒即可，久烫会软烂。', '香辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '牛腩', '500', 'g', TRUE, 1, '/api/ingredients/niurou.jpg'),
  (@r, '干米粉', '300', 'g', TRUE, 2, '/api/ingredients/ganmifen.jpg'),
  (@r, '猪筒骨', '300', 'g', TRUE, 3, '/api/ingredients/zhutonggu.jpg'),
  (@r, '干红辣椒', '15', 'g', TRUE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '八角', '2', '个', TRUE, 6, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '小段', FALSE, 7, '/api/ingredients/guipi.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 9, '/api/ingredients/laochou.jpg'),
  (@r, '辣椒油', '15', 'ml', FALSE, 10, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '小葱', '2', '根', FALSE, 11, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 12, '/api/ingredients/xiangcai.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛腩和筒骨冷水下锅焯水，洗净后放入汤锅', 10),
  (@r, 2, '加姜片、干辣椒、八角、桂皮、生抽老抽，加足量水大火烧开转小火炖2小时', 120),
  (@r, 3, '牛腩捞出稍凉切薄片，汤中加盐调味保持微滚', 5),
  (@r, 4, '米粉入沸水烫15秒，捞入大碗', 1),
  (@r, 5, '码上牛肉片，浇滚烫骨汤，按口味加辣椒油，撒葱花香菜', 2);

-- ========== 26. 栖凤渡鱼粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('栖凤渡鱼粉', '郴州栖凤渡名吃，鲜鱼现熬白汤再冲辣椒红汤，鲜、辣、烫一体，鱼香锁在每一根粉里。', '/api/covers/xiang-qifengdu-yufen.jpg', 15, 40, 55, 2, 2, '湘菜', '主食,米粉,河鲜,地方名吃', 1, TRUE, 135, 520, 28, 16, 64, '鱼头鱼骨先煎再熬，汤才白；红汤辣椒要用热油现泼，趁烫浇粉风味最正。', '鲜辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鳙鱼', '1', '条(约750g)', TRUE, 1, '/api/ingredients/yongyu.jpg'),
  (@r, '干米粉', '300', 'g', TRUE, 2, '/api/ingredients/ganmifen.jpg'),
  (@r, '豆膏', '20', 'g', FALSE, 3, '/api/ingredients/douchi.jpg'),
  (@r, '干红辣椒', '20', 'g', TRUE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '辣椒油', '15', 'ml', TRUE, 7, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '小葱', '3', '根', TRUE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '食用油', '50', 'ml', FALSE, 9, '/api/ingredients/shiyongyou.jpg'),
  (@r, '白胡椒粉', '2', 'g', TRUE, 10, '/api/ingredients/baihujiaofen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鳙鱼取下两侧鱼肉切片，鱼头鱼骨剁块', 10),
  (@r, 2, '锅热油，下鱼头鱼骨煎至金黄，加开水和姜片，大火熬20分钟至汤色奶白', 22),
  (@r, 3, '干红辣椒剪碎，用热油泼成红汤辣子；豆浆菜（豆膏）调散备用', 4),
  (@r, 4, '鱼片用盐、白胡椒粉略腌，放入白汤中烫熟', 3),
  (@r, 5, '米粉烫熟装碗，浇滚烫鱼汤和鱼片，冲入红汤辣子和豆膏汁，撒葱花', 3);

-- ========== 27. 长沙刮凉粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('长沙刮凉粉', '夏天的长沙街头，凉粉刮出细条，浇上蒜水辣椒油和酸甜汁，冰冰凉凉，酸辣开胃，一块钱的老快乐。', '/api/covers/xiang-gua-liangfen.jpg', 10, 5, 15, 1, 2, '湘菜', '小吃,凉菜,夏日,素食', 1, TRUE, 266, 240, 3, 10, 34, '刮凉粉专用的刮子买不到，用刨丝器或切条都行；所有调料汁先兑好再浇，拌匀马上吃。', '酸辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大米凉粉', '400', 'g', TRUE, 1, '/api/ingredients/daliangfen.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 2, '/api/ingredients/dasuan.jpg'),
  (@r, '辣椒油', '20', 'ml', TRUE, 3, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '陈醋', '15', 'ml', TRUE, 4, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '芝麻香油', '5', 'ml', FALSE, 6, '/api/ingredients/xiangyou.jpg'),
  (@r, '萝卜干', '20', 'g', FALSE, 7, '/api/ingredients/luobogan.jpg'),
  (@r, '小葱', '2', '根', FALSE, 8, '/api/ingredients/xiaocong.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大蒜压泥加凉开水兑成蒜水；萝卜干切细丁，葱切花', 5),
  (@r, 2, '凉粉用刮子刮成细条入碗（或切成筷子粗的条）', 3),
  (@r, 3, '加蒜水、生抽、陈醋、辣椒油、芝麻香油', 2),
  (@r, 4, '撒上萝卜干丁和葱花，拌匀即食', 1);

-- ========== 28. 湘西米豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湘西米豆腐', '凤凰古城名小吃。米浆点灰水做成米豆腐，切丁浇上酸辣红汤，滑嫩弹韧，一口回到沱江边。', '/api/covers/xiang-mi-doufu.jpg', 15, 25, 40, 2, 2, '湘菜', '小吃,地方名吃,素食,酸辣', 1, TRUE, 295, 280, 5, 8, 48, '米豆腐下锅前用凉水冲净表面碱味；红汤要用菜籽油炒辣子才出湘西风味。', '酸辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '米豆腐', '400', 'g', TRUE, 1, '/api/ingredients/midoufu.jpg'),
  (@r, '酸豆角', '30', 'g', TRUE, 2, '/api/ingredients/suandoujiao.jpg'),
  (@r, '干红辣椒', '10', 'g', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '陈醋', '10', 'ml', TRUE, 5, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '小葱', '2', '根', FALSE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '食用油', '20', 'ml', FALSE, 8, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '米豆腐冲净，切成1.5厘米小丁；酸豆角切末、蒜切末、葱切花', 6),
  (@r, 2, '锅热油，下干辣椒段、蒜末爆香，加一大碗水烧开', 3),
  (@r, 3, '下米豆腐丁煮2分钟，加酸豆角末、生抽、陈醋', 3),
  (@r, 4, '连汤装碗，撒葱花趁烫吃', 1);

-- ========== 29. 干锅茶树菇 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('干锅茶树菇', '湘菜馆人气素荤搭配。茶树菇干香有嚼头，配五花肉片和干辣椒在干锅里越煮越香，下酒又下饭。', '/api/covers/xiang-ganguo-chashugu.jpg', 30, 15, 45, 1, 3, '湘菜', '家常,下饭,菌菇,干锅', 1, TRUE, 107, 340, 14, 22, 16, '干茶树菇泡发后一定要挤干水分再煸炒，香味才浓缩；垫洋葱的干锅上桌时点小蜡烛保温。', '香辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '干茶树菇', '100', 'g', TRUE, 1, '/api/ingredients/chashugu.jpg'),
  (@r, '五花肉', '150', 'g', TRUE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '洋葱', '1', '个', FALSE, 3, '/api/ingredients/yangcong.jpg'),
  (@r, '干红辣椒', '10', 'g', TRUE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '青蒜苗', '30', 'g', FALSE, 6, '/api/ingredients/qingsuan.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '食用油', '20', 'ml', FALSE, 8, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '干茶树菇温水泡发30分钟，去根洗净切段，挤干水分', 30),
  (@r, 2, '五花肉切薄片，洋葱切丝垫入干锅底', 5),
  (@r, 3, '锅热少许油，下五花肉片煸出油，加蒜片、干辣椒段爆香', 4),
  (@r, 4, '下茶树菇中火煸炒4分钟至干香，加生抽炒匀', 5),
  (@r, 5, '盛入垫洋葱的干锅，撒蒜苗段，小火加热上桌', 2);

-- ========== 30. 干锅肥肠 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('干锅肥肠', '湘菜馆招牌硬菜。卤肥肠煸得外焦里嫩，加辣椒蒜瓣在干锅里咕嘟，肥而不腻、越嚼越香。', '/api/covers/xiang-ganguo-feichang.jpg', 20, 30, 50, 2, 3, '湘菜', '下饭,下酒,干锅,宴客', 1, TRUE, 132, 560, 20, 46, 10, '肥肠清洗时翻面撕掉内壁多余油脂，用面粉+陈醋反复揉搓去黏液异味，焯煮后再卤，风味才正。', '香辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪肥肠', '500', 'g', TRUE, 1, '/api/ingredients/zhufeichang.jpg'),
  (@r, '干红辣椒', '15', 'g', TRUE, 2, '/api/ingredients/ganlajiao.jpg'),
  (@r, '红辣椒', '1', '根', FALSE, 3, '/api/ingredients/honglajiao.jpg'),
  (@r, '洋葱', '1', '个', FALSE, 4, '/api/ingredients/yangcong.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '八角', '2', '个', TRUE, 9, '/api/ingredients/bajiao.jpg'),
  (@r, '面粉', '30', 'g', TRUE, 10, '/api/ingredients/mianfen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '肥肠用面粉、陈醋里外揉搓洗净，冷水下锅加料酒、姜片、八角煮40分钟至软，捞出切小段', 40),
  (@r, 2, '锅热油，下肥肠段中火煸至表面焦香', 6),
  (@r, 3, '下姜蒜片、干辣椒段爆香，加生抽、少许卤汤焖5分钟', 6),
  (@r, 4, '洋葱丝垫干锅底，倒入肥肠，小火加热上桌', 2);

-- ========== 31. 桃江擂茶 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('桃江擂茶', '益阳桃江待客古俗。茶叶、芝麻、花生、生姜入擂钵擂成糊，滚水一冲，再抓一把炒米，咸香暖胃。', '/api/covers/xiang-taojiang-leicha.jpg', 15, 5, 20, 1, 4, '湘菜', '饮品,待客,养生,地方风味', 1, TRUE, 133, 220, 8, 12, 20, '没有擂钵可用料理机加少量温水打成糊，但擂的风味更足；炒米最后放，保持脆感。', '咸香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '绿茶', '15', 'g', TRUE, 1, '/api/ingredients/lucha.jpg'),
  (@r, '白芝麻', '30', 'g', TRUE, 2, '/api/ingredients/baizhima.jpg'),
  (@r, '花生米', '50', 'g', TRUE, 3, '/api/ingredients/huasheng.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大米', '50', 'g', TRUE, 5, '/api/ingredients/dami.jpg'),
  (@r, '盐', '2', 'g', TRUE, 6, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大米炒成金黄的炒米，盛出备用', 8),
  (@r, 2, '茶叶、白芝麻、花生米（留少许整粒）、生姜放入擂钵，加少许温水和盐擂成细糊', 8),
  (@r, 3, '滚烫开水冲入擂钵，搅散成茶汤', 2),
  (@r, 4, '分碗盛入，每碗撒炒米和留用的花生、芝麻即可', 2);

-- ========== 32. 泥鳅钻豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('泥鳅钻豆腐', '洞庭湖区的传统名菜，泥鳅与嫩豆腐同锅炖煮，汤白如奶、泥鳅鲜嫩、豆腐吸味，老少皆宜的滋补菜。', '/api/covers/xiang-niqiu-zuandoufu.jpg', 240, 30, 270, 2, 3, '湘菜', '汤羹,河鲜,滋补,家常', 1, TRUE, 286, 320, 28, 14, 8, '泥鳅买回清水养2天吐净泥沙；"钻豆腐"本是传说，实际做法是先炖豆腐再下泥鳅，汤一样鲜。', '咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '泥鳅', '300', 'g', TRUE, 1, '/api/ingredients/niqiu.jpg'),
  (@r, '嫩豆腐', '400', 'g', TRUE, 2, '/api/ingredients/doufu.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '3', '根', TRUE, 4, '/api/ingredients/xiaocong.jpg'),
  (@r, '干红辣椒', '5', '个', FALSE, 5, '/api/ingredients/ganlajiao.jpg'),
  (@r, '白胡椒粉', '2', 'g', TRUE, 6, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '食用油', '20', 'ml', FALSE, 7, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 8, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '泥鳅清水静养2天，中途换水吐净泥沙', 240),
  (@r, 2, '嫩豆腐切大块，姜切片、葱切花', 5),
  (@r, 3, '锅中放油，下姜片、干辣椒段爆香，加足量开水', 2),
  (@r, 4, '下豆腐块中火炖10分钟至汤微白，放入泥鳅', 10),
  (@r, 5, '加盖炖12分钟至汤色奶白、泥鳅熟透，加盐和白胡椒粉，撒葱花出锅', 13);

-- ========== 33. 长沙凉面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('长沙凉面', '三伏天的长沙味道。碱水面过凉水抖散，蒜水、香醋、辣椒油、芝麻酱层层浇上，酸辣爽利不糊口。', '/api/covers/xiang-liangmian.jpg', 10, 8, 18, 1, 2, '湘菜', '小吃,主食,夏日,快手菜', 1, TRUE, 308, 520, 12, 18, 76, '面条煮至断生立即过凉开水并拌油抖散，根根分明才够"凉面"的格；芝麻酱先用香油澥开再浇。', '酸辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '碱水面', '300', 'g', TRUE, 1, '/api/ingredients/jianshuimian.jpg'),
  (@r, '黄瓜', '1', '根', FALSE, 2, '/api/ingredients/huanggua.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '辣椒油', '20', 'ml', TRUE, 4, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '陈醋', '15', 'ml', TRUE, 5, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '芝麻酱', '20', 'g', TRUE, 7, '/api/ingredients/zhimajiang.jpg'),
  (@r, '绿豆芽', '100', 'g', FALSE, 8, '/api/ingredients/lvdouya.jpg'),
  (@r, '芝麻香油', '10', 'ml', FALSE, 9, '/api/ingredients/xiangyou.jpg'),
  (@r, '萝卜干', '20', 'g', FALSE, 10, '/api/ingredients/luobogan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大蒜压泥加凉开水兑成蒜水；芝麻酱用香油澥开', 5),
  (@r, 2, '碱水面入沸水煮2分钟至断生，捞出过凉开水，拌香油抖散', 8),
  (@r, 3, '黄瓜切细丝，绿豆芽焯熟过凉，萝卜干切末', 5),
  (@r, 4, '面条装碗，铺黄瓜丝、豆芽，浇蒜水、生抽、陈醋、芝麻酱、辣椒油', 3),
  (@r, 5, '撒萝卜干末，拌匀开吃', 1);
