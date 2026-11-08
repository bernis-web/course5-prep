#!/usr/bin/env python3
"""Capture response bodies for selected Chrome DevTools Protocol network events."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import urllib.request
from typing import Any

import websockets


def chrome_targets(port: int) -> list[dict[str, Any]]:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list") as response:
        return json.load(response)


async def capture(
    websocket_url: str,
    navigate: str,
    pattern: re.Pattern[str],
    wait_ms: int,
    click_selector: str | None,
    click_index: int,
) -> list[dict[str, Any]]:
    captured: list[dict[str, Any]] = []
    requests: dict[str, dict[str, Any]] = {}
    next_id = 1

    async with websockets.connect(websocket_url, max_size=128 * 1024 * 1024) as websocket:
        async def send(method: str, params: dict[str, Any] | None = None) -> int:
            nonlocal next_id
            message_id = next_id
            next_id += 1
            await websocket.send(
                json.dumps({"id": message_id, "method": method, "params": params or {}})
            )
            return message_id

        async def receive_response(message_id: int) -> dict[str, Any]:
            while True:
                message = json.loads(await websocket.recv())
                if message.get("id") == message_id:
                    if "error" in message:
                        raise RuntimeError(message["error"])
                    return message.get("result", {})

        enable_network_id = await send("Network.enable")
        await receive_response(enable_network_id)
        disable_cache_id = await send("Network.setCacheDisabled", {"cacheDisabled": True})
        await receive_response(disable_cache_id)

        if navigate:
            navigation_id = await send("Page.navigate", {"url": navigate})
            await receive_response(navigation_id)

        if click_selector:
            await asyncio.sleep(1.0)
            click_id = await send(
                "Runtime.evaluate",
                {
                    "expression": (
                        f"document.querySelectorAll({click_selector!r})"
                        f"[{click_index}].click()"
                    ),
                    "awaitPromise": True,
                    "returnByValue": True,
                },
            )
            await receive_response(click_id)

        deadline = asyncio.get_running_loop().time() + wait_ms / 1000
        pending_bodies: set[str] = set()
        while asyncio.get_running_loop().time() < deadline:
            try:
                raw_message = await asyncio.wait_for(websocket.recv(), timeout=0.25)
            except asyncio.TimeoutError:
                if pending_bodies and not captured:
                    deadline = max(deadline, asyncio.get_running_loop().time() + 1.0)
                continue

            message = json.loads(raw_message)
            method = message.get("method")
            params = message.get("params", {})
            if method == "Network.responseReceived":
                response = params.get("response", {})
                url = response.get("url", "")
                if pattern.search(url):
                    request_id = params.get("requestId", "")
                    requests[request_id] = {
                        "url": url,
                        "status": response.get("status"),
                    }
                    pending_bodies.add(request_id)
            elif method == "Network.loadingFinished" and params.get("requestId") in pending_bodies:
                request_id = params["requestId"]
                body_id = await send("Network.getResponseBody", {"requestId": request_id})
                body_result = await receive_response(body_id)
                item = dict(requests[request_id])
                body = body_result.get("body", "")
                if body_result.get("base64Encoded"):
                    item["base64_body"] = body
                else:
                    try:
                        item["json"] = json.loads(body)
                    except json.JSONDecodeError:
                        item["text"] = body
                captured.append(item)
                pending_bodies.remove(request_id)

        return captured


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9223)
    parser.add_argument("--url-contains", default="dcs.cloud")
    parser.add_argument("--navigate")
    parser.add_argument("--pattern", required=True)
    parser.add_argument("--wait-ms", type=int, default=15000)
    parser.add_argument("--click-selector")
    parser.add_argument("--click-index", type=int, default=0)
    args = parser.parse_args()

    candidates = [
        target
        for target in chrome_targets(args.port)
        if target.get("type") == "page" and args.url_contains in target.get("url", "")
    ]
    if not candidates:
        raise SystemExit(f"No page URL contains {args.url_contains!r}")

    result = asyncio.run(
        capture(
            candidates[0]["webSocketDebuggerUrl"],
            args.navigate,
            re.compile(args.pattern),
            args.wait_ms,
            args.click_selector,
            args.click_index,
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"cdp_capture_responses failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
