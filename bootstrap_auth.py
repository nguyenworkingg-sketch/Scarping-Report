import argparse
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

URLS = {
    "hsc": "https://research.hsc.com.vn/en/user/login",
    "vietcap": "https://www.vietcap.com.vn/en/research-center/",
}


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", choices=URLS)
    args = parser.parse_args()

    Path("auth").mkdir(exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(URLS[args.source])

        print(f"\nĐăng nhập {args.source.upper()} thủ công trong cửa sổ trình duyệt.")
        print("Nếu có OTP/CAPTCHA, hoàn tất như bình thường.")
        input("Khi đã đăng nhập xong và thấy trang research, quay lại cửa sổ này và nhấn Enter... ")

        output = Path("auth") / f"{args.source}_storage_state.json"
        await context.storage_state(path=str(output))
        print(f"Đã lưu session vào: {output}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
