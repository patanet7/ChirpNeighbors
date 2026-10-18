import { z } from 'zod';
export const timestampSchema = z.string().datetime();

/** Shared identity validation for portable events, owner-scoped entities and scene objects. */
export const idSchema = z
  .string()
  .min(1)
  .max(160)
  .regex(/^[a-zA-Z0-9][a-zA-Z0-9._:-]*$/)
  .refine((value) => !['__proto__', 'prototype', 'constructor'].includes(value));
