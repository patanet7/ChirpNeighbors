(async()=>{
 const family=await(await fetch('family-handoff.json')).json(),images={};
 for(const frame of family.frames){const im=new Image();im.src=frame.png;await im.decode();images[frame.id]=im}
 let option='blink',tick=0,running=false,elapsedMs=0,epoch=0;
 const clip=()=>family.clips.find(c=>c.id===option);
 function frameId(){let end=0;for(let i=0;i<clip().durationTicks.length;i++){end+=clip().durationTicks[i];if(tick<end)return clip().frameIds[i]}return clip().frameIds.at(-1)}
 function state(){return{option,tick,running,elapsedMs,tickRate:30,durationTicks:clip().durationTicks,frameId:frameId(),registeredSourceID:family.frames.find(f=>f.id===frameId()).registeredSourceID,fullWorldCanvas:family.fullWorldCanvas,displayStage:family.displayStage,candidateCanvas:family.candidateCanvas,commonCropOrigin:family.commonCropOrigin,candidatePivot:family.candidatePivot,contacts:[],geometryScope:'image-registration-only',physicalSupportReviewed:false,supportWorld:null,sourceReviewUsefulness:'UNKNOWN for assembled family',runtimeAdmission:false,oneShotSourcePreview:true,terminalTick:89,nominalDurationMs:3000}}
 function draw(){for(const bg of ['light','dark']){const c=document.getElementById(bg),x=c.getContext('2d');x.fillStyle=bg==='light'?'#e5e0cd':'#182a32';x.fillRect(0,0,120,120);x.imageSmoothingEnabled=false;x.drawImage(images[frameId()],...family.commonCropOrigin)}document.getElementById('state').textContent=JSON.stringify(state(),null,2);document.getElementById('tick').value=tick}
 function seek(t){epoch++;running=false;tick=Math.max(0,Math.min(89,Math.floor(t)));elapsedMs=tick*1000/30;draw();return state()}
 function select(id){if(!['blink','look','idle'].includes(id))throw Error('Unknown clip');option=id;document.getElementById('option').value=id;return seek(0)}
 function play(){const id=++epoch,start=performance.now();tick=0;elapsedMs=0;running=true;draw();function step(now){if(id!==epoch||!running)return;elapsedMs=Math.max(0,now-start);tick=Math.min(89,Math.floor(elapsedMs*30/1000));if(elapsedMs>=3000)running=false;draw();if(running)requestAnimationFrame(step)}requestAnimationFrame(step);return state()}
 for(const role of ['neutral','blink','look'])for(const bg of ['light','dark']){const c=document.getElementById('still-'+role+'-'+bg),x=c.getContext('2d');x.fillStyle=bg==='light'?'#e5e0cd':'#182a32';x.fillRect(0,0,120,120);x.imageSmoothingEnabled=false;x.drawImage(images[role],...family.commonCropOrigin)}
 document.getElementById('option').onchange=e=>select(e.target.value);document.getElementById('play').onclick=play;document.getElementById('tick').oninput=e=>seek(+e.target.value);window.FAMILY_REVIEW={ready:true,select,play,seek,getState:state};draw();
})();
