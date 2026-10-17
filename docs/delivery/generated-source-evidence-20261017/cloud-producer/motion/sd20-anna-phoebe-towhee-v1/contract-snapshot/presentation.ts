import type { SpeciesManifest } from '../assets/manifest';
import { physicalClearance, reviewedShape, sourceWorldScale } from '../assets/pose-geometry';
import { illustrativeProfile } from './behavior-profiles';
import type { SceneBird } from './types';
/** Fixture-only size tuning never overrides reviewed shape geometry or fidelity-reviewed artwork. */
export function presentationScale(manifest: SpeciesManifest, illustrativeProfiles: boolean) {
  if (manifest.schemaVersion === 4 || manifest.schemaVersion === 5)
    return sourceWorldScale(manifest);
  return illustrativeProfiles &&
    manifest.fixture &&
    !manifest.taxonFidelityReviewed &&
    !reviewedShape(manifest)
    ? (illustrativeProfile(manifest.speciesId)?.sizeScale ?? 1)
    : 1;
}
export function birdPresentation(
  bird: SceneBird,
  manifest: SpeciesManifest,
  illustrativeProfiles: boolean,
): SceneBird {
  const scale =
    manifest.schemaVersion === 4 || manifest.schemaVersion === 5
      ? 1
      : presentationScale(manifest, illustrativeProfiles);
  const reviewed = physicalClearance(manifest);
  const footprint =
    reviewed ??
    (illustrativeProfiles && illustrativeProfile(bird.speciesId)
      ? {
          left: 20 * scale,
          right: 20 * scale,
          back: 12 * scale,
          front: 12 * scale,
        }
      : undefined);
  return { ...bird, ...(footprint ? { footprint } : {}) };
}
