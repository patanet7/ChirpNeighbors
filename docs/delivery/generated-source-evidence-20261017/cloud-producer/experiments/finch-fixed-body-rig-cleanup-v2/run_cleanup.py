"""Run only retained-source layer/export checks; no installation or generation."""
from pathlib import Path
import subprocess,sys
P=Path(__file__).parent
for cmd in [[sys.executable,str(P/'build_cleanup.py')],[sys.executable,str(P/'build_export.py')],['node',str(P/'verify_renderer_contract.mjs')],[sys.executable,str(P/'verify_cleanup.py')],[sys.executable,str(P/'build_review.py')]]:subprocess.run(cmd,check=True,cwd=P)
print('Rigged layer checkpoint rebuilt. Owner jaw/neck and Mac admission remain pending. No generation performed.')
