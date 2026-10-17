"""Run the bounded CPU control proof. Installs/downloads/generation are never invoked."""
from pathlib import Path
import subprocess,sys
P=Path(__file__).parent
for cmd in [[sys.executable,str(P/'build_proof.py')],['node',str(P/'verify_renderer_contract.mjs')],[sys.executable,str(P/'verify_proof.py')],[sys.executable,str(P/'build_review.py')]]:
 subprocess.run(cmd,check=True,cwd=P)
print('Done. Serve review.html on loopback for runtime cutout controls; no app integration or generation occurred.')
