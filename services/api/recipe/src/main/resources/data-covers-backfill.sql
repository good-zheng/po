-- 由 tools/seed-sql.py 生成，请勿手改；重新生成：py tools/seed-sql.py
-- COS 封面回填：只补 cover_image_url 仍为 NULL 的行，重复执行安全。
-- 补图流程：ImageGen 生成源图 -> py tools/cos-upload.py -> py tools/seed-sql.py -> 导入本文件

UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/yue-baiqieji.jpg' WHERE title = '白切鸡' AND category = '粤菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/yue-mizhichashao.jpg' WHERE title = '蜜汁叉烧' AND category = '粤菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/yue-cuipishouya.jpg' WHERE title = '脆皮烧鸭' AND category = '粤菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/yue-qingzhengluyu.jpg' WHERE title = '清蒸鲈鱼' AND category = '粤菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/lu-tangculiyu.jpg' WHERE title = '糖醋鲤鱼' AND category = '鲁菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/lu-youmendaxia.jpg' WHERE title = '油焖大虾' AND category = '鲁菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/min-foitiaoqiang.jpg' WHERE title = '佛跳墙' AND category = '闽菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/su-songshu-guibi.jpg' WHERE title = '松鼠鳜鱼' AND category = '苏菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/su-qingdun-shizitou.jpg' WHERE title = '清炖蟹粉狮子头' AND category = '苏菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/su-nanjing-yan-shuiya.jpg' WHERE title = '南京盐水鸭' AND category = '苏菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-dongporou.jpg' WHERE title = '东坡肉' AND category = '浙菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-xihu-cuyu.jpg' WHERE title = '西湖醋鱼' AND category = '浙菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/zhe-longjing-xiaren.jpg' WHERE title = '龙井虾仁' AND category = '浙菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-chouguiyu.jpg' WHERE title = '臭鳜鱼' AND category = '徽菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-maodoufu.jpg' WHERE title = '毛豆腐' AND category = '徽菜' AND cover_image_url IS NULL;
UPDATE recipe SET cover_image_url = 'https://7072-prod-d7g3zal0655a67232-1496875399.cos.ap-shanghai.myqcloud.com/po/covers/hui-wenzhengshansun.jpg' WHERE title = '问政山笋' AND category = '徽菜' AND cover_image_url IS NULL;
