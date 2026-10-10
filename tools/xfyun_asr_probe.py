"""一次性探针：用 application-local.yaml 里的 xfyun.iat 密钥，复刻 XfyunSigner 的
hmac-sha256 签名，直连讯飞 IAT 发送首帧，验证「密钥 + 签名 + 额度」是否真的可用。

不依赖 Spring Boot，纯 Python 复刻签名逻辑（与 shared/XfyunSigner.java 一一对应）。
注意：只打印密钥长度与讯飞返回的 code/sid，绝不打印密钥原文。
"""
import asyncio
import base64
import datetime
import hashlib
import hmac
import json
import urllib.parse

import websockets
import yaml

LOCAL_YAML = r"D:\dev\po\services\api\api-bootstrap\src\main\resources\application-local.yaml"
HOST = "iat-api.xfyun.cn"
PATH = "/v2/iat"


def load_secrets():
    with open(LOCAL_YAML, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    iat = cfg["xfyun"]["iat"]
    return iat["app-id"], iat["api-key"], iat["api-secret"]


def sign(host: str, path: str, api_key: str, api_secret: str) -> str:
    # 与 XfyunSigner.rfc1123Date 一致：RFC1123 的 UTC 时间
    date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
    signature = base64.b64encode(
        hmac.new(api_secret.encode("utf-8"), origin.encode("utf-8"), hashlib.sha256).digest()
    ).decode("ascii")
    auth_origin = (
        f'api_key="{api_key}", algorithm="hmac-sha256", '
        f'headers="host date request-line", signature="{signature}"'
    )
    authorization = base64.b64encode(auth_origin.encode("utf-8")).decode("ascii")
    # 与 XfyunSigner.urlEncode 一致：URLEncoder 把空格编成 +，讯飞要求 %20
    q = urllib.parse.urlencode({"authorization": authorization, "host": host, "date": date}).replace("+", "%20")
    return f"wss://{host}{path}?{q}"


async def main():
    app_id, api_key, api_secret = load_secrets()
    print(f"[secret] app_id len={len(app_id)} api_key len={len(api_key)} api_secret len={len(api_secret)}")
    url = sign(HOST, PATH, api_key, api_secret)
    # 40ms 静音 @16k/16bit 单声道 = 1280 字节，与小程序端帧大小一致
    audio = base64.b64encode(b"\x00" * 1280).decode("ascii")
    frame = json.dumps({
        "common": {"app_id": app_id},
        "business": {
            "language": "zh_cn",
            "domain": "iat",
            "accent": "mandarin",
            "vad_eos": 5000,
            "dwa": "wpgs",
        },
        "data": {"status": 0, "format": "audio/L16;rate=16000", "encoding": "raw", "audio": audio},
    })
    try:
        async with websockets.connect(url, max_size=None, open_timeout=15, close_timeout=10) as ws:
            await ws.send(frame)
            # 补一帧结束帧（status=2，audio 留空）：讯飞收到后才出最终包，便于确认鉴权与额度
            end_frame = json.dumps({
                "common": {"app_id": app_id},
                "business": {
                    "language": "zh_cn",
                    "domain": "iat",
                    "accent": "mandarin",
                    "vad_eos": 5000,
                    "dwa": "wpgs",
                },
                "data": {"status": 2, "format": "audio/L16;rate=16000", "encoding": "raw", "audio": ""},
            })
            await ws.send(end_frame)
            for _ in range(3):
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=8)
                except asyncio.TimeoutError:
                    print("[recv] 8s 内无更多消息")
                    break
                node = json.loads(msg)
                code = node.get("code", -1)
                sid = node.get("sid", "")
                print(f"[xfyun] code={code} sid={sid}")
                if code == 0:
                    print("[OK] 讯飞鉴权通过、额度正常（ASR 链路密钥/签名/额度三者均 OK）")
                else:
                    print("[ERR] 讯飞返回：" + json.dumps(node, ensure_ascii=False)[:600])
                data = node.get("data", {})
                if data.get("status") == 2:
                    break
    except Exception as e:  # noqa: BLE001
        print(f"[WS_ERROR] {type(e).__name__}: {e}")


if __name__ == "__main__":
    asyncio.run(main())
