from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from core.browser import launch_browser
from core.pdf import extract_pdf_text
from core.utils import already_downloaded, report_paths, save_metadata, sha256_file


class BaseScraper:
    source = "base"
    login_url = ""
    reports_url = ""

    def __init__(self):
        self.max_reports = int(os.getenv("MAX_REPORTS", "30"))
        self.state_path = Path("auth") / f"{self.source}_storage_state.json"

    async def login(self, page):
        raise NotImplementedError

    async def collect_report_links(self, page):
        raise NotImplementedError

    async def ensure_logged_in(self, page):
        await page.goto(self.reports_url, wait_until="domcontentloaded")
        if "login" in page.url.lower():
            await self.login(page)

    async def download_one(self, page, item):
        title = item["title"].strip()
        source_url = item["url"]

        if already_downloaded(self.source, source_url):
            print(f"[SKIP] {self.source}: {title}")
            return False

        raw_path, meta_path, text_path = report_paths(self.source, title)
        pdf_url = source_url

        response = await page.context.request.get(source_url)
        body = await response.body()
        content_type = (response.headers.get("content-type") or "").lower()

        if response.ok and ("application/pdf" in content_type or body[:4] == b"%PDF"):
            raw_path.write_bytes(body)
        else:
            await page.goto(source_url, wait_until="domcontentloaded")
            candidates = await page.locator(
                'a[href*=".pdf"], a[href*="document"], a[href*="download"]'
            ).evaluate_all(
                """els => els.map(a => ({href: a.href, text: (a.innerText || a.textContent || '').trim()}))"""
            )

            downloaded = False
            for candidate in candidates:
                href = candidate.get("href")
                if not href:
                    continue
                r = await page.context.request.get(href)
                b = await r.body()
                ct = (r.headers.get("content-type") or "").lower()
                if r.ok and ("application/pdf" in ct or b[:4] == b"%PDF"):
                    raw_path.write_bytes(b)
                    pdf_url = href
                    downloaded = True
                    break

            if not downloaded:
                print(f"[WARN] Could not find PDF: {title}")
                return False

        try:
            text = extract_pdf_text(raw_path, text_path)
        except Exception as exc:
            text = ""
            print(f"[WARN] PDF text extraction failed: {exc}")

        save_metadata(meta_path, {
            "source": self.source,
            "title": title,
            "source_url": source_url,
            "pdf_url": pdf_url,
            "downloaded_at": datetime.now().astimezone().isoformat(),
            "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
            "raw_path": str(raw_path),
            "text_path": str(text_path),
            "sha256": sha256_file(raw_path),
            "text_chars": len(text),
        })

        print(f"[OK] {self.source}: {title}")
        return True

    async def run(self):
        pw = browser = context = None
        try:
            pw, browser, context = await launch_browser(self.state_path)
            page = await context.new_page()
            await self.ensure_logged_in(page)
            self.state_path.parent.mkdir(exist_ok=True)
            await context.storage_state(path=str(self.state_path))

            items = await self.collect_report_links(page)
            print(f"[INFO] {self.source}: found {len(items)} candidates")

            count = 0
            for item in items[: self.max_reports]:
                try:
                    if await self.download_one(page, item):
                        count += 1
                except Exception as exc:
                    print(f"[ERROR] {self.source}: {item.get('title')}: {exc}")

            print(f"[DONE] {self.source}: downloaded {count} new report(s)")
        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()
            if pw:
                await pw.stop()
