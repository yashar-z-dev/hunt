from playwright.sync_api import sync_playwright

def fetch_from_browser(config):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(config["base_url"], timeout=config["timeout"] * 1000)

            # Wait for data to load
            page.wait_for_selector("div.program-card")

            # Extract all program cards
            elements = page.query_selector_all("div.program-card")
            programs = []
            for el in elements:
                title = el.query_selector("h2").inner_text() if el.query_selector("h2") else "N/A"
                country = el.query_selector(".country").inner_text() if el.query_selector(".country") else "N/A"
                reward = el.query_selector(".reward").inner_text() if el.query_selector(".reward") else "N/A"

                programs.append({
                    "title": title,
                    "country": country,
                    "reward_range": reward
                })

            browser.close()
            return programs

    except Exception as e:
        return {"error": f"Browser fetch failed: {e}"}
