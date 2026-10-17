import type { ArrivalCue, ArrivalSettlement } from '../arrivals/contracts';
import { fixtureManifest } from '../assets/fixtures';
import { sceneLayerVisibility, type SceneLayerVisibility } from './layer-visibility';
import {
  advanceWater,
  createWaterState,
  defaultWaterOptions,
  waterVisuals,
  type WaterOptions,
  type WaterInput,
} from './water';
import {
  createWeatherSurfaceState,
  defaultWeatherSurfaceOptions,
  sampleWeatherSurfaces,
  type WeatherSurfaceOptions,
} from './surface-weather';
import {
  samplePhysicalSurface,
  type PhysicalSurfaceOptions,
  type PhysicalSurfaceDiagnostics,
} from './surface-runtime';
import {
  createYardRuntimeSession,
  selectYardRuntime,
  selectedPhysicalRuntime,
  advanceYardRuntime,
  settleYardRuntime,
  yardRuntimeDiagnostics,
  holdYardRuntime,
  disposeYardRuntime,
  type YardRuntimeSelection,
} from './yard-runtime';
import { surfacePrimitiveReserve } from './surface-budget';
import {
  reviewArtAdmission,
  projectReviewLayer,
  projectReviewObjectSkin,
  projectReviewFoliage,
  type ReviewArtAdmission,
} from './review-art';
import type { ValidatedReviewArt } from '../workbench/asset-package';
import { reviewTextureAdmission, type YardReviewTexture } from './review-texture';
import type { ReviewTextureView } from './review-texture-view';
import { reviewTreeAdmission, sampleReviewTree, type YardReviewTreeOptions } from './review-tree';
import {
  createSurfaceClock,
  admitSurfaceTime,
  drainSurfaceClock,
  surfaceClockSnapshot,
} from './surface-clock';
import {
  reviewTexturePackAdmission,
  reviewTexturePackSceneAdmission,
  type YardReviewTexturePack,
  type CheckedYardReviewTexturePack,
} from './review-texture-pack';
import { birdPresentation, presentationScale } from './presentation';
import { behaviorDisplayDiagnostic } from './behavior-diagnostics';
import { resolveScene, type ResolvedScene } from '../scenes/catalog';
import { layerPrimitives, sceneLayers } from '../scenes/manifest';
// This module must only be imported from a browser lifecycle hook.
import { Application, Container, Graphics, Text, type GraphicsContext } from 'pixi.js';
import { SharedGeometryCache, type GeometryLease } from './shared-geometry-cache';
import { createBirdGraphicsContext } from './bird-graphics-context';
import {
  advanceSimulation,
  admitArrival,
  cancelArrival,
  rejectArrivalCue,
  takeArrivalSettlements,
  triggerDecorativeVisit,
  cancelDecorativeVisit,
  createSimulation,
  reconcileBirds,
  setScenePhase,
  setSceneEnvironment,
  switchScene,
} from './simulation';
import { WORLD_HEIGHT, WORLD_WIDTH } from './scenes';
import { AnimationRegistry, type AssetEntry } from '../assets/registry';
import { sampleClip, sampledGeometryKey } from '../assets/manifest';
import { opaqueHit, poseShape, poseTransform } from '../assets/pose-geometry';
import type { Actor, DecorativeVisit, SceneBird, YardPalette, YardSetting } from './types';
import { defaultObjects, type YardObject } from '../domain/scene';
import {
  budgetCanvas,
  SCENE_RESOURCE_LIMITS,
  selectScenePresentation,
} from './scene-resource-budget';
import {
  sampleEnvironmentWind,
  type EnvironmentWindOptions,
  type EnvironmentWindSample,
  type EnvironmentFrame,
  type WeatherFrame,
} from '../weather';
import {
  createEnvironmentPlayback,
  sampleEnvironmentPlayback,
  targetEnvironmentPlayback,
} from './environment-playback';
import { ENVIRONMENT_VISUAL_LIMITS, type EnvironmentRect } from './environment-visuals';
import {
  PALETTES,
  actorDepth,
  objectDepth,
  objectPrimitives,
  weatherVisuals,
  windSceneryPrimitives,
  windPolicyFrame,
  type PixelRect,
} from './visuals';

export interface RenderOptions {
  arrivalCue?: ArrivalCue | null;
  heldBirdIds?: readonly string[];
  onArrivalSettled?: (settlement: ArrivalSettlement) => void;
  onDecorativeVisitChange?: (phase: DecorativeVisit['phase']) => void;
  sessionSeed?: number;
  illustrativeProfiles?: boolean;
  birds: SceneBird[];
  assets?: readonly AssetEntry[];
  palette: YardPalette;
  setting: YardSetting;
  scene?: ResolvedScene;
  reducedMotion: boolean;
  /** Workbench inspection only; never removes actors, objects or reservations. */
  layerVisibility?: Partial<SceneLayerVisibility>;
  /** Explicit opt-in local review; never a production pin or geometry authority. */
  reviewArt?: ValidatedReviewArt;
  reviewObjectIds?: readonly string[];
  allowDevelopmentCandidates?: boolean;
  /** One unapproved RGBA asset at its declared world size; no physics or persistence authority. */
  reviewTexture?: YardReviewTexture;
  /** Atomic review-only layered RGBA bundle; mutually exclusive with reviewTexture. */
  reviewTexturePack?: YardReviewTexturePack;
  /** Opt-in procedural treatment of two registered review paint entries, never physical foliage. */
  reviewTree?: YardReviewTreeOptions;
  physicalSurfaces?: PhysicalSurfaceOptions;
  yardRuntime?: YardRuntimeSelection;
  interactionRequest?: {
    revision: number;
    action: 'drinking' | 'bathing' | 'cancel';
  };
  physicalTimeRequest?: { revision: number; seconds: number };
  water?: WaterOptions;
  weatherSurfaces?: WeatherSurfaceOptions;
  objects?: readonly YardObject[];
  weather?: WeatherFrame;
  /** Transient illustrative companion; does not alter physical precipitation or stores. */
  wind?: EnvironmentWindOptions;
  environment?: EnvironmentFrame;
  environmentTransitionSeconds?: number;
  environmentClockRunning?: boolean;
  /** Explicit replay command; applies when visible and unpaused. */
  environmentReplayRevision?: number;
  /** Pauses the visible environment only; bird simulation can continue. */
  environmentPaused?: boolean;
  selectedId?: string | null;
  onSelect?: (id: string) => void;
  onFailure?: () => void;
}

function rect(g: Graphics, x: number, y: number, w: number, h: number, color: number, alpha = 1) {
  g.rect(x, y, w, h).fill({ color, alpha });
}
function drawPrimitives(g: Graphics, shapes: readonly PixelRect[], palette: YardPalette) {
  g.clear();
  for (const item of shapes)
    rect(
      g,
      item.x,
      item.y,
      item.width,
      item.height,
      PALETTES[palette][item.color],
      item.alpha ?? 1,
    );
}

function drawBird(g: Graphics, sample: ReturnType<typeof sampleClip>) {
  g.clear();
  for (const item of sample.rectangles)
    rect(g, item.x - sample.pivot.x, item.y - sample.pivot.y, item.width, item.height, item.color);
}

interface BirdView {
  container: Container;
  sprite: Graphics;
  shadow: Graphics;
  label: Text;
  ring: Graphics;
  key: string;
  hovered: boolean;
  rectangles: number;
  geometry: GeometryLease<GraphicsContext>;
}

/** Existing fixture flight is unchanged; annotated poses taper lift at both ends to land on support. */
export function flightLift(actor: Actor, reducedMotion: boolean, annotated: boolean) {
  if (reducedMotion || actor.behavior !== 'moving') return 0;
  if (actor.locomotion === 'hop') {
    const target = actor.route.at(-1);
    const remaining = target ? Math.hypot(target.x - actor.x, target.y - actor.y) : 0;
    return (
      -5 * Math.abs(Math.sin((actor.behaviorTicks * Math.PI) / 8)) * Math.min(1, remaining / 12)
    );
  }
  const amplitude = -8 - Math.sin(actor.behaviorTicks / 4) * 3;
  if (!annotated) return amplitude;
  const target = actor.route.at(-1);
  const remaining = target ? Math.hypot(target.x - actor.x, target.y - actor.y) : 0;
  return amplitude * Math.min(1, actor.behaviorTicks / 6, remaining / 20);
}

