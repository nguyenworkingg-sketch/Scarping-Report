from __future__ import annotations

import os
from scrapers.base import BaseScraper


class HSCScraper(BaseScraper):
    source = "hsc"
    login_url = "https://research.hsc.com.vn/en/user/login"
    reports_url = "https://research.hsc.com.vn/en/"

    async def login(self, page):
        email = os.environ["HSC_EMAIL"]
        password = os.environ["HSC_PASSWORD"]

        print("[INFO] HSC: logging in...")
        await page.goto(self.login_url, wait_until="domcontentloaded")

        email_box = page.get_by_label("Email address", exact=False)
        if await email_box.count() == 0:
            email_box = page.locator('input[type="email"], input[name*="email" i], input[name*="user" i]').first

        password_box = page.get_by_label("Password", exact=False)
        if await password_box.count() == 0:
            password_box = page.locator('input[type="password"]').first

        await email_box.fill(email)
        await password_box.fill(password)

        login_button = page.get_by_role("button", name="Login", exact=False)
        if await login_button.count() == 0:
            login_button = page.locator('button[type="submit"], input[type="submit"]').first

        await login_button.click()
        await page.wait_for_load_state("networkidle")

        if "/user/login" in page.url:
            raise RuntimeError("HSC login failed or requires CAPTCHA/OTP. Use bootstrap_auth.py if needed.")

    async def ensure_logged_in(self, page):
        await page.goto(self.reports_url, wait_until="domcontentloaded")
        if "/user/login" in page.url:
            await self.login(page)

    async def collect_report_links(self, page):
        await page.goto(self.reports_url, wait_until="networkidle")
        links = await page.locator("a[href]").evaluate_all(
            """els => els.map(a => ({href: a.href, text: (a.innerText || a.textContent || '').trim()}))"""
        )

        items, seen = [], set()
        for x in links:
            href = x.get("href") or ""
            title = (x.get("text") or "").strip()
            is_report = "/report/" in href or "FILENAME=" in href or "document?" in href
            if not is_report or href in seen:
                continue
            seen.add(href)
            items.append({"title": title or href.rsplit("/", 1)[-1], "url": href})
        return items
