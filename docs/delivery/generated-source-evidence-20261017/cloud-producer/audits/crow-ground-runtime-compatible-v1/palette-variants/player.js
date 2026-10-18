'use strict';
const frameAt=ms=>{if(!Number.isFinite(ms)||ms<0)throw Error('invalid time');return {clipId:'idle',renderFrameId:'crow-ground-idle-runtime186-c12',elapsedMs:ms,globalTick:Math.floor(ms*30/1000),loopTick:Math.floor(ms*30/1000)%120,frameIndex:0};};
if(typeof module!=='undefined')module.exports={frameAt};
if(typeof window!=='undefined'){
 let token=0,paused=false,start=0;const canvases=['normal','large'].map(id=>document.getElementById(id));const src=document.getElementById('source');const old=new Image(),im=new Image();
 const load=(obj,url)=>new Promise((resolve,reject)=>{obj.onload=resolve;obj.onerror=reject;obj.src=url;});
 const draw=ms=>{for(const c of canvases){const x=c.getContext('2d');x.clearRect(0,0,186,186);x.imageSmoothingEnabled=false;x.drawImage(im,0,0);}const x=src.getContext('2d');x.clearRect(0,0,186,186);x.drawImage(old,0,0);window.crowPaletteState=frameAt(ms);document.getElementById('numeric').textContent=JSON.stringify(window.crowPaletteState,null,2);};
 const run=()=>{paused=false;start=performance.now();const own=++token;function step(now){if(own!==token||paused)return;draw(Math.max(0,now-start));requestAnimationFrame(step);}requestAnimationFrame(step);};
 window.crowPalettePreview={sampleAt:ms=>{paused=true;++token;draw(ms);},pause:()=>{paused=true;++token;},replay:run};
 Promise.all([load(old,'reviewed64-reference.png'),load(im,'crow-ground-idle186-total12.png')]).then(()=>{draw(0);window.crowPaletteReady=true;run();}).catch(e=>window.crowPaletteError=String(e));
 for(const [id,color]of [['light','#d9d4bd'],['dark','#17221f']])document.getElementById(id).onclick=()=>document.querySelectorAll('canvas').forEach(c=>c.style.backgroundColor=color);
 document.getElementById('reset').onclick=run;document.getElementById('pause').onclick=()=>window.crowPalettePreview.pause();
}
