import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(user_data_dir=r'C:\OsintNeoAi\.playwright_session', headless=False)
    page = context.pages[0] if context.pages else context.new_page()
    page.goto('https://procurement.opengov.com/portal/ocgov?departmentId=all&status=all&page=1&limit=50&sortField=releaseProjectDate&sortDirection=ASC', wait_until='domcontentloaded')
    time.sleep(5)
    
    links = page.query_selector_all('a')
    print('Total anchor links on page 1:', len(links))
    for l in links[:20]:
        cls = l.get_attribute('class') or ''
        txt = l.inner_text().strip().replace('\n', ' ')
        href = l.get_attribute('href') or ''
        print(f" - class='{cls[:40]}' | href='{href[:40]}' | txt='{txt[:40]}'")
        
    context.close()
