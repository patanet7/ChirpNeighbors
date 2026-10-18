from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).parent;B=P.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();J=lambda p:json.loads(p.read_text())
m=J(P/'COHORT-SOURCE-MANIFEST.json');proposal=J(P/'cohort-behavior-proposal.json')
# Producer diagnostics when present; otherwise manual source-art region picks, never tracked anatomical endpoints.
manual={'approach':{'feet':[[80,82],[100,82]],'bill':[131,37]},'settle':{'feet':[[82,82],[107,81]],'bill':[128,38]},'dip':{'feet':[[80,80],[103,79]],'bill':[129,79]},'wingflutter':{'feet':[[80,80],[104,80]],'bill':[128,50]},'shake':{'feet':[[77,82],[102,82]],'bill':[125,32]},'exit-preen':{'feet':[[83,83],[107,83]],'bill':[90,37]}}
rows=[]
for r in m['frames']:
 phase=r['phase'];a=Image.open(P/r['wholeCanvasPNG']).convert('RGBA');c=Image.open(P/r['outputPNG']).convert('RGBA');pts=manual[phase];origins=[];reported={}
 d=B/phase/'measurement-proof.json'
 if d.exists():
  j=J(d);pts['feet']=[x['pixel'] for x in j['actualFootRegionSamples']];pts['bill']=j['beakRegionSample']['pixel'];origins.append({'file':str(d.relative_to(B)),'sha256':sha(d),'fields':['actualFootRegionSamples','beakRegionSample']});reported={'feet':j['actualFootRegionSamples'],'bill':j['beakRegionSample']}
 d=B/phase/(phase+'-key.json')
 if d.exists():
  j=J(d)
  if j.get('footImageProbes'):
   pts['feet']=[x['sourceXY'] for x in j['footImageProbes']];origins.append({'file':str(d.relative_to(B)),'sha256':sha(d),'fields':['footImageProbes']});reported['feet']=j['footImageProbes']
 def point(q,role):
  x,y=q;runtime=[x-4,y-8];rgba=list(a.getpixel((x,y)));assert rgba==list(c.getpixel(tuple(runtime)))
  return {'role':role,'source144Canvas':[144,96],'source144Point':q,'cohortCanvas':[136,80],'cohortPoint':runtime,'actualCohortRGBA':rgba,'uncertaintyOutputPixelsAtLeast':1,'selection':'producer diagnostic coordinate where available; otherwise manually selected image region from coordinate-inspection.png','anatomicalEndpointCertified':False,'admittedContact':False,'diagnosticFloorY':76,'floorResidualPixels':runtime[1]-76,'diagnosticWaterY':70,'waterResidualPixels':runtime[1]-70}
 feet=[point(q,'foot/claw-region image proxy, not tracked sole') for q in pts['feet']];bill=point(pts['bill'],'bill-region image proxy, not certified tip or contact')
 root={'kind':'declared shared root origin, not biological alpha anchor','canvas':[136,80],'point':[77,76],'sampleRGBA':list(c.getpixel((77,76))),'uncertaintyOutputPixelsAtLeast':1,'bodyTranslation':[0,0],'physicalSupportApproved':False}
 row={'phase':phase,'sourceFrameId':r['sourceFrameId'],'outputPNG':r['outputPNG'],'outputPNGsha256':r['outputPNGsha256'],'footRegionProxies':feet,'billRegionProxy':bill,'root':root,'producerDiagnosticOrigins':origins,'reportedProducerDiagnosticValues':reported,'contacts':[],'geometryReviewed':False,'supportWorld':None,'limits':'Same144coordinate minus[4,8] crop only; sampler differences can change RGBA versus older producer Pillow outputs. Positive alpha/region picks do not certify anatomy/sole/pressure/water or feather contact.'}
 if phase=='dip':row['dipWaterGap']='Producer bill144[129,79] maps cohort[125,71]; illustrativewater70 residual+1px. No beak-water contact event accepted.'
 rows.append(row)
land={'kind':'source image landmark proxies only','cropCoordinateTransform':'[source144X-4,source144Y-8] with no per-pose offset','phaseLandmarks':rows,'contactApproval':False,'geometryReviewed':False,'supportWorld':None}
(P/'phase-landmark-proxies.json').write_text(json.dumps(land,indent=2)+'\n')
ticks=[0,18,36,48,66,78];proposal['sourceEventMarkers']=[{'type':'phase_enter','tick':t,'phase':s['phase'],'sourceFrameId':next(r['sourceFrameId'] for r in m['frames'] if r['phase']==s['phase']),'proposedRuntimeSemantic':'select authored source phase drawing only; not a measured water/foot contact','acceptedByCurrentMacSchema':False} for t,s in zip(ticks,proposal['plannedSchedule'])]+[{'type':'complete','tick':102,'proposedRuntimeSemantic':'candidate six-phase sequence ends; separate comparison awake outro may be shown outside asset','acceptedByCurrentMacSchema':False}]
proposal['sourceEventSchemaStatus']='illustrative authored proposal, not accepted/current Mac event schema';proposal['landmarkProxyFile']={'file':'phase-landmark-proxies.json','sha256':sha(P/'phase-landmark-proxies.json')}
(P/'cohort-behavior-proposal.json').write_text(json.dumps(proposal,indent=2)+'\n')
m['sourceLandmarkProxyBinding']={'file':'phase-landmark-proxies.json','sha256':sha(P/'phase-landmark-proxies.json')};(P/'COHORT-SOURCE-MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
print('Authored markers0/18/36/48/66/78/complete102 and per-phase actual RGBA proxies written; contacts stay[]')
