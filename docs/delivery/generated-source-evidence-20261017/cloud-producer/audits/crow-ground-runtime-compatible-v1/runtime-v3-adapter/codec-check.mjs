import fs from 'node:fs';
import crypto from 'node:crypto';
import sharp from '/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs';
import {normalizeDecodedPixels} from './exact-runtime-codec.ts';
const input=process.argv[2];
if(!input)throw Error('Usage: node --experimental-strip-types codec-check.mjs INPUT.png [--descriptor OUTPUT.partial.json]');
const {data,info}=await sharp(input).ensureAlpha().raw().toBuffer({resolveWithObject:true});
const sourceRGBAId='frame.sha256.'+crypto.createHash('sha256').update(`RGBA8;${info.width}x${info.height};`).update(data).digest('hex');
try{
 const frames=normalizeDecodedPixels({canvas:{width:info.width,height:info.height},frames:[{rgba:Array.from(data)}],logicalPixelSize:1,paletteLimit:64});
 const check=Buffer.alloc(data.length);
 for(const r of frames[0])for(let y=r.y;y<r.y+r.height;y++)for(let x=r.x;x<r.x+r.width;x++){const i=(y*info.width+x)*4;check[i]=r.color>>>16;check[i+1]=(r.color>>>8)&255;check[i+2]=r.color&255;check[i+3]=255;}
 if(!check.equals(data))throw Error('Exact codec reconstruction changed RGBA');
 const palette=[...new Set(frames[0].map(r=>r.color))].sort((a,b)=>a-b);
 const result={passed:true,inputPNGsha256:crypto.createHash('sha256').update(fs.readFileSync(input)).digest('hex'),decodedRGBAId:sourceRGBAId,canvas:[info.width,info.height],decodedArea:info.width*info.height,rectangles:frames[0].length,opaquePaletteColors:palette.length,pixelReconstructionExact:true,exactCodec:'unchanged extracted normalizeDecodedPixels',fullManifestValidation:false,canonicalMacAdmission:false};
 if(process.argv[3]==='--descriptor'){
  const name=process.argv[4];if(!name)throw Error('Missing descriptor path');
  const d={schemaVersion:3,format:'pixel-rects',canvas:{width:info.width,height:info.height},frames,clips:{idle:{action:'idle',direction:'right-facing-mirrorable',loop:true,poses:[{frame:0,durationTicks:120,pivot:{x:108,y:145},contacts:[],poseId:'crow-static-ground-0',rotation:0}]}},normalization:{algorithm:'lossless-rgba-rects-v2',alpha:'binary',logicalPixelSize:1,palette,loopEdges:[{action:'idle',comparedPixels:info.width*info.height,changedPixels:0,pivotDistance:0,contactLayoutChanged:false}]}};
  fs.writeFileSync(name,JSON.stringify(d,null,2)+'\n');result.partialDescriptor={file:name,sha256:crypto.createHash('sha256').update(fs.readFileSync(name)).digest('hex'),isCompleteManifest:false,pivotRounded:[108,145],pivotDeltaFromContinuous:[.46875,-.3125],requiresCoordinatorMetadata:['speciesId','representation','fixture/fidelity/provenance','conditioning real pins and poseGraph','sourceArtifact real pin']};
 }
 console.log(JSON.stringify(result));
}catch(e){console.log(JSON.stringify({passed:false,inputPNGsha256:crypto.createHash('sha256').update(fs.readFileSync(input)).digest('hex'),decodedRGBAId:sourceRGBAId,errorClass:e.constructor.name,error:e.message,exactCodec:'unchanged extracted normalizeDecodedPixels',fullManifestValidation:false,canonicalMacAdmission:false}));process.exitCode=1;}
