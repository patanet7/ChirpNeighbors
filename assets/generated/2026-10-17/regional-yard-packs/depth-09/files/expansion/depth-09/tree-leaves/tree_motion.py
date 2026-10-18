"""Reusable offline tree/leaf artwork compositor, not an application wind solver.
All source art is copied unchanged. Coordinates are source scene pixels.
Public API phase is radians; 0 and2*pi close exactly. No external state/randomness.
"""
from pathlib import Path
from functools import lru_cache
import math
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
CANVAS=(1536,1024)
TREE_SIZE=(585,585)
TREE_XY=(-32,330)
NATIVE_ROOT=(668,1180)
PINS=((609,451),(270,633),(968,605),(560,238))
CORE_RADIUS=36

def _phase(phase):
    p=float(phase)%(2*math.pi)
    return 0.0 if abs(p)<1e-10 or abs(p-2*math.pi)<1e-10 else p

@lru_cache(None)
def _source(name):
    a=np.array(Image.open(ROOT/'sources'/f'{name}.png').convert('RGBA'))
    # Original bytes stay exact; only remove invisible alpha<=1 contamination from working derivative.
    a[a[:,:,3]<=1]=0
    return Image.fromarray(a)

@lru_cache(None)
def _field():
    yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
    dist=np.min(np.stack([np.hypot(xx-x,yy-y) for x,y in PINS]),axis=0)
    u=np.clip((dist-CORE_RADIUS)/180,0,1)
    return xx,yy,u*u*(3-2*u),dist<=CORE_RADIUS

def _canopy_native(phase,season):
    if season=='winter':return Image.new('RGBA',(1254,1254))
    if season not in ('spring','summer','autumn'):raise ValueError('season must be spring,summer,autumn,winter')
    src=np.array(_source('canopy_sparse_senescent' if season=='autumn' else 'canopy_healthy'))
    phase=_phase(phase)
    if phase==0:return Image.fromarray(src)
    xx,yy,w,_=_field()
    dx=8*math.sin(phase)+1.5*math.sin(2*phase)*yy/1254
    dy=1.2*math.sin(phase)*xx/1254
    sx=xx.copy();sy=yy.copy()
    for _ in range(4):
        ix=np.clip(np.rint(sx).astype(int),0,1253);iy=np.clip(np.rint(sy).astype(int),0,1253)
        sx=xx-dx*w[iy,ix];sy=yy-dy*w[iy,ix]
    ix=np.rint(sx).astype(int);iy=np.rint(sy).astype(int)
    good=(ix>=0)&(ix<1254)&(iy>=0)&(iy<1254)
    out=np.zeros_like(src);out[good]=src[iy[good],ix[good]]
    return Image.fromarray(out)

def _place_tree(src):
    out=Image.new('RGBA',CANVAS)
    out.alpha_composite(src.resize(TREE_SIZE,Image.Resampling.NEAREST),TREE_XY)
    return out

@lru_cache(None)
def _rigid_scene():return _place_tree(_source('wood_bare'))

def make_tree_layers(phase,season='summer'):
    """Independent rigid wood/flexible compound canopy. Original 1254 canvases share one transform."""
    return {'wood':_rigid_scene().copy(),'canopy':_place_tree(_canopy_native(phase,season))}

def make_tree_frame(phase,season='summer'):
    layers=make_tree_layers(phase,season)
    return Image.alpha_composite(layers['wood'],layers['canopy'])

def particle_states(phase,season='autumn'):
    """Illustrative falling/blowing paths with fade at cyclic wrap; not simulated emission or settling."""
    if season not in ('autumn','winter'):return []
    t=_phase(phase)/(2*math.pi);count=8 if season=='autumn' else 3;rows=[]
    for i in range(count):
        u=(t+i/count)%1.0
        opacity=min(1.,u/.08,(1-u)/.08)
        rows.append({'i':i,'u':u,'xy':[round(90+360*u+18*i),round(520+365*u+14*math.sin(2*math.pi*u+i))],
            'rotation_deg':round(35*math.sin(2*math.pi*u+i)+i*31,5),'opacity':max(0.,opacity)})
    return rows

def make_leaf_particles(phase,season='autumn'):
    out=Image.new('RGBA',CANVAS);base=_source('leaf_dry').resize((14,15),Image.Resampling.NEAREST)
    for row in particle_states(phase,season):
        leaf=base.rotate(row['rotation_deg'],Image.Resampling.NEAREST,expand=True)
        leaf.putalpha(leaf.getchannel('A').point(lambda a:round(a*row['opacity'])))
        x,y=row['xy'];out.alpha_composite(leaf,(x-leaf.width//2,y-leaf.height//2))
    return out

def make_litter_frame(season='autumn'):
    out=Image.new('RGBA',CANVAS)
    if season not in ('autumn','winter'):return out
    placements=[('litter_cluster_a',42,(219,904)),('litter_cluster_b',30,(323,899)),('litter_cluster_b',25,(405,921))]
    for name,width,xy in placements:
        src=_source(name);src=src.resize((width,round(src.height*width/src.width)),Image.Resampling.NEAREST)
        out.alpha_composite(src,xy)
    return out

def make_scene_layer(phase,season='summer'):
    out=make_litter_frame(season)
    out.alpha_composite(make_tree_frame(phase,season));out.alpha_composite(make_leaf_particles(phase,season))
    return out
