-- 由 seed/recipes-su.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 苏菜，共 17 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 松鼠鳜鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('松鼠鳜鱼', '苏州帮菜的头牌功夫菜。鳜鱼贴骨片开、剞上菱形花刀，拍粉炸得蓬松竖立如松鼠翘尾，趁热浇滚热的番茄糖醋汁，吱作响，外脆里嫩。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/su-songshu-guibi.jpg', 25, 20, 45, 3, 4, '苏菜', '经典,宴客,河鲜,苏菜名菜', 1, TRUE, 128, 380, 24, 24, 20, '花刀要剞到鱼皮而不切断，拍干粉后抖散才炸出松针；汁熬到滚热浓稠再浇，才有那一声吱吱。', '酸甜酥脆');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '桂鱼', '1', '条(约700g)', TRUE, 1, '/api/ingredients/guiyu.jpg'),
  (@r, '淀粉', '60', 'g', TRUE, 2, '/api/ingredients/dianfen.jpg'),
  (@r, '番茄酱', '80', 'g', TRUE, 3, '/api/ingredients/honglajiao.jpg'),
  (@r, '白糖', '45', 'g', TRUE, 4, '/api/ingredients/baitang.jpg'),
  (@r, '香醋', '15', 'ml', TRUE, 5, '/api/ingredients/xiangcu.jpg'),
  (@r, '绍兴黄酒', '15', 'ml', TRUE, 6, '/api/ingredients/huangjiu.jpg'),
  (@r, '鸡蛋', '1', '个', TRUE, 7, '/api/ingredients/jidan.jpg'),
  (@r, '松子仁', '15', 'g', FALSE, 8, '/api/ingredients/hetaosui.jpg'),
  (@r, '盐', '3', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '700', 'ml', FALSE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '桂鱼去鳞治净，从鳃部贴脊骨片下两片连尾鱼肉，剁去脊骨与胸刺', 10),
  (@r, 2, '肉面朝下斜刀剞0.5厘米菱形花刀，深至鱼皮不断，两面抹黄酒和盐', 8),
  (@r, 3, '鱼身里外拍干淀粉，抖去余粉，使刀缝处也沾上粉', 5),
  (@r, 4, '油烧至七成热，提着鱼尾先炸腹部定型，再整鱼下锅炸至硬挺金黄', 6),
  (@r, 5, '油升至八成热复炸1分钟至外壳酥脆，捞出摆成昂首翘尾状', 3),
  (@r, 6, '锅留底油炒香番茄酱，加白糖、香醋和50ml水煮稠，淋明油熬亮', 4),
  (@r, 7, '滚汁对准鱼身浇下，撒松子仁，听其吱声即刻上桌', 2);

