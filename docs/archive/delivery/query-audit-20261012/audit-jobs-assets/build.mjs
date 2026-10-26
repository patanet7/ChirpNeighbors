import {buildSync} from '/workspace/archive-history/birdsong-yard-sprites/node_modules/esbuild/lib/main.js';
import {writeFileSync,readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const root='/workspace/archive-history/audit-jobs-assets';
const result=buildSync({entryPoints:[`${root}/benchmark.ts`],outfile:`${root}/benchmark.mjs`,bundle:true,platform:'node',format:'esm',target:'node24',packages:'external',metafile:true});
writeFileSync(`${root}/source-binding.json`,JSON.stringify(Object.fromEntries(Object.keys(result.metafile.inputs).filter(p=>p.includes('/src/')).map(p=>[p,createHash('sha256').update(readFileSync(p)).digest('hex')])),null,2));
