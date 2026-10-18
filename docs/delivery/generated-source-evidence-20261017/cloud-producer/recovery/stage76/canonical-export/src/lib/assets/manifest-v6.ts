import { z } from 'zod';
import { speciesManifestV5Schema } from './manifest-v5.ts';
import { commonMotionSchema, commonMotionIssues } from './common-motion.ts';
/** Private development candidate with named idle presentation; no support/fidelity claim. */
export const speciesManifestV6Schema = speciesManifestV5Schema
  .innerType()
  .extend({
    schemaVersion: z.literal(6),
    commonMotion: commonMotionSchema,
    shape: z.never().optional(),
  })
  .strict()
  .superRefine((value, context) => {
    const { commonMotion, ...legacy } = value;
    const checked = speciesManifestV5Schema.safeParse({ ...legacy, schemaVersion: 5 });
    if (!checked.success) {
      for (const issue of checked.error.issues) context.addIssue(issue);
      return;
    }
    if (
      Object.keys(value.clips).length !== 1 ||
      value.clips.idle.poses.length !== 1 ||
      !value.clips.idle.loop ||
      value.clips.idle.poses[0]!.contacts.length
    )
      context.addIssue({
        code: 'custom',
        message:
          'Common-family candidates expose one neutral idle and no physical contact or activity clips.',
      });
    for (const message of commonMotionIssues(
      commonMotion,
      value.frames.length,
      value.canvas.width,
      value.canvas.height,
      value.conditioning.references,
      value.clips.idle.poses[0]!.pivot,
      value.clips.idle.poses[0]!.frame,
    ))
      context.addIssue({ code: 'custom', message });
  });
export type SpeciesManifestV6 = z.infer<typeof speciesManifestV6Schema>;
