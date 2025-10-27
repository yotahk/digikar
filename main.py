from playwright.sync_api import sync_playwright
from pathlib import Path
import argparse
import sys
from typing import Dict


def open_digikar(
    headless: bool = False,
    wait_ms: int = 3000,
    browser_name: str = "chromium",
    profile_dir: str | Path | None = None,
    auto_select_cert: bool = False,
    user_data_dir: str | Path | None = None,
) -> Path:
    """Open the site and save a screenshot.

    Supports launching a persistent profile so an existing session / client
    certificate can be reused. For Firefox, if `auto_select_cert` is True the
    Firefox user preference `security.default_personal_cert` will be set to
    "Select Automatically" so the browser chooses a certificate without the
    selection dialog.

    Returns the path to the saved screenshot.
    """
    out_path = Path.cwd() / "digikar_screenshot.png"
    profile_dir = Path(profile_dir) if profile_dir else Path.cwd() / ".playwright_profile"

    with sync_playwright() as p:
        browser_name = browser_name.lower()
        # Use a persistent context so the browser profile (certs, cookies) is kept
        if browser_name == "firefox":
            firefox_prefs: Dict[str, str | float | int] | None = {}
            if auto_select_cert:
                # Prefer automatic certificate selection to avoid OS/browser prompt
                firefox_prefs["security.default_personal_cert"] = "Select Automatically"
            context = p.firefox.launch_persistent_context(
                str(profile_dir), headless=headless, firefox_user_prefs=firefox_prefs
            )
        else:
            # cdp_endpoint = "http://localhost:9222/"
            cdp_endpoint = "http://127.0.0.1:9222"
            browser = p.chromium.connect_over_cdp(cdp_endpoint)
            context = browser.contexts[0] if browser.contexts else browser.new_context(viewport={"width": 1280, "height": 800})
            # context = browser.new_context()

        page = context.new_page()
        page.goto("https://digikar.jp")
        page.wait_for_timeout(wait_ms)

        # Print a short snippet of the page body so the caller can verify
        # the expected content (e.g. the patients list) appears. Keep the
        # output limited to avoid flooding the terminal.
        try:
            body_text = page.inner_text("body")
        except Exception:
            # If inner_text fails (some pages), fall back to raw content
            body_text = page.content()
        snippet = body_text.strip().replace("\n", " ")[:1000]
        print("Page body snippet:\n", snippet)

        page.screenshot(path=str(out_path), full_page=True)

        # Close the persistent context (keeps profile on disk)
        context.close()

    return out_path


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Open digikar.jp and capture a screenshot using Playwright")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--wait-ms", type=int, default=1000, help="Milliseconds to wait after navigation before screenshot")
    parser.add_argument("--browser", choices=["chromium", "firefox"], default="chromium", help="Browser to use")
    parser.add_argument("--profile-dir", type=str, default=None, help="Path to persistent browser profile (keeps certs/session)")
    parser.add_argument("--auto-select-cert", action="store_true", help="(Firefox only) set security.default_personal_cert to Select Automatically")
    parser.add_argument("--user-data-dir", type=str, default=None, help="Path to Chromium user data directory for logged-in context")

    args = parser.parse_args(argv)

    print(f"Launching {args.browser} (headless={args.headless}) with profile={args.profile_dir} ...")
    out = open_digikar(
        headless=args.headless,
        wait_ms=args.wait_ms,
        browser_name=args.browser,
        profile_dir=args.profile_dir,
        auto_select_cert=args.auto_select_cert,
        user_data_dir=args.user_data_dir,
    )
    print(f"Screenshot saved to: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
