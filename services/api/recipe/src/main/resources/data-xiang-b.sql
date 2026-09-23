-- 由 seed/recipes-xiang-b.json 生成，请勿手改；重新生成：python tools/seed-sql.py
-- 湘菜，共 33 道。author_id = 1，likes 为标题哈希的确定性伪随机值。

-- ========== 1. 组庵鱼翅 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('组庵鱼翅', '官府湘菜的巅峰之作，谭延闿家厨组庵先生所创。鱼翅经煨透后与鸡肉、火腿同炖，汤浓翅糯，清鲜醇厚，是旧时湖南官宴的头菜。', '/api/covers/xiang-zuan-yuchi.jpg', 120, 180, 300, 3, 6, '湘菜', '经典,官府菜,宴客,山珍海味', 1, TRUE, 101, 380, 42, 12, 8, '鱼翅本身无味，全凭高汤入味；高汤用老母鸡、火腿、猪骨慢煨4小时以上，中途不可添冷水。', '醇厚鲜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '水发鱼翅', '300', 'g', TRUE, 1, '/api/ingredients/yuchi.jpg'),
  (@r, '老母鸡', '半', '只', TRUE, 2, '/api/ingredients/tuji.jpg'),
  (@r, '火腿', '50', 'g', TRUE, 3, '/api/ingredients/huotui.jpg'),
  (@r, '猪五花肉', '100', 'g', TRUE, 4, '/api/ingredients/wuhuarou.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '绍兴黄酒', '30', 'ml', TRUE, 6, '/api/ingredients/huangjiu.jpg'),
  (@r, '小葱', '2', '根', TRUE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '盐', '3', 'g', TRUE, 8, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '老母鸡、五花肉冷水下锅焯水，洗净血沫', 15),
  (@r, 2, '大砂锅加足量清水，放入鸡、五花肉、火腿、葱姜，大火烧开转小火煨4小时成高汤', 240),
  (@r, 3, '水发鱼翅用姜片、黄酒焯水去腥，捞出沥干', 10),
  (@r, 4, '鱼翅放入高汤中，小火慢煨2小时至翅针软糯', 120),
  (@r, 5, '捞出鱼翅装碗，滤清原汤，加盐调味后浇回碗中即可', 10);

-- ========== 2. 湖南一号鲍鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湖南一号鲍鱼', '以湘菜浓辣手法烹制大连鲍，剁椒与鲍鱼的跨界组合。鲍鱼软嫩弹牙，剁椒咸辣渗透肌理，一口下去层次鲜明。', '/api/covers/xiang-yihao-baoyu.jpg', 30, 12, 42, 3, 4, '湘菜', '创新,宴客,海鲜,剁椒', 1, TRUE, 200, 260, 28, 8, 10, '鲍鱼改十字花刀但底部不切断，蒸2分半钟最佳，久了会硬如橡皮。', '咸辣鲜香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鲜活鲍鱼', '8', '只', TRUE, 1, '/api/ingredients/baoyu.jpg'),
  (@r, '剁椒', '50', 'g', TRUE, 2, '/api/ingredients/duojiao.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '2', '根', TRUE, 5, '/api/ingredients/xiaocong.jpg'),
  (@r, '蒸鱼豉油', '20', 'ml', TRUE, 6, '/api/ingredients/zhengyuchichou.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 7, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鲍鱼刷洗干净，取肉去内脏，壳留用', 10),
  (@r, 2, '鲍鱼肉表面改十字花刀，底部相连不切断', 8),
  (@r, 3, '鲍鱼肉放回壳内，铺上剁椒、蒜末、姜末', 5),
  (@r, 4, '水开后上锅大火蒸2分半钟，取出', 3),
  (@r, 5, '淋蒸鱼豉油、撒葱花，烧热油浇上激香即成', 2);

-- ========== 3. 毛家火焙鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('毛家火焙鱼', '湘潭乡间名菜。小鱼经柴火慢焙至半干，肉质紧实带烟熏香，与豆豉辣椒同炒，是主席家乡宴席上的下饭名肴。', '/api/covers/xiang-maojia-hubeiyu.jpg', 15, 10, 25, 2, 3, '湘菜', '地方名菜,下饭,河鲜', 1, TRUE, 190, 320, 30, 18, 6, '火焙鱼本身带咸味，炒时先尝再放盐；火要大、动作要快，鱼肉才不散。', '香辣烟熏');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '火焙鱼', '200', 'g', TRUE, 1, '/api/ingredients/hubeiyu.jpg'),
  (@r, '豆豉', '15', 'g', TRUE, 2, '/api/ingredients/douchi.jpg'),
  (@r, '干红辣椒', '8', 'g', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '紫苏叶', '5', '片', FALSE, 6, '/api/ingredients/zisu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 8, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '火焙鱼撕成小段，抖去碎骨', 5),
  (@r, 2, '干辣椒切段，蒜切片，姜切丝', 3),
  (@r, 3, '热油下火焙鱼中火煸至两面微焦香脆，盛出', 4),
  (@r, 4, '锅留底油，下豆豉、干辣椒段、蒜片、姜丝爆香', 2),
  (@r, 5, '倒回火焙鱼，烹生抽大火翻炒均匀，撒紫苏叶出锅', 2);

-- ========== 4. 宁乡口味蛇 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('宁乡口味蛇', '长沙夜宵江湖的头牌。大王蛇斩段高压焖制再回锅收汁，蛇肉紧实如鸡腿，辣香入骨，吃过的人没有不上瘾的。', '/api/covers/xiang-ningxiang-kouweishe.jpg', 30, 40, 70, 3, 4, '湘菜', '地方名菜,夜宵,重辣,宴客', 1, TRUE, 118, 350, 38, 14, 10, '蛇段必须高压锅压12分钟再回锅，直接炒肉硬咬不动；辣度靠干辣椒加鲜椒叠加，香气才足。', '香辣浓郁');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '养殖大王蛇', '1', '条(约1000g)', TRUE, 1, '/api/ingredients/she.jpg'),
  (@r, '干红辣椒', '30', 'g', TRUE, 2, '/api/ingredients/ganlajiao.jpg'),
  (@r, '青辣椒', '100', 'g', TRUE, 3, '/api/ingredients/qinglajiao.jpg'),
  (@r, '大蒜', '50', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '八角', '2', '颗', TRUE, 6, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '小段', TRUE, 7, '/api/ingredients/guipi.jpg'),
  (@r, '啤酒', '330', 'ml', TRUE, 8, '/api/ingredients/pijiu.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 9, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '4', 'g', TRUE, 10, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '蛇剥皮去头尾，斩4厘米段，冷水下锅焯水去腥', 15),
  (@r, 2, '蛇段入高压锅，加姜片、八角、桂皮、盐和适量清水，上汽压12分钟', 15),
  (@r, 3, '干辣椒切段，青辣椒切滚刀块，蒜拍碎', 5),
  (@r, 4, '热油下蒜、姜、干辣椒爆香，倒入蛇段和压蛇原汤、啤酒、生抽', 3),
  (@r, 5, '中火烧5分钟后下青辣椒，大火收汁至油亮浓稠', 8);

-- ========== 5. 湘阴姜盐芝麻豆子茶 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湘阴姜盐芝麻豆子茶', '湘阴家家待客的传统饮品，擂钵擂出的姜盐茶底，冲入芝麻豆子，咸香暖胃。配椒桃酥就是一套完整的待客礼数。', '/api/covers/xiang-xiangyin-jiangyancha.jpg', 15, 5, 20, 1, 4, '湘菜', '地方风味,茶饮,待客', 1, TRUE, 121, 120, 6, 5, 12, '姜要擂不要切，擂出姜汁才有味；盐宁少勿多，喝的是豆香姜暖。', '咸香微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '老黄姜', '30', 'g', TRUE, 1, '/api/ingredients/shengjiang.jpg'),
  (@r, '熟芝麻', '30', 'g', TRUE, 2, '/api/ingredients/baizhima.jpg'),
  (@r, '炒黄豆', '40', 'g', TRUE, 3, '/api/ingredients/huangdou.jpg'),
  (@r, '茶叶', '5', 'g', TRUE, 4, '/api/ingredients/lucha.jpg'),
  (@r, '盐', '3', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '开水', '1200', 'ml', TRUE, 6, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '黄豆干锅炒至焦香开裂，芝麻炒香', 8),
  (@r, 2, '姜去皮，与茶叶、盐同入擂钵擂成茸', 5),
  (@r, 3, '擂好的姜盐茶茸分装入碗，每碗加一勺熟芝麻和黄豆', 3),
  (@r, 4, '滚开水高冲入碗，盖焖2分钟即可饮用', 3);

-- ========== 6. 武冈卤铜鹅 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('武冈卤铜鹅', '武冈古城卤菜之王，明清两代贡品。铜鹅卤制后皮色棕红油亮，卤香浸透纤维，斩件装盘就是一道硬菜。', '/api/covers/xiang-wugang-lutonge.jpg', 20, 60, 80, 2, 4, '湘菜', '地方名菜,卤味,宴客', 1, TRUE, 90, 400, 32, 26, 6, '卤水是灵魂，八角桂皮草果丁香比例要对；卤好后关火浸泡2小时再捞出，入味更深。', '卤香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '武冈铜鹅', '半', '只(约1200g)', TRUE, 1, '/api/ingredients/e.jpg'),
  (@r, '八角', '3', '颗', TRUE, 2, '/api/ingredients/bajiao.jpg'),
  (@r, '桂皮', '1', '段', TRUE, 3, '/api/ingredients/guipi.jpg'),
  (@r, '草果', '1', '颗', TRUE, 4, '/api/ingredients/caoguo.jpg'),
  (@r, '丁香', '2', 'g', TRUE, 5, '/api/ingredients/dingxiang.jpg'),
  (@r, '干辣椒', '10', 'g', TRUE, 6, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '50', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '10', 'ml', TRUE, 9, '/api/ingredients/laochou.jpg'),
  (@r, '冰糖', '20', 'g', TRUE, 10, '/api/ingredients/bingtang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鹅肉冷水下锅焯水，洗净血沫', 10),
  (@r, 2, '锅内加清水、所有香料、姜、生抽、老抽、冰糖，烧开煮出卤香', 10),
  (@r, 3, '放入鹅肉，中火卤40分钟，期间翻面两次', 40),
  (@r, 4, '关火加盖，让鹅在卤水中浸泡2小时', 120),
  (@r, 5, '捞出晾凉，斩件装盘，淋少许卤汁即可', 10);

-- ========== 7. 衡阳荷折片 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('衡阳荷折片', '衡阳人夏天的救命凉菜。米浆蒸成的荷折皮切菱形，拌蒜水辣油，滑嫩爽辣，街头的吃法是剪碎了浇码子。', '/api/covers/xiang-hengyang-hezhepian.jpg', 30, 15, 45, 2, 3, '湘菜', '地方风味,小吃,素食,夏日', 1, TRUE, 312, 240, 6, 8, 36, '米浆摊皮要薄厚均匀，起泡即熟；调味靠蒜水、辣油、香醋三剑客，比例2比2比1。', '酸辣爽滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '粘米粉', '150', 'g', TRUE, 1, '/api/ingredients/zhanmifen.jpg'),
  (@r, '清水', '400', 'ml', TRUE, 2, '/api/ingredients/qingshui.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '辣椒油', '30', 'ml', TRUE, 4, '/api/ingredients/lajiaoyou.jpg'),
  (@r, '香醋', '20', 'ml', TRUE, 5, '/api/ingredients/xiangcu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 7, '/api/ingredients/xiangcai.jpg'),
  (@r, '黄瓜', '半', '根', FALSE, 8, '/api/ingredients/huanggua.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '粘米粉加清水搅成无颗粒米浆，静置15分钟', 15),
  (@r, 2, '平盘刷薄油，舀入米浆摊匀，大火蒸2分钟至起大泡', 2),
  (@r, 3, '取出揭下米皮，晾凉后切菱形片', 10),
  (@r, 4, '黄瓜切丝，蒜捣成蒜泥加凉开水调成蒜水', 5),
  (@r, 5, '米皮与黄瓜丝装盘，淋蒜水、辣椒油、香醋、生抽，撒香菜拌匀', 3);

-- ========== 8. 衡东黄椒炒肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('衡东黄椒炒肉', '衡东三樟黄贡椒是衡东土菜的灵魂。黄椒辣中带甜、肉厚脆嫩，与土猪肉同炒，是衡东人宴席的第一道热炒。', '/api/covers/xiang-hengdong-huangjiaochaorou.jpg', 15, 10, 25, 2, 3, '湘菜', '地方名菜,下饭,黄椒', 1, TRUE, 120, 420, 22, 32, 6, '黄贡椒要剁碎了炒出椒香再下肉；肥肉煸出油再下瘦肉，肉才嫩锅才香。', '香辣微甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '带皮土猪肉', '300', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '衡东黄贡椒', '80', 'g', TRUE, 2, '/api/ingredients/huanggongjiao.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '豆豉', '10', 'g', TRUE, 4, '/api/ingredients/douchi.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 5, '/api/ingredients/shengchou.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 6, '/api/ingredients/shiyongyou.jpg'),
  (@r, '盐', '2', 'g', TRUE, 7, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪肉肥瘦分开切薄片', 8),
  (@r, 2, '黄贡椒剁碎，蒜切片', 3),
  (@r, 3, '热锅少油，下肥肉煸出油脂至微卷', 4),
  (@r, 4, '下瘦肉片滑炒至变色，加豆豉、蒜片', 2),
  (@r, 5, '下黄椒碎大火翻炒，烹生抽、加盐炒匀出锅', 3);

-- ========== 9. 浏阳蒸菜 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('浏阳蒸菜', '浏阳大围山下的千年蒸法，小碗装菜、米粉裹料、上甑齐蒸。一碗一碗码在竹甑里，开盖时米香肉香混作一团。', '/api/covers/xiang-liuyang-zhengcai.jpg', 30, 40, 70, 2, 4, '湘菜', '地方名菜,蒸菜,米粉', 1, TRUE, 141, 380, 20, 18, 30, '拌米粉时淋一勺水让粉裹得均匀；蒸碗不加汤，全靠蒸汽循环出汁。', '鲜香软糯');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '五花肉', '250', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '排骨', '200', 'g', TRUE, 2, '/api/ingredients/zhupaigu.jpg'),
  (@r, '粘米粉', '60', 'g', TRUE, 3, '/api/ingredients/zhanmifen.jpg'),
  (@r, '红辣椒粉', '10', 'g', TRUE, 4, '/api/ingredients/lajiaofen.jpg'),
  (@r, '豆豉', '10', 'g', TRUE, 5, '/api/ingredients/douchi.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 8, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉切厚片，排骨斩小段，分别洗净沥干', 10),
  (@r, 2, '肉和排骨加红椒粉、豆豉、姜末、生抽、食用油拌匀腌15分钟', 15),
  (@r, 3, '拌入粘米粉，加一勺清水抓匀，让米粉均匀裹住肉', 5),
  (@r, 4, '分装小碗，码入竹甑，大火蒸40分钟', 40),
  (@r, 5, '出甑撒葱花，连碗上桌', 2);

-- ========== 10. 平江香干 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('平江香干', '平江县名片小吃。加压卤制的香干紧实有嚼劲，手撕成条凉拌或爆炒，豆香混着卤香，越嚼越香。', '/api/covers/xiang-pingjiang-xianggan.jpg', 15, 12, 27, 2, 3, '湘菜', '地方名菜,小吃,豆制品,下酒', 1, TRUE, 269, 280, 20, 16, 12, '香干先蒸5分钟再撕，纤维松开更入味；炒时用茶油，配小米辣和芹菜段。', '卤香微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '平江香干', '300', 'g', TRUE, 1, '/api/ingredients/xianggan.jpg'),
  (@r, '芹菜', '60', 'g', TRUE, 2, '/api/ingredients/qincai.jpg'),
  (@r, '小米辣', '3', '根', TRUE, 3, '/api/ingredients/xiaomila.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '茶油', '25', 'ml', TRUE, 5, '/api/ingredients/shiyongyou.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '盐', '2', 'g', TRUE, 7, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '香干上锅蒸5分钟，取出稍晾后手撕成粗条', 7),
  (@r, 2, '芹菜切段，小米辣切圈，蒜切片', 3),
  (@r, 3, '热锅下茶油，爆香蒜片、小米辣', 1),
  (@r, 4, '下香干条中火煸炒2分钟至微焦', 2),
  (@r, 5, '下芹菜段，烹生抽、加盐大火炒匀即可', 2);

-- ========== 11. 花菇无黄蛋 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('花菇无黄蛋', '长沙老湘菜馆的看家素菜。鸡蛋只取蛋清，掺入清汤蒸成洁白无黄的蛋，配花菇同烧，形态逼真、清鲜嫩滑，考验刀工火候的老功夫菜。', '/api/covers/xiang-huagu-wuhuangdan.jpg', 40, 20, 60, 3, 4, '湘菜', '经典,宴客,功夫菜,素菜', 1, TRUE, 145, 220, 16, 10, 10, '蛋清掺清汤比例是关键，汤多不成形、汤少不嫩；蒸时用小火，大火必起蜂窝。', '清鲜嫩滑');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸡蛋', '8', '个', TRUE, 1, '/api/ingredients/jidan.jpg'),
  (@r, '干花菇', '30', 'g', TRUE, 2, '/api/ingredients/ganxianggu.jpg'),
  (@r, '鸡清汤', '200', 'ml', TRUE, 3, '/api/ingredients/gaotang.jpg'),
  (@r, '小白菜心', '6', '棵', TRUE, 4, '/api/ingredients/baicai.jpg'),
  (@r, '淀粉', '10', 'g', TRUE, 5, '/api/ingredients/dianfen.jpg'),
  (@r, '盐', '3', 'g', TRUE, 6, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '20', 'ml', TRUE, 7, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡蛋顶端敲开小圆孔，倒出蛋黄另用，蛋清留壳内', 15),
  (@r, 2, '蛋清掺入100ml鸡清汤和少许盐打匀，缓缓灌回蛋壳，封口朝上入笼小火蒸15分钟', 20),
  (@r, 3, '蒸熟取出入冷水浸凉，剥去蛋壳，成洁白无黄蛋', 10),
  (@r, 4, '花菇泡发去蒂，加清汤煨10分钟入味', 10),
  (@r, 5, '无黄蛋与花菇入锅，加剩余清汤烧开勾薄芡，菜心围边装盘', 8);

-- ========== 12. 岳阳姜辣凤爪 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('岳阳姜辣凤爪', '岳阳夜宵摊的王牌。老姜用油慢慢煸香，鸡爪炖到脱骨仍带胶糯，姜辣直冲天灵盖，冬天一锅端上桌瞬间见底。', '/api/covers/xiang-yueyang-jianglafengzhao.jpg', 20, 45, 65, 2, 4, '湘菜', '地方名菜,夜宵,下酒,鸡爪', 1, TRUE, 294, 380, 26, 20, 10, '老姜分量要足，半锅都是姜才算正宗；鸡爪剪去趾甲先焯后炒再焖，胶质才出得来。', '姜辣浓郁');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '鸡爪', '500', 'g', TRUE, 1, '/api/ingredients/jizhua.jpg'),
  (@r, '老姜', '100', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '干红辣椒', '15', 'g', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '八角', '1', '颗', TRUE, 5, '/api/ingredients/bajiao.jpg'),
  (@r, '啤酒', '330', 'ml', TRUE, 6, '/api/ingredients/pijiu.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '5', 'ml', TRUE, 8, '/api/ingredients/laochou.jpg'),
  (@r, '盐', '3', 'g', TRUE, 9, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸡爪剪去趾甲，斩两段，冷水下锅焯水后洗净', 10),
  (@r, 2, '老姜切厚片，干辣椒切段', 5),
  (@r, 3, '热油下姜片小火煸至边缘微焦、姜香四溢', 5),
  (@r, 4, '下鸡爪翻炒，加干辣椒、蒜、八角，烹生抽老抽', 5),
  (@r, 5, '倒入啤酒和适量清水，小火焖30分钟，大火收汁', 35);

-- ========== 13. 湘乡红煨水鱼裙边 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湘乡红煨水鱼裙边', '湘乡传统大菜。甲鱼裙边胶质丰厚，与五花肉同红煨，汤色红亮、入口即化，旧时是宴席压轴的功夫菜。', '/api/covers/xiang-xiangxiang-hongweishuiyu.jpg', 40, 90, 130, 3, 4, '湘菜', '经典,宴客,甲鱼', 1, TRUE, 195, 480, 34, 30, 8, '裙边要保留完整，焯水后刮净黑膜；煨制火候宁小勿大，小火慢煨胶质才溶入汤中。', '浓香软糯');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '甲鱼裙边', '300', 'g', TRUE, 1, '/api/ingredients/jiayuqunbian.jpg'),
  (@r, '五花肉', '150', 'g', TRUE, 2, '/api/ingredients/wuhuarou.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 4, '/api/ingredients/dasuan.jpg'),
  (@r, '干红辣椒', '10', 'g', TRUE, 5, '/api/ingredients/ganlajiao.jpg'),
  (@r, '黄酒', '30', 'ml', TRUE, 6, '/api/ingredients/huangjiu.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '5', 'ml', TRUE, 8, '/api/ingredients/laochou.jpg'),
  (@r, '冰糖', '15', 'g', TRUE, 9, '/api/ingredients/bingtang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '裙边冷水下锅，加姜片黄酒焯水，刮净表面黑膜', 20),
  (@r, 2, '五花肉切厚片，煸出油至微黄', 8),
  (@r, 3, '下姜片、蒜、干辣椒爆香，放入裙边翻炒', 3),
  (@r, 4, '烹黄酒、生抽、老抽，加冰糖和热水没过食材', 3),
  (@r, 5, '小火红煨80分钟至裙边软糯、汤汁浓亮', 80);

-- ========== 14. 湘味糯米蒸排骨 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湘味糯米蒸排骨', '湘宴蒸菜经典。肋排裹米粉垫南瓜同蒸，米粉吸饱肉汁，排骨脱骨，南瓜甜面垫底解腻，一笼两层享受。', '/api/covers/xiang-nuomi-zhengpaigu.jpg', 30, 60, 90, 2, 4, '湘菜', '蒸菜,下饭,宴客', 1, TRUE, 157, 520, 26, 22, 48, '排骨腌足2小时入味；糯米先泡4小时再蒸，粒粒透亮不夹生。', '咸香软糯');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪肋排', '500', 'g', TRUE, 1, '/api/ingredients/zhupaigu.jpg'),
  (@r, '糯米', '150', 'g', TRUE, 2, '/api/ingredients/nuomi.jpg'),
  (@r, '老南瓜', '200', 'g', TRUE, 3, '/api/ingredients/nangua.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 4, '/api/ingredients/shengchou.jpg'),
  (@r, '蚝油', '15', 'g', TRUE, 5, '/api/ingredients/haoyou.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '红辣椒粉', '5', 'g', FALSE, 7, '/api/ingredients/lajiaofen.jpg'),
  (@r, '食用油', '15', 'ml', TRUE, 8, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '糯米淘洗后浸泡4小时，沥干', 240),
  (@r, 2, '肋排斩小段，加生抽、蚝油、姜末、红椒粉、油拌匀腌2小时', 120),
  (@r, 3, '南瓜去皮切厚片，铺在蒸笼底', 10),
  (@r, 4, '排骨滚上糯米，码在南瓜上', 10),
  (@r, 5, '大火蒸60分钟至排骨脱骨、糯米透亮', 60);

-- ========== 15. 长沙口味蟹 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('长沙口味蟹', '口味虾的同胞兄弟，长沙夜宵桌上的双雄之一。青蟹斩块过油，干辣椒花椒紫苏全数招呼，蟹肉紧甜、壳都嘬得有味。', '/api/covers/xiang-changsha-kouweixie.jpg', 20, 15, 35, 2, 3, '湘菜', '地方名菜,夜宵,海鲜,重辣', 1, TRUE, 282, 340, 26, 16, 14, '蟹块切口拍一层薄淀粉再过油，蟹黄蟹膏不流失；紫苏最后下，靠余温出香。', '香辣鲜甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '青蟹', '2', '只(约800g)', TRUE, 1, '/api/ingredients/qingxie.jpg'),
  (@r, '干红辣椒', '20', 'g', TRUE, 2, '/api/ingredients/ganlajiao.jpg'),
  (@r, '花椒', '3', 'g', TRUE, 3, '/api/ingredients/huajiao.jpg'),
  (@r, '紫苏叶', '10', '片', TRUE, 4, '/api/ingredients/zisu.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '啤酒', '100', 'ml', TRUE, 7, '/api/ingredients/pijiu.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '5', 'g', FALSE, 9, '/api/ingredients/baitang.jpg'),
  (@r, '食用油', '400', 'ml', FALSE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '青蟹刷净揭盖去鳃，斩成四块，切口拍薄淀粉', 10),
  (@r, 2, '油烧至七成热，下蟹块炸1分钟至壳红捞出', 3),
  (@r, 3, '锅留底油，下干辣椒段、花椒、姜蒜片爆香', 2),
  (@r, 4, '下蟹块翻炒，烹啤酒、生抽，加糖和少许水烧3分钟', 4),
  (@r, 5, '下紫苏叶翻匀，大火收汁裹匀即成', 2);

-- ========== 16. 邵阳猪血丸子 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('邵阳猪血丸子', '宝庆腊味奇珍，冬至前后家家必做。豆腐拌猪血猪肉揉成球，柴火熏足一月，切片蒸食腊香弹韧，是邵阳人的年味。', '/api/covers/xiang-shaoyang-zhuxuewanzi.jpg', 20, 30, 50, 2, 4, '湘菜', '地方名菜,腊味,年菜', 1, TRUE, 203, 420, 24, 30, 10, '猪血丸子本身咸硬，先蒸20分钟回软再切片；配大蒜叶炒，腊香被蒜香一激更浓。', '腊香咸鲜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪血丸子', '300', 'g', TRUE, 1, '/api/ingredients/zhuxuewanzi.jpg'),
  (@r, '大蒜叶', '80', 'g', TRUE, 2, '/api/ingredients/qingsuan.jpg'),
  (@r, '干红辣椒', '8', 'g', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生姜', '10', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '食用油', '25', 'ml', TRUE, 5, '/api/ingredients/shiyongyou.jpg'),
  (@r, '生抽', '10', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '猪血丸子上锅蒸20分钟，晾凉后切薄片', 22),
  (@r, 2, '大蒜叶斜切段，姜切丝，干辣椒切段', 5),
  (@r, 3, '热油下丸子片中火煸至微卷出油', 4),
  (@r, 4, '下姜丝、干辣椒段爆香，加大蒜叶', 2),
  (@r, 5, '烹生抽大火炒匀，蒜叶断生即出锅', 2);

-- ========== 17. 邵阳血浆鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('邵阳血浆鸭', '邵阳武冈一带的名肴。嫩鸭肉裹着醋血浆炒，酱紫乌亮、醋香开胃，和永州血鸭同源不同韵，浆更稠、味更冲。', '/api/covers/xiang-shaoyang-xuejiangya.jpg', 30, 30, 60, 3, 4, '湘菜', '地方名菜,鸭肉,下饭', 1, TRUE, 316, 520, 32, 34, 8, '血浆用陈醋调，比例是血2醋1；下浆前锅里汤汁要收浓，浆一入锅十秒出锅，久则老。', '酸辣浓香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '嫩鸭', '1', '只(约1200g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '鲜鸭血', '80', 'ml', TRUE, 2, '/api/ingredients/yaxue.jpg'),
  (@r, '陈醋', '40', 'ml', TRUE, 3, '/api/ingredients/xiangcu.jpg'),
  (@r, '生姜', '40', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '干红辣椒', '15', 'g', TRUE, 6, '/api/ingredients/ganlajiao.jpg'),
  (@r, '青辣椒', '3', '根', FALSE, 7, '/api/ingredients/qinglajiao.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '4', 'g', TRUE, 9, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸭血与陈醋混匀调成血浆备用', 3),
  (@r, 2, '鸭子斩小块焯水，姜蒜切粒，干辣椒切段', 12),
  (@r, 3, '热油下鸭块煸炒至水干微黄，下姜蒜辣椒爆香', 12),
  (@r, 4, '烹料酒、加盐、添少量热水，中火焖10分钟', 10),
  (@r, 5, '大火收浓汤汁，倒入血浆快速翻炒十秒，裹匀立即出锅', 1);

-- ========== 18. 土家三下锅 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('土家三下锅', '张家界土家宴客头牌。腊肉、豆腐、萝卜一锅同炖，三下说的是三种主料下锅，越炖越香，火锅边吃边续汤。', '/api/covers/xiang-tujia-sanxiaguo.jpg', 20, 40, 60, 2, 4, '湘菜', '地方名菜,火锅,腊味', 1, TRUE, 102, 560, 28, 40, 18, '腊肉先煮10分钟去咸再炖；干锅版的锅底垫洋葱，边煮边吃更香。', '咸香暖身');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '腊肉', '200', 'g', TRUE, 1, '/api/ingredients/larou.jpg'),
  (@r, '豆腐', '300', 'g', TRUE, 2, '/api/ingredients/doufu.jpg'),
  (@r, '白萝卜', '300', 'g', TRUE, 3, '/api/ingredients/bailuobo.jpg'),
  (@r, '干红辣椒', '10', 'g', TRUE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 5, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 6, '/api/ingredients/dasuan.jpg'),
  (@r, '青蒜', '50', 'g', TRUE, 7, '/api/ingredients/qingsuan.jpg'),
  (@r, '高汤', '800', 'ml', TRUE, 8, '/api/ingredients/gaotang.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '腊肉煮10分钟去咸，切厚片', 12),
  (@r, 2, '豆腐切块，萝卜切滚刀块，青蒜切段', 8),
  (@r, 3, '热锅下腊肉煸出油，下姜蒜、干辣椒爆香', 5),
  (@r, 4, '下萝卜块翻炒，加高汤烧开', 3),
  (@r, 5, '下豆腐块，转中小火炖25分钟，撒青蒜即可', 25);

-- ========== 19. 麻仁香酥鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('麻仁香酥鸭', '长沙老牌名菜，湘厨脱骨功夫的试金石。整鸭脱骨蒸烂，挂糊滚芝麻下锅炸透，外层芝麻酥香、鸭肉软烂，斩条带椒盐上桌。', '/api/covers/xiang-maren-xiangsuya.jpg', 60, 40, 100, 3, 5, '湘菜', '经典,宴客,功夫菜,鸭肉', 1, TRUE, 270, 620, 36, 42, 18, '整鸭脱骨皮不能破，蒸至七成烂即止，太烂挂糊易散；芝麻要滚得密，炸时用手勺淋油定型。', '酥香软烂');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '肥鸭', '1', '只(约1500g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '白芝麻', '100', 'g', TRUE, 2, '/api/ingredients/baizhima.jpg'),
  (@r, '鸡蛋', '2', '个', TRUE, 3, '/api/ingredients/jidan.jpg'),
  (@r, '淀粉', '80', 'g', TRUE, 4, '/api/ingredients/dianfen.jpg'),
  (@r, '面粉', '30', 'g', TRUE, 5, '/api/ingredients/mianfen.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '小葱', '3', '根', TRUE, 7, '/api/ingredients/xiaocong.jpg'),
  (@r, '花椒', '2', 'g', TRUE, 8, '/api/ingredients/huajiao.jpg'),
  (@r, '盐', '5', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '1500', 'ml', FALSE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '整鸭从背部开刀剔骨，保持皮肉完整不破', 30),
  (@r, 2, '鸭肉抹盐、塞葱姜花椒，腌30分钟后上笼蒸40分钟至七成烂', 70),
  (@r, 3, '鸡蛋、淀粉、面粉调成蛋糊，均匀抹在鸭肉上，滚满白芝麻压实', 10),
  (@r, 4, '油烧至六成热，提着鸭下锅炸至定型，再翻炸5分钟至金黄酥脆', 8),
  (@r, 5, '捞出斩条装盘，随椒盐上桌', 5);

-- ========== 20. 湘西社饭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湘西社饭', '湘西苗家清明社日必吃。野蒿菜、腊肠腊肉丁与糯米同蒸，蒿香腊香缠着糯香，是挂在湘西人乡愁里的一碗饭。', '/api/covers/xiang-xx-shetfan.jpg', 60, 40, 100, 2, 4, '湘菜', '地方名菜,主食,苗家风味,野菜', 1, TRUE, 309, 540, 18, 22, 68, '野蒿要焯水和反复揉洗去苦味，攥干再切；糯米与粘米七三比例，蒸出来才软糯不塌。', '腊香蒿香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '糯米', '350', 'g', TRUE, 1, '/api/ingredients/nuomi.jpg'),
  (@r, '粘米', '150', 'g', TRUE, 2, '/api/ingredients/dami.jpg'),
  (@r, '青蒿', '200', 'g', TRUE, 3, '/api/ingredients/qinghao.jpg'),
  (@r, '腊肉', '100', 'g', TRUE, 4, '/api/ingredients/larou.jpg'),
  (@r, '腊肠', '1', '根', TRUE, 5, '/api/ingredients/lachang.jpg'),
  (@r, '大蒜叶', '30', 'g', FALSE, 6, '/api/ingredients/qingsuan.jpg'),
  (@r, '盐', '3', 'g', TRUE, 7, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '糯米、粘米混合淘洗，浸泡4小时', 240),
  (@r, 2, '青蒿焯水后清水浸泡，反复揉洗去苦味，攥干切碎', 20),
  (@r, 3, '腊肉、腊肠切小丁，干锅煸出油', 8),
  (@r, 4, '米沥干与蒿菜碎、腊味丁、盐拌匀，上甑大火蒸40分钟', 40),
  (@r, 5, '撒蒜叶末，再焖5分钟开甑', 5);

-- ========== 21. 古丈毛尖炒虾仁 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('古丈毛尖炒虾仁', '以茶入馔的湘菜新派代表作。古丈毛尖绿茶鲜香清苦，裹着弹嫩河虾仁同炒，茶香解腻、虾鲜衬茶，一青一白清雅脱俗。', '/api/covers/xiang-guzhang-maojian-xiaren.jpg', 20, 8, 28, 2, 3, '湘菜', '创新,宴客,河鲜,茶馔', 1, TRUE, 261, 220, 22, 10, 8, '虾仁上浆冷藏20分钟更弹；茶叶先用温水泡开再下锅，炒久了会苦。', '清鲜茶香');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '河虾仁', '250', 'g', TRUE, 1, '/api/ingredients/hexiaren.jpg'),
  (@r, '古丈毛尖茶叶', '8', 'g', TRUE, 2, '/api/ingredients/lucha.jpg'),
  (@r, '鸡蛋清', '1', '个', TRUE, 3, '/api/ingredients/jidanqing.jpg'),
  (@r, '淀粉', '10', 'g', TRUE, 4, '/api/ingredients/dianfen.jpg'),
  (@r, '盐', '2', 'g', TRUE, 5, '/api/ingredients/yan.jpg'),
  (@r, '料酒', '10', 'ml', TRUE, 6, '/api/ingredients/liaojiu.jpg'),
  (@r, '食用油', '300', 'ml', FALSE, 7, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '虾仁洗净吸干，加蛋清、淀粉、盐、料酒上浆，冷藏20分钟', 25),
  (@r, 2, '毛尖用温水泡2分钟，滗出茶叶留茶汤', 3),
  (@r, 3, '油温三成热，下虾仁快速滑油至变色捞出', 1),
  (@r, 4, '锅留底油，下茶叶略煸，倒回虾仁', 1),
  (@r, 5, '加少许茶汤勾薄芡，颠锅炒匀即出', 2);

-- ========== 22. 湘味干烧桂鱼 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湘味干烧桂鱼', '湘厨做干烧的看家功夫。桂鱼整条改花刀，小火㸆干汤汁亮油，肉如蒜瓣一瓣瓣立着，微辣带甜，筷子一碰骨肉分离。', '/api/covers/xiang-ganshao-guiyu.jpg', 20, 20, 40, 3, 4, '湘菜', '宴客,河鲜,功夫菜', 1, TRUE, 255, 360, 32, 16, 8, '桂鱼煎前一定擦干水分，热锅热油不破皮；㸆汤时只晃锅不翻鱼，鱼形才完整。', '咸辣微甜');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '桂鱼', '1', '条(约750g)', TRUE, 1, '/api/ingredients/guiyu.jpg'),
  (@r, '猪五花肉末', '50', 'g', TRUE, 2, '/api/ingredients/zhuroumo.jpg'),
  (@r, '干红辣椒', '10', 'g', TRUE, 3, '/api/ingredients/ganlajiao.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '15', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '小葱', '3', '根', TRUE, 6, '/api/ingredients/xiaocong.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 7, '/api/ingredients/shengchou.jpg'),
  (@r, '白糖', '10', 'g', TRUE, 8, '/api/ingredients/baitang.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 9, '/api/ingredients/liaojiu.jpg'),
  (@r, '食用油', '50', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '桂鱼两面改一字花刀，擦干水分，用料酒、盐略腌', 10),
  (@r, 2, '热锅热油，两面煎至金黄定形', 6),
  (@r, 3, '下肉末炒散，加姜蒜、干辣椒段爆香', 2),
  (@r, 4, '加生抽、糖、热水适量，中小火㸆10分钟，期间淋汁浇鱼身', 10),
  (@r, 5, '大火收汁至油亮，撒葱花出锅', 3);

-- ========== 23. 湘味酸萝卜老鸭汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湘味酸萝卜老鸭汤', '湘西人炖鸭的看家法子。老水鸭加酸萝卜慢煨，酸香解腻、鸭汤清润，一年四季喝都不腻，秋冬一锅最熨帖。', '/api/covers/xiang-suanluobao-laoyatang.jpg', 20, 120, 140, 2, 4, '湘菜', '汤品,老鸭,酸香', 1, TRUE, 228, 320, 30, 18, 6, '酸萝卜本身有咸味，汤里盐要后放、少放；鸭子先煸后炖，汤色才不浑。', '酸香清润');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '老水鸭', '半', '只(约1000g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '酸萝卜', '200', 'g', TRUE, 2, '/api/ingredients/suanluobo.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '枸杞', '5', 'g', FALSE, 4, '/api/ingredients/gouqi.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 5, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '3', 'g', TRUE, 6, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸭子斩块冷水下锅，加料酒焯水洗净', 10),
  (@r, 2, '酸萝卜切滚刀块', 5),
  (@r, 3, '鸭块入干锅煸炒至微黄出油', 8),
  (@r, 4, '转砂锅加足量开水，放酸萝卜、姜片，小火煨2小时', 120),
  (@r, 5, '撒枸杞，加盐调味再煮5分钟即可', 5);

-- ========== 24. 湘味黄鸭叫煮豆腐 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湘味黄鸭叫煮豆腐', '湘江里的黄鸭叫（黄颡鱼）配水豆腐同煮，汤奶白、豆腐嫩、鱼肉滑，湖南馆子的看家河鲜锅。', '/api/covers/xiang-huangyajiao-zhudoufu.jpg', 15, 20, 35, 2, 3, '湘菜', '河鲜,家常,豆腐', 1, TRUE, 161, 300, 28, 14, 8, '鱼先煎后煮加开水，汤才奶白；紫苏是这锅汤的点睛之笔，不可省。', '奶白鲜辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '黄鸭叫', '4', '条', TRUE, 1, '/api/ingredients/huangyajiao.jpg'),
  (@r, '水豆腐', '300', 'g', TRUE, 2, '/api/ingredients/doufu.jpg'),
  (@r, '紫苏叶', '10', '片', TRUE, 3, '/api/ingredients/zisu.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '青辣椒', '2', '根', FALSE, 6, '/api/ingredients/qinglajiao.jpg'),
  (@r, '盐', '4', 'g', TRUE, 7, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '30', 'ml', TRUE, 8, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '黄鸭叫宰杀洗净，豆腐切块，姜切片', 10),
  (@r, 2, '热油煎鱼至两面微黄', 4),
  (@r, 3, '冲入开水，下姜片、蒜，大火煮10分钟至汤奶白', 10),
  (@r, 4, '下豆腐块、青辣椒圈，中火煮5分钟', 5),
  (@r, 5, '下紫苏叶，加盐调味，煮1分钟出锅', 1);

-- ========== 25. 冰糖湘莲 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('冰糖湘莲', '湘潭湘莲自清代起就是贡品，这道甜品是湘菜宴席的收尾。白莲煨得酥烂开花，糖水清甜沁心，夏冰冬热各有妙处。', '/api/covers/xiang-bingtang-xianglian.jpg', 30, 40, 70, 1, 4, '湘菜', '经典,甜品,宴客,养生', 1, TRUE, 192, 260, 8, 1, 56, '莲子用碱水搓去外衣再蒸，颗颗晶莹；冰糖分两次下，先化三分之二起锅前补，甜更清。', '清甜酥糯');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '湘白莲', '150', 'g', TRUE, 1, '/api/ingredients/xiangbailian.jpg'),
  (@r, '冰糖', '120', 'g', TRUE, 2, '/api/ingredients/bingtang.jpg'),
  (@r, '食用碱', '2', 'g', TRUE, 3, '/api/ingredients/dianfen.jpg'),
  (@r, '枸杞', '5', 'g', FALSE, 4, '/api/ingredients/gouqi.jpg'),
  (@r, '清水', '800', 'ml', TRUE, 5, '/api/ingredients/qingshui.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '干莲入锅加碱和沸水焖片刻，搓去红衣，换水洗净', 15),
  (@r, 2, '莲子加清水上笼蒸20分钟至酥而不碎', 20),
  (@r, 3, '冰糖加500ml水小火熬化成糖水', 10),
  (@r, 4, '莲子入糖水中火煨10分钟，让其吸甜开花', 10),
  (@r, 5, '撒枸杞稍煮，晾温或冰镇后食用皆宜', 5);

-- ========== 26. 湘味烧杂烩 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('湘味烧杂烩', '旧时长沙宴席的压轴大杂烩。肉丸、蛋饺、冬笋、肚片、鹌鹑蛋码成一朵花，浇上原汤上笼蒸透，团圆宴上讨个好彩头。', '/api/covers/xiang-shaozahui.jpg', 60, 40, 100, 3, 6, '湘菜', '经典,宴席,团圆菜', 1, TRUE, 213, 560, 32, 36, 16, '蛋饺皮薄才好看，蛋液里加一勺水淀粉更柔韧；码碗时肉丸打底、蛋饺围边，倒扣出来才成花形。', '鲜香醇厚');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '猪肉末', '300', 'g', TRUE, 1, '/api/ingredients/zhuroumo.jpg'),
  (@r, '鸡蛋', '4', '个', TRUE, 2, '/api/ingredients/jidan.jpg'),
  (@r, '冬笋', '100', 'g', TRUE, 3, '/api/ingredients/dongsun.jpg'),
  (@r, '熟猪肚', '100', 'g', TRUE, 4, '/api/ingredients/shuzhudu.jpg'),
  (@r, '鹌鹑蛋', '8', '个', TRUE, 5, '/api/ingredients/anchundan.jpg'),
  (@r, '小白菜心', '6', '棵', TRUE, 6, '/api/ingredients/baicai.jpg'),
  (@r, '高汤', '500', 'ml', TRUE, 7, '/api/ingredients/gaotang.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 8, '/api/ingredients/shengjiang.jpg'),
  (@r, '淀粉', '20', 'g', TRUE, 9, '/api/ingredients/dianfen.jpg'),
  (@r, '盐', '4', 'g', TRUE, 10, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '肉末加姜末、盐、淀粉、一个蛋清搅打上劲，挤成肉丸汆熟', 20),
  (@r, 2, '三个鸡蛋摊成蛋皮，包入肉馅做成蛋饺', 20),
  (@r, 3, '鹌鹑蛋煮熟剥壳，冬笋切片焯水，肚片切斜刀片', 15),
  (@r, 4, '取大碗抹油，肉丸打底，蛋饺、冬笋、肚片、鹌鹑蛋码成花形', 10),
  (@r, 5, '浇高汤上笼蒸20分钟，倒扣入盘，菜心围边', 25);

-- ========== 27. 南岳素斋一品锅 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('南岳素斋一品锅', '南岳衡山寺庙素斋代表作。山珍菌菇、豆腐、面筋层层码入砂锅，素高汤煨透，一锅吃出山林的清气。', '/api/covers/xiang-nanyue-suzhai.jpg', 40, 40, 80, 2, 4, '湘菜', '素斋,山珍,养生', 1, TRUE, 112, 300, 18, 12, 30, '素高汤用黄豆芽、干香菇蒂熬，鲜味不输鸡汤；面筋先炸后煨才吸汁。', '清鲜素雅');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '干香菇', '30', 'g', TRUE, 1, '/api/ingredients/ganxianggu.jpg'),
  (@r, '猴头菇', '100', 'g', TRUE, 2, '/api/ingredients/houtougu.jpg'),
  (@r, '油面筋', '100', 'g', TRUE, 3, '/api/ingredients/youmianjin.jpg'),
  (@r, '豆腐', '200', 'g', TRUE, 4, '/api/ingredients/doufu.jpg'),
  (@r, '冬笋', '100', 'g', TRUE, 5, '/api/ingredients/dongsun.jpg'),
  (@r, '黄豆芽', '200', 'g', TRUE, 6, '/api/ingredients/huangdouya.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 7, '/api/ingredients/shengjiang.jpg'),
  (@r, '盐', '4', 'g', TRUE, 8, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '黄豆芽加香菇蒂、姜片熬40分钟成素高汤', 40),
  (@r, 2, '干香菇泡发切片，猴头菇撕块，豆腐切块炸定型，面筋炸脆', 20),
  (@r, 3, '砂锅底铺冬笋片，依次码入菌菇、豆腐、面筋', 10),
  (@r, 4, '浇入素高汤，小火煨30分钟至各味交融', 30),
  (@r, 5, '加盐调味，连锅上桌', 2);

-- ========== 28. 新化三合汤 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('新化三合汤', '娄底新化的梅山名食。牛肉、牛血、牛肚三合为一，山胡椒油一点满屋异香，汤红油辣，新化人早上都拿它当头顿饭。', '/api/covers/xiang-xinhua-sanhetang.jpg', 20, 20, 40, 2, 4, '湘菜', '地方名菜,汤品,牛肉,早餐', 1, TRUE, 197, 340, 30, 18, 8, '牛血要嫩块的，久煮会老；山胡椒油是灵魂，起锅前点几滴，切记不可久滚。', '香辣鲜烫');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '黄牛肉', '150', 'g', TRUE, 1, '/api/ingredients/niurou.jpg'),
  (@r, '牛血', '200', 'g', TRUE, 2, '/api/ingredients/niuxue.jpg'),
  (@r, '牛肚', '150', 'g', TRUE, 3, '/api/ingredients/niudu.jpg'),
  (@r, '山胡椒油', '5', 'ml', TRUE, 4, '/api/ingredients/shanhujiaoyou.jpg'),
  (@r, '干红辣椒粉', '10', 'g', TRUE, 5, '/api/ingredients/lajiaofen.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 6, '/api/ingredients/shengjiang.jpg'),
  (@r, '米酒', '15', 'ml', TRUE, 7, '/api/ingredients/mijiu.jpg'),
  (@r, '香菜', '10', 'g', FALSE, 8, '/api/ingredients/xiangcai.jpg'),
  (@r, '盐', '4', 'g', TRUE, 9, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肉、牛肚切薄片，牛血切方块', 10),
  (@r, 2, '牛肚先入高汤煮至八成熟，再下牛肉片汆至变色', 8),
  (@r, 3, '下牛血块、姜末、辣椒粉，中火煮5分钟', 5),
  (@r, 4, '加盐、米酒调味，起锅前滴山胡椒油', 2),
  (@r, 5, '撒香菜，连汤带料趁烫吃', 1);

-- ========== 29. 道州扎肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('道州扎肉', '永州道县古法腌菜。五花肉与米粉、辣椒粉层层码入坛中自然发酵，酸香开胃、肉色粉亮，蒸熟即食，是道州人待客的诚意。', '/api/covers/xiang-daozhou-zharou.jpg', 30, 40, 70, 2, 4, '湘菜', '地方名菜,腌腊,米粉肉', 1, TRUE, 233, 580, 20, 46, 14, '坛子无水无油是发酵成功的关键；腌足半月酸香才正，蒸的时候垫几片干豆角同吸油。', '酸香微辣');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '五花肉', '500', 'g', TRUE, 1, '/api/ingredients/wuhuarou.jpg'),
  (@r, '粘米粉', '50', 'g', TRUE, 2, '/api/ingredients/zhanmifen.jpg'),
  (@r, '红辣椒粉', '30', 'g', TRUE, 3, '/api/ingredients/lajiaofen.jpg'),
  (@r, '盐', '8', 'g', TRUE, 4, '/api/ingredients/yan.jpg'),
  (@r, '白酒', '15', 'ml', TRUE, 5, '/api/ingredients/baijiu.jpg'),
  (@r, '干豆角', '50', 'g', FALSE, 6, '/api/ingredients/gandoujiao.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '五花肉切厚片，加盐、白酒拌匀杀出水分', 30),
  (@r, 2, '粘米粉干锅炒至微黄出香', 8),
  (@r, 3, '肉片裹上米粉与辣椒粉，层层码入无水无油的坛中压实', 15),
  (@r, 4, '封坛置阴凉处发酵15天以上', 1),
  (@r, 5, '取出装碗，垫泡发的干豆角，上锅蒸40分钟即成', 40);

-- ========== 30. 沙锅临武鸭 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('沙锅临武鸭', '郴州临武麻鸭天下闻名，沙锅慢㸆是最地道的吃法。鸭皮糯、肉紧、骨香，酱汁收得浓稠挂勺，端上桌还在咕嘟。', '/api/covers/xiang-shaguo-linwuya.jpg', 20, 50, 70, 2, 4, '湘菜', '地方名菜,鸭肉,沙锅', 1, TRUE, 232, 480, 32, 30, 10, '麻鸭皮薄油少，煸炒时多给点油；沙锅㸆制中途不开盖，香汽不跑味更足。', '酱香浓郁');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '临武麻鸭', '1', '只(约1200g)', TRUE, 1, '/api/ingredients/ya.jpg'),
  (@r, '生姜', '30', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '30', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '干红辣椒', '15', 'g', TRUE, 4, '/api/ingredients/ganlajiao.jpg'),
  (@r, '桂皮', '1', '小段', TRUE, 5, '/api/ingredients/guipi.jpg'),
  (@r, '生抽', '20', 'ml', TRUE, 6, '/api/ingredients/shengchou.jpg'),
  (@r, '老抽', '5', 'ml', TRUE, 7, '/api/ingredients/laochou.jpg'),
  (@r, '料酒', '20', 'ml', TRUE, 8, '/api/ingredients/liaojiu.jpg'),
  (@r, '盐', '3', 'g', TRUE, 9, '/api/ingredients/yan.jpg'),
  (@r, '食用油', '40', 'ml', TRUE, 10, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '鸭子斩小块，冷水下锅加料酒焯水', 10),
  (@r, 2, '热油下鸭块煸炒至表面微黄收干', 10),
  (@r, 3, '下姜块、蒜、干辣椒、桂皮爆香，烹生抽老抽', 3),
  (@r, 4, '转沙锅，加热水没过鸭块，小火㸆35分钟', 35),
  (@r, 5, '开盖大火收汁至浓稠挂勺，加盐调味即可', 8);

-- ========== 31. 永兴马田牛肉 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('永兴马田牛肉', '郴州永兴马田镇的江湖硬菜。黄牛肉切薄片猛火爆炒，只配辣椒姜蒜，镬气冲天，是湘南最霸道的下饭神器。', '/api/covers/xiang-yongxing-matian-niurou.jpg', 20, 6, 26, 2, 3, '湘菜', '地方名菜,牛肉,下饭', 1, TRUE, 186, 380, 34, 22, 6, '牛肉逆纹切薄片，抓蛋清淀粉锁水；全程最大火，20秒内出锅，多一秒都老。', '香辣镬气');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '黄牛后腿肉', '300', 'g', TRUE, 1, '/api/ingredients/niurou.jpg'),
  (@r, '红辣椒', '2', '根', TRUE, 2, '/api/ingredients/honglajiao.jpg'),
  (@r, '青辣椒', '3', '根', TRUE, 3, '/api/ingredients/qinglajiao.jpg'),
  (@r, '生姜', '15', 'g', TRUE, 4, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '25', 'g', TRUE, 5, '/api/ingredients/dasuan.jpg'),
  (@r, '鸡蛋清', '半个', '个', TRUE, 6, '/api/ingredients/jidanqing.jpg'),
  (@r, '淀粉', '10', 'g', TRUE, 7, '/api/ingredients/dianfen.jpg'),
  (@r, '生抽', '15', 'ml', TRUE, 8, '/api/ingredients/shengchou.jpg'),
  (@r, '食用油', '50', 'ml', TRUE, 9, '/api/ingredients/shiyongyou.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '牛肉逆纹切薄片，加蛋清、淀粉、生抽抓匀腌10分钟', 12),
  (@r, 2, '青红椒切斜片，姜蒜切片', 5),
  (@r, 3, '大火烧至锅冒烟，下油滑锅，牛肉片快速滑散至变色盛出', 1),
  (@r, 4, '下姜蒜片、青红椒片爆香', 1),
  (@r, 5, '倒回牛肉，颠锅翻炒20秒出锅', 1);

-- ========== 32. 桂东黄菌炖土鸡 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('桂东黄菌炖土鸡', '郴州桂东高山的黄菌是菌中珍品，只生松林间。与散养土鸡同炖，汤色金黄透亮，一口鲜到脚后跟。', '/api/covers/xiang-guidong-huangjun-tuji.jpg', 20, 90, 110, 2, 4, '湘菜', '地方名菜,汤品,菌菇,养生', 1, TRUE, 96, 380, 34, 20, 8, '黄菌泥沙多，流水冲净后温水泡发，泡菇水滤净留用炖汤；盐最后放。', '鲜香清润');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '干黄菌', '50', 'g', TRUE, 1, '/api/ingredients/huangjun.jpg'),
  (@r, '土鸡', '半', '只(约900g)', TRUE, 2, '/api/ingredients/tuji.jpg'),
  (@r, '生姜', '20', 'g', TRUE, 3, '/api/ingredients/shengjiang.jpg'),
  (@r, '红枣', '5', '颗', FALSE, 4, '/api/ingredients/hongzao.jpg'),
  (@r, '盐', '4', 'g', TRUE, 5, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '黄菌流水冲净泥沙，温水泡发30分钟，泡菇水滤净备用', 35),
  (@r, 2, '土鸡斩块焯水洗净', 10),
  (@r, 3, '鸡块入砂锅，加姜片、黄菌和泡菇水、足量开水', 5),
  (@r, 4, '小火炖80分钟至鸡肉酥烂', 80),
  (@r, 5, '加红枣再炖10分钟，加盐调味', 12);

-- ========== 33. 江永瑶山油茶 ==========
INSERT INTO recipe (title, description, cover_image_url, prep_time, cook_time, total_time, difficulty, servings, category, tags, author_id, is_public, likes_count, calories, protein, fat, carbs, tips, flavor_profile) VALUES ('江永瑶山油茶', '江永瑶族待客古礼。茶叶姜蒜入锅捶打出香，冲水熬浓，配排散、花生、米花喝，一碗下肚寒气全消。', '/api/covers/xiang-jiangyong-youshancha.jpg', 20, 20, 40, 1, 4, '湘菜', '地方风味,茶饮,瑶族风味', 1, TRUE, 283, 180, 6, 8, 20, '茶叶要用老茶枝，捶打出胶才有茶韵；配料按个人喜好加，排散酥脆是标配。', '姜香微苦回甘');
SET @r = LAST_INSERT_ID();
INSERT INTO recipe_ingredient (recipe_id, name, amount, unit, is_essential, sort_order, image_url) VALUES
  (@r, '老茶叶', '20', 'g', TRUE, 1, '/api/ingredients/lucha.jpg'),
  (@r, '老姜', '30', 'g', TRUE, 2, '/api/ingredients/shengjiang.jpg'),
  (@r, '大蒜', '20', 'g', TRUE, 3, '/api/ingredients/dasuan.jpg'),
  (@r, '茶油', '20', 'ml', TRUE, 4, '/api/ingredients/shiyongyou.jpg'),
  (@r, '排散', '60', 'g', TRUE, 5, '/api/ingredients/paisan.jpg'),
  (@r, '花生', '40', 'g', TRUE, 6, '/api/ingredients/huasheng.jpg'),
  (@r, '米花', '30', 'g', FALSE, 7, '/api/ingredients/mihua.jpg'),
  (@r, '盐', '3', 'g', TRUE, 8, '/api/ingredients/yan.jpg');
INSERT INTO recipe_step (recipe_id, step_number, content, duration) VALUES
  (@r, 1, '老姜拍裂，蒜拍碎', 3),
  (@r, 2, '锅烧热下茶油，放茶叶、姜、蒜中小火捶炒出香', 8),
  (@r, 3, '冲入开水，小火熬15分钟至汤浓味厚', 15),
  (@r, 4, '碗底放排散、花生、米花，冲入油茶汤', 5),
  (@r, 5, '加盐调味，趁热连料带汤一起吃喝', 2);
