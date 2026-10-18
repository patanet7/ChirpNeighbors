(async()=>{
  const h=await(await fetch('family-handoff.json')).json(), images={};
  for(const f of h.frames) for(const kind of ['raw','codec']) {
    const im=new Image(); im.src=kind==='raw'?f.rawPNG:f.png;
    await im.decode(); images[kind+'/'+f.role]=im;
  }
  let option='blink', tick=0, running=false, elapsedMs=0, epoch=0;
  const clip=()=>h.clips.find(c=>c.id===option);
  function role(){let t=tick;for(let i=0;i<clip().roles.length;i++){if(t<clip().durationTicks[i])return clip().roles[i];t-=clip().durationTicks[i]}return 'neutral'}
  function state(){return {ready:true,option,tick,role:role(),running,elapsedMs,tickRate:30,durationTicks:clip().durationTicks,loop:clip().loop,displayStage:h.displayStage,candidateCanvas:h.candidateCanvas,commonCropOrigin:h.commonCropOrigin,fullPivot:h.fullPivot,candidatePivot:h.candidatePivot,contacts:[],geometryScope:'image-registration-only',physicalSupportReviewed:false,supportWorld:null,runtimeApproval:false}}
  function draw(){for(const kind of ['raw','codec'])for(const bg of ['light','dark']){const c=document.getElementById(kind+'-'+bg),x=c.getContext('2d');x.fillStyle=bg==='light'?'#e5e0cd':'#182a32';x.fillRect(0,0,...h.displayStage);x.imageSmoothingEnabled=false;const o=kind==='raw'?[0,0]:h.commonCropOrigin;x.drawImage(images[kind+'/'+role()],...o)}document.getElementById('state').textContent=JSON.stringify(state(),null,2);document.getElementById('tick').value=tick}
  function seek(t){++epoch;running=false;tick=Math.max(0,Math.min(89,Math.floor(t)));elapsedMs=tick*1000/30;draw();return state()}
  function select(id){if(!h.clips.some(c=>c.id===id))throw Error('Unknown source clip');option=id;document.getElementById('option').value=id;return seek(0)}
  function play(){const e=++epoch,start=performance.now();running=true;tick=0;elapsedMs=0;draw();function step(now){if(e!==epoch||!running)return;elapsedMs=now-start;tick=clip().loop?Math.floor(elapsedMs*30/1000)%90:Math.min(89,Math.floor(elapsedMs*30/1000));if(!clip().loop&&elapsedMs>=3000)running=false;draw();if(running)requestAnimationFrame(step)}requestAnimationFrame(step);return state()}
  document.getElementById('option').onchange=e=>select(e.target.value);document.getElementById('play').onclick=play;document.getElementById('neutral').onclick=()=>seek(0);document.getElementById('tick').oninput=e=>seek(+e.target.value);
  window.FAMILY_REVIEW=window.REPAIR_REVIEW={ready:true,select,play,seek,getState:state,pause:()=>seek(tick)};draw();
})().catch(e=>{window.FAMILY_REVIEW_ERROR=String(e);throw e});
