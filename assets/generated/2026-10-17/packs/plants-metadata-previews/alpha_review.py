import json
from pathlib import Path
from PIL import Image
import numpy as np
R=Path('/workspace/yard-production/plants');out={}
for p in sorted((R/'sprites').glob('*.png')):
 a=np.array(Image.open(p));rgb=a[:,:,:3];alpha=a[:,:,3]
 # Exact neon hidden RGB colors, distinct from naturally colored petals.
 neon=((rgb[:,:,0]>245)&(rgb[:,:,1]<8)&(rgb[:,:,2]<8))|((rgb[:,:,0]<8)&(rgb[:,:,1]>245)&(rgb[:,:,2]<8))|((rgb[:,:,0]>245)&(rgb[:,:,1]>245)&(rgb[:,:,2]<8))|((rgb[:,:,0]<8)&(rgb[:,:,1]<8)&(rgb[:,:,2]>245))
 out[p.name]={'exact_neon_hidden_rgb_pixel_count':int(neon.sum()),'exact_neon_max_alpha':int(alpha[neon].max()) if neon.any() else 0,'exact_neon_alpha_gt8_count':int((neon&(alpha>8)).sum()),'visual_review':'Light/dark proper alpha-composited contact sheets show no conspicuous neon halo at preview scale; low-alpha hidden RGB can look severe in an RGBA viewer that renders RGB without correct compositing. No cleanup applied.'}
(R/'reviews'/'alpha-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
