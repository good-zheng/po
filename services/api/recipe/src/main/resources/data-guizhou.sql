-- 由 seed/recipes-guizhou.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 贵州菜，共 15 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 凯里酸汤鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('凯里酸汤鱼', '黔东南苗家的待客锅。红酸汤用西红柿加糟辣椒发酵，酸得冲却不涩，下鲜鱼和木姜子油，配一碟糊辣椒蘸水，「三天不吃酸，走路打蹿蹿」。', NULL, 25, 30, 55, 2, 4, '贵州菜', '酸汤,河鲜,火锅,苗族味', 1, TRUE, 133, 360, 38, 16, 12, '买不到红酸汤就用西红柿打泥加糟辣椒炒出红油，再兑米汤或高汤熬10分钟；鱼先煎后煮汤不腥、肉不散；木姜子油起锅前才放，久煮香气就跑光了。', '酸辣冲香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '草鱼', '1', '条(约800g)', TRUE, 1, '/api/ingredients/caoyu.jpg'),
  (@r, '西红柿', '400', 'g', TRUE, 2, '/api/ingredients/xihongshi.jpg'),
  (@r, '糟辣椒', '80', 'g', TRUE, 3, '/api/ingredients/duojiao.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', FALSE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '2', '根', FALSE, 6, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '20', 'g', FALSE, 7, '/api/ingredients/xiangcai.jpg'),
  (@r, '小米辣', '20', 'g', FALSE, 8, '/api/ingredients/xiaomila.jpg'),
  (@r, '山胡椒油', '10', 'ml', TRUE, 9, '/api/ingredients/shanhujiaoyou.jpg'),
  (@r, '料酒', '25', 'ml', TRUE, 10, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '8', 'g', TRUE, 11, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '1200', 'ml', TRUE, 13, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '草鱼宰净去黑膜，斩成3厘米大段，用料酒和少许盐抹匀腌15分钟', 17),
  (@r, 2, '西红柿去皮打成泥，糟辣椒剁细，姜蒜切片，葱切段', 10),
  (@r, 3, '锅下油爆香姜片蒜片，倒西红柿泥和糟辣椒，中小火炒出红油', 8),
  (@r, 4, '冲入清水烧开，转中火熬10分钟成酸汤，加盐调酸咸', 12),
  (@r, 5, '下鱼块，中火煮8分钟至鱼肉变白、用筷子能插入鱼皮', 9),
  (@r, 6, '淋山胡椒油，撒葱段香菜和小米辣，连锅上桌配蘸水', 3);

-- ========== 2. 丝娃娃 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('丝娃娃', '贵阳的素春卷。拇指大的薄饼里夹十几种切得极细的丝，黄瓜丝、萝卜丝、折耳根、豆芽，一卷灌一勺酸辣蘸水，一口一个，脆的软的混在一起。', NULL, 40, 15, 55, 2, 4, '贵州菜', '小吃,素食,蘸水,贵阳名小吃', 1, TRUE, 110, 300, 9, 8, 48, '面皮要烫面加少许盐，擀得薄透才软而不破；丝一律切3毫米以内，粗了卷不住；蘸水靠「酸辣甜咸」四味平衡，缺一样都不对味；现卷现吃，泡久了皮就烂。', '酸辣清脆');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '200', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '黄瓜', '150', 'g', TRUE, 2, '/api/ingredients/huanggua.jpg'),
  (@r, '胡萝卜', '150', 'g', FALSE, 3, '/api/ingredients/huluobo.jpg'),
  (@r, '土豆', '150', 'g', FALSE, 4, '/api/ingredients/tudou.jpg'),
  (@r, '绿豆芽', '150', 'g', TRUE, 5, '/api/ingredients/lvdouya.jpg'),
  (@r, '海带丝', '100', 'g', FALSE, 6, '/api/ingredients/zicai.jpg'),
  (@r, '折耳根', '80', 'g', TRUE, 7, '/api/ingredients/bailuobo.jpg'),
  (@r, '莴笋', '100', 'g', FALSE, 8, '/api/ingredients/wosun.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 9, '/api/ingredients/dasuan.jpg'),
  (@r, '小米辣', '15', 'g', TRUE, 10, '/api/ingredients/xiaomila.jpg'),
  (@r, '香醋', '40', 'ml', TRUE, 11, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 12, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '15', 'g', TRUE, 13, '/api/ingredients/baitang.jpg'),
  (@r, '辣椒油', '20', 'ml', FALSE, 14, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 15, '/api/ingredients/yan.jpg'),
  (@r, '清水', '120', 'ml', TRUE, 16, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '面粉加盐和温水揉成软面团，醒20分钟后擀成薄面皮', 25),
  (@r, 2, '上锅蒸10分钟，揭开后用拇指大的模具压出小圆皮', 12),
  (@r, 3, '黄瓜、胡萝卜、土豆、莴笋全部切细丝，土豆丝焯水断生后过凉', 15),
  (@r, 4, '绿豆芽焯水，海带丝泡发煮熟，折耳根去须洗净切小段', 10),
  (@r, 5, '蒜末、小米辣圈加香醋、生抽、白糖、辣椒油和少许凉开水调成酸辣蘸水', 5),
  (@r, 6, '取一张小皮摊平，各样丝夹一小撮卷成口袋状，灌一勺蘸水立刻入口', 6);

-- ========== 3. 肠旺面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('肠旺面', '贵阳的一碗面骨子。碱水面细而脆，配红亮的猪血、软糯的肥肠和脆哨，汤是鸡汤熬的，面上飘一层鸡油，讲究「面脆、血嫩、肠糯」。', NULL, 40, 120, 160, 3, 2, '贵州菜', '面食,早餐,小吃,贵阳名小吃', 1, TRUE, 175, 640, 28, 30, 66, '碱水面别煮过头，水开下锅点两次冷水就捞，面芯要略脆；肥肠用面粉和盐反复搓洗去味，先煮后卤；猪血切块温水养着，最后烫，滚久了起蜂窝。', '咸鲜油润');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '碱水面', '200', 'g', TRUE, 1, '/api/ingredients/jianshuimian.jpg'),
  (@r, '猪肥肠', '300', 'g', TRUE, 2, '/api/ingredients/zhufeichang.jpg'),
  (@r, '猪血', '200', 'g', TRUE, 3, '/api/ingredients/yaxue.jpg'),
  (@r, '脆哨', '40', 'g', FALSE, 4, '/api/ingredients/wuhuarou.jpg'),
  (@r, '土鸡', '半', '只(约500g)', TRUE, 5, '/api/ingredients/tuji.jpg'),
  (@r, '绿豆芽', '80', 'g', FALSE, 6, '/api/ingredients/lvdouya.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '20', 'g', FALSE, 9, '/api/ingredients/dasuan.jpg'),
  (@r, '花椒', '3', 'g', FALSE, 10, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '2', '个', FALSE, 11, '/api/ingredients/bajiao.jpg'),
  (@r, '料酒', '25', 'ml', TRUE, 12, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 13, '/api/ingredients/shengchou.jpg'),
  (@r, '辣椒面', '8', 'g', FALSE, 14, '/api/ingredients/lajiaofen.jpg'),
  (@r, '猪油', '20', 'g', FALSE, 15, '/api/ingredients/zhuyou.jpg'),
  (@r, '盐', '6', 'g', TRUE, 16, '/api/ingredients/yan.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 17, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '肥肠加面粉和盐反复抓洗三遍，翻面刮去油脂，冷水下锅焯10分钟后捞出', 20),
  (@r, 2, '另起锅下水、姜片、葱、花椒、八角和料酒，肥肠卤煮60分钟至筷子能插透，捞出切小段', 65),
  (@r, 3, '土鸡加清水和姜片熬90分钟做汤底，滤出鸡汤保温，鸡油撇出留用', 95),
  (@r, 4, '猪血切麻将块，泡在温水里备用；脆哨、蒜末、葱花备好', 8),
  (@r, 5, '辣椒面用滚鸡油泼香，碗底放生抽、一半辣椒油和猪油', 3),
  (@r, 6, '水大烧开下碱面条，点两次冷水即捞进碗，避免面煮软', 3),
  (@r, 7, '鸡汤烧开，下猪血块烫1分钟连汤舀进面碗，摆肥肠和豆芽，撒脆哨葱花', 4);

-- ========== 4. 贵阳辣子鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('贵阳辣子鸡', '贵州的辣子鸡不放干辣椒炸，用的是糟辣椒和糁粑辣椒，鸡肉先炒后焖，收成油亮深红，辣中带酸香，是「贵州辣子鸡」和重庆版最大的分别。', NULL, 25, 35, 60, 2, 4, '贵州菜', '辣炒,家常菜,下饭,贵州名菜', 1, TRUE, 237, 520, 40, 34, 12, '糟辣椒和糁粑辣椒本身很咸，生抽要少放；鸡肉剁小块带骨才香，先干煸出水分再下辣椒；全程中火慢炼，火大糟辣椒会苦。', '香辣油润');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '土鸡', '1', '只(约1000g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '糟辣椒', '100', 'g', TRUE, 2, '/api/ingredients/duojiao.jpg'),
  (@r, '干辣椒', '30', 'g', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '40', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '大葱', '1', '根', FALSE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '25', 'ml', TRUE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '15', 'ml', FALSE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '花椒', '3', 'g', FALSE, 10, '/api/ingredients/huajiao.jpg'),
  (@r, '食用油', '50', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '清水', '200', 'ml', TRUE, 13, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '干辣椒煮软后剁成糁粑辣椒，姜蒜切末，葱切段', 15),
  (@r, 2, '土鸡剁2厘米小块，洗净沥干，用料酒腌10分钟', 12),
  (@r, 3, '锅下油烧热，倒鸡块中火干煸，炒到皮收紧、锅里水汽散尽', 10),
  (@r, 4, '下糁粑辣椒和糟辣椒，继续翻炒5分钟把辣味炼进油里', 6),
  (@r, 5, '加姜蒜末、花椒和白糖，翻匀后掺清水加盖焖12分钟', 14),
  (@r, 6, '揭盖转大火收汁，汤汁浓红挂肉时加盐和葱段，炒两下出锅', 5);

-- ========== 5. 豆腐圆子 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('豆腐圆子', '贵阳夜市的小吃。豆腐捏碎拌进肉末和葱花，挤成丸子炸到外壳酥脆、里面还是嫩豆腐的绵软，蘸折耳根辣椒水吃。', NULL, 30, 20, 50, 2, 4, '贵州菜', '小吃,油炸,豆腐,夜市', 1, TRUE, 123, 420, 22, 30, 18, '豆腐要用老豆腐，先压干水分再捏碎，太湿不成丸；加一个鸡蛋和两勺淀粉让丸子不散；油温五成热下锅，浮起来转小火慢炸，外壳才硬；蘸水必须有折耳根。', '外酥内嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '豆腐', '400', 'g', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '猪肉末', '80', 'g', FALSE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '鸡蛋', '1', '个', TRUE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '淀粉', '30', 'g', TRUE, 4, '/api/ingredients/dianfen.jpg'),
  (@r, '小葱', '3', '根', TRUE, 5, '/api/ingredients/xiaocong.jpg'),
  (@r, '折耳根', '40', 'g', TRUE, 6, '/api/ingredients/bailuobo.jpg'),
  (@r, '大蒜', '15', 'g', FALSE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '辣椒面', '8', 'g', TRUE, 9, '/api/ingredients/lajiaofen.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '10', 'ml', FALSE, 11, '/api/ingredients/xiangcu.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 12, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '盐', '5', 'g', TRUE, 13, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '400', 'ml', TRUE, 14, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '豆腐压碎后用纱布挤干水，加肉末、鸡蛋、淀粉、葱姜末、白胡椒粉和盐拌匀', 15),
  (@r, 2, '手心抹少许油，把豆腐糊挤成乒乓球大的丸子', 8),
  (@r, 3, '油烧到五成热（筷子周围起小泡），下丸子浸炸3分钟至定型', 4),
  (@r, 4, '丸子浮起后转小火再炸5分钟，外壳金黄硬挺捞出', 6),
  (@r, 5, '升高油温复炸30秒逼油，捞出沥干装盘', 1),
  (@r, 6, '辣椒面、蒜末、生抽、香醋、盐和折耳根碎加凉开水调成蘸水，配丸子吃', 5);

-- ========== 6. 折耳根炒腊肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('折耳根炒腊肉', '云贵两广都认的一道，贵州最狠。折耳根（鱼腥草）切段和腊肉同炒，蒜苗提味，那股子鱼腥味被腊油和辣子一压，就成了上瘾的下饭菜。', NULL, 15, 10, 25, 1, 3, '贵州菜', '小炒,下饭菜,野菜,贵州家常', 1, TRUE, 114, 330, 14, 27, 10, '折耳根选带白嫩须根的，泡10分钟洗净泥沙，别焯水，焯了那股清香就没了；腊肉先蒸20分钟再切片，咸味会柔和很多；全程大火，折耳根下锅炒一分钟就出锅。', '腊香冲辛');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '折耳根', '250', 'g', TRUE, 1, '/api/ingredients/bailuobo.jpg'),
  (@r, '腊肉', '150', 'g', TRUE, 2, '/api/ingredients/larou.jpg'),
  (@r, '蒜苗', '60', 'g', TRUE, 3, '/api/ingredients/qingsuan.jpg'),
  (@r, '干辣椒', '8', 'g', FALSE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '大蒜', '15', 'g', FALSE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '料酒', '15', 'ml', FALSE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '食用油', '15', 'ml', TRUE, 8, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '1', 'g', FALSE, 9, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '腊肉加姜片和料酒上锅蒸20分钟，取出切薄片', 22),
  (@r, 2, '折耳根掐去老须，泡10分钟后洗净沥干，切5厘米段', 12),
  (@r, 3, '蒜苗切段，白茎和叶分开，干辣椒切节，蒜拍扁', 5),
  (@r, 4, '锅下少许油，腊肉片煸出透明油', 3),
  (@r, 5, '下干辣椒、蒜和蒜苗白茎炒香', 1),
  (@r, 6, '倒折耳根大火快炒1分钟，加蒜苗叶和一点点盐翻两下立刻出锅', 2);

-- ========== 7. 花溪牛肉粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('花溪牛肉粉', '贵阳人的一早。牛骨和牛肉熬出棕红原汤，粗米粉在漏勺里烫热，铺牛肉片、泡椒和香菜，最后浇一勺油辣椒，汤厚粉弹。', NULL, 30, 150, 180, 2, 4, '贵州菜', '米粉,早餐,汤粉,贵阳名小吃', 1, TRUE, 257, 520, 30, 16, 64, '牛骨先冷水泡1小时去血，汤才清亮；牛肉分两块用，一块熬汤撕丝，一块煮到七分熟冷藏切片；米粉烫要快，泡久了不弹；油辣椒现泼，别用陈的。', '醇厚香辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '米粉', '400', 'g', TRUE, 1, '/api/ingredients/ganmifen.jpg'),
  (@r, '黄牛后腿肉', '400', 'g', TRUE, 2, '/api/ingredients/niurou.jpg'),
  (@r, '牛骨', '500', 'g', TRUE, 3, '/api/ingredients/niurou.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '大蒜', '20', 'g', FALSE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '泡红椒', '30', 'g', FALSE, 7, '/api/ingredients/paohongjiao.jpg'),
  (@r, '香菜', '20', 'g', TRUE, 8, '/api/ingredients/xiangcai.jpg'),
  (@r, '花椒', '3', 'g', FALSE, 9, '/api/ingredients/huajiao.jpg'),
  (@r, '干辣椒', '15', 'g', FALSE, 10, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 11, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '8', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', FALSE, 13, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '2500', 'ml', TRUE, 14, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛骨冷水泡1小时，牛肉单独浸水20分钟去血水', 80),
  (@r, 2, '汤锅下水、牛骨、姜片、葱和花椒，烧开撇沫后小火熬2小时成原汤', 125),
  (@r, 3, '另起一锅水，牛肉煮20分钟后加盖焖30分钟，捞出晾凉切薄片', 55),
  (@r, 4, '辣椒面加少许盐，用滚油泼成油辣椒；泡红椒切段，蒜切末，香菜切段', 8),
  (@r, 5, '米粉温水泡软，下沸水用漏勺烫30秒至透，入碗', 3),
  (@r, 6, '汤重新烧开，加生抽和盐调味，浇进粉碗，铺牛肉片、泡椒和香菜，最后舀一勺油辣椒', 5);

-- ========== 8. 遵义羊肉粉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('遵义羊肉粉', '黔北的招牌粉。带骨羊肉和羊骨熬出奶汤，米粉装碗浇汤，撒现切的羊肉、糊辣椒面和花椒粉，配一大把生蒜苗和薄荷，膻香带麻。', NULL, 40, 180, 220, 3, 4, '贵州菜', '米粉,汤粉,早餐,遵义名小吃', 1, TRUE, 237, 560, 34, 24, 58, '羊肉冷水泡2小时再焯，汤不腥不浑；熬汤时不加盖，汤色才白；糊辣椒要现舂，焦香是这道粉的骨架；薄荷和蒜苗别省，是遵义羊肉粉的脸。', '鲜膻麻辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '米粉', '400', 'g', TRUE, 1, '/api/ingredients/ganmifen.jpg'),
  (@r, '羊肉', '600', 'g', TRUE, 2, '/api/ingredients/yangrou.jpg'),
  (@r, '羊骨', '500', 'g', TRUE, 3, '/api/ingredients/yangrou.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 5, '/api/ingredients/dacong.jpg'),
  (@r, '蒜苗', '40', 'g', TRUE, 6, '/api/ingredients/qingsuan.jpg'),
  (@r, '香菜', '20', 'g', FALSE, 7, '/api/ingredients/xiangcai.jpg'),
  (@r, '薄荷', '10', 'g', FALSE, 8, '/api/ingredients/xiangcai.jpg'),
  (@r, '花椒粉', '4', 'g', TRUE, 9, '/api/ingredients/huajiaofen.jpg'),
  (@r, '辣椒面', '15', 'g', TRUE, 10, '/api/ingredients/lajiaofen.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 11, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '10', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '清水', '3000', 'ml', TRUE, 13, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '羊肉切大块冷水泡2小时，中途换两次水；羊骨冲净', 125),
  (@r, 2, '羊肉和羊骨冷水下锅，加一半姜片料酒烧开，撇净浮沫后煮10分钟捞出冲净', 20),
  (@r, 3, '汤锅重新注清水，下羊肉羊骨和剩下的姜葱，大火烧开后不加盖熬2.5小时', 155),
  (@r, 4, '捞出羊肉晾凉切薄片；汤滤净，加盐和花椒粉调口', 15),
  (@r, 5, '辣椒面干锅小火焙到焦香，舂成糊辣椒', 5),
  (@r, 6, '米粉烫热入碗，铺羊肉片，浇滚羊汤，撒糊辣椒、花椒粉、蒜苗香菜和薄荷', 5);

-- ========== 9. 威宁洋芋粑粑 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('威宁洋芋粑粑', '乌蒙山区的土豆饼。洋芋蒸熟压成泥，拌葱盐和面粉，团成饼按扁，平底锅慢煎到两面结壳、里面绵软，蘸辣椒面或折耳根水吃。', NULL, 35, 15, 50, 1, 4, '贵州菜', '小吃,土豆,煎炸,贵州山区', 1, TRUE, 270, 380, 9, 14, 56, '选沙洋芋（黄心起沙的那种），压泥时留一点小颗粒口感更好；粉只加两勺，多了发硬；小火慢煎，急着翻面会散；辣椒面用热油一泼更香。', '外香内绵');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '洋芋', '600', 'g', TRUE, 1, '/api/ingredients/tudou.jpg'),
  (@r, '面粉', '40', 'g', TRUE, 2, '/api/ingredients/mianfen.jpg'),
  (@r, '小葱', '3', '根', TRUE, 3, '/api/ingredients/xiaocong.jpg'),
  (@r, '鸡蛋', '1', '个', FALSE, 4, '/api/ingredients/jidan.jpg'),
  (@r, '辣椒面', '8', 'g', TRUE, 5, '/api/ingredients/lajiaofen.jpg'),
  (@r, '折耳根', '30', 'g', FALSE, 6, '/api/ingredients/bailuobo.jpg'),
  (@r, '生抽', '15', 'ml', FALSE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '五香粉', '2', 'g', FALSE, 8, '/api/ingredients/bajiao.jpg'),
  (@r, '盐', '4', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '洋芋去皮切块，上锅蒸25分钟至筷子一插就透', 27),
  (@r, 2, '趁热压成泥，留些小颗粒，晾到不烫手', 8),
  (@r, 3, '加面粉、蛋液、葱花、五香粉和盐揉成不粘手的软团', 6),
  (@r, 4, '分成八个剂子，团圆再按成1厘米厚的饼', 6),
  (@r, 5, '平底锅放油烧温，下饼小火煎到两面金黄结壳，约每面4分钟', 9),
  (@r, 6, '辣椒面用热油泼香，配生抽折耳根水蘸着吃', 3);

-- ========== 10. 红油米豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('红油米豆腐', '贵州夏天的凉吃小食。米豆腐切方块，沸水一烫捞起，浇辣椒油、蒜水和酱油，撒上折耳根、花生和香菜，滑嫩得筷子夹不住。', NULL, 15, 5, 20, 1, 3, '贵州菜', '凉食,小吃,素食,夏季', 1, TRUE, 158, 260, 7, 14, 26, '米豆腐本身无味，全靠调料，蒜水一定要用凉开水捣出来才不冲；烫的时间别超过半分钟，久了表面起蜂窝；油炸花生末最后撒，早撒就软了。', '香辣滑嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '米豆腐', '400', 'g', TRUE, 1, '/api/ingredients/midoufu.jpg'),
  (@r, '辣椒油', '30', 'ml', TRUE, 2, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '折耳根', '40', 'g', TRUE, 3, '/api/ingredients/bailuobo.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '2', '根', TRUE, 5, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '15', 'g', FALSE, 6, '/api/ingredients/xiangcai.jpg'),
  (@r, '油炸花生米', '30', 'g', FALSE, 7, '/api/ingredients/huasheng.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '10', 'ml', FALSE, 9, '/api/ingredients/xiangcu.jpg'),
  (@r, '白糖', '3', 'g', FALSE, 10, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '3', 'g', TRUE, 11, '/api/ingredients/yan.jpg'),
  (@r, '清水', '50', 'ml', TRUE, 12, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '米豆腐切成2厘米方块', 5),
  (@r, 2, '蒜加盐和凉开水捣成蒜水', 4),
  (@r, 3, '折耳根切小段，葱和香菜切末，花生碾碎', 6),
  (@r, 4, '锅烧宽水，下米豆腐烫30秒至浮起，捞出入碗', 1),
  (@r, 5, '生抽、香醋、白糖、蒜水和辣椒油调成红油汁', 2),
  (@r, 6, '汁浇在米豆腐上，撒折耳根、花生末、葱花和香菜，拌着吃', 2);

-- ========== 11. 贵阳糯米饭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('贵阳糯米饭', '贵阳人的硬核早餐。蒸透的糯米拌上猪油，铺脆哨、酸萝卜、花生和葱花，用薄饼一卷，油润黏香、酸甜解腻，两块钱一卷的量。', NULL, 240, 40, 280, 1, 4, '贵州菜', '主食,早餐,糯米,贵阳小吃', 1, TRUE, 140, 500, 12, 18, 72, '糯米泡够4小时，蒸才透亮；趁热拌猪油和盐，米粒才挂得上味；酸萝卜是解腻的关键，别换成甜萝卜；卷的薄饼可用春卷皮或饺子皮代替。', '油润酸甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '糯米', '400', 'g', TRUE, 1, '/api/ingredients/nuomi.jpg'),
  (@r, '脆哨', '40', 'g', TRUE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '酸萝卜', '80', 'g', TRUE, 3, '/api/ingredients/suanluobo.jpg'),
  (@r, '花生米', '30', 'g', FALSE, 4, '/api/ingredients/huasheng.jpg'),
  (@r, '猪油', '25', 'g', TRUE, 5, '/api/ingredients/zhuyou.jpg'),
  (@r, '小葱', '3', '根', TRUE, 6, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '15', 'g', FALSE, 7, '/api/ingredients/xiangcai.jpg'),
  (@r, '辣椒油', '15', 'ml', FALSE, 8, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '面粉', '100', 'g', FALSE, 9, '/api/ingredients/mianfen.jpg'),
  (@r, '盐', '4', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '清水', '60', 'ml', FALSE, 11, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '糯米淘净，加清水泡4小时以上，沥干铺笼布', 245),
  (@r, 2, '旺火蒸35分钟至米粒透亮，中途洒两次水防干', 37),
  (@r, 3, '趁热拌进猪油和盐，翻匀保温', 3),
  (@r, 4, '面粉加水和少许盐揉软，擀薄后烙成巴掌大的薄饼', 12),
  (@r, 5, '酸萝卜切细丝，葱切花，花生碾成粗末', 6),
  (@r, 6, '薄饼抹少许猪油，铺一层糯米，撒脆哨、酸萝卜、花生、葱花和香菜，喜欢辣就点辣椒油，卷紧成筒', 6);

-- ========== 12. 恋爱豆腐果 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('恋爱豆腐果', '贵阳名号的烤豆腐。豆腐块中间划一刀塞进碱水，炭火烤到肚皮鼓起、壳焦内嫩，夹进折耳根、辣椒和蒜的蘸水，趁烫吃。', NULL, 20, 25, 45, 2, 4, '贵州菜', '小吃,豆腐,烧烤,夜市', 1, TRUE, 146, 320, 20, 20, 12, '豆腐要选有韧性的薄浆豆腐（用胆水豆腐），划刀别切断；烤到鼓成小枕头才成，火太猛外糊里凉；蘸水里的折耳根和蒜是主角，不能只放辣椒；没炭炉用烤箱220℃烤20分钟。', '焦香嫩烫');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '豆腐', '400', 'g', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '折耳根', '50', 'g', TRUE, 2, '/api/ingredients/bailuobo.jpg'),
  (@r, '辣椒面', '12', 'g', TRUE, 3, '/api/ingredients/lajiaofen.jpg'),
  (@r, '大蒜', '25', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '2', '根', TRUE, 5, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '15', 'g', FALSE, 6, '/api/ingredients/xiangcai.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '10', 'ml', FALSE, 8, '/api/ingredients/xiangcu.jpg'),
  (@r, '食用油', '20', 'ml', FALSE, 9, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 10, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '豆腐切4厘米长方块，每块中间横划一刀，深到三分之二不断开', 10),
  (@r, 2, '淡盐水里浸5分钟捞出沥干', 6),
  (@r, 3, '炭火或烤箱中层摆开，烤到两面结硬壳', 12),
  (@r, 4, '翻面继续烤至豆腐从刀口鼓胀成小枕头，约10分钟', 11),
  (@r, 5, '蒜末、折耳根碎、葱花、香菜与辣椒面、生抽、香醋、盐和少许热油拌成蘸水', 5),
  (@r, 6, '把蘸水灌进烤鼓的豆腐刀口里，趁烫吃', 2);

-- ========== 13. 青岩卤猪脚 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('青岩卤猪脚', '贵阳青岩古镇的卤味。猪蹄配红糖、八角、花椒和一锅老卤，小火卤到皮筋糯软、能整块脱骨，蘸五香辣椒面吃，是黔中「卤猪脚」的代表。', NULL, 25, 150, 175, 2, 4, '贵州菜', '卤味,猪肉,小吃,古镇名菜', 1, TRUE, 266, 480, 26, 36, 14, '猪蹄让摊主从爪尖剁开，回家再泡1小时去血；糖色要炒到琥珀色冲热水，别炒焦；卤到筷子能插透皮就够，泡在卤汤里过夜更入味；蘸水用干辣椒面加花椒粉和盐。', '酱甜糯香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪蹄', '2', '只(约1000g)', TRUE, 1, '/api/ingredients/zhuqianzhou.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '1', '根', TRUE, 3, '/api/ingredients/dacong.jpg'),
  (@r, '冰糖', '40', 'g', TRUE, 4, '/api/ingredients/bingtang.jpg'),
  (@r, '八角', '3', '个', TRUE, 5, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '5', 'g', FALSE, 6, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '3', '片', FALSE, 7, '/api/ingredients/xiangye.jpg'),
  (@r, '花椒', '5', 'g', TRUE, 8, '/api/ingredients/huajiao.jpg'),
  (@r, '干辣椒', '10', 'g', FALSE, 9, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生抽', '60', 'ml', TRUE, 10, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '20', 'ml', TRUE, 11, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 12, '/api/ingredients/liaojiu.jpg'),
  (@r, '辣椒面', '10', 'g', TRUE, 13, '/api/ingredients/lajiaofen.jpg'),
  (@r, '花椒粉', '2', 'g', FALSE, 14, '/api/ingredients/huajiaofen.jpg'),
  (@r, '盐', '5', 'g', TRUE, 15, '/api/ingredients/yan.jpg'),
  (@r, '清水', '2000', 'ml', TRUE, 16, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪蹄剁开冷水泡1小时，焯水去净浮沫后冲净', 70),
  (@r, 2, '锅下少许油，冰糖小火炒到琥珀色冒小泡，冲入热水做糖色', 6),
  (@r, 3, '汤锅下猪蹄、糖色、生抽、老抽、料酒和清水，加姜片葱结', 5),
  (@r, 4, '八角、桂皮、香叶、花椒和干辣椒装进纱料包一起下锅', 4),
  (@r, 5, '大火烧开转小火卤2小时，途中翻两次面，筷子能插透猪皮即可', 125),
  (@r, 6, '加盐调咸，关火让猪蹄在卤汤里泡30分钟以上', 35),
  (@r, 7, '捞出斩块，蘸辣椒面加花椒粉和盐调的五香蘸水吃', 6);

-- ========== 14. 贵州豆米火锅 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('贵州豆米火锅', '贵州冬天的锅子。干豌豆（豆米）煮到起沙，兑进骨头汤，下腊肉、猪蹄和豆皮，汤越煮越浓，最后涮蔬菜，一碗豆米汤下肚浑身发热。', NULL, 240, 90, 330, 2, 6, '贵州菜', '火锅,豆类,冬季,聚宴', 1, TRUE, 250, 350, 22, 18, 28, '豆米提前泡3小时以上，用手能捻碎才煮得起沙；一半豆子打成泥回锅，汤才浓白；腊肉先煸出油再下锅；这锅底味重，蘸水可以省。', '沙糯咸香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '豆米', '300', 'g', TRUE, 1, '/api/ingredients/huangdou.jpg'),
  (@r, '腊肉', '150', 'g', TRUE, 2, '/api/ingredients/larou.jpg'),
  (@r, '猪蹄', '500', 'g', FALSE, 3, '/api/ingredients/zhuqianzhou.jpg'),
  (@r, '猪骨', '500', 'g', TRUE, 4, '/api/ingredients/zhutonggu.jpg'),
  (@r, '豆皮', '80', 'g', FALSE, 5, '/api/ingredients/doufu.jpg'),
  (@r, '豌豆尖', '150', 'g', FALSE, 6, '/api/ingredients/wandoujian.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '干辣椒', '10', 'g', FALSE, 9, '/api/ingredients/ganlajiao.jpg'),
  (@r, '料酒', '25', 'ml', FALSE, 10, '/api/ingredients/liaojiu.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '8', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '清水', '2000', 'ml', TRUE, 13, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '豆米洗净泡3小时以上；猪蹄剁块、猪骨焯水', 190),
  (@r, 2, '锅里下水和豆米，加姜片煮40分钟至豆软开花', 45),
  (@r, 3, '捞出一半豆子压成泥，倒回锅里搅匀做沙底', 8),
  (@r, 4, '另起锅下油，腊肉切片煸出油，蒜瓣和干辣椒炒香', 5),
  (@r, 5, '汤锅下猪骨和猪蹄块，掺清水，加料酒，中火煮30分钟', 32),
  (@r, 6, '下炒好的腊肉蒜和豆皮，加盐调味，再煮10分钟', 11),
  (@r, 7, '连锅上桌，边煮边涮豌豆尖，蘸水随意', 8);

-- ========== 15. 兴义刷把头 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('兴义刷把头', '黔西南的糯米点心。糯米泡透蒸熟，和猪肉末、香菇、胡萝卜等炒成咸馅，用薄皮捏成小石榴状，蒸熟后倒扣在盘里，形似旧时的刷把，蘸酸辣汁吃。', NULL, 260, 45, 305, 3, 4, '贵州菜', '点心,糯米,蒸食,黔西南名小吃', 1, TRUE, 279, 400, 12, 12, 62, '糯米全用泡透的整粒米蒸，别打粉，蒸出来才有颗粒感；馅要炒得干一点，湿了就捏不拢；皮用面粉掺淀粉擀薄；收口朝下摆进笼屉，蒸时才不散。', '软糯咸香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '糯米', '200', 'g', TRUE, 1, '/api/ingredients/nuomi.jpg'),
  (@r, '猪肉末', '150', 'g', TRUE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '干香菇', '30', 'g', TRUE, 3, '/api/ingredients/ganxianggu.jpg'),
  (@r, '胡萝卜', '80', 'g', FALSE, 4, '/api/ingredients/huluobo.jpg'),
  (@r, '中筋面粉', '150', 'g', TRUE, 5, '/api/ingredients/mianfen.jpg'),
  (@r, '淀粉', '30', 'g', FALSE, 6, '/api/ingredients/dianfen.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', TRUE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '20', 'ml', FALSE, 10, '/api/ingredients/xiangcu.jpg'),
  (@r, '辣椒油', '15', 'ml', FALSE, 11, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '白糖', '3', 'g', FALSE, 12, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '5', 'g', TRUE, 13, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 14, '/api/ingredients/shiyongyou.jpg'),
  (@r, '清水', '90', 'ml', TRUE, 15, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '糯米泡4小时后沥干，上笼蒸30分钟至熟透', 255),
  (@r, 2, '干香菇泡发切小丁，胡萝卜切丁，姜葱切末', 10),
  (@r, 3, '锅下油炒香姜葱，下肉末炒散，再加香菇丁、胡萝卜丁和一半蒸好的糯米，生抽和盐炒成馅', 8),
  (@r, 4, '面粉加淀粉和温水揉成软面团，醒15分钟后擀薄，切成6厘米圆皮', 22),
  (@r, 5, '每皮放一勺馅，向上收口捏成小石榴状，口朝下摆进笼屉', 15),
  (@r, 6, '旺火蒸12分钟，倒扣装盘', 13),
  (@r, 7, '香醋、生抽、辣椒油、白糖和少许蒜水调成酸辣汁，蘸着吃', 4);
