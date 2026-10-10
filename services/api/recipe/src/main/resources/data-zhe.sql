-- 由 seed/recipes-zhe.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 浙菜，共 16 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 东坡肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('东坡肉', '杭州为纪念苏东坡而得名的头道菜，慢着火、少着水，柴火罨法烹至熟。肉方红亮颤巍巍，肥而不腻，黄酒香醇厚绵长。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-dongporou.jpg', 25, 130, 155, 2, 4, '浙菜', '经典,宴客,猪肉,浙菜名菜', 1, TRUE, 222, 530, 26, 45, 8, '关键全在火候，微火到汤面只起菊花小泡，火大肉散；最后那一步蒸不能省。', '酒香咸甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '800', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '绍兴黄酒', '250', 'ml', TRUE, 2, '/api/ingredients/huangjiu.jpg'),
  (@r, '清水', '250', 'ml', FALSE, 3, '/api/ingredients/qingshui.jpg'),
  (@r, '生抽', '60', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '15', 'ml', TRUE, 5, '/api/ingredients/laochou.jpg'),
  (@r, '冰糖', '30', 'g', TRUE, 6, '/api/ingredients/bingtang.jpg'),
  (@r, '生姜', '50', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '6', '根', TRUE, 8, '/api/ingredients/dacong.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉切成4厘米方块，冷水下锅大火煮5分钟，捞出洗净', 10),
  (@r, 2, '小葱挽成把与厚姜片铺满砂锅底，肉皮朝下码在葱姜上', 5),
  (@r, 3, '下冰糖、生抽、老抽与清水，大火烧开后撇净浮沫', 3),
  (@r, 4, '盖严锅盖转微火焖90分钟，中途不揭盖不翻动', 90),
  (@r, 5, '翻至肉皮朝上，码入浅碗淋原汁，上笼大火蒸20分钟', 20);

-- ========== 2. 西湖醋鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('西湖醋鱼', '西湖楼外楼的百年名菜，取清湖水养草鱼，不沾一滴油只用水汆。浇一层醋椒芡汁，肉质嫩滑带蟹味，酸甜清鲜。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-xihu-cuyu.jpg', 15, 10, 25, 3, 2, '浙菜', '经典,宴客,河鲜,浙菜名菜', 1, TRUE, 112, 220, 33, 6, 5, '草鱼先饿养去尽土腥，汆时水似开非开；芡要浓到挂勺才裹得住鱼身。', '酸甜鲜嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '草鱼', '1', '条(约400g)', TRUE, 1, '/api/ingredients/caoyu.jpg'),
  (@r, '清水', '600', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '盐', '3', 'g', TRUE, 3, '/api/ingredients/yan.jpg'),
  (@r, '香醋', '40', 'ml', TRUE, 4, '/api/ingredients/xiangcu.jpg'),
  (@r, '酱油', '20', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '绍兴黄酒', '15', 'ml', TRUE, 6, '/api/ingredients/huangjiu.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '淀粉', '15', 'g', TRUE, 8, '/api/ingredients/dianfen.jpg'),
  (@r, '白胡椒粉', '1', 'g', TRUE, 9, '/api/ingredients/baihujiaofen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '草鱼宰杀去鳞鳃，从背部开片成相连两块，鱼肉面剞花刀', 8),
  (@r, 2, '锅中清水加盐烧至似开非开，鱼皮朝下大火汆3分钟', 4),
  (@r, 3, '捞出装盘，滗出鱼汤150毫升倒入净锅', 1),
  (@r, 4, '加姜末、香醋、酱油、黄酒烧开，水淀粉勾成浓芡', 3),
  (@r, 5, '撒白胡椒粉，把醋椒芡汁均匀浇遍鱼身即成', 1);

-- ========== 3. 龙井虾仁 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('龙井虾仁', '杭州春天茶宴上的名菜，明前龙井配现剥河虾仁，不见一丝酱油着色。虾仁玉白莹润，茶叶碧绿清翠，鲜得极其雅致。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-longjing-xiaren.jpg', 25, 15, 40, 2, 2, '浙菜', '经典,时令,河鲜,浙菜名菜', 1, TRUE, 304, 250, 30, 12, 4, '滑油时下锅即离火，靠余温焖熟才嫩；茶叶取茶汤入炒，久煮则苦涩。', '清鲜茶香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '河虾仁', '250', 'g', TRUE, 1, '/api/ingredients/hexiaren.jpg'),
  (@r, '茶叶', '3', 'g', TRUE, 2, '/api/ingredients/lucha.jpg'),
  (@r, '鸡蛋清', '1', '个', TRUE, 3, '/api/ingredients/jidanqing.jpg'),
  (@r, '淀粉', '8', 'g', TRUE, 4, '/api/ingredients/dianfen.jpg'),
  (@r, '盐', '2', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '清水', '100', 'ml', TRUE, 6, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 7, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '河虾仁冲洗沥干，撒盐腌10分钟后滗去水分', 12),
  (@r, 2, '虾仁用鸡蛋清和淀粉拌匀上浆，冷藏静置30分钟', 30),
  (@r, 3, '茶叶用100毫升沸水冲泡5分钟，滗出25毫升茶汤', 5),
  (@r, 4, '锅下食用油烧至四成热，离火下虾仁拨散泡至变色捞出', 3),
  (@r, 5, '余油烧至六成热回下虾仁，烹入茶汤大火快炒10秒装盘', 1);

-- ========== 4. 宋嫂鱼羹 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('宋嫂鱼羹', '南宋御宴传下的名羹，相传淳熙皇帝游西湖尝后大加赞叹。桂鱼肉嫩赛蟹，火腿笋蕈丝羹匀，醋香胡椒气扑鼻。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-songsao-yugeng.jpg', 30, 20, 50, 3, 4, '浙菜', '经典,宴客,汤羹,浙菜名菜', 1, TRUE, 204, 140, 15, 5, 8, '羹要分次勾芡，浓到能挂住鱼丝；白胡椒粉与香醋最后下锅香气才足。', '酸香滑润');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '桂鱼', '1', '条(约500g)', TRUE, 1, '/api/ingredients/guiyu.jpg'),
  (@r, '火腿', '30', 'g', TRUE, 2, '/api/ingredients/huotui.jpg'),
  (@r, '冬笋', '80', 'g', TRUE, 3, '/api/ingredients/dongsun.jpg'),
  (@r, '干香菇', '20', 'g', TRUE, 4, '/api/ingredients/ganxianggu.jpg'),
  (@r, '高汤', '800', 'ml', TRUE, 5, '/api/ingredients/gaotang.jpg'),
  (@r, '小葱', '3', '根', TRUE, 6, '/api/ingredients/xiaocong.jpg'),
  (@r, '绍兴黄酒', '15', 'ml', TRUE, 7, '/api/ingredients/huangjiu.jpg'),
  (@r, '淀粉', '20', 'g', TRUE, 8, '/api/ingredients/dianfen.jpg'),
  (@r, '盐', '4', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '2', 'g', TRUE, 10, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '香醋', '10', 'ml', TRUE, 11, '/api/ingredients/xiangcu.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '桂鱼去鳞鳃与葱段同蒸，大火8分钟后取出撕成细丝', 10),
  (@r, 2, '火腿、冬笋、水发香菇分别切成细丝', 6),
  (@r, 3, '高汤烧开后下鱼丝与三丝，烹黄酒小火煮3分钟', 4),
  (@r, 4, '加盐与白胡椒粉，分次淋水淀粉勾成浓羹', 3),
  (@r, 5, '盛碗，淋香醋撒余下胡椒粉，趁热上桌', 1);

-- ========== 5. 干炸响铃 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('干炸响铃', '杭州名菜因声得名，腐皮卷肉末切段落油锅，炸时叮当作响。外壳酥薄一碰即碎，内里咸鲜松软，最宜下酒。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-ganzha-xiangling.jpg', 20, 10, 30, 2, 4, '浙菜', '经典,宴客,小吃,浙菜名菜', 1, TRUE, 238, 290, 9, 22, 14, '腐皮只许喷潮不许泡透，泡透就炸不酥；复炸半分钟逼油才脆响。', '酥香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '腐皮', '8', '张(约15cm见方)', TRUE, 1, '/api/ingredients/doufu.jpg'),
  (@r, '猪肉末', '150', 'g', TRUE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '鸡蛋', '1', '个', TRUE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '淀粉', '10', 'g', TRUE, 4, '/api/ingredients/dianfen.jpg'),
  (@r, '绍兴黄酒', '10', 'ml', TRUE, 5, '/api/ingredients/huangjiu.jpg'),
  (@r, '盐', '3', 'g', TRUE, 6, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '1', 'g', TRUE, 7, '/api/ingredients/baihujiaofen.jpg'),
  (@r, '食用油', '300', 'ml', TRUE, 8, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪肉末加盐、白胡椒粉与黄酒10毫升拌匀成稀馅', 3),
  (@r, 2, '清水喷润腐皮回软，摊平抹上薄薄一层肉馅', 5),
  (@r, 3, '卷成指头粗长条切4厘米段，切口抹蛋液黏合', 5),
  (@r, 4, '油烧至六成热转中火，下腐皮卷炸至金黄浮起', 5),
  (@r, 5, '升高油温复炸半分钟至外壳酥脆，捞出沥油装盘', 1);

-- ========== 6. 油焖春笋 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('油焖春笋', '江南春天的第一口鲜，天目山春笋破土即采。重油宽糖加盖焖透，笋块酱红油亮，咬下去脆嫩咸甜带酱香。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-youmen-chunsun.jpg', 10, 12, 22, 1, 3, '浙菜', '时令,家常,竹笋,浙菜名菜', 1, TRUE, 227, 190, 4, 13, 15, '笋一定要拍裂再焖，断口才吸饱酱汁；收汁收到酱色发亮裹壳不见汤。', '咸甜鲜嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '春笋', '400', 'g', TRUE, 1, '/api/ingredients/dongsun.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 2, '/api/ingredients/shiyongyou.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 3, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '10', 'g', TRUE, 4, '/api/ingredients/baitang.jpg'),
  (@r, '清水', '150', 'ml', TRUE, 5, '/api/ingredients/qingshui.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 6, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '春笋剥壳去老根，刀拍松后切成4厘米段', 5),
  (@r, 2, '油烧至六成热下笋块，中火煸2分钟至边缘微焦', 3),
  (@r, 3, '加生抽、白糖与清水150毫升，翻匀加盖焖5分钟', 5),
  (@r, 4, '转大火收汁至酱色油亮挂在笋上', 3),
  (@r, 5, '淋香油翻匀，装盘上桌', 1);

-- ========== 7. 雪菜大汤黄鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('雪菜大汤黄鱼', '宁波人的待客头菜，大黄鱼配雪里蕻咸菜熬出奶白大汤。汤浓鱼嫩，雪菜脆爽带咸鲜，一碗下去鲜得眉毛掉落。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-xuecai-huangyu.jpg', 15, 15, 30, 2, 4, '浙菜', '家常,海鲜,汤羹,浙菜名菜', 1, TRUE, 292, 220, 24, 10, 5, '汤要奶白必须冲沸水再大火滚足；雪菜先冲水挤干定咸度再下锅。', '咸鲜醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '黄鱼', '1', '条(约600g)', TRUE, 1, '/api/ingredients/bianyu.jpg'),
  (@r, '雪菜', '80', 'g', TRUE, 2, '/api/ingredients/suandoujiao.jpg'),
  (@r, '豆腐', '300', 'g', TRUE, 3, '/api/ingredients/doufu.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '3', '根', TRUE, 5, '/api/ingredients/xiaocong.jpg'),
  (@r, '料酒', '15', 'ml', TRUE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '4', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '15', 'ml', TRUE, 8, '/api/ingredients/shiyongyou.jpg'),
  (@r, '白胡椒粉', '1', 'g', TRUE, 9, '/api/ingredients/baihujiaofen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '黄鱼去鳞鳃与内脏，两面各剞两刀，抹盐和料酒腌10分钟', 12),
  (@r, 2, '雪菜冲洗挤干切碎，豆腐切成2厘米方块', 5),
  (@r, 3, '锅下油烧热，中火煸香雪菜与姜片2分钟', 2),
  (@r, 4, '冲入沸水1000毫升，下黄鱼大火滚10分钟至汤色奶白', 10),
  (@r, 5, '下豆腐与葱段再煮3分钟，撒白胡椒粉调味出锅', 3);

-- ========== 8. 蜜汁火方 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('蜜汁火方', '金华火腿上的甜咸绝唱，取上方精肉蜜糖慢蒸。火方块方镶着金边，咸香中透出蜜甜，是浙宴压轴的功夫大菜。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-mizhi-huofang.jpg', 20, 85, 105, 3, 3, '浙菜', '经典,宴客,火腿,浙菜名菜', 1, TRUE, 276, 400, 26, 21, 22, '火腿生咸，泡水两小时不能省；收蜜汁要守在锅边，糖汁一糊满盘皆毁。', '咸甜蜜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '火腿', '300', 'g', TRUE, 1, '/api/ingredients/huotui.jpg'),
  (@r, '冰糖', '60', 'g', TRUE, 2, '/api/ingredients/bingtang.jpg'),
  (@r, '蜂蜜', '40', 'ml', TRUE, 3, '/api/ingredients/mayatang.jpg'),
  (@r, '绍兴黄酒', '25', 'ml', TRUE, 4, '/api/ingredients/huangjiu.jpg'),
  (@r, '清水', '50', 'ml', TRUE, 5, '/api/ingredients/qingshui.jpg'),
  (@r, '红枣', '3', '颗', FALSE, 6, '/api/ingredients/hongzao.jpg'),
  (@r, '枸杞', '10', 'g', FALSE, 7, '/api/ingredients/gouqi.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '火腿切麻将块剞十字花刀，温水浸泡两小时', 120),
  (@r, 2, '火腿皮朝下码入碗，加冰糖、黄酒与清水', 3),
  (@r, 3, '上笼大火蒸60分钟至火腿软透', 60),
  (@r, 4, '滗出原汁与蜂蜜同锅，小火熬至浓亮挂勺', 6),
  (@r, 5, '火方翻扣盘中，淋蜜汁，蜜枣枸杞围边', 2);

-- ========== 9. 片儿川 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('片儿川', '杭州面馆百年头牌，雪菜、笋片、瘦肉片三样滚刀川入汤面。汤色清亮面身滑韧，雪菜鲜笋脆肉片嫩，一碗见功夫。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-pianerchuan.jpg', 15, 10, 25, 1, 2, '浙菜', '经典,主食,面食,浙菜名菜', 1, TRUE, 103, 310, 10, 8, 50, '雪菜咸淡不一，先冲水挤干再尝汤补盐；肉片上浆才滑嫩。', '鲜香爽滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '细面条', '250', 'g', TRUE, 1, '/api/ingredients/ximiantiao.jpg'),
  (@r, '猪里脊', '100', 'g', TRUE, 2, '/api/ingredients/zhuliji.jpg'),
  (@r, '雪菜', '50', 'g', TRUE, 3, '/api/ingredients/suandoujiao.jpg'),
  (@r, '春笋', '100', 'g', TRUE, 4, '/api/ingredients/dongsun.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', FALSE, 6, '/api/ingredients/xiaocong.jpg'),
  (@r, '食用油', '15', 'ml', TRUE, 7, '/api/ingredients/shiyongyou.jpg'),
  (@r, '绍兴黄酒', '10', 'ml', TRUE, 8, '/api/ingredients/huangjiu.jpg'),
  (@r, '淀粉', '5', 'g', TRUE, 9, '/api/ingredients/dianfen.jpg'),
  (@r, '盐', '3', 'g', TRUE, 10, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '1', 'g', TRUE, 11, '/api/ingredients/baihujiaofen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '里脊切薄片用黄酒和淀粉抓匀，春笋切片，雪菜挤干', 8),
  (@r, 2, '热油15毫升下肉片，大火滑炒至变色盛出', 2),
  (@r, 3, '余油下姜末雪菜与笋片，中火煸出香', 2),
  (@r, 4, '加清水700毫升大火烧开，下细面条煮3分钟', 4),
  (@r, 5, '回锅肉片，加盐与胡椒粉，连汤盛碗', 2);

-- ========== 10. 宁波猪油汤圆 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('宁波猪油汤圆', '宁波城里传了七百年的甜点，猪油拌白糖作芯，糯米皮薄得透光。煮熟一碗，咬开一个小口，滚烫的猪油甜馅流满嘴。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-zhuyou-tangyuan.jpg', 35, 10, 45, 2, 4, '浙菜', '经典,小吃,甜品,浙菜名菜', 1, TRUE, 276, 340, 4, 13, 52, '馅球必须冻硬才好包；下锅后勺背轻推，浮起转中火煮才不破皮。', '甜润油香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '糯米粉', '200', 'g', TRUE, 1, '/api/ingredients/nuomifen.jpg'),
  (@r, '猪油', '60', 'g', TRUE, 2, '/api/ingredients/zhuyou.jpg'),
  (@r, '白糖', '60', 'g', TRUE, 3, '/api/ingredients/baitang.jpg'),
  (@r, '糖桂花', '20', 'g', TRUE, 4, '/api/ingredients/guihuatang.jpg'),
  (@r, '温水', '150', 'ml', TRUE, 5, '/api/ingredients/qingshui.jpg'),
  (@r, '清水', '800', 'ml', TRUE, 6, '/api/ingredients/qingshui.jpg'),
  (@r, '白芝麻', '10', 'g', FALSE, 7, '/api/ingredients/baizhima.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪油加白糖与糖桂花拌匀，冻硬后捏成8克小馅球', 10),
  (@r, 2, '糯米粉加温水150毫升揉成软面团，盖湿布饧20分钟', 22),
  (@r, 3, '面团下12克一个剂子，按扁包入馅球收口搓圆', 10),
  (@r, 4, '锅中清水烧开下汤圆，勺背轻推防粘底，中火煮至浮起', 4),
  (@r, 5, '转小火再煮2分钟至皮软馅化，连汤盛碗', 2);

-- ========== 11. 温州鱼丸 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('温州鱼丸', '温州码头的独特小吃，鱼丸不圆而是条条状。黄鱼肉擂茸拌红薯粉摔打上劲，入原汤带汤，一枚入口既弹嫩又鲜甜。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-wenzhou-yuwan.jpg', 30, 20, 50, 3, 3, '浙菜', '经典,小吃,海鲜,浙菜名菜', 1, TRUE, 280, 260, 26, 4, 20, '鱼茸必须擂够上劲才弹；成型时水温将开未开，下滚水鱼条就散。', '清鲜弹嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '黄鱼', '500', 'g', TRUE, 1, '/api/ingredients/bianyu.jpg'),
  (@r, '红薯淀粉', '60', 'g', TRUE, 2, '/api/ingredients/dianfen.jpg'),
  (@r, '鸡蛋清', '1', '个', TRUE, 3, '/api/ingredients/jidanqing.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', TRUE, 5, '/api/ingredients/xiaocong.jpg'),
  (@r, '清水', '1000', 'ml', TRUE, 6, '/api/ingredients/qingshui.jpg'),
  (@r, '盐', '5', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '白胡椒粉', '1', 'g', TRUE, 8, '/api/ingredients/baihujiaofen.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '黄鱼去头骨皮，取净肉用刀背剁成鱼茸', 10),
  (@r, 2, '鱼茸加盐、鸡蛋清与红薯粉，朝一个方向擂20分钟上劲', 20),
  (@r, 3, '鱼骨加清水800毫升大火煮10分钟，滤渣留原汤', 12),
  (@r, 4, '鱼糊挤成不规则条状下温水，烧开后转中火煮3分钟', 5),
  (@r, 5, '原汤下鱼丸，加盐与胡椒粉烧开，撒葱花盛碗', 3);

-- ========== 12. 三丝敲鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('三丝敲鱼', '温州平阳的古法名菜，鲜鱼片蘸淀粉以木槌敲薄如纸，配火腿鸡丝蕈丝入高汤煨成。汤清味鲜，敲鱼滑溜弹牙。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-sansi-qiaoyu.jpg', 25, 15, 40, 3, 3, '浙菜', '经典,宴客,河鲜,浙菜名菜', 1, TRUE, 192, 200, 25, 5, 10, '敲鱼垫布防粘，敲到透光才滑溜；三丝先煮软再下鱼片收火功。', '清鲜滑嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '草鱼', '400', 'g', TRUE, 1, '/api/ingredients/caoyu.jpg'),
  (@r, '淀粉', '50', 'g', TRUE, 2, '/api/ingredients/dianfen.jpg'),
  (@r, '火腿', '30', 'g', TRUE, 3, '/api/ingredients/huotui.jpg'),
  (@r, '鸡胸肉', '50', 'g', TRUE, 4, '/api/ingredients/jitui.jpg'),
  (@r, '干香菇', '15', 'g', TRUE, 5, '/api/ingredients/ganxianggu.jpg'),
  (@r, '高汤', '800', 'ml', TRUE, 6, '/api/ingredients/gaotang.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '盐', '4', 'g', TRUE, 8, '/api/ingredients/yan.jpg'),
  (@r, '绍兴黄酒', '10', 'ml', TRUE, 9, '/api/ingredients/huangjiu.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '草鱼去皮取净肉，用干净布吸干表面水分', 6),
  (@r, 2, '鱼片两面拍干淀粉，垫布以木槌敲薄至透亮', 6),
  (@r, 3, '敲薄鱼片切3厘米菱形片，入沸水汆1分钟捞出', 3),
  (@r, 4, '火腿、鸡胸肉、泡发香菇分别切细丝', 6),
  (@r, 5, '高汤下姜丝烧开，加鱼片与三丝小火煮2分钟', 4),
  (@r, 6, '加盐和黄酒调味，连汤盛入汤碗', 2);

-- ========== 13. 霉干菜焖肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('霉干菜焖肉', '绍兴人家常的下饭硬菜，霉干菜与猪肉同焖。干菜吸尽猪油变得黑亮，肉染上菜香，焖到肥肉用筷子一夹即散。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-meigancai-menrou.jpg', 20, 95, 115, 2, 4, '浙菜', '家常,下饭,猪肉,浙菜名菜', 1, TRUE, 156, 560, 16, 44, 6, '干菜要反复淘净否则有沙毁全菜；肥肉多些才润，蒸足时辰不能心软。', '咸甜醇香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '霉干菜', '100', 'g', TRUE, 1, '/api/ingredients/gandoujiao.jpg'),
  (@r, '带皮五花肉', '500', 'g', TRUE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '绍兴黄酒', '30', 'ml', TRUE, 3, '/api/ingredients/huangjiu.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '冰糖', '15', 'g', TRUE, 5, '/api/ingredients/bingtang.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '温水', '200', 'ml', FALSE, 7, '/api/ingredients/qingshui.jpg'),
  (@r, '食用油', '10', 'ml', TRUE, 8, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '霉干菜淘洗两遍，温水泡20分钟后挤干切碎', 22),
  (@r, 2, '五花肉切3厘米方块，冷水下锅大火煮5分钟捞出', 8),
  (@r, 3, '热锅下油10毫升，中火煸香霉干菜，加冰糖5克翻匀', 3),
  (@r, 4, '肉皮朝下码入砂锅，淋黄酒与生抽，盖上干菜', 3),
  (@r, 5, '上笼大火蒸90分钟至肥肉一夹即散', 90),
  (@r, 6, '取出装盘，把干菜围在肉块四周', 2);

-- ========== 14. 绍兴糟鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('绍兴糟鸡', '绍兴人把黄酒的风味封进鸡肉里。白煮三黄鸡抹遍酒糟，封坛腌渍两日，糟香钻进骨头，冷吃斩件，越嚼越香。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-shaoxing-zaoji.jpg', 25, 30, 55, 2, 6, '浙菜', '经典,凉菜,鸡肉,浙菜名菜', 1, TRUE, 257, 270, 30, 15, 3, '鸡煮好必须彻底凉透再糟；糟匀封紧至少腌四小时，腌足两日更香。', '糟香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '三黄鸡', '半', '只(约800g)', TRUE, 1, '/api/ingredients/tuji.jpg'),
  (@r, '酒糟', '150', 'g', TRUE, 2, '/api/ingredients/mijiu.jpg'),
  (@r, '绍兴黄酒', '30', 'ml', TRUE, 3, '/api/ingredients/huangjiu.jpg'),
  (@r, '盐', '15', 'g', TRUE, 4, '/api/ingredients/yan.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大葱', '2', '根', TRUE, 6, '/api/ingredients/dacong.jpg'),
  (@r, '清水', '1500', 'ml', TRUE, 7, '/api/ingredients/qingshui.jpg'),
  (@r, '香油', '5', 'ml', FALSE, 8, '/api/ingredients/xiangyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '三黄鸡去爪翅，内外洗净沥干', 5),
  (@r, 2, '锅中清水下鸡与姜片葱结，大火烧开转中小火煮15分钟，关火焖10分钟', 25),
  (@r, 3, '捞出沥干晾至彻底凉透', 8),
  (@r, 4, '酒糟加盐与黄酒搅成糟糊，抹遍鸡身内外', 4),
  (@r, 5, '装入陶坛密封，冷藏腌渍至少4小时入味', 240),
  (@r, 6, '取出刮净糟糊，斩成条块装盘，淋上香油', 5);

-- ========== 15. 清汤鱼圆 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('清汤鱼圆', '宁波宴席上的手工名菜，鱼肉刮茸加水朝一个方向搅打至竹筷直立不倒，入清汤养熟。鱼圆白嫩如云，入口即化。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-qingtang-yuyuan.jpg', 25, 15, 40, 3, 4, '浙菜', '家常,汤羹,河鲜,浙菜名菜', 1, TRUE, 275, 110, 18, 2, 3, '搅鱼茸只朝一个方向，水分次加；养熟用微火，汤大滚鱼圆就散。', '清鲜柔嫩');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '草鱼', '500', 'g', TRUE, 1, '/api/ingredients/caoyu.jpg'),
  (@r, '高汤', '1000', 'ml', TRUE, 2, '/api/ingredients/gaotang.jpg'),
  (@r, '淀粉', '20', 'g', TRUE, 3, '/api/ingredients/dianfen.jpg'),
  (@r, '盐', '5', 'g', TRUE, 4, '/api/ingredients/yan.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', TRUE, 6, '/api/ingredients/xiaocong.jpg'),
  (@r, '清水', '200', 'ml', TRUE, 7, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '草鱼去骨刮下鱼肉，剁成细腻鱼茸', 10),
  (@r, 2, '鱼茸加盐与200毫升清水，朝一个方向搅10分钟至发黏起胶', 12),
  (@r, 3, '手抓鱼糊从虎口挤出圆子，逐个下入微温水中', 6),
  (@r, 4, '高汤加姜片烧开后转微火，下鱼圆浸养3分钟至全部浮起', 5),
  (@r, 5, '拣去姜片，加盐调味撒葱花，连汤盛碗', 2);

-- ========== 16. 荷叶粉蒸肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('荷叶粉蒸肉', '杭州夏日时新菜，糯米炒香粗磨成粉裹肉，干荷叶包裹慢蒸。启叶时荷香扑鼻，米粉软糯，肥肉咸甜绵软不腻。', 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-heye-fenzhengrou.jpg', 35, 80, 115, 2, 4, '浙菜', '经典,时令,猪肉,浙菜名菜', 1, TRUE, 283, 540, 16, 45, 15, '荷叶要泡软才不裂；蒸足两小时荷叶转暗，肥肉才化在米香里。', '荷香糯润');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮五花肉', '500', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '糯米', '150', 'g', TRUE, 2, '/api/ingredients/nuomi.jpg'),
  (@r, '大米', '50', 'g', TRUE, 3, '/api/ingredients/dami.jpg'),
  (@r, '八角', '2', '颗', TRUE, 4, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '3', 'g', TRUE, 5, '/api/ingredients/guipi.jpg'),
  (@r, '干荷叶', '2', '张', TRUE, 6, '/api/ingredients/ganye.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 8, '/api/ingredients/laochou.jpg'),
  (@r, '绍兴黄酒', '15', 'ml', TRUE, 9, '/api/ingredients/huangjiu.jpg'),
  (@r, '冰糖', '10', 'g', TRUE, 10, '/api/ingredients/bingtang.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 11, '/api/ingredients/shengjiang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '干锅小火下糯米、大米、八角、桂皮炒至微黄出香', 12),
  (@r, 2, '捡去香料，米粉晾凉后粗磨成颗粒', 8),
  (@r, 3, '五花肉切1厘米厚片，加生抽、老抽、黄酒、冰糖与姜末腌20分钟', 22),
  (@r, 4, '肉片逐片裹匀米粉，让干粉吃进肉汁变得潮润', 4),
  (@r, 5, '干荷叶泡软铺平，肉片包成方包收口朝下码入碗中', 6),
  (@r, 6, '上笼大火蒸60分钟至荷叶转暗、肉糯出油', 60);
