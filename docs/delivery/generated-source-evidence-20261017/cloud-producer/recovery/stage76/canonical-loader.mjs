// Node compatibility only: the exact UI TypeScript files remain unchanged.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
export function registerCanonicalLoader(zodDirectory) {
  const zodEntry=pathToFileURL(path.join(zodDirectory,'index.js')).href;
  return registerHooks({
    resolve(specifier,context,nextResolve) {
      if(specifier==='zod') return nextResolve(zodEntry,context);
      try{return nextResolve(specifier,context);}catch(error){
        if(specifier.startsWith('.')&&!path.extname(specifier))
          return nextResolve(specifier+'.ts',context);
        throw error;
      }
    },
    load(url,context,nextLoad) {
      // Vite accepts these exact JSON imports without import attributes. Node
      // receives a module wrapper around the same hash-verified JSON bytes.
      if(url.startsWith('file:')&&url.endsWith('.json'))
        return {format:'module',source:'export default '+fs.readFileSync(fileURLToPath(url),'utf8')+';',shortCircuit:true};
      return nextLoad(url,context);
    },
  });
}
