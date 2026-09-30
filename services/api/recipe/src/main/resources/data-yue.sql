-- 由 seed/recipes-yue.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 粤菜，共 18 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 白切鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('白切鸡', '粤菜“无鸡不成宴”的头牌。三黄鸡入虾眼水三起三落、浸焖至骨带血丝，冰水激脆皮，斩件蘸姜葱蓉，皮爽肉滑骨香，吃的是本味。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/yue-baiqieji.jpg', 15, 45, 60, 2, 4, '粤菜', '经典,宴客,鸡肉,广东名菜', 1, TRUE, 182, 290, 34, 16, 1, '浸鸡的水宁小勿沸，滚水会把皮煮破失爽；关火后再焖15分钟靠余温焖熟，斩件前冰水激透皮才脆。', '清鲜原味');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '三黄鸡', '1', '只(约1250g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '生姜', '50', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '5', '根', TRUE, 3, '/api/ingredients/xiaocong.jpg'),
  (@r, '盐', '8', 'g', TRUE, 4, '/api/ingredients/yan.jpg'),
  (@r, '料酒', '15', 'ml', FALSE, 5, '/api/ingredients/liaojiu.jpg'),
  (@r, '芝麻香油', '15', 'ml', FALSE, 6, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '三黄鸡去净杂毛、掏净内脏，姜一半切片一半留茸，小葱挽结并切葱花', 5),
  (@r, 2, '大锅烧清水加姜片、葱结、料酒，煮至虾眼水（约90℃冒小泡）', 12),
  (@r, 3, '提鸡头把鸡身入水浸10秒提起，反复三起三落让腔内外水温一致', 2),
  (@r, 4, '水再开转小火加盖浸焖25分钟，中途翻面一次，关火再焖15分钟', 40),
  (@r, 5, '竹筷插鸡腿无血水冒出即熟，捞出立刻浸入冰水激脆鸡皮', 10),
  (@r, 6, '姜茸葱花加盐拌匀，淋滚油激香成姜葱蓉；鸡斩件装盘蘸食', 8);