-- ========== 2. 清炖蟹粉狮子头 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('清炖蟹粉狮子头', '扬州由隋代“葵花斩肉”传下的炖焖绝活。肥肉三成瘦肉七，粗斩细剁成拳头大的丸子，嵌进蟹粉入鸡清汤微火炖足两小时，汤清而肉化。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/su-qingdun-shizitou.jpg', 40, 200, 240, 3, 4, '苏菜', '经典,宴客,汤羹,苏菜名菜', 1, TRUE, 246, 500, 25, 42, 6, '肉要切成石榴米丁再粗剁，粒粒有筋才酥而不散；丸子只微火“炖”不许滚，火大一沸就散汤就浑。', '清鲜酥烂');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪前腿肉馅', '400', 'g', TRUE, 1, '/api/ingredients/zhuroumo.jpg'),
  (@r, '五花肉', '200', 'g', TRUE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '青蟹', '2', '只(约600g)', TRUE, 3, '/api/ingredients/qingxie.jpg'),
  (@r, '鸡蛋清', '2', '个', TRUE, 4, '/api/ingredients/jidanqing.jpg'),
  (@r, '淀粉', '20', 'g', TRUE, 5, '/api/ingredients/dianfen.jpg'),
  (@r, '鸡清汤', '1200', 'ml', TRUE, 6, '/api/ingredients/gaotang.jpg'),
  (@r, '小白菜心', '250', 'g', TRUE, 7, '/api/ingredients/baicai.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '绍兴黄酒', '15', 'ml', TRUE, 9, '/api/ingredients/huangjiu.jpg'),
  (@r, '盐', '5', 'g', TRUE, 10, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '腿肉与五花肉切成0.8厘米丁再粗剁成馅，加盐搅至发黏起筋', 15),
  (@r, 2, '蛋清加干淀粉调成浆，与葱姜水一起分三次拌入肉馅，顺一个方向打上劲', 15),
  (@r, 3, '青蟹上蒸锅大火蒸12分钟，拆出蟹肉与蟹黄蟹粉', 20),
  (@r, 4, '肉馅分四份在两掌间摔打成光面大丸子，每只中心按入一勺蟹粉', 10),
  (@r, 5, '砂锅下鸡清汤烧沸，丸子垫菜叶轻放入汤，微火加盖炖2小时', 125),
  (@r, 6, '下小白菜心续炖10分钟至酥，调盐，连锅上桌撒剩下蟹粉', 12);

-- ========== 3. 南京盐水鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('南京盐水鸭', '南京人从六朝腌到今天的桂花鸭。花椒盐炒热擦身、老卤浸透，白水煮到骨边带一线猩红，皮白肉嫩骨绿，咸鲜里泛出秋桂的清香。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/su-nanjing-yan-shuiya.jpg', 45, 60, 105, 2, 6, '苏菜', '经典,卤味,时令,苏菜名菜', 1, TRUE, 221, 320, 30, 20, 0, '煮鸭不能大火翻滚，微火虾眼水泡到骨边带红才嫩；捞起后回原汤晾凉，皮才不皱肉不发干。', '咸鲜细嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '嫩鸭', '半', '只(约1000g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '盐', '40', 'g', TRUE, 2, '/api/ingredients/yan.jpg'),
  (@r, '花椒', '5', 'g', TRUE, 3, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '3', 'g', TRUE, 4, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '3', 'g', TRUE, 5, '/api/ingredients/guipi.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '30', 'g', TRUE, 7, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '30', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '清水', '2000', 'ml', TRUE, 9, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '干锅下盐、花椒、八角、桂皮，小火炒至微黄出香气', 5),
  (@r, 2, '热盐加料酒擦遍鸭身内外，入缸压腌4小时以上', 250),
  (@r, 3, '腌好的鸭入清水泡30分钟洗去浮盐，两翅别进腹腔', 35),
  (@r, 4, '鸭入锅加姜葱和足量清水，大火烧沸撇净浮沫转微火焖煮40分钟', 45),
  (@r, 5, '筷子插腿厚处无血水即熟，连汤浸凉，捞出切条装盘淋原汤', 20);

-- ========== 4. 无锡酱排骨 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('无锡酱排骨', '无锡三凤酱肉坊传了百年的浓油赤酱。肋排焯水后与酱油、冰糖、黄酒同煨，收膏到酱红发亮，骨肉酥到能一口脱开，甜香压住咸鲜。', NULL, 20, 110, 130, 2, 4, '苏菜', '经典,下饭,卤味,苏菜名菜', 1, TRUE, 171, 460, 24, 34, 18, '冰糖要炒到枣红色再下排骨，上色才亮；焖足一个半小时后大火收膏，酱汁挂得住骨头才算无锡味。', '浓油赤酱');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪肋排', '800', 'g', TRUE, 1, '/api/ingredients/zhupaigu.jpg'),
  (@r, '冰糖', '50', 'g', TRUE, 2, '/api/ingredients/bingtang.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 3, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '25', 'ml', TRUE, 4, '/api/ingredients/laochou.jpg'),
  (@r, '绍兴黄酒', '50', 'ml', TRUE, 5, '/api/ingredients/huangjiu.jpg'),
  (@r, '桂皮', '3', 'g', TRUE, 6, '/api/ingredients/guipi.jpg'),
  (@r, '八角', '3', 'g', TRUE, 7, '/api/ingredients/bajiao.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '25', 'g', TRUE, 9, '/api/ingredients/dacong.jpg'),
  (@r, '香醋', '5', 'ml', FALSE, 10, '/api/ingredients/xiangcu.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '肋排斩成6厘米长段，冷水下锅加黄酒焯透，捞出冲净血沫', 15),
  (@r, 2, '锅下油放冰糖，小火炒至枣红冒小泡', 5),
  (@r, 3, '下排骨翻裹糖色，加黄酒、生抽、老抽、桂皮八角和姜葱炒匀', 6),
  (@r, 4, '加清水没过排骨，大火烧开转小火加盖焖80分钟', 85),
  (@r, 5, '捡去香料，大火收汁至酱膏裹肉发亮，淋香醋翻匀出锅', 10);

-- ========== 5. 大煮干丝 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('大煮干丝', '扬州早茶的头一道功夫。一方豆腐干先批成薄可透光的二十片，再切成火柴棍细丝，入鸡清汤与火腿笋丝同煮，干丝绵软汤头鲜醇。', NULL, 30, 25, 55, 3, 4, '苏菜', '经典,宴客,汤羹,苏菜名菜', 1, TRUE, 295, 300, 25, 12, 20, '方干要片到二十片不断才敢切丝；干丝先沸水烫两遍去豆腥，煮靠鸡汤吊味，火大了丝就碎。', '鲜醇绵软');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '香干', '6', '块(约450g)', TRUE, 1, '/api/ingredients/xianggan.jpg'),
  (@r, '鸡清汤', '900', 'ml', TRUE, 2, '/api/ingredients/gaotang.jpg'),
  (@r, '火腿', '40', 'g', TRUE, 3, '/api/ingredients/huotui.jpg'),
  (@r, '鸡胸肉', '80', 'g', TRUE, 4, '/api/ingredients/jitui.jpg'),
  (@r, '河虾仁', '60', 'g', TRUE, 5, '/api/ingredients/hexiaren.jpg'),
  (@r, '冬笋', '60', 'g', TRUE, 6, '/api/ingredients/dongsun.jpg'),
  (@r, '豌豆尖', '80', 'g', TRUE, 7, '/api/ingredients/wandoujian.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '15', 'g', TRUE, 9, '/api/ingredients/dacong.jpg'),
  (@r, '盐', '3', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 11, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '每块方干先批片成20片薄皮，叠起切成0.2厘米火柴丝', 18),
  (@r, 2, '干丝入沸水烫2分钟捞起，换沸水再烫一遍去豆腥', 8),
  (@r, 3, '火腿、鸡脯肉、冬笋全切成同样粗细的丝，姜葱切片', 8),
  (@r, 4, '鸡清汤烧沸，下干丝与火腿笋丝鸡丝，加姜葱中火煮10分钟', 12),
  (@r, 5, '捞起干丝配料堆入大碗，汤回锅下虾仁豌豆尖烫熟，浇汤淋香油', 6);

-- ========== 6. 软兜长鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('软兜长鱼', '淮安鳝鱼席上的头名，又叫开洋软兜。黄鳝烫到血刚凝便划出脊背肉，只用猪油旺火十几秒爆匀，蒜香胡椒冲鼻，筷子夹起两头下垂如兜。', NULL, 25, 10, 35, 3, 3, '苏菜', '经典,宴客,河鲜,苏菜名菜', 1, TRUE, 173, 240, 24, 13, 4, '鳝段要冷水下锅烫到血刚凝就捞，老了骨划不下；猪油七成热下锅，全程大火十几秒出锅才兜得住。', '鲜嫩蒜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鳝鱼片', '500', 'g', TRUE, 1, '/api/ingredients/shanyupian.jpg'),
  (@r, '猪油', '40', 'g', TRUE, 2, '/api/ingredients/zhuyou.jpg'),
  (@r, '大蒜', '25', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '白胡椒粉', '2', 'g', TRUE, 5, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '香醋', '10', 'ml', TRUE, 6, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '绍兴黄酒', '15', 'ml', TRUE, 8, '/api/ingredients/huangjiu.jpg'),
  (@r, '水淀粉', '40', 'ml', TRUE, 9, '/api/ingredients/dianfen.jpg'),
  (@r, '小葱', '20', 'g', TRUE, 10, '/api/ingredients/xiaocong.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 11, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鳝鱼片冷水下锅，加姜葱和黄酒，烧沸后煮3分钟至肉紧', 10),
  (@r, 2, '捞出划去脊骨与腹刺只留背肉，切6厘米段，蒜姜切末丝、葱切段', 12),
  (@r, 3, '猪油烧至七成热，下鳝段快速划散', 2),
  (@r, 4, '下蒜末姜丝爆香，烹黄酒、生抽、香醋，撒白胡椒粉', 2),
  (@r, 5, '水淀粉勾薄芡翻匀，淋香油装盘，鳝段软垂两头下垂即成', 3);

-- ========== 7. 响油鳝糊 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('响油鳝糊', '本帮年菜的看家鳝菜。鳝丝配酱油冰糖焖到酥软，堆成小山，当中窝心埋葱姜蒜末与胡椒粉，一勺冒烟的滚油浇下哔剥作响，故名响油。', NULL, 20, 15, 35, 2, 3, '苏菜', '经典,宴客,河鲜,苏菜名菜', 1, TRUE, 242, 270, 26, 15, 6, '蒜末姜丝胡椒粉要埋进鳝糊窝心，油烧到冒烟一次浇透；浇完趁热拌散，放凉了鳝糊要返腥。', '酱香软嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鳝鱼片', '450', 'g', TRUE, 1, '/api/ingredients/shanyupian.jpg'),
  (@r, '猪油', '35', 'g', TRUE, 2, '/api/ingredients/zhuyou.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 3, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 4, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '15', 'g', TRUE, 5, '/api/ingredients/baitang.jpg'),
  (@r, '绍兴黄酒', '20', 'ml', TRUE, 6, '/api/ingredients/huangjiu.jpg'),
  (@r, '大蒜', '25', 'g', TRUE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '白胡椒粉', '2', 'g', TRUE, 9, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '熟芝麻', '5', 'g', FALSE, 10, '/api/ingredients/baizhima.jpg'),
  (@r, '清水', '60', 'ml', TRUE, 11, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '25', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鳝鱼片入沸水煮3分钟，捞出切成5厘米长的鳝丝', 10),
  (@r, 2, '锅下猪油，姜片葱末炝锅，下鳝丝大火炒2分钟', 3),
  (@r, 3, '加黄酒、生抽、老抽、白糖和清水，中火加盖焖烧6分钟', 7),
  (@r, 4, '开盖大火收汁至浓，装盘堆成小山，当中按出一个窝', 4),
  (@r, 5, '窝中放蒜末、姜丝、白胡椒粉、芝麻，余油烧至冒烟对准窝心浇下', 2);

-- ========== 8. 腌笃鲜 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('腌笃鲜', '江南立春后的头一锅鲜。“腌”是咸肉，“鲜”是鲜肉，“笃”是小火微沸慢焖，加春笋滚刀块同炖，汤白汁浓，一箸笋尖比肉还抢手。', NULL, 25, 120, 145, 1, 4, '苏菜', '经典,时令,汤羹,苏菜名菜', 1, TRUE, 205, 400, 26, 30, 6, '咸肉先用温水泡去浮盐，全程一滴油不加；小火“笃”到汤色奶白，盐最后尝味再补，宁淡不咸。', '咸鲜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '腊肉', '200', 'g', TRUE, 1, '/api/ingredients/larou.jpg'),
  (@r, '猪排骨', '400', 'g', TRUE, 2, '/api/ingredients/zhupaigu.jpg'),
  (@r, '春笋', '400', 'g', TRUE, 3, '/api/ingredients/dongsun.jpg'),
  (@r, '百叶结', '100', 'g', TRUE, 4, '/api/ingredients/doufu.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '20', 'g', TRUE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '绍兴黄酒', '20', 'ml', TRUE, 7, '/api/ingredients/huangjiu.jpg'),
  (@r, '盐', '2', 'g', FALSE, 8, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '1', 'g', FALSE, 9, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '清水', '1800', 'ml', TRUE, 10, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '腊肉切4厘米大片，温水泡10分钟去浮盐；排骨冷水焯透洗净', 18),
  (@r, 2, '春笋切滚刀块，沸水焯2分钟去掉涩麻味', 8),
  (@r, 3, '砂锅下排骨、腊肉、姜葱，一次加足清水，大火烧沸撇净浮沫', 10),
  (@r, 4, '转小火笃1小时，下笋块续炖30分钟至汤色乳白', 95),
  (@r, 5, '下百叶结煮5分钟，撒白胡椒粉，尝味后再决定补不补盐', 8);

-- ========== 9. 桂花糯米藕 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('桂花糯米藕', '苏南水乡秋天的甜零食。七孔粉藕的孔洞里一粒粒灌满糯米，配冰糖红糖慢煨到酥，切片时拉出糖丝，浇上桂花蜜，糯香桂花香缠绕。', NULL, 30, 150, 180, 2, 6, '苏菜', '甜品,时令,小吃,苏菜名菜', 1, TRUE, 88, 260, 3, 1, 56, '选七孔粉藕才糯，糯米泡足两小时只灌九分满；煮好必须在原汤里泡到凉透，热切就散粒。', '软糯甜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '藕', '2', '节(约700g)', TRUE, 1, '/api/ingredients/ou.jpg'),
  (@r, '糯米', '100', 'g', TRUE, 2, '/api/ingredients/nuomi.jpg'),
  (@r, '冰糖', '60', 'g', TRUE, 3, '/api/ingredients/bingtang.jpg'),
  (@r, '红糖', '40', 'g', TRUE, 4, '/api/ingredients/hongtang.jpg'),
  (@r, '糖桂花', '15', 'g', TRUE, 5, '/api/ingredients/guihuatang.jpg'),
  (@r, '红枣', '6', '颗', FALSE, 6, '/api/ingredients/hongzao.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 7, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '糯米淘净用清水泡2小时，捞出沥干', 120),
  (@r, 2, '藕削去外皮，一端切下3厘米作盖，孔洞刷洗干净控干', 10),
  (@r, 3, '用细筷把糯米一点点灌满每个藕孔，盖回原位以竹签别牢', 15),
  (@r, 4, '藕入锅加清水、冰糖、红糖和红枣，大火烧沸转小火煮2小时至筷子能扎透', 130),
  (@r, 5, '连汤浸凉，改刀成0.5厘米厚片码盘，糖汁收浓淋在藕片上', 20);

-- ========== 10. 碧螺虾仁 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('碧螺虾仁', '苏州以洞庭碧螺春入馔的清鲜名菜。太湖河虾仁上浆过油，只在虾仁玉白将熟时下茶叶快翻两下，茶香裹着鲜甜，一压就弹牙。', NULL, 25, 8, 33, 2, 3, '苏菜', '经典,时令,河鲜,苏菜名菜', 1, TRUE, 128, 210, 24, 10, 4, '虾仁上浆后要四成油温滑到刚变色就起；茶叶最后十几秒连茶汤下锅，久炒茶汤发苦叶转黄。', '茶香清鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '河虾仁', '300', 'g', TRUE, 1, '/api/ingredients/hexiaren.jpg'),
  (@r, '绿茶', '4', 'g', TRUE, 2, '/api/ingredients/lucha.jpg'),
  (@r, '鸡蛋清', '1', '个', TRUE, 3, '/api/ingredients/jidanqing.jpg'),
  (@r, '淀粉', '15', 'g', TRUE, 4, '/api/ingredients/dianfen.jpg'),
  (@r, '绍兴黄酒', '10', 'ml', TRUE, 5, '/api/ingredients/huangjiu.jpg'),
  (@r, '盐', '3', 'g', TRUE, 6, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '1', 'g', FALSE, 7, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '猪油', '30', 'g', TRUE, 8, '/api/ingredients/zhuyou.jpg'),
  (@r, '清水', '100', 'ml', TRUE, 9, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '河虾仁加盐抓出黏性，漂洗两次沥干，与蛋清、干淀粉拌匀腌15分钟', 20),
  (@r, 2, '绿茶用80度左右的100ml水泡开，滗出茶汤30ml留茶叶分开放', 6),
  (@r, 3, '锅下猪油烧至四成热，虾仁下锅滑散至刚变色捞出', 3),
  (@r, 4, '锅留底油，虾仁回锅，烹黄酒、撒盐，倒入茶汤快速翻匀', 2),
  (@r, 5, '最后撒茶叶颠两下装盘，虾仁玉白茶叶翠绿', 2);

-- ========== 11. 常熟叫花鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('常熟叫花鸡', '常熟虞山传了数百年的叫化子菜。三黄鸡腹中酿进香菇笋丁五花肉，两层荷叶裹紧、外封厚面皮入炉烤透，敲开硬壳荷香四溅，酥烂脱骨。', NULL, 60, 100, 160, 3, 6, '苏菜', '经典,宴客,鸡肉,苏菜名菜', 1, TRUE, 260, 400, 32, 26, 8, '面皮要裹严实不许漏气，全凭内部蒸汽把鸡焖熟；烤足80分钟，敲开硬壳时鸡腿能轻松脱骨。', '荷香酥烂');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '三黄鸡', '1', '只(约1200g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '干荷叶', '2', '张', TRUE, 2, '/api/ingredients/ganye.jpg'),
  (@r, '中筋面粉', '500', 'g', TRUE, 3, '/api/ingredients/mianfen.jpg'),
  (@r, '五花肉', '120', 'g', TRUE, 4, '/api/ingredients/wuhuarou.jpg'),
  (@r, '干香菇', '30', 'g', TRUE, 5, '/api/ingredients/ganxianggu.jpg'),
  (@r, '冬笋', '80', 'g', TRUE, 6, '/api/ingredients/dongsun.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '绍兴黄酒', '30', 'ml', TRUE, 8, '/api/ingredients/huangjiu.jpg'),
  (@r, '冰糖', '20', 'g', TRUE, 9, '/api/ingredients/bingtang.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 10, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '25', 'g', TRUE, 11, '/api/ingredients/dacong.jpg'),
  (@r, '盐', '4', 'g', TRUE, 12, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '三黄鸡去爪与翅尖，抽去翅骨，用生抽、黄酒、盐抹匀内外腌1小时', 70),
  (@r, 2, '干香菇泡发切丁，冬笋、五花肉切丁，下锅炒香加冰糖和生抽成馅', 18),
  (@r, 3, '馅料全部塞进鸡腹，刀口用竹签别紧封口', 8),
  (@r, 4, '荷叶烫软，两层包裹扎紧，面皮擀开裹成封严的枕头状', 15),
  (@r, 5, '入烤箱200度烤80分钟至外壳龟裂，敲开面壳揭荷叶斩块装盘', 80);

-- ========== 12. 扬州炒饭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('扬州炒饭', '淮扬厨子的试刀菜。隔夜粳米饭抓散到粒粒分明，配火腿丁鸡丁虾仁青豆，猪油热锅大火炒成“金裹银”，饭粒在锅里跳动不结块。', NULL, 20, 12, 32, 2, 3, '苏菜', '经典,主食,小吃,苏菜名菜', 1, TRUE, 266, 560, 16, 18, 85, '饭要用隔夜的冷粳米饭，下锅前先抓散；猪油热锅大火把蛋液裹成金衣，炒到粒粒在锅里跳才起。', '鲜香粒爽');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大米', '250', 'g', TRUE, 1, '/api/ingredients/dami.jpg'),
  (@r, '鸡蛋', '3', '个', TRUE, 2, '/api/ingredients/jidan.jpg'),
  (@r, '火腿', '60', 'g', TRUE, 3, '/api/ingredients/huotui.jpg'),
  (@r, '鸡胸肉', '80', 'g', TRUE, 4, '/api/ingredients/jitui.jpg'),
  (@r, '河虾仁', '80', 'g', TRUE, 5, '/api/ingredients/hexiaren.jpg'),
  (@r, '青豆', '50', 'g', TRUE, 6, '/api/ingredients/wandoujian.jpg'),
  (@r, '干香菇', '20', 'g', FALSE, 7, '/api/ingredients/ganxianggu.jpg'),
  (@r, '大葱', '20', 'g', TRUE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '猪油', '40', 'g', TRUE, 9, '/api/ingredients/zhuyou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '1', 'g', FALSE, 11, '/api/ingredients/baihujiaofen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大米蒸成稍硬的饭摊凉隔夜；火腿、鸡胸肉、泡发的香菇切1厘米丁，葱切末', 12),
  (@r, 2, '鸡丁与虾仁加盐、蛋清、干淀粉抓匀上浆腌10分钟', 12),
  (@r, 3, '锅下猪油烧至六成热，蛋液下锅炒至刚凝，倒入米饭大火炒散', 4),
  (@r, 4, '下鸡丁、虾仁、火腿丁、青豆、香菇丁，不断颠炒至粒粒挂油', 5),
  (@r, 5, '撒盐与葱花，炒到饭粒在锅里跳动作响、颗颗分明出锅', 3);

-- ========== 13. 梁溪脆鳝 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('梁溪脆鳝', '无锡惠山泉边的百年老菜，又叫脆鳝。鳝丝两次热油炸到干酥挺硬，投入酱油冰糖浓汁里离火翻裹，根根油亮撒芝麻，甜咸里透着姜辣。', NULL, 20, 20, 40, 3, 3, '苏菜', '经典,小吃,河鲜,苏菜名菜', 1, TRUE, 197, 440, 27, 25, 25, '复炸要八成热、下手快，鳝丝炸酥才吸得住汁；浓汁熬好后离火再拌鳝丝，回锅一煮就软而不脆。', '甜咸酥韧');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鳝鱼片', '400', 'g', TRUE, 1, '/api/ingredients/shanyupian.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 2, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '35', 'g', TRUE, 3, '/api/ingredients/baitang.jpg'),
  (@r, '绍兴黄酒', '15', 'ml', TRUE, 4, '/api/ingredients/huangjiu.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '八角粉', '1', 'g', FALSE, 6, '/api/ingredients/bajiao.jpg'),
  (@r, '熟芝麻', '5', 'g', FALSE, 7, '/api/ingredients/baizhima.jpg'),
  (@r, '香油', '8', 'ml', TRUE, 8, '/api/ingredients/xiangyou.jpg'),
  (@r, '盐', '2', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '清水', '20', 'ml', TRUE, 10, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '800', 'ml', FALSE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鳝鱼片入沸水煮2分钟捞出，切成6厘米鳝丝，加黄酒、盐腌10分钟', 18),
  (@r, 2, '生姜切细丝，沥干鳝丝表面水分', 5),
  (@r, 3, '六成油温下鳝丝炸2分钟至变硬，捞起用手捡散', 4),
  (@r, 4, '油升八成热复炸30秒至干酥，立即捞入漏勺沥油', 2),
  (@r, 5, '锅留底油，下姜丝、生抽、白糖和20ml水，小火熬至浓稠起小泡', 4),
  (@r, 6, '倒回鳝丝离火翻裹挂汁，淋香油撒芝麻，摊凉装盘', 3);

-- ========== 14. 文思豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('文思豆腐', '扬州文思院的百年清羹，淮扬刀工的巅峰。嫩豆腐先片成二十余片薄皮，再切成细如发丝的豆腐丝，入鸡清汤烫开，碗中散成一团云雾。', NULL, 40, 15, 55, 3, 4, '苏菜', '经典,宴客,汤羹,苏菜名菜', 1, TRUE, 235, 130, 10, 6, 6, '刀薄手稳，片到二十片不断才敢下切丝；豆腐丝只烫不煮，入沸汤十几秒就起，滚久了就成糊。', '清鲜柔滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '嫩豆腐', '1', '盒(约400g)', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '鸡清汤', '1000', 'ml', TRUE, 2, '/api/ingredients/gaotang.jpg'),
  (@r, '火腿', '30', 'g', TRUE, 3, '/api/ingredients/huotui.jpg'),
  (@r, '冬笋', '50', 'g', TRUE, 4, '/api/ingredients/dongsun.jpg'),
  (@r, '鸡胸肉', '60', 'g', TRUE, 5, '/api/ingredients/jitui.jpg'),
  (@r, '豌豆尖', '60', 'g', TRUE, 6, '/api/ingredients/wandoujian.jpg'),
  (@r, '盐', '4', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '1', 'g', FALSE, 8, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 9, '/api/ingredients/xiangyou.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 10, '/api/ingredients/shengjiang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '嫩豆腐切去老皮，先片成0.1厘米薄片，叠起切成细如发丝的豆腐丝', 25),
  (@r, 2, '豆腐丝入清水中养着，用细漏勺淘去断渣与碎末', 8),
  (@r, 3, '火腿、鸡脯肉、冬笋全部切成与豆腐丝同粗的细丝', 10),
  (@r, 4, '鸡清汤烧沸，下笋丝鸡丝火腿丝煮3分钟，加盐和白胡椒粉调底味', 6),
  (@r, 5, '豆腐丝连水倒入汤中，微火烫1分钟即散开如云雾', 3),
  (@r, 6, '盛入大汤碗放豌豆尖，淋香油上桌，汤清而丝匀', 3);

-- ========== 15. 镇江肴肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('镇江肴肉', '镇江“肴肉不当菜”的三怪之一。猪前肘以花椒盐腌透，加葱姜白煮酥烂，趁热拆骨压平、原汤回灌，冷凝切片水晶透亮，蘸姜丝香醋。', NULL, 50, 150, 200, 3, 8, '苏菜', '地方名菜,卤味,凉菜,苏菜名菜', 1, TRUE, 319, 250, 25, 15, 1, '腌足一天再煮，咸味才进到肉心；趁热拆骨、压平、回灌原汤慢冷，冻得越透切片越亮越不散。', '咸鲜酥弹');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪前肘', '1', '只(约1500g)', TRUE, 1, '/api/ingredients/zhuqianzhou.jpg'),
  (@r, '盐', '35', 'g', TRUE, 2, '/api/ingredients/yan.jpg'),
  (@r, '花椒', '5', 'g', TRUE, 3, '/api/ingredients/huajiao.jpg'),
  (@r, '八角', '4', 'g', TRUE, 4, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '5', 'g', TRUE, 5, '/api/ingredients/guipi.jpg'),
  (@r, '香叶', '2', 'g', FALSE, 6, '/api/ingredients/xiangye.jpg'),
  (@r, '生姜', '25', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '40', 'g', TRUE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '40', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '清水', '2500', 'ml', TRUE, 10, '/api/ingredients/qingshui.jpg'),
  (@r, '香醋', '30', 'ml', FALSE, 11, '/api/ingredients/xiangcu.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪前肘刮洗干净，剔去大骨，皮面划几刀方便入味', 12),
  (@r, 2, '盐与花椒干锅小火炒香，晾凉后擦匀肘子内外，压腌24小时', 250),
  (@r, 3, '肘子入清水泡30分钟洗去浮盐，冷水下锅加姜葱料酒，烧沸撇沫', 20),
  (@r, 4, '加桂皮八角香叶和足量水，微火焖煮2小时至肉酥筷插即透', 125),
  (@r, 5, '趁热拆净碎骨，皮朝下码入方盘压平，滤入原汤冷藏凝冻4小时', 30),
  (@r, 6, '改刀成3毫米薄片码盘，配姜丝香醋蘸食', 10);

-- ========== 16. 拆烩鲢鱼头 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('拆烩鲢鱼头', '常州镇江一带的冬日宴席大菜。鳙鱼头煮到骨肉将离后拆尽细刺仍留全形，配火腿笋片香菇入鸡汤烩透，鱼肉嫩滑，汤浓白似乳汁。', NULL, 35, 45, 80, 3, 4, '苏菜', '经典,宴客,河鲜,苏菜名菜', 1, TRUE, 185, 340, 32, 20, 6, '鱼头煮到筷子能插透就捞，趁热拆骨最省力，凉了刺碎肉散；拆好的肉只㸆不翻动，勾芡才不碎。', '鲜嫩醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鳙鱼头', '1', '个(约1500g)', TRUE, 1, '/api/ingredients/yongyutou.jpg'),
  (@r, '鸡清汤', '800', 'ml', TRUE, 2, '/api/ingredients/gaotang.jpg'),
  (@r, '火腿', '40', 'g', TRUE, 3, '/api/ingredients/huotui.jpg'),
  (@r, '干香菇', '6', '朵', TRUE, 4, '/api/ingredients/ganxianggu.jpg'),
  (@r, '冬笋', '80', 'g', TRUE, 5, '/api/ingredients/dongsun.jpg'),
  (@r, '河虾仁', '60', 'g', FALSE, 6, '/api/ingredients/hexiaren.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '30', 'g', TRUE, 8, '/api/ingredients/dacong.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '白胡椒粉', '2', 'g', TRUE, 10, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '猪油', '40', 'g', TRUE, 11, '/api/ingredients/zhuyou.jpg'),
  (@r, '水淀粉', '50', 'ml', TRUE, 12, '/api/ingredients/dianfen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鱼头去鳃黑膜洗净，沸水下锅加姜葱料酒煮12分钟至筷子能插透', 15),
  (@r, 2, '捞出浸入温水，趁热用手指拆尽脊骨与细刺，保持鱼形完整', 18),
  (@r, 3, '火腿、冬笋、泡发的香菇切成薄片，虾仁用蛋清淀粉上浆', 10),
  (@r, 4, '锅下猪油，笋片火腿香菇片炒出香，冲入鸡清汤烧沸', 5),
  (@r, 5, '放入拆好的鱼肉，加盐和白胡椒粉，微火㸆10分钟入味', 10),
  (@r, 6, '下虾仁烫熟，水淀粉勾薄芡，淋香油推入大汤碗上桌', 5);

-- ========== 17. 扬州三丁包 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('扬州三丁包', '扬州富春茶社早茶的台柱。鸡丁、肉丁、笋丁切得一般大小，加酱油冰糖收浓成馅，发面包出鱼尾状褶，蒸好卤汁渗进面皮，咸甜带酱香。', NULL, 120, 15, 135, 3, 8, '苏菜', '经典,主食,小吃,苏菜名菜', 1, TRUE, 319, 340, 12, 12, 45, '三丁馅必须彻底晾凉再包，热馅会把面皮烫塌捏不出褶；包好醒足20分钟，上汽后大火蒸12分钟。', '酱香咸甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '中筋面粉', '300', 'g', TRUE, 1, '/api/ingredients/mianfen.jpg'),
  (@r, '温水', '150', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '酵母', '4', 'g', TRUE, 3, '/api/ingredients/mianfen.jpg'),
  (@r, '鸡腿肉', '150', 'g', TRUE, 4, '/api/ingredients/jitui.jpg'),
  (@r, '猪瘦肉', '150', 'g', TRUE, 5, '/api/ingredients/zhushourou.jpg'),
  (@r, '冬笋', '100', 'g', TRUE, 6, '/api/ingredients/dongsun.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 8, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '25', 'g', TRUE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '淀粉', '15', 'g', TRUE, 10, '/api/ingredients/dianfen.jpg'),
  (@r, '猪油', '25', 'g', TRUE, 11, '/api/ingredients/zhuyou.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 12, '/api/ingredients/shengjiang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '温水化开酵母，倒入面粉揉成光面面团，加盖发酵1.5小时至两倍大', 95),
  (@r, 2, '鸡腿肉、猪瘦肉、冬笋全部切成1厘米见方的丁，姜切末', 10),
  (@r, 3, '锅下猪油，肉丁先炒至吐油，加姜末、生抽、老抽、白糖翻匀', 6),
  (@r, 4, '下鸡丁笋丁翻炒，加50ml水焖5分钟，水淀粉勾浓汁，盛出晾冷', 10),
  (@r, 5, '面团揉搓排气搓条，下45克剂子，擀成中间厚边缘薄的皮', 15),
  (@r, 6, '每只包入30克馅，右手捏出15道以上鱼尾褶，收口朝上码入垫布笼屉', 15),
  (@r, 7, '醒20分钟后上旺火蒸12分钟，揭盖趁热吃', 32);
