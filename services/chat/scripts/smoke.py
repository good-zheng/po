"""Live smoke test against a running uvicorn instance."""

import asyncio

import httpx
import websockets

BASE = "http://127.0.0.1:5090"


async def check_ws() -> None:
    async with websockets.connect("ws://127.0.0.1:5090/ws/chat") as ws:
        await ws.send('{"type":"message","content":"测试"}')
        tokens = ""
        async for raw in ws:
            import json

            frame = json.loads(raw)
            if frame["type"] == "token":
                tokens += frame["content"]
            elif frame["type"] == "done":
                break
        print("WS reply:", tokens)


def check_crud() -> None:
    with httpx.Client(base_url=BASE) as client:
        created = client.post("/api/items", json={"name": "烟测", "price": 9.9})
        print("POST /api/items ->", created.status_code, created.json()["id"])
        item_id = created.json()["id"]

        print("GET /api/items/{id} ->", client.get(f"/api/items/{item_id}").status_code)
        patched = client.patch(f"/api/items/{item_id}", json={"price": 8.8})
        print("PATCH ->", patched.status_code, "price:", patched.json()["price"])
        print("GET /api/items ->", client.get("/api/items").status_code)
        print("DELETE ->", client.delete(f"/api/items/{item_id}").status_code)
        print("GET missing ->", client.get(f"/api/items/{item_id}").status_code)


check_crud()
asyncio.run(check_ws())
print("SMOKE OK")
