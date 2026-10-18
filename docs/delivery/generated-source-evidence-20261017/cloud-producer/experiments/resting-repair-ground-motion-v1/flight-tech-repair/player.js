(async()=>{
 const h=await(await fetch('airborne-source-handoff.json')).json(),ims={};
 for(const f of h.frames)for(const kind of ['raw96','codec64']){const im=new Image();im.src=kind==='raw96'?f.original96PNG:f.png;await im.decode();ims[kind+'/'+f.id]=im}
 let tick=0,running=false,elapsedMs=0,epoch=0;const frame=()=>h.frames[tick%4];
 function state(){return {tick,running,elapsedMs,frameId:frame().id,primarySourceFrameID:frame().sourceFrameID,worldCanvas:[64,64],rawCanvas:[96,96],codecCanvas:[64,64],density:1,proposedPivot:[36,45],rootTravel:[0,0],contacts:[],supportState:'airborne source artwork',durationTicks:24,tickRate:30,loop:false,physicalWingbeatClaim:false,fullFlightAdmission:false}}
 function draw(){for(const kind of ['raw96','codec64'])for(const bg of ['light','dark']){const c=document.getElementById(kind+'-'+bg),x=c.getContext('2d');x.fillStyle=bg==='light'?'#e5e0cd':'#182a32';x.fillRect(0,0,c.width,c.height);x.imageSmoothingEnabled=false;x.drawImage(ims[kind+'/'+frame().id],0,0)}document.getElementById('tick').value=tick;document.getElementById('state').textContent=JSON.stringify(state(),null,2)}
 function seek(t){++epoch;running=false;tick=Math.max(0,Math.min(23,Math.floor(t)));elapsedMs=tick*1000/30;draw();return state()}
 function play(){const e=++epoch,start=performance.now();tick=0;running=true;elapsedMs=0;draw();function step(now){if(e!==epoch||!running)return;elapsedMs=now-start;tick=Math.min(23,Math.floor(elapsedMs*30/1000));if(elapsedMs>=800)running=false;draw();if(running)requestAnimationFrame(step)}requestAnimationFrame(step);return state()}
 document.getElementById('play').onclick=play;document.getElementById('tick').oninput=e=>seek(+e.target.value);window.FLIGHT_TECH_REVIEW=window.AIRBORNE_TECH_REVIEW={ready:true,play,seek,getState:state,pause:()=>seek(tick)};draw();
})().catch(e=>{window.FLIGHT_TECH_ERROR=String(e);throw e});