export async function createYardRenderer(host: HTMLElement, initial: RenderOptions) {
  let options = initial;
  let scene = initial.scene ?? resolveScene(initial.setting);
  const registry = new AnimationRegistry();
  registry.replace(initial.assets, initial.allowDevelopmentCandidates);
  let reviewAdmission: ReviewArtAdmission = {
    status: 'off',
    reason: null,
    primitiveCount: 0,
    art: null,
  };
  let reviewPaintRevision = 0;
  let textureAdmission = reviewTextureAdmission(undefined);
  let texturePackAdmission = reviewTexturePackAdmission(undefined);
  let treeAdmission: ReturnType<typeof reviewTreeAdmission>;
  function selectPresentation(value: RenderOptions) {
    const conflicting = value.reviewTexture !== undefined && value.reviewTexturePack !== undefined;
    const conflictReason = 'Provide either reviewTexture or reviewTexturePack, never both.';
    textureAdmission = conflicting
      ? { status: 'rejected', reason: conflictReason, texture: null, primitiveCount: 0 }
      : reviewTextureAdmission(value.reviewTexture);
    texturePackAdmission = conflicting
      ? { status: 'rejected', reason: conflictReason, pack: null, primitiveCount: 0 }
      : reviewTexturePackAdmission(value.reviewTexturePack);
    const surfaces = surfacePrimitiveReserve(
      value.water,
      value.weatherSurfaces,
      value.physicalSurfaces,
    );
    reviewAdmission = reviewArtAdmission({
      art: value.reviewArt,
      scene: scene.manifest,
      objects: value.objects ?? defaultObjects(scene.manifest),
      surfacePrimitives:
        surfaces + textureAdmission.primitiveCount + texturePackAdmission.primitiveCount,
      physicalSurfacesEnabled: Boolean(value.physicalSurfaces?.enabled),
    });
    treeAdmission = reviewTreeAdmission({
      tree: value.reviewTree,
      pack: texturePackAdmission.pack,
      scene: scene.manifest,
      objects: value.objects ?? defaultObjects(scene.manifest),
      additionalPrimitives:
        surfaces +
        reviewAdmission.primitiveCount +
        textureAdmission.primitiveCount +
        texturePackAdmission.primitiveCount,
    });
    if (!conflicting && texturePackAdmission.pack)
      texturePackAdmission = reviewTexturePackSceneAdmission({
        pack: value.reviewTexturePack,
        scene: scene.manifest,
        objects: value.objects ?? defaultObjects(scene.manifest),
        additionalPrimitives:
          surfaces +
          reviewAdmission.primitiveCount +
          textureAdmission.primitiveCount +
          treeAdmission.primitiveCount,
      });
    if (!texturePackAdmission.pack && treeAdmission.tree)
      treeAdmission = reviewTreeAdmission({
        tree: value.reviewTree,
        pack: null,
        scene: scene.manifest,
        objects: value.objects ?? defaultObjects(scene.manifest),
        additionalPrimitives: 0,
      });
    reviewPaintRevision++;
    return selectScenePresentation({
      birds: value.birds,
      registry,
      scene: scene.manifest,
      objects: value.objects ?? defaultObjects(scene.manifest),
      additionalPrimitives:
        surfaces +
        reviewAdmission.primitiveCount +
        textureAdmission.primitiveCount +
        texturePackAdmission.primitiveCount +
        treeAdmission.primitiveCount,
      selectedId: value.selectedId,
      arrivalCue: value.arrivalCue,
      heldBirdIds: value.heldBirdIds,
    });
  }
  let presentation = selectPresentation(initial);
  function withFootprint(bird: SceneBird): SceneBird {
    return birdPresentation(
      bird,
      registry.resolve(bird).manifest,
      Boolean(initial.illustrativeProfiles),
    );
  }
  const simulation = createSimulation(
    presentation.birds.filter((bird) => !initial.heldBirdIds?.includes(bird.id)).map(withFootprint),
    initial.setting,
    initial.objects,
    initial.environment?.status === 'ready'
      ? initial.environment.phase
      : initial.weather?.status === 'ready'
        ? initial.weather.phase
        : 'day',
    scene.manifest,
    {
      ...(initial.sessionSeed === undefined ? {} : { sessionSeed: initial.sessionSeed }),
      illustrativeProfiles: Boolean(initial.illustrativeProfiles),
    },
  );
  function syncArrival() {
    if (simulation.arrival && simulation.arrival.token !== options.arrivalCue?.token)
      cancelArrival(simulation);
    const bird = options.arrivalCue
      ? presentation.birds.find((bird) => bird.id === options.arrivalCue!.birdId)
      : undefined;
    if (options.arrivalCue && !bird) rejectArrivalCue(simulation, options.arrivalCue);
    if (options.arrivalCue && bird)
      admitArrival(
        simulation,
        options.arrivalCue,
        withFootprint(bird),
        options.reducedMotion || document.hidden,
      );
  }
  function notifyArrivals() {
    for (const settlement of takeArrivalSettlements(simulation))
      options.onArrivalSettled?.(settlement);
  }
  syncArrival();
  const app = new Application();
  const initialCanvas = budgetCanvas(host.clientWidth, host.clientHeight, window.devicePixelRatio);
  try {
    await app.init({
      width: initialCanvas.width,
      height: initialCanvas.height,
      antialias: false,
      autoDensity: true,
      resolution: initialCanvas.resolution,
      backgroundAlpha: 0,
      // Limit Pixi to the backend whose context lifecycle we handle. A string
      // preference also permits WebGPU/canvas, bypassing our static SVG fallback.
      preference: ['webgl'],
      autoStart: false,
    });
  } catch (error) {
    // A failed GPU initialization must not leave an application or stage behind.
    if (app.renderer)
      app.destroy({ removeView: true, releaseGlobalResources: false }, { children: true });
    else app.stage.destroy({ children: true });
    throw error;
  }
  const canvas = app.canvas;
  canvas.setAttribute('aria-hidden', 'true');
  canvas.setAttribute('data-scene-renderer', 'pixi');
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  canvas.style.display = 'block';
  host.append(canvas);
  const world = new Container();
  const background = new Container({ label: 'background' });
  const backgroundSky = new Graphics();
  const backgroundArt = new Graphics();
  const celestial = new Graphics();
  const clouds = new Graphics();
  background.addChild(backgroundSky, celestial, clouds, backgroundArt);
  const decorativeVisitor = new Graphics({
    label: 'decorative-hawk-concept-generic-fixture',
  });
  decorativeVisitor.eventMode = 'none';
  const visitorManifest = fixtureManifest('cn-species-erithacus-rubecula', true);
  let visitorFrame = -1,
    lastVisitPhase: DecorativeVisit['phase'] = 'idle';
  const ground = new Graphics({ label: 'ground' });
  const depthLayer = new Container({ label: 'objects-and-residents' });
  depthLayer.sortableChildren = true;
  const foreground = new Graphics({ label: 'foreground' });
  let foregroundPaint: readonly (PixelRect | EnvironmentRect)[] = layerPrimitives(
    scene.manifest,
    'foreground',
  );
  const atmosphere = new Container({ label: 'weather-lighting' });
  const lighting = new Graphics(),
    fog = new Graphics(),
    particles = new Graphics(),
    wind = new Graphics();
  atmosphere.addChild(lighting, fog, particles, wind);
  world.addChild(background, decorativeVisitor, ground, depthLayer, foreground, atmosphere);
  app.stage.addChild(world);
  let reviewFoliageBack: Graphics | undefined;
  let reviewFoliageFront: Graphics | undefined;
  let reviewFoliageForegroundPaint: readonly EnvironmentRect[] = [];

  // Current scene geometry plus a replacement scene fit within this cache even
  // while a frame/version switch briefly holds both old and new active contexts.
  const geometryCache = new SharedGeometryCache<GraphicsContext>(
    { entries: 256, rectangles: 65_536 },
    (context) => context.destroy(),
  );
  const views = new Map<string, BirdView>();
  const objectViews = new Map<
    string,
    { graphics: Graphics; key: string; rectangles: readonly (PixelRect | EnvironmentRect)[] }
  >();
  const yardSession = createYardRuntimeSession(simulation, initial.yardRuntime?.runtimeId);
  selectYardRuntime(yardSession, initial.yardRuntime);
  function readYardRuntimeDiagnostics() {
    return yardRuntimeDiagnostics(
      yardSession,
      [...simulation.actors.values()].slice(0, 128).map((actor) => registry.resolve(actor).key),
    );
  }
  canvas.dataset.yardRuntime = JSON.stringify(readYardRuntimeDiagnostics());
  let physicalSample: ReturnType<typeof samplePhysicalSurface> | undefined;
  const waterState = createWaterState(initial.water);
  const snowState = createWeatherSurfaceState(initial.weatherSurfaces);
  let waterGround: Graphics | undefined;
  let snowGround: Graphics | undefined;
  const waterObjects = new Map<string, Graphics>();
  const snowObjects = new Map<string, Graphics>();
  let waterSample: ReturnType<typeof waterVisuals> | undefined;
  let snowSample: ReturnType<typeof sampleWeatherSurfaces> | undefined;
  let lastSurfaceTick = -1;
  let surfaceDelta = 0;
  let createdBirdViews = 0,
    destroyedBirdViews = 0;
  let destroyed = false,
    visualTime = 0;
  let requestedTexture: YardReviewTexture | undefined;
  let requestedTextureKey: string | undefined;
  let requestedTexturePng: string | undefined;
  let textureLoadGeneration = 0;
  let textureAbort: AbortController | undefined;
  let textureView: ReviewTextureView | undefined;
  let textureStatus: 'absent' | 'pending' | 'ready' | 'rejected' = 'absent';
  let textureReason: string | null = null;
  let requestedPackKey: string | undefined;
  let requestedPackPngs: readonly string[] = [];
  let packLoadGeneration = 0;
  let packAbort: AbortController | undefined;
  let packStatus: 'absent' | 'pending' | 'ready' | 'rejected' = 'absent';
  let packReason: string | null = null;
  let packViews: {
    entry: CheckedYardReviewTexturePack['entries'][number];
    view: ReviewTextureView;
  }[] = [];
  let packPendingViews: typeof packViews = [];
  let packLoadingEntryId: string | null = null;
  const packLayers = new Map<string, Container>();
  let treeClock: ReturnType<typeof createSurfaceClock> | null = null;
  let treeGraphics: Graphics | undefined;
  let treePaintViews: typeof packViews = [];
  let treeSample: ReturnType<typeof sampleReviewTree> | undefined;
  let treeError: string | null = null;
  let treeReplayRevision = initial.environmentReplayRevision ?? 0;

  let visualTimeCompensation = 0;
  let environmentPlayback = initial.environment
    ? createEnvironmentPlayback(initial.environment)
    : undefined;
  let effectiveEnvironment = initial.environment;
  let effectiveWind: EnvironmentWindSample | undefined;
  let appliedReplayRevision = initial.environmentReplayRevision ?? 0;
  let environmentSamples = 0,
    lastEnvironmentSample = -1,
    maxEnvironmentDelta = 0,
    // Historical diagnostic: resident geometry assignments (previously drawBird calls).
    // Actual shared context construction is reported separately in geometryCache.builds.
    birdGeometryBuilds = 0;
  let playbackWasStopped = true,
    skipNextDelta = true;
  let lastVisual = weatherVisuals(initial.weather, 0, effectiveEnvironment, initial.palette);
  let lastSkyKey = '',
    lastEnvironmentFrameKey = '',
    lastEnvironmentPalette = options.palette;
  function reviewTextureDiagnostics() {
    return {
      status: textureStatus,
      reason: textureReason,
      reservedPrimitiveCount: textureAdmission.primitiveCount,
      canonicalVerification: textureStatus === 'ready' ? 'verified-before-upload' : 'not-uploaded',
      ...(textureView?.diagnostics() ?? {
        frameId: null,
        animated: false,
        static: false,
        primitiveCount: 0,
        decodedRgbaBytes: 0,
        textureCount: 0,
        disposed: textureStatus === 'absent',
        depthY: null,
      }),
    };
  }
  function clearReviewTexture() {
    textureLoadGeneration++;
    textureAbort?.abort();
    textureAbort = undefined;
    textureView?.destroy();
    textureView = undefined;
  }
  function sampleReviewTexture() {
    if (!textureView) return;
    try {
      // Legacy callers without an EnvironmentFrame may still explicitly replay the review clip.
      const replay = options.environmentReplayRevision ?? 0;
      if (
        !options.environment &&
        !options.environmentPaused &&
        !document.hidden &&
        replay !== appliedReplayRevision
      ) {
        visualTime = 0;
        visualTimeCompensation = 0;
        lastEnvironmentSample = -1;
        appliedReplayRevision = replay;
      }
      textureView.sample(visualTime, options.reducedMotion);
    } catch (error) {
      clearReviewTexture();
      textureStatus = 'rejected';
      textureReason = error instanceof Error ? error.message : 'Review texture playback failed.';
    }
    canvas.dataset.reviewTexture = JSON.stringify(reviewTextureDiagnostics());
  }
  function syncReviewTexture() {
    const selection = textureAdmission.texture;
    if (!options.reviewTexture && requestedTextureKey === undefined) return;
    const key = selection
      ? JSON.stringify([
          selection.placement,
          selection.clipId,
          selection.showContacts,
          selection.packageData.manifest,
          selection.packageData.receipt,
        ])
      : JSON.stringify([textureAdmission.status, textureAdmission.reason]);
    const png = selection?.packageData.canonicalPngBase64;
    if (key === requestedTextureKey && png === requestedTexturePng) return;
    requestedTexture = options.reviewTexture;
    requestedTextureKey = options.reviewTexture ? key : undefined;
    requestedTexturePng = png;
    clearReviewTexture();
    textureStatus = !requestedTexture ? 'absent' : selection ? 'pending' : 'rejected';
    textureReason = textureAdmission.reason;
    canvas.dataset.reviewTexture = JSON.stringify(reviewTextureDiagnostics());
    if (!selection) return;
    const generation = textureLoadGeneration;
    const abort = new AbortController();
    textureAbort = abort;
    void import('./review-texture-view')
      .then(({ createReviewTextureView }) => {
        if (destroyed || abort.signal.aborted || generation !== textureLoadGeneration)
          return undefined;
        return createReviewTextureView(selection, abort.signal);
      })
      .then((view) => {
        if (!view) return;
        if (destroyed || abort.signal.aborted || generation !== textureLoadGeneration) {
          view.destroy();
          return;
        }
        textureView = view;
        depthLayer.addChild(view.container);
        view.container.visible = sceneLayerVisibility(options.layerVisibility).objects;
        textureStatus = 'ready';
        textureReason = null;
        sampleReviewTexture();
        syncDepthOrder();
        publishResources();
        app.render();
      })
      .catch((error: unknown) => {
        if (destroyed || abort.signal.aborted || generation !== textureLoadGeneration) return;
        clearReviewTexture();
        textureStatus = 'rejected';
        textureReason =
          error instanceof Error ? error.message : 'Review texture could not initialize.';
        canvas.dataset.reviewTexture = JSON.stringify(reviewTextureDiagnostics());
        publishResources();
      });
  }
  function reviewTexturePackDiagnostics() {
    const entries = [...packViews, ...packPendingViews].map(({ entry, view }) => ({
      id: entry.id,
      layer: entry.layer,
      scale: entry.scale,
      bounds: entry.bounds,
      attached: packStatus === 'ready',
      canonicalVerification: 'verified-before-upload' as const,
      ...view.diagnostics(),
    }));
    return {
      status: packStatus,
      reason: packReason,
      reservedPrimitiveCount: texturePackAdmission.primitiveCount,
      loadingEntryId: packLoadingEntryId,
      canonicalVerification:
        packStatus === 'ready'
          ? 'verified-before-upload'
          : entries.length
            ? 'partial-verified-before-upload'
            : 'not-uploaded',
      decodedRgbaBytes: entries.reduce((sum, entry) => sum + entry.decodedRgbaBytes, 0),
      primitiveCount: entries.reduce((sum, entry) => sum + entry.primitiveCount, 0),
      textureCount: entries.reduce((sum, entry) => sum + entry.textureCount, 0),
      entries,
    };
  }
  function publishTexturePack() {
    canvas.dataset.reviewTexturePack = JSON.stringify(reviewTexturePackDiagnostics());
  }
  function clearReviewTexturePack() {
    clearReviewTree();
    packLoadGeneration++;
    packAbort?.abort();
    packAbort = undefined;
    for (const { view } of [...packViews, ...packPendingViews]) view.destroy();
    packViews = [];
    packPendingViews = [];
    packLoadingEntryId = null;
    for (const layer of packLayers.values()) layer.destroy({ children: false });
    packLayers.clear();
  }
  function sampleReviewTexturePack() {
    if (!packViews.length) return;
    try {
      const replay = options.environmentReplayRevision ?? 0;
      if (
        !options.environment &&
        !options.environmentPaused &&
        !document.hidden &&
        replay !== appliedReplayRevision
      ) {
        visualTime = 0;
        visualTimeCompensation = 0;
        lastEnvironmentSample = -1;
        appliedReplayRevision = replay;
      }
      for (const { view } of packViews) view.sample(visualTime, options.reducedMotion);
    } catch (error) {
      clearReviewTexturePack();
      packStatus = 'rejected';
      packReason = error instanceof Error ? error.message : 'Review texture pack playback failed.';
      syncLayerVisibility();
    }
    publishTexturePack();
  }
  function syncReviewTexturePack() {
    const selection = texturePackAdmission.pack;
    if (options.reviewTexturePack === undefined && requestedPackKey === undefined) return;
    const key = selection
      ? JSON.stringify(
          selection.entries.map(({ id, layer, texture }) => [
            id,
            layer,
            texture.placement,
            texture.clipId,
            texture.showContacts,
            texture.packageData.manifest,
            texture.packageData.receipt,
          ]),
        )
      : JSON.stringify([texturePackAdmission.status, texturePackAdmission.reason]);
    const pngs =
      selection?.entries.map(({ texture }) => texture.packageData.canonicalPngBase64) ?? [];
    if (
      key === requestedPackKey &&
      pngs.length === requestedPackPngs.length &&
      pngs.every((png, index) => png === requestedPackPngs[index])
    ) {
      // Scale is review paint only. Retain verified sources and the shared clock when
      // only this transform changes; pending entries adopt it before atomic attach.
      if (selection)
        for (const item of [...packViews, ...packPendingViews]) {
          const entry = selection.entries.find((candidate) => candidate.id === item.entry.id)!;
          item.entry = entry;
          item.view.container.scale.set(entry.scale);
        }
      publishTexturePack();
      return;
    }
    requestedPackKey = options.reviewTexturePack === undefined ? undefined : key;
    requestedPackPngs = pngs;
    clearReviewTexturePack();
    packStatus =
      options.reviewTexturePack === undefined ? 'absent' : selection ? 'pending' : 'rejected';
    packReason = texturePackAdmission.reason;
    syncLayerVisibility();
    publishTexturePack();
    if (!selection) return;
    const generation = packLoadGeneration;
    const abort = new AbortController();
    packAbort = abort;
    const partial: typeof packViews = [];
    packPendingViews = partial;
    const current = () => !destroyed && !abort.signal.aborted && generation === packLoadGeneration;
    void import('./review-texture-view')
      .then(async ({ createReviewTextureView }) => {
        // At most one image decode is in flight. No view joins the live graph until all succeed.
        for (const entry of selection.entries) {
          if (!current()) return;
          packLoadingEntryId = entry.id;
          publishTexturePack();
          const view = await createReviewTextureView(entry.texture, abort.signal);
          if (!current()) {
            view.destroy();
            return;
          }
          const latestEntry =
            texturePackAdmission.pack?.entries.find((candidate) => candidate.id === entry.id) ??
            entry;
          view.container.scale.set(latestEntry.scale);
          partial.push({ entry: latestEntry, view });
          publishTexturePack();
          publishResources();
        }
        if (!current()) return;
        packViews = partial;
        packPendingViews = [];
        packLoadingEntryId = null;
        for (const { entry, view } of packViews) {
          view.container.label = `review-texture-pack-entry:${entry.id}`;
          if (entry.layer === 'objects') depthLayer.addChild(view.container);
          else {
            let layer = packLayers.get(entry.layer);
            if (!layer) {
              layer = new Container({ label: `review-texture-pack-${entry.layer}` });
              packLayers.set(entry.layer, layer);
              if (entry.layer === 'background') background.addChild(layer);
              else
                world.addChildAt(
                  layer,
                  world.getChildIndex(entry.layer === 'ground' ? ground : foreground) + 1,
                );
            }
            layer.addChild(view.container);
          }
        }
        packStatus = 'ready';
        packReason = null;
        sampleReviewTexturePack();
        syncReviewTree(0);
        syncLayerVisibility();
        syncDepthOrder();
        publishResources();
        app.render();
      })
      .catch((error: unknown) => {
        for (const { view } of partial) view.destroy();
        if (!current()) return;
        clearReviewTexturePack();
        packStatus = 'rejected';
        packReason =
          error instanceof Error ? error.message : 'Review texture pack could not initialize.';
        syncLayerVisibility();
        publishTexturePack();
        publishResources();
      });
  }
  function restoreTreeTransforms() {
    for (const { entry, view } of treePaintViews)
      if (!view.container.destroyed) {
        view.container.pivot.set(0);
        view.container.position.set(entry.texture.placement.x, entry.texture.placement.y);
        view.container.scale.set(entry.scale);
        view.container.rotation = 0;
        view.container.skew.set(0);
        view.container.tint = 0xffffff;
        view.container.alpha = 1;
      }
    treePaintViews = [];
  }
  function clearReviewTree() {
    restoreTreeTransforms();
    treeGraphics?.destroy({ context: true });
    treeGraphics = undefined;
    treeClock = null;
    treeSample = undefined;
    treeError = null;
  }
  function reviewTreeDiagnostics() {
    return {
      status:
        destroyed || options.reviewTree === undefined
          ? 'absent'
          : treeAdmission.status === 'rejected' || treeError || packStatus === 'rejected'
            ? 'rejected'
            : treeSample && packStatus === 'ready'
              ? 'ready'
              : 'pending',
      reason: treeError ?? treeAdmission.reason ?? (packStatus === 'rejected' ? packReason : null),
      provenance: 'unapproved-procedural-tree-preview' as const,
      reservedPrimitiveCount: destroyed ? 0 : treeAdmission.primitiveCount,
      primitiveCount: treeGraphics ? (treeSample?.leaves.length ?? 0) : 0,
      clock: treeClock ? surfaceClockSnapshot(treeClock) : null,
      replayRevision: treeReplayRevision,
      canopy: treeSample?.canopy ?? null,
      wind: treeSample?.wind ?? null,
      leaves: treeSample?.leaves ?? [],
      sample: treeSample?.diagnostics ?? null,
      timing: 'separate-fixed-preview-clock-20-steps-per-turn' as const,
    };
  }
  function publishReviewTree() {
    canvas.dataset.reviewTree = JSON.stringify(reviewTreeDiagnostics());
  }
  function syncReviewTree(elapsedSeconds: number, drain = false) {
    const selection = treeAdmission.tree;
    if (!selection || packStatus !== 'ready') {
      if (treeClock || treeGraphics || treePaintViews.length) clearReviewTree();
      if (options.reviewTree !== undefined || canvas.dataset.reviewTree !== undefined)
        publishReviewTree();
      return;
    }
    const replay = options.environmentReplayRevision ?? 0;
    if (!treeClock || replay !== treeReplayRevision) {
      treeClock = createSurfaceClock();
      treeError = null;
      treeReplayRevision = replay;
    }
    const held =
      Boolean(options.environmentPaused) ||
      options.reducedMotion ||
      document.hidden ||
      !sceneLayerVisibility(options.layerVisibility).objects;
    // Render/control refreshes may update holds or replay, but only the ticker
    // drains accepted time: at most twenty fixed ticks per visible scheduler turn.
    if (drain || held || treeError)
      admitSurfaceTime(treeClock, drain ? elapsedSeconds : 0, { hold: held || treeError !== null });
    if (drain) drainSurfaceClock(treeClock, () => true);
    if (treeError) {
      publishReviewTree();
      return;
    }
    try {
      const environment =
        options.environment ??
        (options.weather
          ? {
              status: options.weather.status,
              particleSeed: options.weather.particleSeed,
              effects: { cloud: 0, rain: 0, snow: 0, fog: 0, wind: options.weather.wind },
            }
          : {
              status: 'ready' as const,
              particleSeed: 0,
              effects: { cloud: 0, rain: 0, snow: 0, fog: 0, wind: 0 },
            });
      const sampled = sampleReviewTree(selection, {
        timeSeconds: treeClock.tick * treeClock.dtSeconds,
        environment,
        ...(options.wind === undefined ? {} : { wind: options.wind }),
        reducedMotion: options.reducedMotion,
      });
      restoreTreeTransforms();
      const branch = packViews.find(({ entry }) => entry.id === options.reviewTree?.branchEntryId);
      const canopy = packViews.find(({ entry }) => entry.id === options.reviewTree?.foliageEntryId);
      if (!branch || !canopy) throw new Error('The complete tree paint entries are not attached.');
      treePaintViews = [branch, canopy];
      canopy.view.container.pivot.set(sampled.canopy.anchorLocal.x, sampled.canopy.anchorLocal.y);
      canopy.view.container.position.set(
        sampled.canopy.anchorWorld.x,
        sampled.canopy.anchorWorld.y,
      );
      canopy.view.container.rotation = sampled.canopy.rotationRadians;
      canopy.view.container.tint = sampled.canopy.tint;
      canopy.view.container.alpha = sampled.canopy.alpha;
      if (sampled.leaves.length) {
        if (!treeGraphics) {
          treeGraphics = new Graphics({ label: 'review-tree-leaves-unapproved' });
          treeGraphics.eventMode = 'none';
          depthLayer.addChild(treeGraphics);
        }
        treeGraphics.zIndex = branch.entry.texture.depthY + 0.3;
        drawEnvironmentRects(treeGraphics, sampled.leaves);
        treeGraphics.visible = sceneLayerVisibility(options.layerVisibility).objects;
      } else {
        treeGraphics?.destroy({ context: true });
        treeGraphics = undefined;
      }
      treeSample = sampled;
    } catch (error) {
      restoreTreeTransforms();
      treeGraphics?.destroy({ context: true });
      treeGraphics = undefined;
      treeSample = undefined;
      treeError = error instanceof Error ? error.message : 'Tree preview sampling failed.';
      admitSurfaceTime(treeClock, 0, { hold: true });
    }
    publishReviewTree();
  }
  function environmentDiagnostics() {
    const sample = environmentPlayback
      ? sampleEnvironmentPlayback(environmentPlayback, visualTime)
      : undefined;
    return {
      ...lastVisual.diagnostics,
      wind: effectiveWind ?? null,
      windMotionSuppressed: options.reducedMotion,
      frame: effectiveEnvironment ?? null,
      target: options.environment ?? null,
      birdGeometryBuilds,
      replayRevision: appliedReplayRevision,
      behaviorPolicy: simulation.environment,
      clockProgress: sample?.clockProgress ?? 1,
      weatherProgress: sample?.weatherProgress ?? 1,
      paused: Boolean(options.environmentPaused),
      reducedMotion: options.reducedMotion,
      hidden: document.hidden,
      samples: environmentSamples,
      maxDeltaSeconds: maxEnvironmentDelta,
      colors: {
        sky: lastVisual.sky,
        skyLow: lastVisual.skyLow,
        tint: lastVisual.tint,
        sceneryTint: lastVisual.sceneryTint,
      },
      primitives: {
        sun: lastVisual.sun.slice(0, 4),
        cloud: lastVisual.cloudRects.slice(0, 4),
        particles:
          lastVisual.particles.length > 4
            ? [...lastVisual.particles.slice(0, 2), ...lastVisual.particles.slice(-2)]
            : lastVisual.particles,
        fog: lastVisual.fog.slice(0, 4),
        wind: lastVisual.wind.slice(0, 4),
      },
    };
  }
  function targetEnvironment() {
    if (options.environmentPaused || document.hidden) return;
    if (!options.environment) {
      environmentPlayback = undefined;
      effectiveEnvironment = undefined;
      return;
    }
    const replayRevision = options.environmentReplayRevision ?? 0;
    if (replayRevision !== appliedReplayRevision) {
      visualTime = 0;
      visualTimeCompensation = 0;
      lastEnvironmentSample = -1;
      appliedReplayRevision = replayRevision;
      environmentPlayback = createEnvironmentPlayback(options.environment, visualTime);
      effectiveEnvironment = options.environment;
    } else if (!environmentPlayback)
      environmentPlayback = createEnvironmentPlayback(options.environment, visualTime);
    else
      targetEnvironmentPlayback(
        environmentPlayback,
        options.environment,
        visualTime,
        options.environmentTransitionSeconds ?? 3,
        options.reducedMotion,
        options.environmentClockRunning ?? options.environment.source === 'simulated',
      );
  }

  function syncLayerVisibility() {
    const visible = sceneLayerVisibility(options.layerVisibility);
    if (textureView) textureView.container.visible = visible.objects;
    if (treeGraphics) treeGraphics.visible = visible.objects;
    background.visible = visible.background;
    // Only suppress fixture scenery after an entire bundle is attached. Sky, sun,
    // clouds, weather and separately selected review art retain their own authority.
    const replaces = (role: string) =>
      packStatus === 'ready' && packViews.some(({ entry }) => entry.layer === role);
    backgroundArt.visible = !replaces('background');
    ground.visible =
      visible.ground &&
      (!replaces('ground') ||
        Boolean(reviewAdmission.art?.layers.some((entry) => entry.role === 'ground')));
    foreground.visible =
      visible.foreground &&
      (!replaces('foreground') ||
        Boolean(reviewAdmission.art?.layers.some((entry) => entry.role === 'foreground')));
    for (const { entry, view } of packViews) view.container.visible = visible[entry.layer];
    for (const [role, layer] of packLayers)
      layer.visible = visible[role as 'background' | 'ground' | 'foreground'];
    atmosphere.visible = visible.weather;
    if (reviewFoliageBack) reviewFoliageBack.visible = visible.background;
    if (reviewFoliageFront) reviewFoliageFront.visible = visible.foreground;
    if (waterGround) waterGround.visible = visible.ground && visible.weather;
    if (snowGround) snowGround.visible = visible.ground && visible.weather;
    for (const graphics of [...waterObjects.values(), ...snowObjects.values()])
      graphics.visible = visible.objects && visible.weather;
    canvas.dataset.layerVisibility = JSON.stringify(visible);
  }
  function syncScenery() {
    canvas.dataset.sceneLayers = sceneLayers(scene.manifest).join(',');
    canvas.dataset.sceneManifest = JSON.stringify({
      id: scene.manifest.id,
      version: scene.manifest.version,
      publicSceneId: scene.manifest.publicSceneId,
      status: scene.status,
    });
    const art = reviewAdmission.art;
    const backgroundLayer = art?.layers.find((layer) => layer.role === 'background');
    if (backgroundLayer) {
      drawEnvironmentRects(backgroundSky, projectReviewLayer(backgroundLayer));
      backgroundArt.clear();
    } else {
      drawPrimitives(
        backgroundArt,
        layerPrimitives(scene.manifest, 'background').filter(
          (item) => item.color !== 'sky' && item.color !== 'skyLow',
        ),
        options.palette,
      );
    }
    lastSkyKey = '';
    const groundLayer = art?.layers.find((layer) => layer.role === 'ground');
    if (groundLayer) drawEnvironmentRects(ground, projectReviewLayer(groundLayer));
    else drawPrimitives(ground, layerPrimitives(scene.manifest, 'ground'), options.palette);
    const foregroundLayer = art?.layers.find((layer) => layer.role === 'foreground');
    if (foregroundLayer) {
      const shapes = projectReviewLayer(foregroundLayer);
      foregroundPaint = shapes;
      drawEnvironmentRects(foreground, shapes);
    } else {
      const shapes = layerPrimitives(scene.manifest, 'foreground');
      foregroundPaint = shapes;
      drawPrimitives(foreground, shapes, options.palette);
    }
    syncReviewFoliage();
    canvas.dataset.reviewArt = JSON.stringify(reviewArtDiagnostics());
  }
  function syncReviewFoliage() {
    const art = reviewAdmission.art;
    const foliage = art?.schemaVersion === 2 ? art.foliage : [];
    const visible = sceneLayerVisibility(options.layerVisibility);
    for (const depth of ['background', 'foreground'] as const) {
      const shapes = foliage.filter((entry) => entry.depth === depth).flatMap(projectReviewFoliage);
      let graphics = depth === 'background' ? reviewFoliageBack : reviewFoliageFront;
      if (!shapes.length) {
        graphics?.destroy({ context: true });
        if (depth === 'background') reviewFoliageBack = undefined;
        else {
          reviewFoliageFront = undefined;
          reviewFoliageForegroundPaint = [];
        }
        continue;
      }
      if (!graphics) {
        graphics = new Graphics({ label: `review-foliage:${depth}` });
        graphics.eventMode = 'none';
        world.addChildAt(
          graphics,
          world.getChildIndex(depth === 'background' ? depthLayer : atmosphere),
        );
        if (depth === 'background') reviewFoliageBack = graphics;
        else reviewFoliageFront = graphics;
      }
      graphics.visible = visible[depth];
      graphics.tint = lastVisual.sceneryTint;
      drawEnvironmentRects(graphics, shapes);
      if (depth === 'foreground') reviewFoliageForegroundPaint = shapes;
    }
  }
  function reviewArtDiagnostics() {
    const art = reviewAdmission.art;
    return {
      status: reviewAdmission.status,
      reason: reviewAdmission.reason,
      primitiveCount: reviewAdmission.primitiveCount,
      productionApproved: false,
      scope: 'local-review-only',
      packageId: art?.packageId ?? null,
      packageVersion: art?.packageVersion ?? null,
      season: art?.season ?? null,
      worldWidth: WORLD_WIDTH,
      worldHeight: WORLD_HEIGHT,
      sourceLayerScale: 4,
      foliage:
        art?.schemaVersion === 2
          ? art.foliage.map((entry) => ({
              id: entry.id,
              foliageId: entry.foliageId,
              themeId: entry.themeId,
              placement: entry.placement,
              pivot: entry.pivot,
              scale: entry.scale,
              depth: entry.depth,
              physicalBehavior: 'none',
              windResponse: 'none',
            }))
          : [],
    };
  }
  function syncObjects() {
    const present = new Set(simulation.scene.objects.map((object) => object.id));
    for (const [id, view] of objectViews)
      if (!present.has(id)) {
        view.graphics.destroy();
        objectViews.delete(id);
      }
    for (const object of simulation.scene.objects) {
      let view = objectViews.get(object.id);
      if (!view) {
        const graphics = new Graphics({ label: `object:${object.id}` });
        depthLayer.addChild(graphics);
        view = { graphics, key: '', rectangles: [] };
        objectViews.set(object.id, view);
      }
      const physicalBowl = Boolean(
        options.physicalSurfaces?.enabled &&
        object.id === selectedPhysicalRuntime(yardSession)?.selectedBathId,
      );
      const skin =
        options.reviewObjectIds === undefined || options.reviewObjectIds.includes(object.id)
          ? reviewAdmission.art?.objectSkins.find((entry) => entry.kind === object.kind)
          : undefined;
      const key = `${object.kind}:${options.palette}:${physicalBowl}:${skin ? reviewPaintRevision : 'off'}`;
      if (view.key !== key) {
        if (skin) {
          const shapes = projectReviewObjectSkin(skin);
          view.rectangles = shapes;
          drawEnvironmentRects(view.graphics, shapes);
        } else {
          const shapes = objectPrimitives(object.kind).filter(
            (item) => !physicalBowl || (item.color !== 'water' && item.color !== 'glow'),
          );
          view.rectangles = shapes;
          drawPrimitives(view.graphics, shapes, options.palette);
        }
        view.key = key;
      }
      view.graphics.tint = lastVisual.sceneryTint;
      view.graphics.position.set(object.x, object.y);
      view.graphics.zIndex = objectDepth(object);
      view.graphics.visible = sceneLayerVisibility(options.layerVisibility).objects;
    }
  }
  function syncDecorativeVisitor() {
    const visit = simulation.decorativeVisit;
    decorativeVisitor.visible =
      sceneLayerVisibility(options.layerVisibility).residents &&
      (visit.phase === 'approach' || visit.phase === 'scatter');
    const sample = sampleClip(visitorManifest, 'moving', visit.ticks, options.reducedMotion);
    if (visitorFrame !== sample.frame) {
      drawBird(decorativeVisitor, sample);
      visitorFrame = sample.frame;
    }
    const progress =
      visit.phase === 'approach'
        ? visit.ticks / 45
        : visit.phase === 'scatter'
          ? 1 + visit.ticks / 150
          : 0;
    decorativeVisitor.position.set(-60 + progress * 570, 95 + Math.sin(progress * Math.PI) * 15);
    canvas.dataset.decorativeVisit = JSON.stringify({
      phase: visit.phase,
      ticks: visit.ticks,
      pending: visit.pending,
      sequence: visit.sequence,
      frame: sample.frame,
      x: decorativeVisitor.x,
      y: decorativeVisitor.y,
      fixtureOnly: true,
    });
    if (visit.phase !== lastVisitPhase) {
      lastVisitPhase = visit.phase;
      options.onDecorativeVisitChange?.(visit.phase);
    }
  }
  function drawEnvironmentRects(graphics: Graphics, rectangles: readonly EnvironmentRect[]) {
    graphics.clear();
    for (const item of rectangles)
      rect(graphics, item.x, item.y, item.width, item.height, item.color, item.alpha);
  }
  function syncPhysicalSurfaces(delta = 0) {
    const physical = options.physicalSurfaces;
    if (!physical) return;
    selectYardRuntime(yardSession, options.yardRuntime);
    physicalSample = advanceYardRuntime(yardSession, {
      physical,
      delta,
      paused: Boolean(options.environmentPaused),
      hidden: document.hidden,
      reducedMotion: options.reducedMotion,
      ...(options.interactionRequest ? { interactionRequest: options.interactionRequest } : {}),
      ...(options.physicalTimeRequest ? { timeRequest: options.physicalTimeRequest } : {}),
    });
    canvas.dataset.yardRuntime = JSON.stringify(readYardRuntimeDiagnostics());
    if (!physicalSample) {
      waterGround?.clear();
      for (const graphics of waterObjects.values()) graphics.clear();
      delete canvas.dataset.physicalSurface;
      syncObjects();
      return;
    }
    if (!waterGround) {
      waterGround = new Graphics({ label: 'physical-SI-ground' });
      world.addChildAt(waterGround, world.children.indexOf(depthLayer));
    }
    drawEnvironmentRects(waterGround, physicalSample.ground);
    snowGround?.clear();
    for (const graphics of snowObjects.values()) graphics.destroy();
    snowObjects.clear();
    const present = new Set(physicalSample.objects.map((object) => object.id));
    for (const [id, graphics] of waterObjects)
      if (!present.has(id)) {
        graphics.destroy();
        waterObjects.delete(id);
      }
    for (const object of physicalSample.objects) {
      let graphics = waterObjects.get(object.id);
      if (!graphics) {
        graphics = new Graphics({ label: `physical-SI-object:${object.id}` });
        graphics.eventMode = 'none';
        depthLayer.addChild(graphics);
        waterObjects.set(object.id, graphics);
      }
      graphics.zIndex = object.depth + 0.1;
      graphics.tint = lastVisual.sceneryTint;
      drawEnvironmentRects(graphics, object.rectangles);
    }
    canvas.dataset.physicalSurface = JSON.stringify({
      ...physicalSample.diagnostics,
      interaction: readYardRuntimeDiagnostics().interaction,
    });
    delete canvas.dataset.water;
    delete canvas.dataset.snow;
    syncObjects();
    syncLayerVisibility();
  }
  function syncSurfaces(delta = 0, force = false) {
    if (options.physicalSurfaces) {
      syncPhysicalSurfaces(delta);
      return;
    }
    if (!options.water && !options.weatherSurfaces) return;
    const tick = Math.floor(visualTime * ENVIRONMENT_VISUAL_LIMITS.sampleHz);
    const frozen = options.reducedMotion || document.hidden || Boolean(options.environmentPaused);
    surfaceDelta += frozen ? 0 : delta;
    if (!force && tick === lastSurfaceTick) return;
    lastSurfaceTick = tick;
    const elapsed = surfaceDelta;
    surfaceDelta = 0;
    const weatherOptions = options.weatherSurfaces ?? defaultWeatherSurfaceOptions();
    snowSample = sampleWeatherSurfaces(snowState, {
      objects: simulation.scene.objects,
      scene: simulation.scene.manifest,
      timeSeconds: visualTime,
      options: weatherOptions,
      paused: Boolean(options.environmentPaused),
      hidden: document.hidden,
      reducedMotion: options.reducedMotion,
    });
    const input: WaterInput = {
      paused: Boolean(options.environmentPaused),
      hidden: document.hidden,
      reducedMotion: options.reducedMotion,
      actors: simulation.actors.values(),
      bathAnchors: simulation.scene.slots
        .filter((slot) => slot.affordance === 'bath' && slot.objectId)
        .map((slot) => ({
          id: slot.id,
          objectId: slot.objectId!,
          x: slot.x,
          y: slot.y,
          depth: slot.depth,
        })),
      meltwaterRate: snowSample.meltwaterRate,
      ...(weatherOptions.rainIntensity ? { impacts: snowSample.impacts } : {}),
    };
    const waterOptions = options.water ?? defaultWaterOptions();
    // The model has its own fixed-step cap. Sampling at20Hz must retain the whole admitted interval.
    advanceWater(waterState, elapsed, waterOptions, input);
    waterSample = waterVisuals(waterState, waterOptions, input);
    if (!waterGround && options.water) {
      waterGround = new Graphics({ label: 'workbench-water' });
      world.addChildAt(waterGround, world.children.indexOf(depthLayer));
    }
    if (!snowGround && options.weatherSurfaces) {
      snowGround = new Graphics({ label: 'workbench-snow' });
      world.addChildAt(snowGround, world.children.indexOf(depthLayer));
    }
    if (waterGround) drawEnvironmentRects(waterGround, waterSample.ground);
    if (snowGround) drawEnvironmentRects(snowGround, snowSample.ground);
    const syncSurfaceObjects = (
      views: Map<string, Graphics>,
      entries: readonly {
        id: string;
        depth: number;
        rectangles: readonly EnvironmentRect[];
      }[],
      label: string,
      offset: number,
    ) => {
      const present = new Set(entries.map((entry) => entry.id));
      for (const [id, graphics] of views)
        if (!present.has(id)) {
          graphics.destroy();
          views.delete(id);
        }
      for (const entry of entries) {
        let graphics = views.get(entry.id);
        if (!graphics) {
          graphics = new Graphics({ label: `${label}:${entry.id}` });
          depthLayer.addChild(graphics);
          views.set(entry.id, graphics);
        }
        graphics.zIndex = entry.depth + offset;
        graphics.eventMode = 'none';
        graphics.tint = lastVisual.sceneryTint;
        drawEnvironmentRects(graphics, entry.rectangles);
      }
    };
    syncSurfaceObjects(waterObjects, waterSample.baths, 'water', 0.1);
    syncSurfaceObjects(snowObjects, snowSample.objects, 'snow', 0.15);
    canvas.dataset.water = JSON.stringify(waterSample.diagnostics);
    canvas.dataset.snow = JSON.stringify(snowSample.diagnostics);
    syncLayerVisibility();
  }
  function syncWeather(force = false) {
    const scaledTime = visualTime * ENVIRONMENT_VISUAL_LIMITS.sampleHz;
    const nearestTick = Math.round(scaledTime);
    // Only forgive floating-point roundoff at a tick boundary; preserve sub-tick sampling.
    const sampleTick =
      Math.abs(scaledTime - nearestTick) <= Number.EPSILON * Math.max(1, Math.abs(scaledTime)) * 8
        ? nearestTick
        : Math.floor(scaledTime);
    const sampleTime = sampleTick / ENVIRONMENT_VISUAL_LIMITS.sampleHz;
    if (!force && sampleTick === lastEnvironmentSample) return;
    if (environmentPlayback)
      effectiveEnvironment = sampleEnvironmentPlayback(environmentPlayback, visualTime).frame;
    const frameKey = JSON.stringify([
      effectiveEnvironment ?? options.weather,
      options.wind,
      options.reducedMotion,
    ]);
    if (
      sampleTick === lastEnvironmentSample &&
      frameKey === lastEnvironmentFrameKey &&
      options.palette === lastEnvironmentPalette &&
      lastSkyKey !== ''
    )
      return;
    lastEnvironmentSample = sampleTick;
    lastEnvironmentFrameKey = frameKey;
    lastEnvironmentPalette = options.palette;
    const windFrame =
      effectiveEnvironment ??
      (options.weather
        ? {
            status: options.weather.status,
            particleSeed: options.weather.particleSeed,
            effects: {
              cloud: 0,
              rain: 0,
              snow: 0,
              fog: 0,
              wind: options.weather.wind,
            },
          }
        : undefined);
    effectiveWind = windFrame
      ? sampleEnvironmentWind(windFrame, sampleTime, options.wind)
      : undefined;
    // Authored speed/gust wins over the legacy scalar for the existing illustrative hysteresis.
    setSceneEnvironment(
      simulation,
      windPolicyFrame(effectiveEnvironment ?? options.weather, effectiveWind),
    );
    const visual = weatherVisuals(
      options.weather,
      sampleTime,
      effectiveEnvironment,
      options.palette,
      effectiveWind,
      !options.reducedMotion,
    );
    lastVisual = visual;
    const skyKey = `${visual.sky}:${visual.skyLow}`;
    const reviewBackground = reviewAdmission.art?.layers.some(
      (layer) => layer.role === 'background',
    );
    if (!reviewBackground && skyKey !== lastSkyKey) {
      backgroundSky.clear();
      for (const item of layerPrimitives(scene.manifest, 'background'))
        if (item.color === 'sky' || item.color === 'skyLow')
          rect(
            backgroundSky,
            item.x,
            item.y,
            item.width,
            item.height,
            visual[item.color],
            item.alpha ?? 1,
          );
      lastSkyKey = skyKey;
    }
    if (reviewBackground) lastSkyKey = `review:${reviewPaintRevision}`;
    backgroundSky.tint = reviewBackground ? visual.sceneryTint : 0xffffff;
    backgroundArt.tint = ground.tint = foreground.tint = visual.sceneryTint;
    if (reviewFoliageBack) reviewFoliageBack.tint = visual.sceneryTint;
    if (reviewFoliageFront) reviewFoliageFront.tint = visual.sceneryTint;
    for (const view of objectViews.values()) view.graphics.tint = visual.sceneryTint;
    lighting.clear();
    if (visual.alpha) rect(lighting, 0, 0, WORLD_WIDTH, WORLD_HEIGHT, visual.tint, visual.alpha);
    drawEnvironmentRects(celestial, visual.sun);
    drawEnvironmentRects(clouds, visual.cloudRects);
    drawEnvironmentRects(fog, visual.fog);
    drawEnvironmentRects(particles, visual.particles);
    drawEnvironmentRects(wind, visual.wind);
    if (options.wind) {
      if (!reviewBackground)
        drawPrimitives(
          backgroundArt,
          windSceneryPrimitives(
            layerPrimitives(scene.manifest, 'background').filter(
              (r) => r.color !== 'sky' && r.color !== 'skyLow',
            ),
            effectiveWind,
            sampleTime,
            options.reducedMotion,
          ),
          options.palette,
        );
      if (!reviewAdmission.art?.layers.some((layer) => layer.role === 'foreground')) {
        const shapes = windSceneryPrimitives(
          layerPrimitives(scene.manifest, 'foreground'),
          effectiveWind,
          sampleTime,
          options.reducedMotion,
        );
        foregroundPaint = shapes;
        drawPrimitives(foreground, shapes, options.palette);
      }
    }
    environmentSamples++;
    canvas.dataset.environment = JSON.stringify(environmentDiagnostics());
  }
  syncScenery();
  syncObjects();
  syncWeather();

  function destroyBirdView(view: BirdView) {
    // These two contexts are private. Container.destroy({ children:true }) does
    // not destroy owned GraphicsContexts when context:true is absent in Pixi8.
    view.shadow.context.destroy();
    view.ring.context.destroy();
    // The sprite context is shared: detach the display object before releasing it.
    view.container.destroy({ children: true });
    view.geometry.release();
    destroyedBirdViews++;
  }
  function syncViews() {
    for (const [id, view] of views) {
      if (
        !simulation.actors.has(id) ||
        simulation.actors.get(id)?.placement === 'waiting-for-space'
      ) {
        destroyBirdView(view);
        views.delete(id);
      }
    }
    for (const actor of simulation.actors.values()) {
      if (actor.placement === 'waiting-for-space') continue;
      const asset = registry.resolve(actor);
      const sample = sampleClip(
        asset.manifest,
        options.reducedMotion && simulation.phase === 'night' ? 'sleeping' : actor.behavior,
        actor.behaviorTicks,
        options.reducedMotion,
      );
      const key = sampledGeometryKey(asset.key, sample);
      let view = views.get(actor.id);
      if (!view) {
        const container = new Container({ label: `bird:${actor.id}` });
        const shadow = new Graphics().ellipse(0, 0, 17, 4).fill({ color: 0x233c39, alpha: 0.15 });
        const ring = new Graphics().ellipse(0, 1, 26, 8).stroke({ color: 0xfff2ba, width: 2 });
        const geometry = geometryCache.acquire(key, sample.rectangles.length, () =>
          createBirdGraphicsContext(sample),
        );
        const sprite = new Graphics({ context: geometry.resource });
        const label = new Text({
          text: actor.name ?? '',
          style: {
            fontFamily: 'sans-serif',
            fontSize: 13,
            fontWeight: '600',
            fill: 0x253e39,
            stroke: { color: 0xf9eed6, width: 3 },
          },
        });
        label.anchor.set(0.5, 1);
        label.y = -48;
        container.addChild(shadow, ring, sprite, label);
        container.interactiveChildren = false;
        shadow.eventMode = ring.eventMode = label.eventMode = sprite.eventMode = 'none';
        container.eventMode = 'static';
        container.cursor = 'pointer';
        container.on('pointertap', () => options.onSelect?.(actor.id));
        container.on('pointerover', () => {
          const current = views.get(actor.id);
          if (current) current.hovered = true;
          label.visible = true;
          app.render();
        });
        container.on('pointerout', () => {
          const current = views.get(actor.id);
          if (current) current.hovered = false;
          label.visible = options.selectedId === actor.id;
          app.render();
        });
        depthLayer.addChild(container);
        view = {
          container,
          sprite,
          shadow,
          label,
          ring,
          key,
          hovered: false,
          rectangles: sample.rectangles.length,
          geometry,
        };
        birdGeometryBuilds++;
        createdBirdViews++;
        views.set(actor.id, view);
      }
      view.container.x = actor.x;
      view.container.visible = sceneLayerVisibility(options.layerVisibility).residents;
      view.container.y = actor.y;
      view.container.zIndex = actorDepth(actor, simulation.scene);
      const transform = poseTransform(
        asset.manifest,
        sample,
        actor,
        actor.direction,
        flightLift(actor, options.reducedMotion, Boolean(poseShape(asset.manifest, sample))),
        presentationScale(asset.manifest, Boolean(simulation.options.illustrativeProfiles)),
      );
      view.sprite.scale.set(transform.direction * (transform.scale ?? 1), transform.scale ?? 1);
      view.sprite.rotation = transform.rotation;
      view.sprite.position.set(transform.origin.x - actor.x, transform.origin.y - actor.y);
      view.container.hitArea = {
        contains(x: number, y: number) {
          const point = { x: x + actor.x, y: y + actor.y };
          if (!opaqueHit(sample, transform, point)) return false;
          const covered = (rect: {
            x: number;
            y: number;
            width: number;
            height: number;
            alpha?: number | undefined;
          }) =>
            (rect.alpha ?? 1) === 1 &&
            point.x >= rect.x &&
            point.x < rect.x + rect.width &&
            point.y >= rect.y &&
            point.y < rect.y + rect.height;
          const visible = sceneLayerVisibility(options.layerVisibility);
          if (
            visible.foreground &&
            (foregroundPaint.some(covered) || reviewFoliageForegroundPaint.some(covered))
          )
            return false;
          return (
            !visible.objects ||
            !simulation.scene.objects.some(
              (object) =>
                objectDepth(object) > actorDepth(actor, simulation.scene) &&
                (objectViews.get(object.id)?.rectangles ?? objectPrimitives(object.kind)).some(
                  (rect) =>
                    covered({
                      ...rect,
                      x: rect.x + object.x,
                      y: rect.y + object.y,
                    }),
                ),
            )
          );
        },
      };
      view.shadow.alpha = actor.behavior === 'moving' ? 0.4 : 1;
      view.ring.visible = options.selectedId === actor.id;
      view.label.text = actor.name ?? '';
      // Nearby birds share objects; reveal one label on selection/hover instead of overlapping names.
      view.label.visible = options.selectedId === actor.id || view.hovered;
      if (view.key !== key) {
        const geometry = geometryCache.acquire(key, sample.rectangles.length, () =>
          createBirdGraphicsContext(sample),
        );
        // Switch the user first; releasing its old lease may destroy a retired context.
        view.sprite.context = geometry.resource;
        view.geometry.release();
        view.geometry = geometry;
        birdGeometryBuilds++;
        view.rectangles = sample.rectangles.length;
        view.key = key;
      }
    }
  }

  function syncDepthOrder() {
    depthLayer.sortChildren();
    canvas.dataset.depthOrder = JSON.stringify(depthLayer.children.map((child) => child.label));
  }

  function diagnostics() {
    return [...simulation.actors.values()].map((actor) => {
      const asset = registry.resolve(actor);
      const sample = sampleClip(
        asset.manifest,
        options.reducedMotion && simulation.phase === 'night' ? 'sleeping' : actor.behavior,
        actor.behaviorTicks,
        options.reducedMotion,
      );
      return {
        ...behaviorDisplayDiagnostic(actor, asset, {
          phase: simulation.phase,
          reducedMotion: options.reducedMotion,
          illustrativeProfiles: Boolean(simulation.options.illustrativeProfiles),
          mode: 'pixi',
          worldScale: world.scale.x,
          pixelRatio: app.renderer.resolution,
          flightOffset: flightLift(
            actor,
            options.reducedMotion,
            Boolean(poseShape(asset.manifest, sample)),
          ),
          ...(simulation.options.sessionSeed === undefined
            ? {}
            : { sessionSeed: simulation.options.sessionSeed }),
        }),
      };
    });
  }

  function resourceDiagnostics() {
    let graphicsCount = 0,
      displayObjectCount = 0,
      textCount = 0;
    function count(node: Container) {
      displayObjectCount++;
      if (node instanceof Graphics) graphicsCount++;
      if (node instanceof Text) textCount++;
      for (const child of node.children) count(child);
    }
    if (!destroyed) count(app.stage);
    const staticGeometry =
      (['background', 'ground', 'foreground'] as const).reduce(
        (total, layer) =>
          total +
          (reviewAdmission.art?.layers.find((entry) => entry.role === layer)?.rectangles.length ??
            layerPrimitives(scene.manifest, layer).length),
        0,
      ) +
      reviewFoliageForegroundPaint.length +
      (reviewAdmission.art?.schemaVersion === 2
        ? reviewAdmission.art.foliage
            .filter((entry) => entry.depth === 'background')
            .reduce((sum, entry) => sum + entry.rectangles.length, 0)
        : 0) +
      simulation.scene.objects.reduce(
        (total, object) =>
          total +
          (objectViews.get(object.id)?.rectangles.length ?? objectPrimitives(object.kind).length),
        0,
      );
    const weatherGeometry =
      lastVisual.sun.length +
      lastVisual.cloudRects.length +
      lastVisual.fog.length +
      lastVisual.particles.length +
      lastVisual.wind.length +
      (lastVisual.alpha ? 1 : 0);
    return {
      limits: SCENE_RESOURCE_LIMITS,
      ...presentation.stats,
      disposed: destroyed,
      activeActorCount: destroyed ? 0 : simulation.actors.size,
      viewCount: views.size,
      waitingActorCount: destroyed
        ? 0
        : [...simulation.actors.values()].filter((actor) => actor.placement === 'waiting-for-space')
            .length,
      objectViewCount: objectViews.size,
      graphicsCount,
      displayObjectCount,
      textCount,
      currentPrimitiveCount: destroyed
        ? 0
        : staticGeometry +
          weatherGeometry +
          (textureView?.diagnostics().primitiveCount ?? 0) +
          reviewTexturePackDiagnostics().primitiveCount +
          reviewTreeDiagnostics().primitiveCount +
          (options.physicalSurfaces
            ? (physicalSample?.diagnostics.primitiveCount ?? 0)
            : (waterSample?.diagnostics.primitiveCount ?? 0) +
              (snowSample?.diagnostics.primitiveCount ?? 0)) +
          (visitorFrame < 0 ? 0 : visitorManifest.frames[visitorFrame]!.length) +
          [...views.values()].reduce((total, view) => total + view.rectangles + 3, 0),
      reservedPrimitiveCount: destroyed ? 0 : presentation.stats.reservedPrimitiveCount,
      reservedManifestRectangleCount: destroyed
        ? 0
        : presentation.stats.reservedManifestRectangleCount,
      reviewTexture: reviewTextureDiagnostics(),
      reviewTexturePack: reviewTexturePackDiagnostics(),
      reviewTree: reviewTreeDiagnostics(),
      registry: registry.resourceDiagnostics(),
      geometryCache: {
        ...geometryCache.diagnostics(),
        assignments: birdGeometryBuilds,
      },
      createdBirdViews,
      destroyedBirdViews,
      birdGeometryBuilds,
      canvasWidth: destroyed ? 0 : canvas.width,
      canvasHeight: destroyed ? 0 : canvas.height,
      canvasPixels: destroyed ? 0 : canvas.width * canvas.height,
      tickerStarted: !destroyed && app.ticker.started,
    };
  }
  function publishResources() {
    canvas.dataset.resources = JSON.stringify(resourceDiagnostics());
  }
  function resize() {
    if (destroyed) return;
    const surface = budgetCanvas(host.clientWidth, host.clientHeight, window.devicePixelRatio);
    const { width, height } = surface;
    app.renderer.resize(width, height, surface.resolution);
    // Pixi autoDensity writes logical pixel CSS sizes on resize; retain the host layout
    // when a large surface is deliberately downsampled. Pointer conversion uses its bounds.
    canvas.style.width = canvas.style.height = '100%';
    const scale = Math.min(width / WORLD_WIDTH, height / WORLD_HEIGHT);
    world.scale.set(scale);
    world.position.set((width - WORLD_WIDTH * scale) / 2, (height - WORLD_HEIGHT * scale) / 2);
    canvas.dataset.assetPins = JSON.stringify(diagnostics());
    publishResources();
    app.render();
  }
  function updatePlayback() {
    if (destroyed) return;
    if (options.reviewTree !== undefined) syncReviewTree(0);
    if (options.physicalSurfaces) syncPhysicalSurfaces(0);
    if (options.reducedMotion || document.hidden) {
      cancelDecorativeVisit(simulation);
      if (simulation.arrival) cancelArrival(simulation);
      notifyArrivals();
      syncViews();
      syncDecorativeVisitor();
      app.stop();
      playbackWasStopped = true;
    } else {
      if (playbackWasStopped) skipNextDelta = true;
      playbackWasStopped = false;
      targetEnvironment();
      app.start();
    }
    canvas.dataset.environment = JSON.stringify(environmentDiagnostics());
    canvas.dataset.assetPins = JSON.stringify(diagnostics());
    publishResources();
  }
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(host);
  document.addEventListener('visibilitychange', updatePlayback);
  function onContextLost(event: Event) {
    event.preventDefault();
    app.stop();
    clearReviewTexture();
    textureStatus = options.reviewTexture ? 'rejected' : 'absent';
    textureReason = options.reviewTexture
      ? 'Review texture stopped after graphics context loss.'
      : null;
    canvas.dataset.reviewTexture = JSON.stringify(reviewTextureDiagnostics());
    clearReviewTexturePack();
    packStatus = options.reviewTexturePack === undefined ? 'absent' : 'rejected';
    packReason =
      options.reviewTexturePack === undefined
        ? null
        : 'Review texture pack stopped after graphics context loss.';
    syncLayerVisibility();
    publishTexturePack();
    if (options.reviewTree !== undefined) publishReviewTree();
    options.onFailure?.();
  }
  canvas.addEventListener('webglcontextlost', onContextLost);
  let lastDiagnosticTick = -15;
  app.ticker.add((ticker) => {
    const physicalDelta = skipNextDelta ? 0 : Math.max(0, ticker.elapsedMS / 1000);
    const delta = Math.min(physicalDelta, 0.15);
    skipNextDelta = false;
    if (!options.environmentPaused) {
      // Kahan accumulation keeps equal admitted visible durations equal across frame cadences.
      const correctedDelta = delta - visualTimeCompensation;
      const nextVisualTime = visualTime + correctedDelta;
      visualTimeCompensation = nextVisualTime - visualTime - correctedDelta;
      visualTime = nextVisualTime;
      maxEnvironmentDelta = Math.max(maxEnvironmentDelta, delta);
    }
    syncWeather();
    sampleReviewTexture();
    sampleReviewTexturePack();
    syncReviewTree(physicalDelta, true);
    syncSurfaces(options.physicalSurfaces ? physicalDelta : delta);
    advanceSimulation(simulation, delta);
    if (options.physicalSurfaces?.enabled) {
      settleYardRuntime(yardSession, {
        paused: Boolean(options.environmentPaused),
        hidden: document.hidden,
        reducedMotion: options.reducedMotion,
      });
      canvas.dataset.yardRuntime = JSON.stringify(readYardRuntimeDiagnostics());
    }
    notifyArrivals();
    syncDecorativeVisitor();
    syncViews();
    syncDepthOrder();
    if (simulation.ticks - lastDiagnosticTick >= 15) {
      canvas.dataset.assetPins = JSON.stringify(diagnostics());
      publishResources();
      lastDiagnosticTick = simulation.ticks;
    }
  });
  syncViews();
  syncSurfaces(0, true);
  syncLayerVisibility();
  syncDepthOrder();
  syncReviewTexture();
  syncReviewTexturePack();
  resize();
  syncDecorativeVisitor();
  notifyArrivals();
  updatePlayback();
  return {
    diagnostics,
    environmentDiagnostics,
    reviewArtDiagnostics,
    reviewTextureDiagnostics,
    reviewTexturePackDiagnostics,
    reviewTreeDiagnostics,
    resourceDiagnostics,
    yardRuntimeDiagnostics: () => readYardRuntimeDiagnostics(),
    physicalSurfaceDiagnostics(): PhysicalSurfaceDiagnostics | undefined {
      return physicalSample
        ? {
            ...physicalSample.diagnostics,
            interaction: readYardRuntimeDiagnostics().interaction,
          }
        : undefined;
    },
    waterDiagnostics() {
      return waterSample?.diagnostics;
    },
    snowDiagnostics() {
      return snowSample?.diagnostics;
    },
    currentEnvironmentFrame() {
      return effectiveEnvironment ? structuredClone(effectiveEnvironment) : undefined;
    },
    triggerDecorativeVisit() {
      if (destroyed || options.reducedMotion || document.hidden) return 'unavailable' as const;
      const result = triggerDecorativeVisit(simulation);
      syncDecorativeVisitor();
      app.render();
      return result;
    },
    cancelDecorativeVisit() {
      if (!destroyed) {
        cancelDecorativeVisit(simulation);
        syncViews();
        syncDecorativeVisitor();
        app.render();
      }
    },
    update(next: RenderOptions) {
      if (destroyed) return;
      const nextScene = next.scene ?? resolveScene(next.setting);
      const repaint =
        next.palette !== options.palette ||
        nextScene.key !== scene.key ||
        Boolean(next.wind) !== Boolean(options.wind);
      scene = nextScene;
      switchScene(simulation, next.setting, next.objects, scene.manifest);
      if (
        next.assets !== options.assets ||
        next.allowDevelopmentCandidates !== options.allowDevelopmentCandidates
      ) {
        registry.replace(next.assets, next.allowDevelopmentCandidates);
        geometryCache.invalidate();
      }
      options = next;
      selectYardRuntime(yardSession, next.yardRuntime);
      if (!next.physicalSurfaces) {
        holdYardRuntime(yardSession);
        physicalSample = undefined;
      }
      canvas.dataset.yardRuntime = JSON.stringify(readYardRuntimeDiagnostics());
      syncLayerVisibility();
      const priorReview = reviewAdmission;
      presentation = selectPresentation(next);
      syncReviewTexture();
      syncReviewTexturePack();
      if (
        repaint ||
        priorReview.status !== reviewAdmission.status ||
        priorReview.art !== reviewAdmission.art
      )
        syncScenery();
      reconcileBirds(
        simulation,
        presentation.birds
          .filter((bird) => !next.heldBirdIds?.includes(bird.id) || simulation.actors.has(bird.id))
          .map(withFootprint),
      );
      syncArrival();
      if (!next.environment)
        setScenePhase(simulation, next.weather?.status === 'ready' ? next.weather.phase : 'day');
      targetEnvironment();
      sampleReviewTexture();
      sampleReviewTexturePack();
      syncReviewTree(0);
      syncObjects();
      syncViews();
      syncDepthOrder();
      syncWeather(true);
      syncSurfaces(0, true);
      syncDecorativeVisitor();
      notifyArrivals();
      updatePlayback();
      app.render();
    },
    destroy() {
      if (destroyed) return;
      destroyed = true;
      clearReviewTexture();
      textureStatus = 'absent';
      textureReason = null;
      clearReviewTexturePack();
      packStatus = 'absent';
      packReason = null;
      if (canvas.dataset.reviewTree !== undefined) publishReviewTree();
      disposeYardRuntime(yardSession);
      canvas.dataset.yardRuntime = JSON.stringify(readYardRuntimeDiagnostics());
      cancelDecorativeVisit(simulation);
      cancelArrival(simulation);
      notifyArrivals();
      resizeObserver.disconnect();
      document.removeEventListener('visibilitychange', updatePlayback);
      canvas.removeEventListener('webglcontextlost', onContextLost);
      // Other yard/preview renderers may still own resources in Pixi’s global pools.
      for (const view of views.values()) destroyBirdView(view);
      views.clear();
      geometryCache.destroy();
      // Shared bird contexts are detached above; every remaining GraphicsContext is private.
      // Pixi skips its owned-context default when an explicit destroy options object is passed.
      app.destroy(
        { removeView: true, releaseGlobalResources: false },
        { children: true, context: true },
      );
      objectViews.clear();
      reviewFoliageBack = undefined;
      reviewFoliageFront = undefined;
      reviewFoliageForegroundPaint = [];
      waterObjects.clear();
      snowObjects.clear();
      simulation.actors.clear();
      simulation.occupancy.clear();
      registry.retain([]);
      publishResources();
    },
  };
}

export type ReviewTreeDiagnostics = ReturnType<
  Awaited<ReturnType<typeof createYardRenderer>>['reviewTreeDiagnostics']
>;
