import { createHash } from 'node:crypto';

/** Canonical JSON rejects lossy values instead of hashing NaN/undefined as something else. */
export function canonicalJson(value: unknown): string {
  const seen = new Set<object>();
  const visit = (current: unknown, depth: number): string => {
    if (depth > 64) throw new PermanentStageError('Pipeline JSON is too deeply nested');
    if (current === null || typeof current === 'boolean' || typeof current === 'string') {
      return JSON.stringify(current);
    }
    if (typeof current === 'number' && Number.isFinite(current)) return JSON.stringify(current);
    if (!current || typeof current !== 'object')
      throw new PermanentStageError('Expected finite JSON data');
    if (seen.has(current)) throw new PermanentStageError('Cyclic pipeline JSON');
    seen.add(current);
    let encoded: string;
    if (Array.isArray(current)) {
      encoded = '[' + Array.from(current, (item) => visit(item, depth + 1)).join(',') + ']';
    } else {
      if (
        Object.getPrototypeOf(current) !== Object.prototype &&
        Object.getPrototypeOf(current) !== null
      ) {
        throw new PermanentStageError('Pipeline data must contain plain JSON objects');
      }
      const entries: [string, unknown][] = Object.entries(current);
      encoded =
        '{' +
        entries
          .sort(([left], [right]) => (left < right ? -1 : left > right ? 1 : 0))
          .map(([key, item]) => JSON.stringify(key) + ':' + visit(item, depth + 1))
          .join(',') +
        '}';
    }
    seen.delete(current);
    return encoded;
  };
  const result = visit(value, 0);
  if (Buffer.byteLength(result) > 1_000_000)
    throw new PermanentStageError('Pipeline JSON exceeds 1 MB');
  return result;
}

export const digest = (value: unknown): string =>
  createHash('sha256').update(canonicalJson(value)).digest('hex');

export class PipelineConflict extends Error {
  readonly code = 'pipeline_conflict';
}

export class PipelineNotFound extends Error {
  readonly code = 'pipeline_not_found';
  constructor() {
    super('Pipeline resource not found');
  }
}

export class PermanentStageError extends Error {}
