from pathlib import Path
from playwright.sync_api import sync_playwright
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import json,threading,hashlib,zipfile,datetime
R=Path(__file__).parent;P=R/'batches/house-finch-perching-review-v1';checks=[];review=json.loads((P/'reuse-review.json').read_text());bank=json.loads((R/'frame-bank.json').read_text());idx={f['frameId']:f for f in bank['frames']}
checks.append({'name':'26 prior frames reviewed with zero verified reuse','passed':len(review['rows'])==26 and review['summary']['verifiedNarrowBranchReuses']==0 and review['summary']['verifiedFlatPlatformReuses']==0})
for row in review['rows']:assert row['frameId'] in idx;assert hashlib.sha256((R/row['sourceFile']).read_bytes()).hexdigest()==row['sourceFileSha256']
checks.append({'name':'all reviewed source pixel files unchanged','passed':True})
for sex in ['male','female']:
 for action in ['idle','feed']:
  n=f'house-finch-{sex}-{action}-v1';path=f'batches/{n}/manifest.json'
  with zipfile.ZipFile(R/'delivery'/f'ChirpNeighbors-{n}.zip') as z:assert z.read(path)==(R/path).read_bytes()
checks.append({'name':'four delivered animation manifests unchanged','passed':True})
class H(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(H,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start();errors=[]
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/perch-test-scene.html');page.wait_for_selector('#pose option',state='attached');page.wait_for_function('document.querySelector("#verdict").textContent.length>0');checks.append({'name':'five embedded source/candidate pose choices','passed':page.locator('#pose option').count()==5});page.locator('#pose').select_option('4');checks.append({'name':'candidate rejection explicit in scene','passed':'Not accepted' in page.locator('#verdict').inner_text()});page.locator('#support').select_option('flat');page.locator('#front').check();page.locator('#anchors').uncheck();checks.append({'name':'support/occlusion/diagnostic controls operate','passed':not errors});b.close()
finally:server.shutdown();server.server_close()
receipt={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,'pageErrors':errors,'passed':all(c['passed'] for c in checks) and not errors,'priorHarnessIssue':'Option nodes are attached but not visible until select opens; wait corrected to attached. No page error observed.','scope':'diagnostic scene/source preservation, no biomechanical or app integration acceptance'};(P/'review-check.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));assert receipt['passed']
