import { arrivalCueSchema, type ArrivalCue, type ArrivalSettlement } from '../arrivals/contracts';
import { simulationOptionsSchema, type SimulationOptions } from './behavior-contracts';
import { illustrativeProfile, speciesTraits, fictionalPersonality } from './behavior-profiles';
import {
  activitySupports,
  applyBehaviorExperiment,
  behaviorPriority,
  effectiveCaution,
  socialClearance,
  supportPriority,
} from './behavior-policy';
import type { BehaviorDecisionTrace } from './ontology-contracts';
import type { WeatherFrame } from '../weather/contracts';
import type { EnvironmentFrame } from '../weather/environment-contracts';
import {
  compatibleShelter,
  describeEnvironmentDecision,
  environmentPriority,
  environmentSupports as baseEnvironmentSupports,
  resolveEnvironmentPolicy,
} from './environment-policy';
import { boundsOverlap, footprintBounds } from '../assets/shape';
import { containsBounds, containsPoint, type SceneManifest } from '../scenes/manifest';
import { findRoute, sceneDefinition } from './scenes';
import type {
  Actor,
  Affordance,
  Behavior,
  SceneBird,
  ScenePhase,
  SceneSlot,
  RoutineBehavior,
  Simulation,
  YardSetting,
} from './types';
import { objectFootprint, type ObjectCapability, type YardObject } from '../domain/scene';

export type { Actor, Behavior, SceneBird, Simulation, YardPalette, YardSetting } from './types';
export const FIXED_STEP_SECONDS = 1 / 30;
const MOVE_SPEED = 112;
/** Local physical-preview admission; deliberately outside saved/wire SimulationOptions. */
export interface PreviewSurfaceAdmission {
  actorId: string;
  objectId: string;
  generation: number;
