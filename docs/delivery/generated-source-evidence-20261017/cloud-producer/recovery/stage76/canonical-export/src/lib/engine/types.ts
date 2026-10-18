/** Presentation inputs only. No private observation or location data enters the renderer. */
export interface SceneBird {
  savedBehavior?: import('../domain/bird-behavior').SavedBirdBehavior | undefined;
  /** Actual admitted clips, distinct from simulation intentions. */
  animationActions?: readonly Behavior[];
  /** Actual registered expression clip lengths, not assumed animal attention timing. */
  attentionClips?: { blink: number; look: number };
  /** Local developer presentation experiment, never persisted as owner data. */
  behaviorExperiment?: import('./ontology-contracts').BehaviorExperiment;
  id: string;
  speciesId: string;
  artworkId?: string | null;
  /** Reviewed ground-plane clearance; absent assets retain legacy point/slot placement. */
  footprint?: import('../assets/shape').PhysicalFootprint;
  /** Renderer inputs allow explicit absence when clearing an optional display label. */
  name?: string | undefined;
}

export type YardPalette = 'twilight' | 'fieldnotes' | 'moonlit';
export type YardSetting = 'garden' | 'courtyard';
export type Behavior =
  | 'idle'
  | 'moving'
  | 'perching'
  | 'singing'
  | 'feeding'
  | 'bathing'
  | 'sleeping'
  | 'playing'
  | 'nesting';
export type Affordance = 'ground' | 'perch' | 'feed' | 'bath' | 'roost' | 'nest';
export type RoutineBehavior = 'playing' | 'nesting';
export interface Point {
  x: number;
  y: number;
}
export interface SceneSlot extends Point {
  id: string;
  affordance: Affordance;
  neighbors: string[];
  objectId?: string;
  capability?: import('../domain/scene').ObjectCapability;
  /** Fixture-only roofed seat preference; not reviewed species-specific shelter geometry. */
  shelter?: 'fixture-feeder-roof';
  /** Ground anchor depth, distinct from the height of a bird on an object. */
  depth: number;
}
export interface SceneDefinition {
  id: YardSetting;
  version: number;
  manifest: import('../scenes/manifest').SceneManifest;
  width: number;
  height: number;
  slots: SceneSlot[];
  objects: import('../domain/scene').YardObject[];
  /** All connections are unobstructed flight corridors, not walking through scenery. */
  navigation: 'flight-corridors';
}
export interface Actor extends Point {
  savedBehavior?: import('../domain/bird-behavior').SavedBirdBehavior | undefined;
  /** Transient ground projection stays separate from elevated paint coordinates. */
  currentGroundY?: number;
  travelGround?: { from: number; to: number; length: number; travelled: number };
  animationActions?: readonly Behavior[];
  /** Actual registered expression clip lengths, not assumed animal attention timing. */
  attentionClips?: { blink: number; look: number };
  /** Transient environment diagnostics never enter saved residents or legacy trace contracts. */
  environmentDecision?: import('./environment-policy').EnvironmentDecision;
  environmentKey?: string;
  behaviorExperiment?: import('./ontology-contracts').BehaviorExperiment;
  placement: 'placed' | 'waiting-for-space';
  traits: Readonly<import('./ontology-contracts').SpeciesBehaviorTraits> | null;
  personality: Readonly<import('./ontology-contracts').FictionalPersonality> | null;
  decision:
    | import('./ontology-contracts').BehaviorDecisionTrace
    | import('./behavior-trace-v2').BehaviorDecisionTraceV2
    | null;
  /** Transient clocks; never persisted in owner data or interpreted as reviewed contacts. */
  motion?: import('./actor-motion').ActorMotion;
  attentionSeed?: number;
  profile: Readonly<import('./behavior-contracts').IllustrativeSpeciesProfile> | null;
  locomotion: 'flight' | 'hop' | 'walk';
  id: string;
  speciesId: string;
  artworkId?: string | null;
  /** Reviewed ground-plane clearance; absent assets retain legacy point/slot placement. */
  footprint?: import('../assets/shape').PhysicalFootprint;
  name?: string | undefined;
  behavior: Behavior;
  behaviorTicks: number;
  remainingTicks: number;
  direction: -1 | 1;
  frame: number;
  slotId: string | null;
  targetSlotId: string | null;
  route: Point[];
  nextBehavior: Behavior;
  lastActivity: Behavior;
  lastRoutine: RoutineBehavior | null;
  randomState: number;
  transitionCount: number;
}
export type ScenePhase = 'dawn' | 'day' | 'dusk' | 'night';
export interface DecorativeVisit {
  phase: 'idle' | 'approach' | 'scatter' | 'return' | 'cooldown';
  ticks: number;
  pending: boolean;
  sequence: number;
  participants: Map<string, { slotId: string | null; point: Point; delay: number }>;
}
export interface Simulation {
  environment: import('./environment-policy').EnvironmentPolicy | null;
  decorativeVisit: DecorativeVisit;
  arrival: { token: string; birdId: string; ticks: number } | null;
  arrivalSettlements: import('../arrivals/contracts').ArrivalSettlement[];
  settledArrivalTokens: string[];
  options: import('./behavior-contracts').SimulationOptions;
  phase: ScenePhase;
  scene: SceneDefinition;
  actors: Map<string, Actor>;
  /** Occupied slots and in-flight destination reservations share one arbitration map. */
  occupancy: Map<string, string>;
  /** FIFO turns for decorative routines; actor removal cleans queues, admission rotates a turn. */
  routineTurns: Record<RoutineBehavior, string[]>;
  ticks: number;
  accumulator: number;
}

/** Decorative daytime routines; sleeping is phase-driven. */
export const IMPLEMENTED_BEHAVIORS: readonly Behavior[] = [
  'idle',
  'moving',
  'perching',
  'singing',
  'feeding',
  'bathing',
  'playing',
  'nesting',
];
