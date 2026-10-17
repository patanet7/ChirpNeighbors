const {chromium}=require('playwright');const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=__dirname;const html=fs.readFileSync(path.join(root,'review.html'),'utf8');
const old="function loop(now){if(playing){tick=Math.min(60,Math.floor((now-start)*30/1000));if(tick===60)playing=false;draw()}requestAnimationFrame(loop)}";
const fixed="function loop(now){if(playing){const end=manifest.ticks.length-1;const elapsed=Math.max(0,Math.min(end*1000/manifest.tickRate,now-start));tick=Math.max(0,Math.min(end,Math.floor(elapsed*manifest.tickRate/1000)));if(tick===end)playing=false;draw()}requestAnimationFrame(loop)}";
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
try{const results=[];for(const [variant,body] of [['old-control',html.replace(fixed,old)],['fixed',html]]){
 const page=await browser.newPage({viewport:{width:1200,height:950}});const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.evaluate(()=>{window.rafQueue=[];window.requestAnimationFrame=fn=>{window.rafQueue.push(fn);return window.rafQueue.length}});await page.setContent(body);await page.waitForFunction(()=>window.reviewState&&window.rafQueue.length);
 const stale=await page.evaluate(()=>{try{window.rafQueue.shift()(performance.now()-10000);return {error:null,state:window.reviewState}}catch(e){return {error:e.message,state:window.reviewState}}});
 let end=null,replay=null;if(variant==='fixed'){
  end=await page.evaluate(()=>{window.rafQueue.shift()(performance.now()+1000000);return window.reviewState});await page.click('#replay');replay=await page.evaluate(()=>{window.rafQueue.shift()(performance.now()-10000);return window.reviewState});
  if(stale.error||stale.state.tick!==0||!end||end.tick!==60||end.playing||end.root[0]!==20||!replay||replay.tick!==0||!replay.playing||errors.length)throw Error('Fixed timing regression check failed');
 }else if(!stale.error||!stale.error.includes('pose'))throw Error('Old control failed to reproduce original defect');
 results.push({variant,staleCallback:stale,terminalCallback:end,manualReplayStaleCallback:replay,pageErrors:errors});await page.close();
 }
 const r={status:'passed',method:'Real Chromium page.setContent with controlled requestAnimationFrame callback timestamps, negative/stale timestamp and far-future terminal timestamp; old-code in-memory control reproduces defect. No source files altered.',testedAt:new Date().toISOString(),htmlSHA256:crypto.createHash('sha256').update(html).digest('hex'),results,noCaptureImagesCreated:true};fs.writeFileSync(path.join(root,'receipts','viewer-timing-validation.json'),JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify(r));
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
