"""把 tools/seed-sql.py 用到的新菜系封面（PNG）压成 JPEG 上传到腾讯云 COS。

对象键与库里 cover_image_url 一一对应：po/covers/<slug>.jpg。
幂等：桶里已存在的对象默认跳过，--force 才覆盖。

    py tools/cos-upload.py                # 只传缺失的
    py tools/cos-upload.py --force        # 全部重传
    py tools/cos-upload.py --only yue-    # 只传指定前缀

密钥读取顺序：环境变量 COS_SECRET_ID/COS_SECRET_KEY → application-local.yaml（已 gitignore）。
"""
import glob
import hashlib
import hmac
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(REPO, 'services/api/recipe/src/main/resources/seed')
VIBE = os.path.join(REPO, 'vibe_images')
LOCAL_YAML = os.path.join(
    REPO, 'services/api/api-bootstrap/src/main/resources/application-local.yaml')

# 与 tools/seed-sql.py 的 cos 分支保持一致
COS_FILES = ['recipes-yue.json', 'recipes-lu.json', 'recipes-min.json',
             'recipes-su.json', 'recipes-zhe.json', 'recipes-hui.json']
REGION = os.environ.get('COS_REGION', 'ap-shanghai')
BUCKET = os.environ.get('COS_BUCKET', '7072-prod-d7g3zal0655a67232-1496875399')
PREFIX = os.environ.get('COS_KEY_PREFIX', 'po')
HOST = '%s.cos.%s.myqcloud.com' % (BUCKET, REGION)
JPEG_QUALITY = 85


def secrets():
    sid = os.environ.get('COS_SECRET_ID')
    skey = os.environ.get('COS_SECRET_KEY')
    if sid and skey:
        return sid, skey
    if not os.path.exists(LOCAL_YAML):
        raise SystemExit('未配置 COS 密钥：设 COS_SECRET_ID/COS_SECRET_KEY，或准备好 application-local.yaml')
    inside = False
    found = {}
    for line in open(LOCAL_YAML, encoding='utf-8'):
        if line.startswith('cos:'):
            inside = True
            continue
        if inside:
            if not line.startswith((' ', '\t')):
                break
            stripped = line.strip()
            if ':' in stripped and not stripped.startswith('#'):
                k, _, v = stripped.partition(':')
                found[k.strip()] = v.split('#')[0].strip()
    if not found.get('secret-id') or not found.get('secret-key'):
        raise SystemExit('application-local.yaml 里找不到 cos.secret-id / cos.secret-key')
    return found['secret-id'], found['secret-key']


def authorization(method, key, extra_headers, secret_id, secret_key, expire=600):
    """COS API 密钥签名版本 v1（q-sign-algorithm=sha1）。只签请求头，不签 URL 参数。"""
    now = int(time.time())
    key_time = '%d;%d' % (now, now + expire)
    sign_key = hmac.new(secret_key.encode(), key_time.encode(), hashlib.sha1).hexdigest()
    params = ''
    headers = '&'.join(
        '%s=%s' % (quote(k.lower(), safe=''), quote(v, safe=''))
        for k, v in sorted(extra_headers.items()))
    header_list = ';'.join(sorted(quote(k.lower(), safe='') for k in extra_headers))
    http_string = '\n'.join([method.lower(), '/' + quote(key), params, headers, ''])
    string_to_sign = '\n'.join(['sha1', key_time, hashlib.sha1(http_string.encode()).hexdigest(), ''])
    signature = hmac.new(sign_key.encode(), string_to_sign.encode(), hashlib.sha1).hexdigest()
    return ('q-sign-algorithm=sha1&q-ak=%s&q-sign-time=%s&q-key-time=%s'
            '&q-header-list=%s&q-url-param-list=&q-signature=%s'
            % (secret_id, key_time, key_time, header_list, signature))


def request(method, key, secret_id, secret_key, body=None, content_type=None, timeout=60):
    headers = {}
    if content_type:
        headers['Content-Type'] = content_type
    auth = authorization(method, key, headers, secret_id, secret_key)
    req = urllib.request.Request('https://%s/%s' % (HOST, quote(key)), data=body, method=method)
    req.add_header('Authorization', auth)
    for k, v in headers.items():
        req.add_header(k, v)
    return req


def send(req, explain):
    """统一发请求，把 COS 返回的 XML 错误体打出来，便于分辨签名/权限问题。"""
    try:
        return urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace')
        raise SystemExit('%s 失败 HTTP %d: %s' % (explain, e.code, body[:1500]))


def exists(key, secret_id, secret_key):
    try:
        with urllib.request.urlopen(request('HEAD', key, secret_id, secret_key), timeout=30):
            return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise SystemExit('HEAD %s 失败 HTTP %d: %s' % (key, e.code, e.read().decode('utf-8', 'replace')[:1500]))


def to_jpeg(png_path):
    from PIL import Image
    im = Image.open(png_path).convert('RGB')
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=JPEG_QUALITY, optimize=True)
    return buf.getvalue()


def wanted_slugs(only):
    slugs = []
    for fn in COS_FILES:
        data = json.load(open(os.path.join(SEED, fn), encoding='utf-8'))
        for r in data['recipes']:
            slug = r['cover']['slug']
            if not only or slug.startswith(only):
                slugs.append(slug)
    return slugs


def main():
    args = sys.argv[1:]
    force = '--force' in args
    only = None
    if '--only' in args:
        only = args[args.index('--only') + 1]
    elif any(a.startswith('--only=') for a in args):
        only = next(a.split('=', 1)[1] for a in args if a.startswith('--only='))
    secret_id, secret_key = secrets()

    if not os.path.isdir(VIBE):
        raise SystemExit('找不到封面源图目录：' + VIBE)
    pngs = {os.path.basename(p).split('_')[0]: p
            for p in sorted(glob.glob(os.path.join(VIBE, '*.png')))}

    uploaded = skipped = missing = 0
    for slug in wanted_slugs(only):
        key = '%s/covers/%s.jpg' % (PREFIX, slug)
        src = pngs.get(slug)
        if src is None:
            print('  ! 缺源图 %s（vibe_images/%s_*.png）' % (slug, slug))
            missing += 1
            continue
        if not force and exists(key, secret_id, secret_key):
            skipped += 1
            continue
        body = to_jpeg(src)
        req = request('PUT', key, secret_id, secret_key, body=body, content_type='image/jpeg')
        req.add_header('Content-Length', str(len(body)))
        with send(req, 'PUT ' + key) as resp:
            if resp.status not in (200, 204):
                raise SystemExit('上传失败 %s: HTTP %d' % (slug, resp.status))
        uploaded += 1
        print('  + %s -> https://%s/%s (%d KB)' % (slug, HOST, quote(key), len(body) // 1024))

    print('uploaded=%d skipped_already_in_bucket=%d missing_source=%d' % (uploaded, skipped, missing))
    if missing:
        raise SystemExit('有用餐谱没有对应封面源图，先跑 ImageGen 再重试')


if __name__ == '__main__':
    main()