-- ========== 2. 蜜汁叉烧 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('蜜汁叉烧', '广式烧腊铺的金字招牌。梅头肉以生抽蚝油酒腌足隔夜，挂炉高温烤出焦边蜜汁，肥瘦相间带脆边，甜咸交织最下饭。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/yue-mizhichashao.jpg', 30, 45, 75, 3, 4, '粤菜', '经典,烧腊,烤肉,广东名菜', 1, TRUE, 98, 370, 30, 22, 12, '选肥瘦相间的梅头肉才不柴；腌足一夜最入味，最后刷蜂蜜麦芽糖只烤几分钟，火大糖易焦黑发苦。', '甜咸酱香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '梅头肉', '750', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 2, '/api/ingredients/shengchou.jpg'),
  (@r, '蚝油', '30', 'g', TRUE, 3, '/api/ingredients/haoyou.jpg'),
  (@r, '冰糖', '30', 'g', TRUE, 4, '/api/ingredients/bingtang.jpg'),
  (@r, '白酒', '15', 'ml', TRUE, 5, '/api/ingredients/baijiu.jpg'),
  (@r, '五香粉', '3', 'g', TRUE, 6, '/api/ingredients/bajiao.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '蜂蜜', '50', 'g', FALSE, 9, '/api/ingredients/mayatang.jpg'),
  (@r, '麦芽糖', '30', 'g', FALSE, 10, '/api/ingredients/mayatang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '梅头肉切三指厚长条用刀背拍松，加生抽、蚝油、酒、五香粉、姜蒜末抓匀腌一晚（至少4小时）', 30),
  (@r, 2, '腌好的肉条沥出，烤箱预热220℃，烤架架在锡盘上接油', 8),
  (@r, 3, '入炉烤20分钟取出刷一层腌汁，翻面再烤15分钟', 35),
  (@r, 4, '蜂蜜加麦芽糖和少许热水调成蜜汁，刷上再烤5分钟至边缘焦红', 10),
  (@r, 5, '出炉静置5分钟逆纹切片，淋盘底余汁上桌', 5);

-- ========== 3. 脆皮烧鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('脆皮烧鸭', '与深井烧鹅同源的做法。光鸭腹腔抹五香生抽，吹气烫皮后淋麦芽糖醋酸皮水，风干一夜入明炉，枣红油亮、皮脆肉嫩。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/yue-cuipishouya.jpg', 60, 70, 130, 3, 4, '粤菜', '经典,烧腊,宴客,广东名菜', 1, TRUE, 169, 420, 32, 30, 5, '脆皮的命门在皮水与风干：烫皮要收紧、脆皮水要挂匀，皮没彻底吹干就上炉则脆不起来。', '咸香脆皮');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '肥鸭', '1', '只(约1500g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '五香粉', '5', 'g', TRUE, 2, '/api/ingredients/bajiao.jpg'),
  (@r, '陈皮', '3', 'g', FALSE, 3, '/api/ingredients/luobogan.jpg'),
  (@r, '生抽', '40', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '6', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 7, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '3', '根', FALSE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '白醋', '60', 'ml', FALSE, 9, '/api/ingredients/baicu.jpg'),
  (@r, '麦芽糖', '40', 'g', FALSE, 10, '/api/ingredients/mayatang.jpg'),
  (@r, '白酒', '20', 'ml', FALSE, 11, '/api/ingredients/baijiu.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '光鸭去净余毛、掏净肺管，斩去翅尖脚爪，沥干水分', 12),
  (@r, 2, '五香粉、陈皮末、生抽、姜蒜调成卤汁灌入鸭腹抹匀，牙签封住开口', 12),
  (@r, 3, '烧开水淋烫鸭身至皮紧绷收缩，挂起沥干', 10),
  (@r, 4, '白醋、麦芽糖、白酒与温水化成脆皮水，趁热均匀淋挂鸭皮', 8),
  (@r, 5, '悬挂通风处风干一夜至皮干爽如纸（急用吹风机冷风吹2小时）', 180),
  (@r, 6, '烤箱200℃烤约60分钟至枣红脆皮，中途翻面，出炉斩件淋汁', 70);

-- ========== 4. 清蒸鲈鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('清蒸鲈鱼', '考验食材与火候的粤菜试金石。活鲈鱼猛火足汽蒸八分钟，倒腥水铺姜葱丝，淋蒸鱼豉油浇滚油激香，肉若蒜瓣鲜甜尽出。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/yue-qingzhengluyu.jpg', 15, 12, 27, 1, 2, '粤菜', '经典,河鲜,清淡,广东名菜', 1, TRUE, 232, 180, 30, 6, 2, '水大滚才下锅、汽足才蒸得嫩；蒸出的腥水务必倒掉，豉油最后淋别早放，否则肉发老发咸。', '清鲜嫩滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鲈鱼', '1', '条(约600g)', TRUE, 1, '/api/ingredients/bianyu.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '4', '根', TRUE, 3, '/api/ingredients/xiaocong.jpg'),
  (@r, '蒸鱼豉油', '25', 'ml', TRUE, 4, '/api/ingredients/zhengyuchichou.jpg'),
  (@r, '盐', '2', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '料酒', '15', 'ml', FALSE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '食用油', '25', 'ml', FALSE, 7, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鲈鱼去鳞鳃内脏洗净，背脊两面各剞刀，抹薄盐与料酒腌10分钟', 12),
  (@r, 2, '盘底垫姜片和筷子架起鱼身，铺姜丝，水开上笼旺火蒸8分钟', 10),
  (@r, 3, '关火虚蒸1分钟取出，倒掉盘内腥水，拣去旧姜葱', 3),
  (@r, 4, '鱼身铺新鲜葱姜丝，沿盘淋入蒸鱼豉油', 2),
  (@r, 5, '食用油烧至冒烟浇在葱姜丝上激香即成', 1);

-- ========== 5. 白灼虾 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('白灼虾', '粤式鲜货最朴素的致敬。鲜活基围虾下葱姜滚水，只见蜷红便捞起，蘸姜葱豉油，虾肉弹牙带甜，讲究的正是鲜字与精准火候。', NULL, 10, 5, 15, 1, 3, '粤菜', '经典,海鲜,清淡,广东名菜', 1, TRUE, 128, 160, 33, 2, 2, '水要大滚、虾要鲜活，全部蜷红变硬即捞别迟疑；过一遍冷开水壳肉分离更好剥，灼久了肉质发粉。', '清鲜原味');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '基围虾', '500', 'g', TRUE, 1, '/api/ingredients/hexiaren.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '3', '根', TRUE, 3, '/api/ingredients/xiaocong.jpg'),
  (@r, '蒸鱼豉油', '30', 'ml', TRUE, 4, '/api/ingredients/zhengyuchichou.jpg'),
  (@r, '料酒', '20', 'ml', FALSE, 5, '/api/ingredients/liaojiu.jpg'),
  (@r, '食用油', '10', 'ml', FALSE, 6, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '基围虾剪去须脚、挑净虾线洗净沥干，姜切片、葱挽结', 8),
  (@r, 2, '小碗调蘸料：蒸鱼豉油加姜葱末，淋热油激香', 3),
  (@r, 3, '锅烧清水加姜片、葱结、料酒，大火烧至翻滚', 5),
  (@r, 4, '下虾灼至全部蜷曲转红约1分钟即捞出，过冷开水保持弹牙', 2),
  (@r, 5, '装盘配蘸料上桌', 1);

-- ========== 6. 干炒牛河 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('干炒牛河', '大排档师傅的看家绝活，镬气是命门。河粉干身不结块，牛肉滑油至嫩，旺火快炒不粘锅、不断碎、不糊底，盘底只见油不见汁。', NULL, 20, 12, 32, 3, 2, '粤菜', '经典,镬气,主食,广东名菜', 1, TRUE, 280, 550, 28, 22, 60, '河粉必先拨散干爽才不结团，镬要烧到冒烟再下料，全程猛火快颠；老抽只上色别放多，否则发黑发苦。', '咸香镬气');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '河粉', '400', 'g', TRUE, 1, '/api/ingredients/ganmifen.jpg'),
  (@r, '牛肉', '150', 'g', TRUE, 2, '/api/ingredients/niurou.jpg'),
  (@r, '绿豆芽', '100', 'g', TRUE, 3, '/api/ingredients/lvdouya.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '15', 'ml', TRUE, 5, '/api/ingredients/laochou.jpg'),
  (@r, '淀粉', '8', 'g', TRUE, 6, '/api/ingredients/dianfen.jpg'),
  (@r, '料酒', '10', 'ml', TRUE, 7, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '2', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '韭黄', '50', 'g', FALSE, 9, '/api/ingredients/qingsuan.jpg'),
  (@r, '洋葱', '40', 'g', FALSE, 10, '/api/ingredients/yangcong.jpg'),
  (@r, '小葱', '2', '根', FALSE, 11, '/api/ingredients/xiaocong.jpg'),
  (@r, '食用油', '40', 'ml', FALSE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肉逆纹切薄片，加生抽、老抽、料酒、淀粉和少许油抓匀腌15分钟', 15),
  (@r, 2, '河粉用手轻轻拨散务必干爽不结团，韭黄切段、洋葱切丝、葱切段', 6),
  (@r, 3, '宽锅烧油下牛肉滑炒至刚变色盛出，锅内留底油', 3),
  (@r, 4, '下洋葱丝、绿豆芽、河粉大火翻炒，淋生抽老抽上色，全程猛火', 4),
  (@r, 5, '回入牛肉与韭黄葱段，颠锅快炒收干，盘底见油不见汁即出锅', 2);

-- ========== 7. 腊味煲仔饭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('腊味煲仔饭', '瓦煲生米煮成熟饭的功夫。丝苗米配腊肠腊肉同焗，沿煲边淋油焏出锅巴，熄火焖透揭盖浇甜豉油拌开，饭干身、腊味润、锅巴脆。', NULL, 30, 40, 70, 2, 2, '粤菜', '经典,主食,腊味,广东名菜', 1, TRUE, 210, 640, 22, 24, 85, '米先浸再煮才夹生不糊，水高出米一指；沿煲边淋一圈油才焏得金黄锅巴，听到吱吱声且闻到焦香即关火焖透。', '咸香锅巴');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大米', '200', 'g', TRUE, 1, '/api/ingredients/dami.jpg'),
  (@r, '腊肠', '80', 'g', TRUE, 2, '/api/ingredients/lachang.jpg'),
  (@r, '腊肉', '60', 'g', TRUE, 3, '/api/ingredients/larou.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '5', 'ml', TRUE, 5, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '3', 'g', TRUE, 6, '/api/ingredients/baitang.jpg'),
  (@r, '清水', '300', 'ml', TRUE, 7, '/api/ingredients/qingshui.jpg'),
  (@r, '菜心', '150', 'g', FALSE, 8, '/api/ingredients/baicai.jpg'),
  (@r, '鸡蛋', '1', '个', FALSE, 9, '/api/ingredients/jidan.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 10, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', FALSE, 11, '/api/ingredients/xiaocong.jpg'),
  (@r, '芝麻香油', '8', 'ml', FALSE, 12, '/api/ingredients/xiangyou.jpg'),
  (@r, '食用油', '15', 'ml', FALSE, 13, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大米洗净浸30分钟沥干，腊肠腊肉斜切薄片，菜心焯熟，姜切丝', 30),
  (@r, 2, '煲内米加水（高出米一指），中火煮至收水见蟹眼孔', 12),
  (@r, 3, '铺上腊味放姜丝，盖盖转小火焗15分钟', 15),
  (@r, 4, '沿煲边淋一圈食用油，大火焏2分钟转中火焏至出锅巴（听到吱吱声）', 6),
  (@r, 5, '关火焖10分钟，调甜豉油淋面，摆菜心窝蛋拌匀上桌', 10);

-- ========== 8. 豉油皇炒面 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('豉油皇炒面', '把最寻常的酱油炒出皇者气。碱水面先蒸散水汽，旺火热镬下葱姜芽菜，面少翻多抖煎出香，沿镬边淋豉油皇焦化，干身爽滑油而不腻。', NULL, 15, 12, 27, 2, 2, '粤菜', '经典,主食,镬气,广东名菜', 1, TRUE, 251, 510, 16, 18, 70, '面先蒸后炒去水汽才干身不粘；豉油皇沿滚烫镬边淋下才能焦香出镬气，别一股脑倒面中间，会发咸结块。', '咸香镬气');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '碱水面', '300', 'g', TRUE, 1, '/api/ingredients/jianshuimian.jpg'),
  (@r, '绿豆芽', '80', 'g', TRUE, 2, '/api/ingredients/lvdouya.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 3, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 4, '/api/ingredients/laochou.jpg'),
  (@r, '白糖', '3', 'g', TRUE, 5, '/api/ingredients/baitang.jpg'),
  (@r, '小葱', '3', '根', FALSE, 6, '/api/ingredients/xiaocong.jpg'),
  (@r, '韭黄', '40', 'g', FALSE, 7, '/api/ingredients/qingsuan.jpg'),
  (@r, '鸡蛋', '2', '个', FALSE, 8, '/api/ingredients/jidan.jpg'),
  (@r, '芝麻香油', '5', 'ml', FALSE, 9, '/api/ingredients/xiangyou.jpg'),
  (@r, '食用油', '30', 'ml', FALSE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '碱水面抖散铺盘，蒸锅大火蒸8分钟取出拨松去掉多余水分', 12),
  (@r, 2, '调豉油皇：生抽、老抽、糖加少许高汤或水化开', 2),
  (@r, 3, '热镬下油倒入蛋液炒散盛出', 2),
  (@r, 4, '下绿豆芽、葱姜爆香，入蒸好的面大火少翻多抖煎炒', 4),
  (@r, 5, '沿镬边淋入豉油皇，回蛋和韭黄快速炒匀至干身上色出锅', 3);

-- ========== 9. 艇仔粥 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('艇仔粥', '昔日珠江船家的水上早味。绵滑白粥底滚入现切鲩鱼片、河虾、叉烧、浮皮与油条，撒花生蛋丝葱花，一碗尽纳河海鲜味，鲜热绵稠。', NULL, 30, 90, 120, 2, 4, '粤菜', '经典,粥品,小吃,广东名菜', 1, TRUE, 175, 330, 22, 9, 40, '生料全放碗底，靠重新烧至大滚的粥底趁滚烫冲下去烫熟，鱼片虾才嫩；粥底要熬到开花绵滑，忌清汤寡水。', '鲜甜绵滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大米', '100', 'g', TRUE, 1, '/api/ingredients/dami.jpg'),
  (@r, '草鱼', '200', 'g', TRUE, 2, '/api/ingredients/caoyu.jpg'),
  (@r, '河虾仁', '100', 'g', TRUE, 3, '/api/ingredients/hexiaren.jpg'),
  (@r, '盐', '4', 'g', TRUE, 4, '/api/ingredients/yan.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 5, '/api/ingredients/qingshui.jpg'),
  (@r, '叉烧肉', '80', 'g', FALSE, 6, '/api/ingredients/wuhuarou.jpg'),
  (@r, '油条', '1', '根', FALSE, 7, '/api/ingredients/paisan.jpg'),
  (@r, '炸猪皮', '30', 'g', FALSE, 8, '/api/ingredients/wuhuarou.jpg'),
  (@r, '花生', '30', 'g', FALSE, 9, '/api/ingredients/huasheng.jpg'),
  (@r, '鸡蛋', '1', '个', FALSE, 10, '/api/ingredients/jidan.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 11, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '3', '根', FALSE, 12, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 13, '/api/ingredients/xiangcai.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 14, '/api/ingredients/baihujiaofen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大米洗净加少许油和盐拌匀腌半小时，加清水大火煮开转小火熬90分钟成绵滑粥底，中途搅防糊', 95),
  (@r, 2, '草鱼片下两片净肉斜切薄片，用少许盐和姜丝拌匀，河虾仁洗净', 12),
  (@r, 3, '叉烧、油条、炸猪皮切丝，花生碾碎，蛋煎成蛋皮切丝，姜切丝葱切花', 12),
  (@r, 4, '取滚粥入碗，碗底码生鱼片、虾仁、叉烧丝、猪皮丝、油条丝、蛋丝花生姜丝', 3),
  (@r, 5, '另把粥底烧至大滚趁滚烫冲入碗中烫熟鱼片虾，撒葱花香菜白胡椒粉即食', 5);

-- ========== 10. 及第粥 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('及第粥', '广州老火粥的头名，取“状元及第”吉意。绵粥底现滚猪肝片、猪腰片、猪肉丸三鲜，靠粥的余温烫至刚熟，粉嫩鲜甜，早茶夜宵两相宜。', NULL, 20, 90, 110, 2, 4, '粤菜', '经典,粥品,小吃,广东名菜', 1, TRUE, 265, 270, 18, 6, 35, '猪腰务必片去白色臊腺并泡洗干净否则腥；内脏只在滚粥里烫至刚熟，久煮发硬失粉嫩，粥底先要熬绵。', '鲜甜绵滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '大米', '100', 'g', TRUE, 1, '/api/ingredients/dami.jpg'),
  (@r, '猪肝', '80', 'g', TRUE, 2, '/api/ingredients/zhugan.jpg'),
  (@r, '猪腰', '60', 'g', TRUE, 3, '/api/ingredients/zhuyao.jpg'),
  (@r, '猪瘦肉', '60', 'g', TRUE, 4, '/api/ingredients/zhushourou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '料酒', '10', 'ml', TRUE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 7, '/api/ingredients/qingshui.jpg'),
  (@r, '猪肉丸', '100', 'g', FALSE, 8, '/api/ingredients/zhuroumo.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 9, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '3', '根', FALSE, 10, '/api/ingredients/xiaocong.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 11, '/api/ingredients/xiangcai.jpg'),
  (@r, '白胡椒粉', '2', 'g', FALSE, 12, '/api/ingredients/baihujiaofen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '大米洗净加油盐腌半小时，加清水大火煮沸转小火熬90分钟至粥绵，期间不时搅防糊', 95),
  (@r, 2, '猪肝猪腰切薄片、猪腰去臊腺泡洗，加料酒姜丝腌，瘦肉切薄片', 12),
  (@r, 3, '粥烧至滚沸先下猪肉丸煮2分钟', 3),
  (@r, 4, '转大火滚粥下猪肝猪腰肉片快速搅散烫至变色刚熟', 2),
  (@r, 5, '调味盐、白胡椒粉，撒葱花香菜即成', 1);

-- ========== 11. 蒜蓉粉丝蒸扇贝 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('蒜蓉粉丝蒸扇贝', '海鲜排档的蒸锅台柱。粉丝铺底吸汁，扇贝肉卧蒜蓉，猛火汽蒸几分钟贝肉饱满弹牙，最后葱丝热油一激，蒜香咸鲜全渗进粉丝里。', NULL, 20, 8, 28, 1, 3, '粤菜', '经典,海鲜,蒸菜,广东名菜', 1, TRUE, 175, 205, 16, 9, 15, '蒜蓉一半温油炸成金蒜再拌生蒜，金银蒜最香；扇贝别蒸过火，贝肉一收即出，汽要足时间要短。', '蒜香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '扇贝', '6', '只', TRUE, 1, '/api/ingredients/baoyu.jpg'),
  (@r, '粉丝', '60', 'g', TRUE, 2, '/api/ingredients/hongshufen.jpg'),
  (@r, '大蒜', '40', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '3', '根', TRUE, 4, '/api/ingredients/xiaocong.jpg'),
  (@r, '蒸鱼豉油', '20', 'ml', TRUE, 5, '/api/ingredients/zhengyuchichou.jpg'),
  (@r, '生抽', '10', 'ml', FALSE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '食用油', '25', 'ml', FALSE, 7, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '粉丝温水泡软剪段铺盘底，扇贝刷洗取肉去砂袋洗净摆回壳上', 15),
  (@r, 2, '大蒜剁蓉，温油小火炒至金黄出香成金蒜，拌入少许生抽调味', 6),
  (@r, 3, '每只扇贝肉上铺一层蒜蓉', 2),
  (@r, 4, '水开上笼旺火汽蒸5分钟至贝肉饱满', 5),
  (@r, 5, '淋蒸鱼豉油撒葱丝，滚油浇下激香即食', 1);

-- ========== 12. 菠萝咕噜肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('菠萝咕噜肉', '粤菜馆的甜酸担当。猪里脊裹蛋液拍粉炸至外酥，回锅裹上番茄糖醋汁，配菠萝块青红椒，酸甜开胃外脆里嫩，是小朋友也爱的老广味。', NULL, 20, 15, 35, 2, 3, '粤菜', '经典,甜酸,猪肉,广东名菜', 1, TRUE, 198, 460, 30, 22, 35, '肉块要复炸才酥而持久；糖醋汁熬浓挂勺再下肉快翻，炒久了外壳吸汁变软就失了脆；菠萝最后放保清香。', '酸甜酥脆');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪里脊', '300', 'g', TRUE, 1, '/api/ingredients/zhuliji.jpg'),
  (@r, '菠萝', '200', 'g', TRUE, 2, '/api/ingredients/nangua.jpg'),
  (@r, '鸡蛋', '1', '个', TRUE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '淀粉', '40', 'g', TRUE, 4, '/api/ingredients/dianfen.jpg'),
  (@r, '番茄酱', '40', 'g', TRUE, 5, '/api/ingredients/honglajiao.jpg'),
  (@r, '白糖', '30', 'g', TRUE, 6, '/api/ingredients/baitang.jpg'),
  (@r, '白醋', '20', 'ml', TRUE, 7, '/api/ingredients/baicu.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '2', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '面粉', '30', 'g', FALSE, 10, '/api/ingredients/mianfen.jpg'),
  (@r, '青辣椒', '1', '个', FALSE, 11, '/api/ingredients/qinglajiao.jpg'),
  (@r, '红辣椒', '1', '个', FALSE, 12, '/api/ingredients/honglajiao.jpg'),
  (@r, '食用油', '300', 'ml', FALSE, 13, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪里脊切厚片改刀成块，加盐、少许生抽、蛋液抓匀，拍干淀粉和面粉', 10),
  (@r, 2, '菠萝切块、青红椒切菱形片备用', 6),
  (@r, 3, '油烧六成热肉块逐个下锅炸至定型微黄捞出，升油温复炸至金黄酥脆', 8),
  (@r, 4, '锅留底油下番茄酱、糖、白醋、生抽和少许水煮开成糖醋汁勾薄芡', 4),
  (@r, 5, '倒入炸肉菠萝青红椒快速翻炒裹匀酱汁出锅', 2);

-- ========== 13. 客家盐焗鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('客家盐焗鸡', '客家山区的传世咸香。整鸡抹沙姜五香，埋进炒烫的粗海盐里小火焗熟，借盐的余温逼熟锁汁，皮爽骨香咸鲜入骨，撕开热气腾腾。', NULL, 20, 60, 80, 3, 4, '粤菜', '经典,客家,鸡肉,广东名菜', 1, TRUE, 236, 310, 36, 18, 1, '鸡身必须彻底擦干否则焗不香反腥；粗盐要炒到发黄滚烫再埋，全程小火靠盐的蓄热焗熟，急火会糊盐苦鸡。', '咸香骨软');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '三黄鸡', '1', '只(约1100g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '粗盐', '1500', 'g', TRUE, 2, '/api/ingredients/yan.jpg'),
  (@r, '沙姜粉', '5', 'g', TRUE, 3, '/api/ingredients/shannai.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 4, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '5', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '五香粉', '3', 'g', FALSE, 6, '/api/ingredients/bajiao.jpg'),
  (@r, '生姜', '15', 'g', FALSE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', FALSE, 8, '/api/ingredients/xiaocong.jpg'),
  (@r, '芝麻香油', '8', 'ml', FALSE, 9, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '三黄鸡洗净彻底抹干水分去鸡屁股，腹腔用厨房纸擦干（务必干身否则不香）', 10),
  (@r, 2, '沙姜粉、五香粉、少许盐与料酒调匀，里外抹遍鸡身腌30分钟', 30),
  (@r, 3, '炒锅下粗盐加姜葱炒至发黄滚烫', 10),
  (@r, 4, '砂锅底铺厚盐放鸡（可包纱纸），四周顶部盖满热盐封口', 5),
  (@r, 5, '小火焗约40分钟至熟，敲开盐壳取出抖净余盐，撕件或斩件装盘', 40);

-- ========== 14. 客家酿豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('客家酿豆腐', '客家南迁不忘中原饺子的乡愁。卤水豆腐中间酿入拌了香菇虾米的猪肉馅，先煎至两面金黄再砂锅焖煮入味，豆腐弹嫩肉馅鲜香汁浓下饭。', NULL, 25, 20, 45, 2, 3, '粤菜', '经典,客家,豆腐,广东名菜', 1, TRUE, 163, 310, 24, 20, 8, '选结实的老豆腐（卤水豆腐）才酿得住不散；挖坑别挖穿，肉馅搅上劲才饱满；馅面朝下先煎定型再翻。', '咸鲜浓郁');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '水豆腐', '400', 'g', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '猪前腿肉馅', '200', 'g', TRUE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '小葱', '3', '根', TRUE, 3, '/api/ingredients/xiaocong.jpg'),
  (@r, '生抽', '25', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '淀粉', '10', 'g', TRUE, 5, '/api/ingredients/dianfen.jpg'),
  (@r, '干香菇', '15', 'g', FALSE, 6, '/api/ingredients/ganxianggu.jpg'),
  (@r, '虾皮', '10', 'g', FALSE, 7, '/api/ingredients/xiapi.jpg'),
  (@r, '生姜', '10', 'g', FALSE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '老抽', '5', 'ml', FALSE, 9, '/api/ingredients/laochou.jpg'),
  (@r, '蚝油', '10', 'g', FALSE, 10, '/api/ingredients/haoyou.jpg'),
  (@r, '食用油', '30', 'ml', FALSE, 11, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '干香菇泡发切末、虾皮泡软，与猪肉馅、姜末、少许生抽、淀粉同搅上劲成馅', 12),
  (@r, 2, '豆腐切麻将块中间挖小坑（挖深不挖穿），填入肉馅抹平', 12),
  (@r, 3, '平底锅多放些油馅面朝下中火煎至金黄，翻面把豆腐四面煎香', 10),
  (@r, 4, '转入砂锅加生抽、老抽、蚝油和少许水，盖盖中小火焖煮8分钟入味', 8),
  (@r, 5, '收汁至浓撒葱花，连砂锅上桌', 2);

-- ========== 15. 梅菜扣肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('梅菜扣肉', '惠州梅菜与五花肉的相逢。带皮五花肉煮炸上色切薄片，与炒香的梅菜相间码碗，长时间蒸至肥油尽入菜中，肉烂不散梅菜咸甜回甘。', NULL, 40, 100, 140, 3, 6, '粤菜', '经典,客家,猪肉,广东名菜', 1, TRUE, 147, 490, 30, 38, 8, '炸肉皮防溅务必加盖，炸后泡冷水才起虎皮；梅菜要反复淘洗去沙并炒透才香；蒸足一个半钟肥肉化于菜中才不腻。', '咸甜软糯');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '750', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '梅菜', '150', 'g', TRUE, 2, '/api/ingredients/gandoujiao.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '生抽', '30', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '15', 'ml', TRUE, 6, '/api/ingredients/laochou.jpg'),
  (@r, '冰糖', '20', 'g', TRUE, 7, '/api/ingredients/bingtang.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '3', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '五香粉', '3', 'g', FALSE, 10, '/api/ingredients/bajiao.jpg'),
  (@r, '干红辣椒', '5', 'g', FALSE, 11, '/api/ingredients/ganlajiao.jpg'),
  (@r, '食用油', '30', 'ml', FALSE, 12, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉冷水下锅加姜葱料酒煮20分钟至筷子能插入，捞出沥干', 25),
  (@r, 2, '肉皮吸干抹一层老抽，热油炸至皮起泡上色（防溅加盖），捞出泡冷水10分钟起虎皮', 18),
  (@r, 3, '梅菜反复洗净挤干切碎，少油加姜蒜、生抽、冰糖炒香出味', 10),
  (@r, 4, '肉切半厘米厚片，加生抽、老抽、五香粉、料酒拌匀', 10),
  (@r, 5, '肉皮朝下码入碗铺上炒好的梅菜倒余汁，上蒸锅大火蒸1小时30分至软烂', 95),
  (@r, 6, '取出翻扣入盘淋上倒出的汁即成', 2);

-- ========== 16. 胡椒猪肚鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('胡椒猪肚鸡', '冬日暖胃的老火靓汤。整猪肚塞鸡块，加拍破的白胡椒与姜煲足两小时，汤色奶白胡椒辛香窜鼻，猪肚爽脆鸡肉鲜甜，先喝汤再剪件蘸料。', NULL, 30, 120, 150, 2, 4, '粤菜', '经典,汤羹,暖身,广东名菜', 1, TRUE, 230, 300, 30, 18, 4, '猪肚用盐、面粉、料酒反复揉搓去黏液焯水刮净白膜才不腥；白胡椒要拍破才出辛香；大火滚煲汤才奶白。', '辛香醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪肚', '1', '个(约700g)', TRUE, 1, '/api/ingredients/shuzhudu.jpg'),
  (@r, '老母鸡', '500', 'g', TRUE, 2, '/api/ingredients/tuji.jpg'),
  (@r, '白胡椒粒', '15', 'g', TRUE, 3, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 5, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '6', 'g', TRUE, 6, '/api/ingredients/yan.jpg'),
  (@r, '清水', '2500', 'ml', TRUE, 7, '/api/ingredients/qingshui.jpg'),
  (@r, '枸杞', '15', 'g', FALSE, 8, '/api/ingredients/gouqi.jpg'),
  (@r, '红枣', '40', 'g', FALSE, 9, '/api/ingredients/hongzao.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪肚反复用盐、面粉和料酒揉搓洗净黏液，焯水刮净白膜', 20),
  (@r, 2, '老母鸡斩件焯水去血沫，白胡椒拍破，姜切片', 10),
  (@r, 3, '鸡块塞入猪肚内用牙签封口，与胡椒姜片同入砂锅加清水', 10),
  (@r, 4, '大火烧开撇沫转小火煲2小时至汤色奶白、猪肚软韧', 120),
  (@r, 5, '取出猪肚剪成条回锅，加红枣枸杞再煲10分钟，起锅加盐调味', 10);

-- ========== 17. 姜撞奶 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('姜撞奶', '番禺沙湾的甜蜜魔法。老姜磨汁挤进碗底，全脂牛奶煮至七八十度从高处一冲撞入，静置数分钟凝成嫩滑奶冻，姜香辛辣与奶甜交融。', NULL, 15, 14, 29, 2, 2, '粤菜', '经典,甜品,小吃,广东名菜', 1, TRUE, 172, 340, 17, 18, 28, '牛奶温度是成败关键，约70-80℃最宜，煮沸或太凉都凝不住；从高处一气冲撞不搅动，盖住静置五分钟即成冻。', '姜香嫩滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '牛奶', '500', 'ml', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '老姜', '50', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '白糖', '25', 'g', TRUE, 3, '/api/ingredients/baitang.jpg'),
  (@r, '糖桂花', '8', 'g', FALSE, 4, '/api/ingredients/guihuatang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '老姜去皮磨成姜蓉，纱布包裹挤净姜汁分入两只碗底', 10),
  (@r, 2, '全脂牛奶加白糖小火煮至微冒泡约七八十度，切勿煮沸', 8),
  (@r, 3, '趁热从距碗约二十厘米高处把牛奶一气冲撞入姜汁碗中，迅速盖住', 1),
  (@r, 4, '静置5分钟不要搅动，凝成嫩滑奶冻即可食用', 5);

-- ========== 18. 陈皮红豆沙 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('陈皮红豆沙', '粤式糖水的暖心收尾。新会陈皮浸软刮瓤与红豆同煲至豆壳尽化绵沙起沙，冰糖调味，一碗红润浓稠，陈皮甘香解腻，冷食热食皆宜。', NULL, 30, 120, 150, 1, 4, '粤菜', '经典,甜品,糖水,广东名菜', 1, TRUE, 128, 280, 12, 1, 55, '陈皮务必泡软刮去内层白瓤，否则发苦；豆要煲到开花再用勺背碾擦才起沙，加冰糖后勤搅防粘底糊锅。', '甘香绵沙');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '红豆', '200', 'g', TRUE, 1, '/api/ingredients/xuedou.jpg'),
  (@r, '陈皮', '5', 'g', TRUE, 2, '/api/ingredients/luobogan.jpg'),
  (@r, '冰糖', '80', 'g', TRUE, 3, '/api/ingredients/bingtang.jpg'),
  (@r, '清水', '1200', 'ml', TRUE, 4, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '红豆洗净清水浸泡2小时，陈皮温水泡软刮去内层白瓤剪丝（去苦）', 20),
  (@r, 2, '红豆与陈皮丝同入锅加清水大火煮开转小火煲1小时至豆软开花', 60),
  (@r, 3, '用勺背沿锅碾擦豆粒使其起沙（可留些颗粒）', 10),
  (@r, 4, '加冰糖续煮20分钟至浓稠挂勺，期间勤搅防粘底', 20),
  (@r, 5, '盛碗，可作热糖水或冷藏成冻食用', 2);
