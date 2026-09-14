from __future__ import annotations

import os
import re
from scrapers.base import BaseScraper


class VietcapScraper(BaseScraper):
    source = "vietcap"
    login_url = "https://www.vietcap.com.vn/en/research-center/"
    reports_url = "https://www.vietcap.com.vn/en/research-center/"

    async def login(self, page):
        username = os.environ["VIETCAP_USERNAME"]
        password = os.environ["VIETCAP_PASSWORD"]

        print("[INFO] Vietcap: logging in...")
        await page.goto(self.login_url, wait_until="domcontentloaded")

        user_box = page.get_by_placeholder(re.compile(r"username|tài khoản", re.I))
        if await user_box.count() == 0:
            user_box = page.locator('input[name*="user" i], input[type="text"]').first

        pass_box = page.get_by_placeholder(re.compile(r"password|mật khẩu", re.I))
        if await pass_box.count() == 0:
            pass_box = page.locator('input[type="password"]').first

        await user_box.fill(username)
        await pass_box.fill(password)

        login_button = page.get_by_role("button", name=re.compile(r"login|đăng nhập", re.I))
        if await login_button.count() == 0:
            login_button = page.locator('button[type="submit"]').first

        await login_button.click()
        await page.wait_for_load_state("networkidle")

        if await page.locator('input[type="password"]:visible').count() > 0:
            raise RuntimeError("Vietcap login may require OTP/CAPTCHA or selector adjustment. Use bootstrap_auth.py if needed.")

    async def ensure_logged_in(self, page):
        await page.goto(self.reports_url, wait_until="domcontentloaded")
        if await page.locator('input[type="password"]:visible').count() > 0:
            await self.login(page)

    async def collect_report_links(self, page):
        await page.goto(self.reports_url, wait_until="networkidle")
        links = await page.locator('a[href*="/research-center/"]').evaluate_all(
            """els => els.map(a => ({href: a.href, text: (a.innerText || a.textContent || '').trim()}))"""
        )

        items, seen = [], set()
        for x in links:
            href = x.get("href") or ""
            title = (x.get("text") or "").strip()
            tail = href.rstrip("/").split("/")[-1]
            if tail in {"research-center", "en", "vi"} or href in seen or not title:
                continue
            seen.add(href)
            items.append({"title": title[:300], "url": href})
        return items
