from __future__ import annotations

import os
from pathlib import Path
from playwright.async_api import async_playwright


async def launch_browser(storage_state: Path | None = None):
    pw = await async_playwright().start()
    headless = os.getenv("HEADLESS", "true").lower() not in ("0", "false", "no")
    browser = await pw.chromium.launch(headless=headless, args=["--disable-dev-shm-usage"])

    kwargs = {
        "accept_downloads": True,
        "viewport": {"width": 1440, "height": 1000},
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
    }
    if storage_state and storage_state.exists():
        kwargs["storage_state"] = str(storage_state)

    context = await browser.new_context(**kwargs)
    return pw, browser, context
