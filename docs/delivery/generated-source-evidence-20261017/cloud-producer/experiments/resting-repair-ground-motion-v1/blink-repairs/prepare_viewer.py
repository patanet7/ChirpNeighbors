from pathlib import Path
from PIL import Image
import sys,json,hashlib
P=Path(__file__).resolve().parent;D=P/sys.argv[1];h=json.loads((D/'family-handoff.json').read_text());N=h['candidateCanvas'][0]
template=Path('/workspace/asset-production/experiments/common-slot-zero-call-batch-v1/contract-check/families/mourning_dove/player.js').read_text()
template=template.replace("kind==='raw'?'raw-full/'+f.role+'.png':f.png","kind==='raw'?f.rawPNG:f.png").replace('fillRect(0,0,192,192)','fillRect(0,0,...h.displayStage)').replace('window.FAMILY_REVIEW={ready:true','window.FAMILY_REVIEW=window.REPAIR_REVIEW={ready:true')
(D/'player.js').write_text(template)
html=f'''<!doctype html><meta charset="utf-8"><title>{D.name} blink repair source</title><style>body{{font:16px system-ui;background:#eee9da;margin:24px}}table{{border-spacing:14px}}td{{padding:10px}}canvas{{width:{N}px;height:{N}px;image-rendering:pixelated}}pre{{font-size:12px;white-space:pre-wrap}}button,select{{padding:8px}}</style><h1>{D.name.replace('_',' ')} — bounded blink repair</h1><p>Actual{N}CSS/world. One new native closure, exact existing source neutral/look. Enlarged diagnostics cannot determine normal-size closure acceptance.</p><select id="option"><option value="blink">Blink60 /3 /27</option><option value="look">Existing look60 /6 /24</option><option value="idle">Static neutral60</option></select><button id="play">Play once</button><button id="neutral">Hold neutral</button><input id="tick" type="range" min="0" max="89" value="0"><table><tr><th></th><th>Raw whole-canvas source</th><th>Binary alpha/common palette</th></tr>'''
for bg in ['light','dark']:
    html+='<tr><th>'+bg+'</th>'+''.join(f'<td><canvas id="{kind}-{bg}" width="{N}" height="{N}"></canvas></td>' for kind in ['raw','codec'])+'</tr>'
html+='</table><p>Authored clocks at30Hz. Closed100ms, exact neutral return. No body travel or support approval. Source proposal only: rights, private declarations/pins, full input5/admission and live scene acceptance remain unresolved by this source packet.</p><pre id="state"></pre><script src="player.js"></script>'
(D/'review.html').write_text(html)
diagnostics=[]
for f in h['frames']:
    im=Image.open(D/f['png']).convert('RGBA');raw=Image.open(D/f['rawPNG']).convert('RGBA');a=im.getchannel('A');diagnostics.append({'role':f['role'],'canvas':[N,N],'opaqueBBox':a.getbbox(),'root':h['candidatePivot'],'rootRGBA':list(im.getpixel(tuple(h['candidatePivot']))),'rootQualification':'Declared common image-registration origin only; it may be transparent and does not certify sole/support.','rawAlphaPositivePixels':sum(v>0 for v in raw.getchannel('A').getdata()),'codecOpaquePixels':sum(v==255 for v in a.getdata()),'partialAlphaPreservedInRaw':True})
(D/'pixel-diagnostics.json').write_text(json.dumps({'frames':diagnostics,'contacts':[],'geometryReviewed':False,'physicalSupportReviewed':False,'supportWorld':None,'noPerPoseRegistrationCorrection':True},indent=2)+'\n')
# Head/feet inspection is source art, never a captured browser frame; not normal-size acceptance evidence.
sheet=Image.new('RGB',(N*3,N*4),'#e5e0cd')
for j,(kind,bg) in enumerate([('raw','#e5e0cd'),('codec','#e5e0cd'),('raw','#182a32'),('codec','#182a32')]):
    for i,f in enumerate(h['frames']):
        im=Image.open(D/(f['rawPNG'] if kind=='raw' else f['png'])).convert('RGBA');tile=Image.new('RGBA',(N,N),bg);tile.alpha_composite(im);sheet.paste(tile.convert('RGB'),(N*i,N*j))
sheet.save(D/'normal-source-codec-light-dark.png')
print(json.dumps({'viewer':str(D/'review.html'),'normalCSS':N,'API':'REPAIR_REVIEW or FAMILY_REVIEW: ready/select/play/seek/getState/pause'}))
