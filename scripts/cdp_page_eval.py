#!/usr/bin/env python3
"""Evaluate a read-only JavaScript expression in an already-open Chrome page."""

from __future__ import annotations

import argparse
import asyncio
import json
import base64
import sys
import urllib.request
from typing import Any

import websockets


def chrome_targets(port: int) -> list[dict[str, Any]]:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list") as response:
        return json.load(response)


async def evaluate(
    websocket_url: str,
    expression: str,
    navigate: str | None,
    wait_ms: int,
    screenshot: str | None,
) -> Any:
    async with websockets.connect(websocket_url, max_size=64 * 1024 * 1024) as websocket:
        next_id = 1

        async def send(method: str, params: dict[str, Any] | None = None) -> int:
            nonlocal next_id
            message_id = next_id
            next_id += 1
            await websocket.send(
                json.dumps({"id": message_id, "method": method, "params": params or {}})
            )
            return message_id

        async def receive(message_id: int) -> dict[str, Any]:
            while True:
                message = json.loads(await websocket.recv())
                if message.get("id") == message_id:
                    if "error" in message:
                        raise RuntimeError(message["error"])
                    return message.get("result", {})

        await send("Page.enable")
        if navigate:
            navigation_id = await send("Page.navigate", {"url": navigate})
            await receive(navigation_id)
            await asyncio.sleep(wait_ms / 1000)
        if screenshot:
            screenshot_id = await send("Page.captureScreenshot", {"format": "png"})
            screenshot_result = await receive(screenshot_id)
            with open(screenshot, "wb") as handle:
                handle.write(base64.b64decode(screenshot_result["data"]))
            return {"screenshot": screenshot}
        eval_id = await send(
            "Runtime.evaluate",
            {
                "expression": expression,
                "awaitPromise": True,
                "returnByValue": True,
            },
        )
        result = (await receive(eval_id)).get("result", {})
        if "value" in result:
            return result["value"]
        return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9223)
    parser.add_argument("--url-contains", default="dcs.cloud")
    parser.add_argument("--navigate")
    parser.add_argument("--wait-ms", type=int, default=2000)
    parser.add_argument("--screenshot")
    parser.add_argument("expression")
    args = parser.parse_args()

    candidates = [
        target
        for target in chrome_targets(args.port)
        if target.get("type") == "page"
        and args.url_contains in target.get("url", "")
    ]
    if not candidates:
        raise SystemExit(f"No page URL contains {args.url_contains!r}")
    target = candidates[0]
    result = asyncio.run(
        evaluate(
            target["webSocketDebuggerUrl"],
            args.expression,
            args.navigate,
            args.wait_ms,
            args.screenshot,
        )
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"cdp_page_eval failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
