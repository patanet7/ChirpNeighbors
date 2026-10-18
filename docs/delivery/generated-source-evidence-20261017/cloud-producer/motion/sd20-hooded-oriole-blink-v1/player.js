'use strict';
function frameAt(profile,clipId,elapsedMs,once=false){
 if(!Number.isFinite(elapsedMs)||elapsedMs<0)throw new RangeError('invalid elapsed time');
 const clip=profile.clips.find(c=>c.id===clipId);if(!clip)throw new Error('missing clip');
 const globalTick=Math.floor(elapsedMs*clip.tickRate/1000),totalTicks=clip.frames.reduce((n,f)=>n+f.durationTicks,0);
 const terminal=once&&globalTick>=totalTicks;
 let tick=(!once&&clip.loop)?globalTick%totalTicks:Math.min(globalTick,totalTicks-1);
 for(const step of clip.frames){if(tick<step.durationTicks)return{frame:profile.frames.find(f=>f.id===step.frameId),globalTick,totalTicks,terminal,clipId};tick-=step.durationTicks;}
 throw new Error('invalid clip frame schedule');
}
if(typeof module!=='undefined')module.exports={frameAt};
if(typeof window!=='undefined')(async()=>{
 const profile=await(await fetch('texture-review-manifest.json')).json(),map=await(await fetch('frame-to-action-map.json')).json();
 const atlas=new Image();atlas.src=map.atlasBinding.file;await atlas.decode();
 let epoch=0,generation=0,raf=0,running=false,clipId='blink';
 function draw(elapsedMs){const state=frameAt(profile,clipId,elapsedMs,!document.querySelector('#loop').checked),f=state.frame,r=f.sourceRect;
  for(const c of document.querySelectorAll('canvas')){const ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;ctx.clearRect(0,0,192,192);ctx.drawImage(atlas,r.x,r.y,r.width,r.height,0,0,192,192);if(document.querySelector('#contacts').checked){ctx.fillStyle='#e65388';for(const p of f.contacts)ctx.fillRect(p.x,p.y,1,1);ctx.fillStyle='#238dbd';ctx.fillRect(f.pivot.x-1,f.pivot.y,3,1);}}
  const row=map.sourceToRenderFrames.find(x=>x.renderFrameId===f.id);const numeric={elapsedMs,clipId,globalTick:state.globalTick,totalTicks:state.totalTicks,terminal:state.terminal,renderFrameId:f.id,primarySourceFrameId:row.primarySourceFrameId,pivot:f.pivot,contacts:f.contacts,density:f.sourcePixelsPerWorldUnit,world:f.world,heldSource:true,appBound:false};
  window.orioleState=numeric;document.querySelector('#numeric').textContent=JSON.stringify(numeric,null,2);return numeric;
 }
 function tick(now,g){if(g!==generation||!running)return;const s=draw(Math.max(0,now-epoch));if(s.terminal){running=false;return;}raf=requestAnimationFrame(t=>tick(t,g));}
 function replay(id='blink'){clipId=id;generation++;cancelAnimationFrame(raf);epoch=performance.now();running=true;draw(0);const g=generation;raf=requestAnimationFrame(t=>tick(t,g));}
 function pause(){running=false;generation++;cancelAnimationFrame(raf);}
 window.ORIOLE_BLINK_REVIEW={ready:true,profile,map,replay,pause,sampleAt:t=>{pause();return draw(t);},getState:()=>window.orioleState};
 document.querySelector('#blink').onclick=()=>replay('blink');document.querySelector('#idle').onclick=()=>{pause();clipId='idle';draw(0);};document.querySelector('#pause').onclick=pause;document.querySelector('#loop').onchange=()=>replay(clipId);document.querySelector('#contacts').onchange=()=>draw(window.orioleState?.elapsedMs??0);
 replay('blink');
})().catch(e=>{window.orioleError=String(e);});
