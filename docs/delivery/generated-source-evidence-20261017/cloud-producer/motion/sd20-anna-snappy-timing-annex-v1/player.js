'use strict';
// Authored pose and root channels share elapsed time but never reset each other.
function stateAt(data,elapsedMs,mode='snappy'){
 if(!Number.isFinite(elapsedMs)||elapsedMs<0)throw new RangeError('elapsedMs must be finite and nonnegative');
 if(!data.modes[mode])throw new RangeError('unknown comparison mode');
 const path=data.modes[mode],tick=elapsedMs*30/1000,poseTick=Math.floor(tick),segments=path.segments;
 let segment=segments.find(s=>tick>=s.ticks[0]&&tick<s.ticks[1])||segments[segments.length-1];
 let u=Math.max(0,Math.min(1,(tick-segment.ticks[0])/(segment.ticks[1]-segment.ticks[0])));
 let v=segment.interpolation==='uSquared'?u*u:segment.interpolation==='2uMinusUSquared'?2*u-u*u:0;
 const root=segment.interpolation==='hold'?[...segment.rootTo]:segment.rootFrom.map((x,i)=>x+(segment.rootTo[i]-x)*v);
 const clip=data.clips.find(c=>c.id===segment.poseClipId);if(!clip)throw new Error('missing source clip');
 const total=clip.frames.reduce((n,f)=>n+f.durationTicks,0);let phaseTick=poseTick%total,selected=clip.frames[0];
 for(const f of clip.frames){if(phaseTick<f.durationTicks){selected=f;break}phaseTick-=f.durationTicks}
 const frame=data.frames.find(f=>f.id===selected.frameId);if(!frame)throw new Error('missing source frame');
 const duration=path.durationTicks||path.totalTicks;
 return {elapsedMs,mode,rootTick:tick,poseTick,phaseTick,frameId:frame.id,primarySourceFrameId:frame.primarySourceFrameId,pivot:{...frame.pivot},root,phase:segment.phase||segment.poseClipId,poseClipId:clip.id,terminal:tick>=duration,contacts:[]};
}
if(typeof module!=='undefined')module.exports={stateAt};
if(typeof window!=='undefined')window.stateAt=stateAt;
async function startPreview(){
 const data=await(await fetch('preview-data.json')).json(),atlas=new Image();atlas.src=data.atlas.file;await atlas.decode();
 const views=[document.querySelector('#yard'),document.querySelector('#zoom')];
 let mode='snappy',epoch=performance.now(),generation=0,raf=0,running=true,lastState=null;
 function render(elapsedMs){
  const state=stateAt(data,elapsedMs,mode),frame=data.frames.find(f=>f.id===state.frameId),r=frame.sourceRect;
  for(const c of views){const scale=c.width/data.viewWorldCanvas[0],ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;ctx.clearRect(0,0,c.width,c.height);const x=data.displayRootBase[0]+state.root[0]-frame.pivot.x/frame.sourcePixelsPerWorldUnit,y=data.displayRootBase[1]+state.root[1]-frame.pivot.y/frame.sourcePixelsPerWorldUnit;ctx.drawImage(atlas,r.x,r.y,r.width,r.height,x*scale,y*scale,frame.world.width*scale,frame.world.height*scale)}
  lastState=state;window.currentDartState=state;document.querySelector('#numeric').textContent=JSON.stringify(state,null,2);return state;
 }
 function step(now,token){if(token!==generation||!running)return false;render(Math.max(0,now-epoch));raf=requestAnimationFrame(t=>step(t,token));return true}
 function replay(){cancelAnimationFrame(raf);generation++;epoch=performance.now();running=true;const token=generation;raf=requestAnimationFrame(t=>step(t,token));return token}
 function pause(){cancelAnimationFrame(raf);generation++;running=false;return generation}
 window.annexController={data,stateAt:(t,m=mode)=>stateAt(data,t,m),sampleAt:t=>render(t),pause,replay,setMode:m=>{if(!data.modes[m])throw new Error('unknown mode');mode=m;document.querySelector('#mode').value=m;return replay()},generation:()=>generation,current:()=>lastState,callbackForTest:(now,token)=>step(now,token)};
 document.querySelector('#mode').onchange=e=>window.annexController.setMode(e.target.value);
 document.querySelector('#replay').onclick=replay;document.querySelector('#pause').onclick=pause;
 for(const[id,color]of[['light','#d9d4bd'],['dark','#17221f']])document.querySelector('#'+id).onclick=()=>views.forEach(c=>c.style.background=color);
 document.querySelector('#sample').onclick=()=>{pause();render(Number(document.querySelector('#elapsed').value))};
 replay();window.annexReady=true;
}
if(typeof window!=='undefined')startPreview().catch(e=>{window.annexError=String(e);document.querySelector('#numeric').textContent=String(e)});
