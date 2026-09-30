-- 由 seed/recipes-yunnan.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 云南菜，共 15 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 过桥米线 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('过桥米线', '云南米线的排面。滚鸡汤加盖一层鸡油封住热气，先下生肉片、鹌鹑蛋，再烫蔬菜，最后卧米线，全靠汤的高温把料焖熟。大海碗上桌，配料分小碟摆一圈。', NULL, 30, 120, 150, 3, 2, '云南菜', '米线,汤粉,云南名菜,宴客', 1, TRUE, 177, 620, 38, 22, 70, '汤要沸到能烫熟肉片，老鸡加猪筒骨熬够两小时，起锅前泼一勺滚鸡油封口保温；肉片切得越薄越安全，不放心的先把肉片快速汆熟；下料顺序是荤在先、素在后、米线最后。', '鲜香醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '米线', '200', 'g', TRUE, 1, '/api/ingredients/ganmifen.jpg'),
  (@r, '土鸡', '1', '只(约1000g)', TRUE, 2, '/api/ingredients/tuji.jpg'),
  (@r, '猪筒骨', '500', 'g', TRUE, 3, '/api/ingredients/zhutonggu.jpg'),
  (@r, '猪里脊', '150', 'g', TRUE, 4, '/api/ingredients/zhuliji.jpg'),
  (@r, '鸡胸肉', '100', 'g', FALSE, 5, '/api/ingredients/jitui.jpg'),
  (@r, '鹌鹑蛋', '6', '个', FALSE, 6, '/api/ingredients/anchundan.jpg'),
  (@r, '豌豆尖', '150', 'g', TRUE, 7, '/api/ingredients/wandoujian.jpg'),
  (@r, '腐皮', '50', 'g', FALSE, 8, '/api/ingredients/doufu.jpg'),
  (@r, '火腿', '40', 'g', FALSE, 9, '/api/ingredients/huotui.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 10, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', FALSE, 11, '/api/ingredients/xiaocong.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 12, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '盐', '6', 'g', TRUE, 13, '/api/ingredients/yan.jpg'),
  (@r, '清水', '2500', 'ml', TRUE, 14, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '土鸡宰净斩大块，和猪筒骨一起冷水下锅，加姜片烧开，撇净浮沫', 15),
  (@r, 2, '转小火加盖熬90分钟，滤出汤里的料渣，舀出面上鸡油留用', 92),
  (@r, 3, '猪里脊、鸡胸肉和火腿切薄片，分小碟码好；豌豆尖、腐皮洗净沥干', 15),
  (@r, 4, '鹌鹑蛋煮熟去壳；另起一锅水煮开，下米线烫透捞出盛进空碗', 10),
  (@r, 5, '鸡油回烧至冒烟泼进汤碗封住热气，滚汤连大碗上桌', 2),
  (@r, 6, '先磕入鹌鹑蛋，再依次下肉片、腐皮和豌豆尖，用汤温烫熟，最后把米线挑进汤里，边烫边吃', 4);

-- ========== 2. 汽锅鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('汽锅鸡', '建水汽锅的看家菜。汽锅中间立一根空心管，锅里不放水，全靠蒸汽沿管子往上顶、在锅盖冷凝成汤，两小时蒸出一锅清澈的原味鸡汤，只下姜片和盐。', NULL, 20, 180, 200, 2, 4, '云南菜', '蒸菜,汤羹,云南名菜,原汁原味', 1, TRUE, 139, 320, 32, 18, 4, '汽锅不能用普通汤锅替，锅沿和底锅接缝要用湿纱布封严，漏气就蒸不出汤；底锅水烧干前记得添热水；中途千万别揭盖加水，一锅汤全靠蒸汽凝出来。', '清鲜本味');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '土鸡', '1', '只(约1200g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '枸杞', '10', 'g', FALSE, 3, '/api/ingredients/gouqi.jpg'),
  (@r, '干香菇', '30', 'g', FALSE, 4, '/api/ingredients/ganxianggu.jpg'),
  (@r, '猪油', '5', 'g', FALSE, 5, '/api/ingredients/zhuyou.jpg'),
  (@r, '料酒', '20', 'ml', FALSE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '5', 'g', TRUE, 7, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '土鸡洗净斩四大块，冷水下锅加料酒烧开，焯去血沫后捞出冲凉', 12),
  (@r, 2, '汽锅内壁抹一层薄薄的猪油防粘，姜片铺底，鸡块皮朝上码进去', 6),
  (@r, 3, '香菇泡发，和枸杞一起摆在鸡块上，淋料酒，锅里不加水', 5),
  (@r, 4, '汽锅坐进盛足水的汤锅，锅沿用湿布封严，大火烧开后转中火蒸2小时', 125),
  (@r, 5, '端出汽锅，加盐调味，撇去表面浮油，连锅上桌', 3);

-- ========== 3. 香茅草烤鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('香茅草烤鱼', '傣味烧烤的头牌。鱼两面夹上竹片，塞进拍散的香茅草和蒜末辣椒，炭火慢烤到外皮焦香、香茅的柠檬气渗进鱼肉，闻着就上头。', NULL, 30, 25, 55, 2, 4, '云南菜', '烧烤,河鲜,傣味,云南名菜', 1, TRUE, 132, 340, 40, 14, 5, '香茅草要拍裂再切末，精油才出得来；没有炭炉用烤箱230℃两层烤15分钟，中途刷一次油；竹片夹紧鱼身能定型，翻面不容易散。', '辛香酸辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鲤鱼', '1', '条(约700g)', TRUE, 1, '/api/ingredients/caoyu.jpg'),
  (@r, '香茅草', '3', '根', TRUE, 2, '/api/ingredients/qingsuan.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '小米辣', '20', 'g', TRUE, 4, '/api/ingredients/xiaomila.jpg'),
  (@r, '香菜', '20', 'g', FALSE, 5, '/api/ingredients/xiangcai.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '3', 'g', FALSE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '6', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '25', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鱼去鳞鳃和内脏，从背部剖开摊平成一片，腹内黑膜刮净', 12),
  (@r, 2, '香茅草拍裂，2根切细末，1根编成草绳或塞在鱼腹里', 8),
  (@r, 3, '蒜末、小米辣圈、盐、生抽、料酒和白糖拌成香料酱，抹遍鱼身里外腌20分钟', 22),
  (@r, 4, '用竹片把鱼夹住，炭火或烤箱中层烤8分钟', 9),
  (@r, 5, '翻面刷一层油再烤7至8分钟，至表皮焦脆、鱼眼发白', 8),
  (@r, 6, '拆去草绳，撒香菜末，连竹片装盘上桌', 2);

-- ========== 4. 景颇鬼鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('景颇鬼鸡', '景颇族的凉拌手撕鸡。整鸡煮至刚熟，晾凉手撕成丝，配香茅草末、小米辣、蒜末和芫荽，用盐与野花椒拌匀，酸辣辛香、越拌越入味。', NULL, 15, 30, 75, 2, 4, '云南菜', '凉菜,手撕鸡,傣景颇味,下酒', 1, TRUE, 217, 280, 36, 12, 6, '鸡腿比整鸡好操作，煮15分钟加盖焖10分钟最嫩；一定要彻底晾凉再撕，热撕会成渣；拌好冷藏半小时，香茅和辣椒的味道才融进肉里。', '酸辣辛香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸡腿', '4', '只(约600g)', TRUE, 1, '/api/ingredients/jitui.jpg'),
  (@r, '香茅草', '2', '根', TRUE, 2, '/api/ingredients/qingsuan.jpg'),
  (@r, '小米辣', '15', 'g', TRUE, 3, '/api/ingredients/xiaomila.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '香菜', '30', 'g', TRUE, 5, '/api/ingredients/xiangcai.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '花椒粉', '3', 'g', FALSE, 7, '/api/ingredients/huajiaofen.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '15', 'ml', FALSE, 9, '/api/ingredients/xiangcu.jpg'),
  (@r, '白糖', '3', 'g', FALSE, 10, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '5', 'g', TRUE, 11, '/api/ingredients/yan.jpg'),
  (@r, '料酒', '20', 'ml', FALSE, 12, '/api/ingredients/liaojiu.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡腿冷水下锅，加姜片、葱和料酒，烧开撇沫后煮15分钟', 20),
  (@r, 2, '关火加盖焖10分钟，捞出插筷子无血水即熟', 11),
  (@r, 3, '香茅草拍裂切细末，小米辣切圈，蒜剁泥，香菜切段', 8),
  (@r, 4, '鸡腿晾凉后顺纹理撕成细丝，粗的鸡骨边肉剔掉', 10),
  (@r, 5, '把香茅末、辣椒、蒜泥、香菜和盐、生抽、香醋、白糖、花椒粉一起倒进鸡丝', 5),
  (@r, 6, '用手抓拌均匀，冷藏腌渍30分钟以上再吃', 32);

-- ========== 5. 大救驾 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('大救驾', '腾冲名菜，主角是饵块。饵块切薄片，配火腿、鸡蛋、西红柿和豌豆尖爆炒，酸香开胃、饵片软糯带焦边，据说因救了南明皇帝的驾而得名。', NULL, 15, 12, 27, 2, 3, '云南菜', '炒饵块,主食,腾冲名菜,家常', 1, TRUE, 115, 480, 20, 20, 58, '饵块买回来略晾干再切，切片不粘刀；下锅前先煸火腿出油，再炒西红柿出沙，饵块最后下、大火快翻，炒太久会糊成一团。', '酸香浓郁');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '饵块', '400', 'g', TRUE, 1, '/api/ingredients/niangao.jpg'),
  (@r, '火腿', '40', 'g', TRUE, 2, '/api/ingredients/huotui.jpg'),
  (@r, '鸡蛋', '2', '个', TRUE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '西红柿', '150', 'g', TRUE, 4, '/api/ingredients/xihongshi.jpg'),
  (@r, '豌豆尖', '100', 'g', FALSE, 5, '/api/ingredients/wandoujian.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '大葱', '1', '根', FALSE, 7, '/api/ingredients/dacong.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '4', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '猪油', '15', 'g', FALSE, 11, '/api/ingredients/zhuyou.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '饵块切成3毫米厚的片，太黏的话摊开晾10分钟', 12),
  (@r, 2, '火腿切小片，西红柿切丁，豌豆尖洗净，蒜切末，葱切马耳朵', 8),
  (@r, 3, '鸡蛋打散，热锅宽油炒成大块盛出', 3),
  (@r, 4, '锅留底油加猪油，下火腿煸出油，再下蒜末葱白和西红柿丁炒出沙', 5),
  (@r, 5, '下饵块大火翻炒，加生抽、白糖和少许盐，锅里太干就沿锅边点两次水', 5),
  (@r, 6, '饵片变软透亮后回鸡蛋、下豌豆尖，翻匀断生即可出锅', 2);

-- ========== 6. 小锅米线 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('小锅米线', '昆明人的早点。一只小铜锅现煮，猪油炝锅下肉末，加酸腌菜、西红柿和高汤烧开，再烫米线下豌豆尖，一锅一碗，汤浓味重。', NULL, 10, 12, 22, 1, 1, '云南菜', '米线,汤粉,早餐,昆明小吃', 1, TRUE, 257, 520, 24, 20, 62, '米线别煮太久，回软下锅烫30秒就捞，煮烂了不成形；猪油是灵魂，换成植物油香味差一半；一人一小锅，最多加两份料，锅小汤才浓。', '咸鲜微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '米线', '150', 'g', TRUE, 1, '/api/ingredients/ganmifen.jpg'),
  (@r, '猪肉末', '80', 'g', TRUE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '豌豆尖', '60', 'g', TRUE, 3, '/api/ingredients/wandoujian.jpg'),
  (@r, '西红柿', '80', 'g', FALSE, 4, '/api/ingredients/xihongshi.jpg'),
  (@r, '腐皮', '30', 'g', FALSE, 5, '/api/ingredients/doufu.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '1', '根', FALSE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '小米辣', '10', 'g', FALSE, 8, '/api/ingredients/xiaomila.jpg'),
  (@r, '猪油', '15', 'g', TRUE, 9, '/api/ingredients/zhuyou.jpg'),
  (@r, '高汤', '400', 'ml', TRUE, 10, '/api/ingredients/gaotang.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 11, '/api/ingredients/shengchou.jpg'),
  (@r, '白胡椒粉', '1', 'g', FALSE, 12, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '盐', '3', 'g', TRUE, 13, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '米线提前用温水泡10分钟至散开，蒜切末，葱切花，小米辣切圈', 11),
  (@r, 2, '小铜锅下猪油烧化，爆香蒜末和肉末，炒到肉末发白吐油', 3),
  (@r, 3, '下西红柿丁和小米辣炒出红汁', 2),
  (@r, 4, '掺高汤烧开，加生抽、白胡椒粉和盐调味', 4),
  (@r, 5, '下米线和腐皮，煮到米线回软吸味，约1分钟', 2),
  (@r, 6, '最后下豌豆尖，一烫就断生，撒葱花连锅端上桌', 1);

-- ========== 7. 牛肝菌炒肉片 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('牛肝菌炒肉片', '云南人夏天的执念。新鲜牛肝菌切厚片，宽油加大蒜、干辣椒和青椒猛火爆炒，菌片滑嫩带坚果香，油都舍不得倒。', NULL, 20, 10, 30, 3, 4, '云南菜', '野生菌,爆炒,时令,云南名菜', 1, TRUE, 131, 380, 22, 28, 8, '菌子只买认识的品种，量不要贪杂；蒜要多，一半拍一半切片，据说蒜变色就弃食；菌片下锅前先干焙出水汽，再宽油爆炒才香而不黏；吃菌三不：不认识的不吃、不熟的不吃、隔夜的不吃。', '浓香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '牛肝菌', '400', 'g', TRUE, 1, '/api/ingredients/huangjun.jpg'),
  (@r, '猪瘦肉', '120', 'g', TRUE, 2, '/api/ingredients/zhushourou.jpg'),
  (@r, '大蒜', '40', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '干辣椒', '8', 'g', FALSE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '青辣椒', '30', 'g', FALSE, 5, '/api/ingredients/qinglajiao.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '料酒', '15', 'ml', FALSE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '猪油', '20', 'g', FALSE, 9, '/api/ingredients/zhuyou.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '5', 'g', TRUE, 11, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肝菌用湿布擦净泥沙，切5毫米厚片，碎边留着一起下锅', 12),
  (@r, 2, '瘦肉切薄片，用料酒和少许生抽抓腌10分钟', 11),
  (@r, 3, '干辣椒段、青椒滚刀块、姜蒜切片备好，蒜量要盖住菌片', 6),
  (@r, 4, '净锅烧热下菌片中火干焙，出汽后倒掉黑水，盛出', 6),
  (@r, 5, '锅重新下食用油和猪油，油宽一些，爆香姜蒜辣椒', 2),
  (@r, 6, '下肉片滑炒至变色，再倒菌片大火翻匀，加生抽和盐', 3),
  (@r, 7, '保持猛火炒足4分钟，出锅前尝一下咸淡，配米饭趁热吃', 4);

-- ========== 8. 酸笋煮鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('酸笋煮鸡', '云南边地的开胃硬菜。自制酸笋切段，和土鸡、花椒、姜蒜同煮，汤味酸香冲鼻、鸡肉不柴，酸笋吸饱鸡油比肉还抢手。', NULL, 20, 60, 80, 2, 4, '云南菜', '酸汤,炖煮,傣味,下饭', 1, TRUE, 192, 400, 34, 24, 6, '酸笋先干锅焙去水汽，酸味更纯正、汤不浑；买来的酸笋偏咸，泡10分钟再切；鸡先煸后煮，汤才乳白；这锅汤别放太多调料，盐和辣椒足够。', '酸香冲辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '酸笋', '300', 'g', TRUE, 1, '/api/ingredients/yansun.jpg'),
  (@r, '土鸡', '半', '只(约600g)', TRUE, 2, '/api/ingredients/tuji.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '25', 'g', FALSE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '小米辣', '20', 'g', TRUE, 5, '/api/ingredients/xiaomila.jpg'),
  (@r, '花椒', '3', 'g', FALSE, 6, '/api/ingredients/huajiao.jpg'),
  (@r, '香菜', '20', 'g', FALSE, 7, '/api/ingredients/xiangcai.jpg'),
  (@r, '猪油', '25', 'g', TRUE, 8, '/api/ingredients/zhuyou.jpg'),
  (@r, '料酒', '20', 'ml', FALSE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '6', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 11, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '酸笋切厚片，净锅小火焙3分钟去水汽，盛出', 5),
  (@r, 2, '土鸡斩块洗净，加料酒腌10分钟', 11),
  (@r, 3, '锅下猪油，把鸡块煸到皮微黄、油渗出', 6),
  (@r, 4, '下姜片、蒜、花椒和小米辣炒香，冲入沸水', 3),
  (@r, 5, '下酸笋，大火烧开后转中小火煮40分钟', 42),
  (@r, 6, '加盐调味，再煮10分钟让酸味进肉，撒香菜连锅上桌', 12);

-- ========== 9. 菌子火锅 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('菌子火锅', '雨季云南的仪式感。牛肝菌、鸡枞、香菇和木耳一锅烩，用猪筒骨或鸡汤做底，先喝一碗汤再涮菜，菌子必须煮够时间才动筷。', NULL, 30, 45, 75, 2, 6, '云南菜', '火锅,野生菌,时令,聚宴', 1, TRUE, 106, 300, 22, 14, 12, '菌子种类控制在三到四种，全部洗净切厚片；开锅后计时20分钟再吃，别抢着捞；底汤宁淡勿咸，蘸水单独调（生抽加小米辣和香菜）；涮菜选豌豆尖、豆腐这类不抢味的。', '鲜香醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '牛肝菌', '250', 'g', TRUE, 1, '/api/ingredients/huangjun.jpg'),
  (@r, '鸡枞菌', '150', 'g', TRUE, 2, '/api/ingredients/ganxianggu.jpg'),
  (@r, '干香菇', '40', 'g', FALSE, 3, '/api/ingredients/ganxianggu.jpg'),
  (@r, '木耳', '30', 'g', FALSE, 4, '/api/ingredients/muer.jpg'),
  (@r, '猪筒骨', '500', 'g', TRUE, 5, '/api/ingredients/zhutonggu.jpg'),
  (@r, '嫩豆腐', '200', 'g', FALSE, 6, '/api/ingredients/doufu.jpg'),
  (@r, '豌豆尖', '150', 'g', FALSE, 7, '/api/ingredients/wandoujian.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 9, '/api/ingredients/dasuan.jpg'),
  (@r, '小米辣', '15', 'g', FALSE, 10, '/api/ingredients/xiaomila.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 11, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '8', 'g', TRUE, 12, '/api/ingredients/yan.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 13, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪筒骨冷水下锅，加姜片烧开撇沫，小火熬40分钟做底汤', 45),
  (@r, 2, '牛肝菌、鸡枞切厚片，香菇泡发，木耳泡开撕小朵', 15),
  (@r, 3, '锅下油，蒜片爆香，菌片一起下锅炒2分钟去腥提香', 4),
  (@r, 4, '炒过的菌倒进底汤，大火烧开转中火煮20分钟', 22),
  (@r, 5, '加盐调味，先给每人盛一碗头道菌汤', 3),
  (@r, 6, '再下豆腐和豌豆尖涮着吃，蘸水用生抽加小米辣、蒜末和香菜调', 8);

-- ========== 10. 火腿炒豌豆尖 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('火腿炒豌豆尖', '云南冬天最家常的一盘。宣威火腿切小片煸出油，下蒜和豌豆尖大火快炒，只放一撮糖不加水，豆尖脆嫩、火腿咸香，盘子底只剩一层油。', NULL, 10, 5, 15, 1, 2, '云南菜', '小炒,时蔬,下饭菜,冬季', 1, TRUE, 135, 230, 14, 16, 10, '豌豆尖要现摘现炒，洗净后彻底沥干，带水下锅就成煮菜；火腿本身很咸，盐几乎不用放；全程最大火，从下锅到出锅不超过一分钟。', '咸鲜清甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '豌豆尖', '300', 'g', TRUE, 1, '/api/ingredients/wandoujian.jpg'),
  (@r, '火腿', '50', 'g', TRUE, 2, '/api/ingredients/huotui.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '猪油', '25', 'g', TRUE, 4, '/api/ingredients/zhuyou.jpg'),
  (@r, '白糖', '2', 'g', FALSE, 5, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '1', 'g', FALSE, 6, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '豌豆尖掐去老根，只留嫩尖和嫩叶，洗净沥干水', 8),
  (@r, 2, '火腿切薄片，蒜拍扁剁碎', 4),
  (@r, 3, '锅下猪油烧到冒烟，先煸火腿出油至边卷', 2),
  (@r, 4, '下蒜末爆香，随即倒豌豆尖', 1),
  (@r, 5, '大火翻炒十几下，加白糖和少许盐，豆尖塌秧就立刻出锅', 1);

-- ========== 11. 石屏包浆豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('石屏包浆豆腐', '建水、石屏一带的街头小吃。小方豆腐先用盐水浸透，宽油小火慢煎到两面结硬壳、里面还是浆，蘸干碟或卤汁吃，一口爆浆。', NULL, 15, 20, 35, 2, 4, '云南菜', '小吃,豆腐,煎炸,夜市', 1, TRUE, 176, 350, 22, 24, 10, '豆腐选压得实、有弹性的包浆豆腐或老豆腐，嫩豆腐做不出爆浆；淡盐水浸10分钟定型去豆腥；小火慢煎到外壳硬、鼓起来才成，急火外焦里生；蘸水里蒜和香菜要生。', '外香内嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '豆腐', '400', 'g', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '食用油', '60', 'ml', TRUE, 2, '/api/ingredients/shiyongyou.jpg'),
  (@r, '辣椒面', '10', 'g', TRUE, 3, '/api/ingredients/lajiaofen.jpg'),
  (@r, '花椒粉', '3', 'g', FALSE, 4, '/api/ingredients/huajiaofen.jpg'),
  (@r, '孜然粉', '3', 'g', FALSE, 5, '/api/ingredients/bajiao.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '2', '根', FALSE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '15', 'g', FALSE, 8, '/api/ingredients/xiangcai.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '3', 'g', FALSE, 10, '/api/ingredients/baitang.jpg'),
  (@r, '盐', '4', 'g', TRUE, 11, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '豆腐切成3厘米见方的小块，投入淡盐水浸10分钟后彻底沥干', 12),
  (@r, 2, '平底锅宽油烧到五成热，下豆腐块转小火慢煎', 3),
  (@r, 3, '每隔两三分钟翻一次面，煎到六面结硬壳、豆腐微微鼓起', 18),
  (@r, 4, '辣椒面、花椒粉、孜然粉和盐炒香，盛出做成干碟', 3),
  (@r, 5, '蒜末、葱花、香菜加生抽和少许凉开水调成蘸汁', 3),
  (@r, 6, '豆腐捞出控油，趁热蘸干碟或蘸汁吃', 2);

-- ========== 12. 铜锅洋芋焖饭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('铜锅洋芋焖饭', '云南人把土豆当主角的焖饭。铜锅或厚底锅里猪油拌米，铺上洋芋丁、火腿和青豆，一次加足水焖到土豆起沙、米饭吸味，锅底还有焦香锅巴。', NULL, 20, 35, 55, 2, 4, '云南菜', '主食,焖饭,土豆,家常', 1, TRUE, 111, 560, 16, 18, 82, '水比平时煮饭略少，土豆会出水；米提前泡20分钟更匀；猪油换菜籽油也行，但少了那股香；全程中小火，听到锅底咔咔响就关火再焖10分钟，别急着揭盖。', '油润咸香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大米', '400', 'g', TRUE, 1, '/api/ingredients/dami.jpg'),
  (@r, '洋芋', '300', 'g', TRUE, 2, '/api/ingredients/tudou.jpg'),
  (@r, '火腿', '50', 'g', TRUE, 3, '/api/ingredients/huotui.jpg'),
  (@r, '青豆', '80', 'g', FALSE, 4, '/api/ingredients/wandoujian.jpg'),
  (@r, '猪油', '30', 'g', TRUE, 5, '/api/ingredients/zhuyou.jpg'),
  (@r, '大葱', '1', '根', FALSE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '盐', '5', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '清水', '500', 'ml', TRUE, 8, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大米淘净泡20分钟，沥干', 22),
  (@r, 2, '洋芋去皮切2厘米丁，火腿切小丁，葱切花', 8),
  (@r, 3, '铜锅下猪油化开，先煸火腿丁和葱白出香', 3),
  (@r, 4, '下洋芋丁翻炒，掺入大米一起拌匀，让每粒米挂上油', 4),
  (@r, 5, '加盐一次注足清水，大火烧开后转小火加盖焖25分钟', 28),
  (@r, 6, '撒青豆再焖5分钟，听到锅底有细微响声就关火，焖10分钟揭盖拌匀，撒葱花', 16);

-- ========== 13. 菠萝饭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('菠萝饭', '傣味甜点兼主食。糯米泡透蒸熟，拌进白糖和菠萝丁，装回挖空的菠萝壳再蒸一回，开壳时酸甜气扑鼻，米粒带果香。', NULL, 30, 55, 300, 1, 4, '云南菜', '主食,甜点,傣味,宴客', 1, TRUE, 168, 430, 8, 3, 92, '糯米至少泡4小时，指尖能碾碎才蒸得透；菠萝选熟透的，挖肉时留一层果肉别戳穿外壳；蒸回壳里时盖上保鲜膜防滴水；放凉也能吃，夏天冰过更爽口。', '酸甜果香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '糯米', '300', 'g', TRUE, 1, '/api/ingredients/nuomi.jpg'),
  (@r, '菠萝', '1', '个(约800g)', TRUE, 2, '/api/ingredients/nangua.jpg'),
  (@r, '白糖', '40', 'g', TRUE, 3, '/api/ingredients/baitang.jpg'),
  (@r, '蜂蜜', '20', 'g', FALSE, 4, '/api/ingredients/mayatang.jpg'),
  (@r, '熟芝麻', '5', 'g', FALSE, 5, '/api/ingredients/baizhima.jpg'),
  (@r, '清水', '1000', 'ml', FALSE, 6, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '糯米淘净，加清水浸泡4小时以上，沥干铺在笼布里', 245),
  (@r, 2, '旺火蒸30分钟至米粒透明无硬芯', 31),
  (@r, 3, '菠萝顶部切下当盖，刀划井字后挖出果肉，壳留用', 10),
  (@r, 4, '三分之一果肉切小丁，其余榨汁后与白糖、蜂蜜小火熬到糖化', 8),
  (@r, 5, '把糖浆拌进蒸好的糯米，加菠萝丁拌匀', 5),
  (@r, 6, '装回菠萝壳，表面再放些菠萝丁，加盖再蒸15分钟', 16),
  (@r, 7, '取出撒熟芝麻，连壳上桌，分碗挖着吃', 2);

-- ========== 14. 鸡枞菌凉米线 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('鸡枞菌凉米线', '夏天的一碗。米线冰镇过，浇一勺用油浸透的鸡枞，配黄瓜丝、胡萝卜丝和酸辣蘸水式调料，拌开又脆又香，鸡枞油沉在碗底。', NULL, 20, 15, 35, 2, 2, '云南菜', '凉食,米线,野生菌,夏季', 1, TRUE, 133, 470, 14, 18, 62, '鸡枞别水洗，用刀刮净泥沙，撕成条后用温油小火浸炸20分钟，油多才香、能放一周；米线煮好过冰水，沥干拌一点油不粘；酸辣汁先淡后调，拌面时再补。', '酸辣鲜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '米线', '200', 'g', TRUE, 1, '/api/ingredients/ganmifen.jpg'),
  (@r, '鸡枞菌', '150', 'g', TRUE, 2, '/api/ingredients/ganxianggu.jpg'),
  (@r, '黄瓜', '100', 'g', FALSE, 3, '/api/ingredients/huanggua.jpg'),
  (@r, '胡萝卜', '60', 'g', FALSE, 4, '/api/ingredients/huluobo.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '香菜', '20', 'g', FALSE, 6, '/api/ingredients/xiangcai.jpg'),
  (@r, '小米辣', '10', 'g', FALSE, 7, '/api/ingredients/xiaomila.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '香醋', '20', 'ml', TRUE, 9, '/api/ingredients/xiangcu.jpg'),
  (@r, '白糖', '8', 'g', FALSE, 10, '/api/ingredients/baitang.jpg'),
  (@r, '辣椒油', '15', 'ml', FALSE, 11, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '食用油', '60', 'ml', TRUE, 12, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 13, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡枞菌撕成条，锅里放宽油烧到三成热，下鸡枞小火浸炸20分钟，加盐后连油盛出晾凉', 22),
  (@r, 2, '大锅水烧开下米线煮透，捞出过冰水，沥干后拌少许油', 10),
  (@r, 3, '黄瓜、胡萝卜切丝，蒜捣成泥加凉开水做成蒜水，香菜和小米辣切段', 8),
  (@r, 4, '香醋、生抽、白糖、辣椒油和蒜水调成酸辣汁尝味', 3),
  (@r, 5, '米线入碗，铺上黄瓜丝胡萝卜丝，浇两勺鸡枞和鸡枞油', 3),
  (@r, 6, '淋酸辣汁，撒香菜小米辣，吃前拌匀', 2);

-- ========== 15. 昭通小肉串 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('昭通小肉串', '昭通把小肉串烤成了一座城的夜宵。黄牛肉切小片签成一口一串，只刷油撒盐，炭火上烤到微焦，出炉前撒孜然和辣椒面，配生蒜吃。', NULL, 25, 20, 45, 2, 4, '云南菜', '烧烤,夜宵,牛肉,云南名小吃', 1, TRUE, 280, 320, 28, 20, 4, '牛肉选后腿或里脊，带一点肥的夹着穿；一片肉一签，串得松一点才烤得匀；盐先淡后补，最后撒料离火，孜然和辣椒面遇久火就苦；家用烤箱230℃上层8至10分钟，中途翻面刷油。', '干香孜然');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '黄牛后腿肉', '500', 'g', TRUE, 1, '/api/ingredients/niurou.jpg'),
  (@r, '孜然粉', '5', 'g', TRUE, 2, '/api/ingredients/bajiao.jpg'),
  (@r, '辣椒面', '8', 'g', TRUE, 3, '/api/ingredients/lajiaofen.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 4, '/api/ingredients/shiyongyou.jpg'),
  (@r, '生抽', '20', 'ml', FALSE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '料酒', '15', 'ml', FALSE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '4', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '大蒜', '30', 'g', FALSE, 8, '/api/ingredients/dasuan.jpg'),
  (@r, '香菜', '20', 'g', FALSE, 9, '/api/ingredients/xiangcai.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肉顺纹切成3毫米厚小片，加料酒和生抽抓匀腌15分钟', 17),
  (@r, 2, '每签穿一片肉，串得宽松一些，肥瘦相间', 12),
  (@r, 3, '炭火烧到无明火、红炭铺平，上串烤1分钟', 2),
  (@r, 4, '刷一层薄油，翻面再烤1分钟，反复两次', 5),
  (@r, 5, '肉色转深、边缘起焦时撒盐和辣椒面、孜然粉，再各烤半分钟', 3),
  (@r, 6, '出炉配生蒜瓣和香菜，趁热吃', 2);
