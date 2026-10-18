#!/usr/bin/env python3
"""Validate producer records against an exact received source-review catalog.

--records is {records: [...], evidence_root?: directory, contract_version?: N}.
Relative evidence_root resolves beside the records file; default is this tool's
parent directory (the producer corpus). Record source_file is optional if an
evidence file already has source_sha256. All file/sha256 objects, including
nested provenance/lineage objects, are verified. Contextual source_file/sha256
pairs are verified too. jsonPointer is RFC6901 (not a
URI fragment); optional value must equal the resolved value. Extra contextual
fields are retained, not certified as a complete typed schema. No art scoring,
label assignment, rights/support/runtime admission or file mutation occurs.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

class Invalid(ValueError): pass

def require(ok, reason):
    if not ok: raise Invalid(reason)

def digest(data): return hashlib.sha256(data).hexdigest()

def hash_value(value, where):
    require(isinstance(value, str) and re.fullmatch(r'[0-9a-fA-F]{64}', value),
            where + ': expected SHA256 hex')
    return value.lower()

def pointer(document, text):
    require(isinstance(text, str) and (text == '' or text.startswith('/')),
            'jsonPointer must be an RFC6901 string')
    value = document
    if text == '': return value
    for raw in text[1:].split('/'):
        require(re.search(r'~(?:[^01]|$)', raw) is None, 'Invalid jsonPointer escape')
        token = raw.replace('~1', '/').replace('~0', '~')
        if isinstance(value, dict):
            require(token in value, 'Missing jsonPointer object member: ' + text)
            value = value[token]
        elif isinstance(value, list):
            require(re.fullmatch(r'0|[1-9][0-9]*', token) is not None,
                    'Invalid jsonPointer array index: ' + text)
            require(int(token) < len(value), 'Missing jsonPointer array item: ' + text)
            value = value[int(token)]
        else: raise Invalid('jsonPointer traverses a scalar: ' + text)
    return value

def validate(contract_path, contract_sha, records_path):
    observed = {}
    def read(path, expected=None):
        data = path.read_bytes(); actual = digest(data)
        if expected is not None:
            require(actual == hash_value(expected, str(path)), 'SHA256 mismatch: ' + str(path))
        if path in observed: require(observed[path] == actual, 'Input changed: ' + str(path))
        observed[path] = actual
        return data
    contract_bytes = read(contract_path, contract_sha)
    contract = json.loads(contract_bytes)
    require(contract.get('document_kind') == 'shared-source-art-defect-label-contract',
            'Not a shared source-art defect catalog')
    require(isinstance(contract.get('version'), int) and not isinstance(contract['version'], bool),
            'Catalog version missing')
    labels = [v['id'] for v in contract['labels']]
    require(len(set(labels)) == len(labels) and all(isinstance(v, str) for v in labels),
            'Duplicate or invalid catalog labels')
    required = contract['record_requirements']
    require(isinstance(required, list) and all(isinstance(k, str) for k in required),
            'Invalid catalog record requirements')
    raw = read(records_path); envelope = json.loads(raw)
    require(isinstance(envelope, dict) and isinstance(envelope.get('records'), list),
            'Records envelope must contain records[]')
    if 'contract_version' in envelope:
        require(envelope['contract_version'] == contract['version'], 'Contract version differs')
    root = Path(envelope.get('evidence_root', Path(__file__).resolve().parent.parent))
    if not root.is_absolute(): root = records_path.parent / root
    require(not root.is_symlink(), 'Evidence root cannot be a symlink')
    root = root.resolve(strict=True); require(root.is_dir(), 'Evidence root is not a directory')
    def file(relative):
        require(isinstance(relative, str) and relative and not Path(relative).is_absolute()
                and '..' not in Path(relative).parts, 'Evidence file must be an in-root relative path')
        p = root
        for part in Path(relative).parts:
            p /= part; require(not p.is_symlink(), 'Evidence symlink forbidden: ' + relative)
        p = p.resolve(strict=True)
        require(p.is_relative_to(root) and p.is_file(), 'Evidence is not an in-root file: ' + relative)
        return p
    declared_contract = envelope.get('contract')
    if declared_contract is not None:
        require(isinstance(declared_contract, dict), 'Envelope contract must be an object')
        require(hash_value(declared_contract.get('sha256'), 'contract.sha256') == digest(contract_bytes)
                and type(declared_contract.get('version')) is int
                and declared_contract['version'] == contract['version'],
                'Envelope contract hash/version differs from actual pinned catalog')
        if 'snapshot' in declared_contract:
            require(read(file(declared_contract['snapshot']), declared_contract['sha256']) == contract_bytes,
                    'Envelope catalog snapshot differs')
    validations = []
    for index, record in enumerate(envelope['records']):
        where = f'records[{index}]'
        require(isinstance(record, dict), where + ': expected object')
        require(all(k in record for k in required),
                where + ': missing required fields: ' + ', '.join(k for k in required if k not in record))
        for key in ['asset_id', 'variant_id', 'reason']:
            require(isinstance(record[key], str) and record[key].strip(), where + ': empty ' + key)
        revision = record['candidate_revision']
        require((isinstance(revision, str) and revision.strip()) or
                (isinstance(revision, int) and not isinstance(revision, bool) and revision >= 0),
                where + ': candidate_revision must identify a revision')
        for key, values in [('scope', contract['scopes']),
                            ('grade', contract['qualification_grades']),
                            ('canonical_label', labels), ('finding_state', contract['finding_states'])]:
            require(isinstance(record[key], str) and record[key] in values,
                    where + ': unknown ' + key + ': ' + str(record[key]))
        for key in ['severity', 'confidence']:
            require(record.get(key) is None,
                    where + ': ' + key + ' must remain null; this catalog supplies no rubric')
        source_sha = hash_value(record['source_sha256'], where + '.source_sha256')
        require(isinstance(record['evidence'], list) and record['evidence'],
                where + ': evidence must be a nonempty list')
        require(all(isinstance(e, dict) and 'file' in e and 'sha256' in e
                    for e in record['evidence']), where + ': evidence entries need file and sha256')
        references = []
        def walk(value, location):
            if isinstance(value, dict):
                if 'file' in value or 'sha256' in value:
                    path_key = 'file' if 'file' in value else 'source_file'
                    require(path_key in value and 'sha256' in value,
                            location + ': incomplete file/hash reference')
                    p = file(value[path_key]); data = read(p, value['sha256'])
                    ref = {'location': location, 'file': value[path_key], 'sha256': digest(data)}
                    if 'jsonPointer' in value:
                        resolved = pointer(json.loads(data), value['jsonPointer'])
                        if 'value' in value:
                            require(json.dumps(resolved, sort_keys=True) == json.dumps(value['value'], sort_keys=True),
                                    location + ': pointer value differs')
                        ref.update(jsonPointer=value['jsonPointer'], resolvedValue=resolved)
                    references.append(ref)
                for k, child in value.items(): walk(child, location + '/' + k)
            elif isinstance(value, list):
                for i, child in enumerate(value): walk(child, location + '/' + str(i))
        walk(record, where)
        if 'source_file' in record:
            p = file(record['source_file']); read(p, source_sha)
            source_binding = {'file': record['source_file'], 'sha256': source_sha}
        else:
            match = next((r for r in references if r['sha256'] == source_sha), None)
            require(match is not None, where + ': source_sha256 needs source_file or exact evidence binding')
            source_binding = {'file': match['file'], 'sha256': source_sha}
        retained = copy.deepcopy(record)
        retained.setdefault('severity', None); retained.setdefault('confidence', None)
        validations.append({'record': retained, 'sourceBinding': source_binding,
                            'verifiedReferences': references, 'valid': True})
    # Recheck all bytes observed, including contract/records and lineage evidence.
    require(all(digest(p.read_bytes()) == h for p, h in observed.items()), 'An input changed during validation')
    return {'valid': True, 'validationScope': 'Received catalog required fields/enums and exact file/hash/pointer bindings only',
            'fullTypedSchemaValidation': False, 'catalog': {'file': str(contract_path),
                'sha256': digest(contract_bytes), 'version': contract['version'],
                'status': contract.get('status'), 'labelCount': len(labels)},
            'recordsFile': str(records_path), 'recordsSHA256': digest(raw), 'evidenceRoot': str(root),
            'declaredContractProvenance': declared_contract,
            'recordCount': len(validations), 'validatedRecords': validations,
            'inputFilesUnchanged': True, 'modelCalls': 0, 'sourceMutations': 0,
            'artGradesAssignedByAdapter': 0, 'runtimeAdmission': False,
            'limits': ['No subjective, anatomical, physical, rights or runtime acceptance inferred.',
                       'Lineage versions/provenance are retained as supplied; exact nested references and pointers are verified.',
                       'Missing unstructured context is not certified by this small adapter.']}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['contract', 'records', 'out']: parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--contract-sha256', required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Output must be a new path; refusing overwrite')
    try:
        result = validate(args.contract.resolve(strict=True), args.contract_sha256,
                          args.records.resolve(strict=True)); code = 0
    except (Invalid, OSError, ValueError, KeyError, TypeError) as error:
        result = {'valid': False, 'error': str(error), 'fullTypedSchemaValidation': False,
                  'runtimeAdmission': False, 'sourceMutations': 0, 'modelCalls': 0}; code = 1
    result['adapterSHA256'] = digest(Path(__file__).read_bytes())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream: json.dump(result, stream, indent=2, ensure_ascii=False); stream.write('\n')
    print(json.dumps({'valid': result['valid'], 'out': str(args.out), 'error': result.get('error')}))
    return code

if __name__ == '__main__':
    try: raise SystemExit(main())
    except (Invalid, OSError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}), file=sys.stderr); raise SystemExit(1)
