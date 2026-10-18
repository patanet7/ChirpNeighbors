import { z } from 'zod';

export const weatherConditionSchema = z.enum(['clear', 'cloudy', 'rain', 'snow']);
export type WeatherCondition = z.infer<typeof weatherConditionSchema>;

/** Settings contain no coordinates, device location or provider credentials. */
export const weatherSettingsSchema = z
  .object({
    mode: z.enum(['simulated', 'manual', 'real']),
    manual: z
      .object({
        condition: weatherConditionSchema,
        hour: z.number().int().min(0).max(23),
      })
      .strict(),
    simulation: z
      .object({
        seed: z.number().int().safe(),
        dayLengthSeconds: z.number().int().min(120).max(86_400),
        epoch: z.string().datetime(),
      })
      .strict(),
  })
  .strict();

export type WeatherSettings = z.infer<typeof weatherSettingsSchema>;

/** Fresh objects prevent one yard's settings edits from affecting another yard. */
export function defaultWeatherSettings(): WeatherSettings {
  return {
    mode: 'simulated',
    manual: { condition: 'clear', hour: 12 },
    simulation: {
      seed: 17,
      dayLengthSeconds: 600,
      epoch: '2026-01-01T00:00:00Z',
    },
  };
}

export interface WeatherFrame {
  condition: WeatherCondition;
  phase: 'dawn' | 'day' | 'dusk' | 'night';
  /** Scene clock, including fractional hours for smooth simulated daylight. */
  hour: number;
  light: number;
  source: 'simulated' | 'manual' | 'unconfigured';
  status: 'ready' | 'unconfigured';
  /** Normalized scene wind strength; no physical speed unit is implied. */
  wind: number;
  /** Unsigned 32-bit seed. Renderers derive repeatable particle positions from it. */
  particleSeed: number;
}
