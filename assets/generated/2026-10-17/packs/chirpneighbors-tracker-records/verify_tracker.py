from playwright.sync_api import sync_playwright
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import json,threading,datetime
R=Path(__file__).parent
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'target':str(R/'tracker.html'),'checks':[],'errors':[],'scope':'local tracker only; no app integration evidence'}
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1400,'height':1000});page.on('pageerror',lambda e:receipt['errors'].append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/tracker.html');page.wait_for_selector('#rows tr');receipt['checks'].append({'name':'initial rows and embedded data','passed':page.locator('#rows tr').count()==50})
  page.locator('#species').select_option('american_crow');receipt['checks'].append({'name':'distinct American crow filter','passed':page.locator('#rows tr').count()>0 and all('american_crow' in t for t in page.locator('#rows tr td:first-child').all_inner_texts())})
  page.locator('#species').select_option('common_raven');receipt['checks'].append({'name':'distinct common raven filter','passed':page.locator('#rows tr').count()>0 and all('common_raven' in t for t in page.locator('#rows tr td:first-child').all_inner_texts())})
  page.locator('#family').select_option('bird');page.locator('#species').select_option('');page.locator('#state').select_option('reviewed');receipt['checks'].append({'name':'reviewed bird rows separate from integration','passed':'10 matches' in page.locator('#shown').inner_text() and 'integrated: unverified' in page.locator('#rows').inner_text()})
  page.locator('#family').select_option('');page.locator('#state').select_option('');page.locator('#search').fill('no-dedicated-slot');receipt['checks'].append({'name':'unsupported runtime slots searchable','passed':page.locator('#rows tr').count()>0})
  page.locator('#search').fill('Corvus corax');receipt['checks'].append({'name':'scientific identity searchable','passed':page.locator('#rows tr').count()>0 and all('common_raven' in t for t in page.locator('#rows tr td:first-child').all_inner_texts())})
  page.locator('#search').fill('');page.locator('#next').click();receipt['checks'].append({'name':'next page','passed':'page 2/' in page.locator('#shown').inner_text()});page.locator('#previous').click();receipt['checks'].append({'name':'previous page','passed':'page 1/' in page.locator('#shown').inner_text()})
  page.locator('details').filter(has=page.locator('#previews')).first.locator('summary').click();page.wait_for_function('Array.from(document.querySelectorAll("#previews img")).every(i=>i.complete&&i.naturalWidth>0)');receipt['checks'].append({'name':'nine GIF preview files decode','passed':page.locator('#previews img').count()==9})
  receipt['checks'].append({'name':'San Diego first scope visible','passed':'San Diego' in page.locator('#region').inner_text()})
  page.locator('details').filter(has=page.locator('#card-preview')).first.locator('summary').first.click();page.locator('#card-species').select_option('american_crow');receipt['checks'].append({'name':'source-cited American crow learning preview','passed':page.locator('#card-preview').get_by_text('American Crow',exact=False).count()>0 and page.locator('#card-preview a').count()>0})
  page.locator('#pack').select_option('san-diego-proposed-first-release');page.locator('#gap').select_option('scale');receipt['checks'].append({'name':'pack-specific missing calibration query','passed':page.locator('#rows tr').count()>0})
  page.locator('#gap').select_option('runtime');receipt['checks'].append({'name':'runtime gap query remains separate from art','passed':page.locator('#rows tr').count()>0})
  page.locator('#gap').select_option('license');receipt['checks'].append({'name':'candidate source license evidence remains pending','passed':page.locator('#rows tr').count()>0})
  page.locator('#gap').select_option('integration');receipt['checks'].append({'name':'integration query does not promote candidates','passed':'integrated: unverified' in page.locator('#rows').inner_text()})
  page.screenshot(path='/tmp/chirp-tracker-internal-qa.png');b.close()
finally:server.shutdown();server.server_close()
receipt['passed']=all(c['passed'] for c in receipt['checks']) and not receipt['errors'];(R/'receipts/tracker-browser-check.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));assert receipt['passed']
