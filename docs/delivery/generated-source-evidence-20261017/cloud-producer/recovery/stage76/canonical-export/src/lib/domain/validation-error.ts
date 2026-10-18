const messages = {
  objectPlacement:
    'Objects must fit inside the yard ground area without overlapping other objects.',
  sceneCapacity: 'This yard has no collision-free placement for all objects.',
  legacySpeciesIdentity: 'Legacy species key mismatch',
  legacyArtworkIdentity: 'Legacy artwork identity mismatch',
} as const;

/** Reviewed input failures shared by browser/domain and server code. Callers choose
 * a fixed reason; submitted values, storage errors and arbitrary text cannot enter it. */
export class YardValidationError extends Error {
  readonly code = 'INVALID';
  constructor(reason: keyof typeof messages) {
    super(messages[reason]);
    this.name = 'YardValidationError';
  }
}
