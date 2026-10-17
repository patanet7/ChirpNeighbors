"""Shared source resolution, isolated staging, review imaging and immutable packing."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from PIL import Image
PREFIX=Path('assets/generated/2026-10-17/regional-yard-packs')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n')
def records(repo):return json.loads((Path(repo)/PREFIX/'repair-07/manifest.json').read_text())['files']
def resolve(repo,key):return Path(repo)/next(e['canonical_path']for e in records(repo)if e['source_key']==key)
def stage_scope(repo,scope,destination):
    prefix='expansion/repair-07/'+scope+'/'
    def paths(v):
        if isinstance(v,str)and v.startswith('assets/generated/')and(Path(repo)/v).is_file():return str(Path(repo)/v)
        if isinstance(v,list):return [paths(x)for x in v]
        if isinstance(v,dict):return {k:paths(x)for k,x in v.items()}
        return v
    for e in records(repo):
        if not e['source_key'].startswith(prefix):continue
        p=Path(destination)/e['source_key'][len(prefix):];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(Path(repo)/e['canonical_path'],p)
        if p.suffix=='.json':write_json(p,paths(json.loads(p.read_text())))
def save_loop(frames,path,durations):
    """One shared palette; retain exact closing frame, verify decoded loop."""
    from PIL import ImageSequence
    strip=Image.new('RGB',(frames[0].width,frames[0].height*3))
    for i,f in enumerate([frames[0],frames[len(frames)//3],frames[2*len(frames)//3]]):strip.paste(f,(0,i*f.height))
    palette=strip.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
    indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE)for f in frames]
    indexed[0].save(path,save_all=True,append_images=indexed[1:],duration=durations,loop=0,optimize=False,disposal=1)
    im=Image.open(path);decoded=[x.convert('RGB').copy()for x in ImageSequence.Iterator(im)];hs=[hashlib.sha256(x.tobytes()).hexdigest()for x in decoded]
    assert hs[0]==hs[-1]and len(set(hs))>2
    return {'sha256':sha(path),'bytes':Path(path).stat().st_size,'dimensions_px':list(im.size),'decoded_frames':len(decoded),'unique_decoded_frames':len(set(hs)),'first_last_decoded_equal':True,'shared_palette':True,'frames':decoded}
def pack(files,root,target):
    root=Path(root);target=Path(target);target.parent.mkdir(parents=True,exist_ok=True)
    members={str(Path(p).relative_to(root)):sha(p)for p in files}
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in files:z.write(p,str(Path(p).relative_to(root)))
        z.writestr('package-members-sha256.json',json.dumps(members,indent=2)+'\n')
    with zipfile.ZipFile(target)as z:
        assert z.testzip()is None
        for p,h in members.items():assert hashlib.sha256(z.read(p)).hexdigest()==h
    assert target.stat().st_size<8_000_000
    return {'file':target.name,'bytes':target.stat().st_size,'sha256':sha(target),'CRC_and_member_hashes_pass':True,'immutable':True}
