import type { Application, ImageSource, Sprite, Graphics, Texture } from 'pixi.js';
import {
  textureReviewClientPackageSchema,
  textureReviewFrameAt,
  TEXTURE_REVIEW_LIMITS,
  type TextureReviewClientPackage,
  type TextureReviewFrame,
  type TextureReviewManifest,
} from './texture-profile';

export type TexturePreviewDisplayMode = 'fit' | 'world-1x';
export type TexturePreviewFiltering = 'nearest' | 'linear';
export type TexturePreviewBackground = 'checkerboard' | 'light' | 'dark';

export interface TexturePreviewPlayback {
  clipId: string;
  paused: boolean;
  reducedMotion: boolean;
  replayRevision: number;
  displayMode?: TexturePreviewDisplayMode;
  filtering?: TexturePreviewFiltering;
  background?: TexturePreviewBackground;
}
export interface TexturePreviewController {
  update(playback: TexturePreviewPlayback): void;
  destroy(): void;
}
const WIDTH = 640;
const HEIGHT = 400;

/** Browser-only verification of the bounded transport, before image decode or GPU allocation. */
export async function verifyTexturePreviewPackage(
  value: TextureReviewClientPackage,
  signal?: AbortSignal,
) {
  signal?.throwIfAborted();
  const packageData = textureReviewClientPackageSchema.parse(value);
  const binary = atob(packageData.canonicalPngBase64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index++) bytes[index] = binary.charCodeAt(index);
  const hash = new Uint8Array(await crypto.subtle.digest('SHA-256', bytes.buffer));
  signal?.throwIfAborted();
  const sha256 = [...hash].map((byte) => byte.toString(16).padStart(2, '0')).join('');
  if (sha256 !== packageData.receipt.canonical.sha256)
    throw new Error('Canonical texture PNG hash mismatch. No texture was uploaded.');
  const view = new DataView(bytes.buffer);
  if (
    bytes.length < 33 ||
    view.getUint32(0) !== 0x89504e47 ||
    view.getUint32(4) !== 0x0d0a1a0a ||
    view.getUint32(8) !== 13 ||
    view.getUint32(12) !== 0x49484452 ||
    view.getUint32(16) !== packageData.manifest.atlas.width ||
    view.getUint32(20) !== packageData.manifest.atlas.height
  )
    throw new Error('Canonical texture PNG header or atlas dimensions mismatch.');
  return { packageData, bytes };
}

/** Coordinates remain in source pixels for Texture.orig/trim and Sprite.pivot. */
export function texturePreviewGeometry(frame: TextureReviewFrame) {
  const density = frame.sourcePixelsPerWorldUnit;
  return {
    frame: { ...frame.sourceRect },
    orig: { x: 0, y: 0, width: frame.canvas.width, height: frame.canvas.height },
    trim: { ...frame.trim, width: frame.sourceRect.width, height: frame.sourceRect.height },
    pivot: { ...frame.pivot },
    sourceScale: 1 / density,
    bounds: {
      left: -frame.pivot.x / density,
      top: -frame.pivot.y / density,
      right: (frame.canvas.width - frame.pivot.x) / density,
      bottom: (frame.canvas.height - frame.pivot.y) / density,
    },
    contacts: frame.contacts.map((point) => ({
      id: point.id,
      x: (point.x - frame.pivot.x) / density,
      y: (point.y - frame.pivot.y) / density,
    })),
  };
}

/** Clock hold drops hidden/paused time; long foreground stalls recover at most 250 ms per tick. */
export function advanceTexturePreviewClock(
  elapsedMs: number,
  deltaMs: number,
  hold: { paused: boolean; reducedMotion: boolean; hidden: boolean },
) {
  if (hold.paused || hold.reducedMotion || hold.hidden || !Number.isFinite(deltaMs) || deltaMs <= 0)
    return elapsedMs;
  return elapsedMs + Math.min(deltaMs, 250);
}

/** World 1x keeps one CSS canvas pixel per world unit; oversized art is clipped by this fixed viewport. */
export function texturePreviewLayout(
  manifest: TextureReviewManifest,
  displayMode: TexturePreviewDisplayMode = 'fit',
) {
  const bounds = manifest.frames.map((frame) => texturePreviewGeometry(frame).bounds);
  const left = Math.min(...bounds.map((bound) => bound.left));
  const top = Math.min(...bounds.map((bound) => bound.top));
  const width = Math.max(...bounds.map((bound) => bound.right)) - left;
  const height = Math.max(...bounds.map((bound) => bound.bottom)) - top;
  const scale =
    displayMode === 'world-1x' ? 1 : Math.min((WIDTH - 64) / width, (HEIGHT - 64) / height, 4);
  return {
    scale,
    x: 32 + (WIDTH - 64 - width * scale) / 2 - left * scale,
    y: 32 + (HEIGHT - 64 - height * scale) / 2 - top * scale,
  };
}

async function decodeImage(image: HTMLImageElement, signal?: AbortSignal) {
  let timer: ReturnType<typeof setTimeout> | undefined;
  let abort: (() => void) | undefined;
  try {
    await Promise.race([
      image.decode(),
      new Promise<never>((_, reject) => {
        abort = () => reject(new DOMException('Texture preview cancelled.', 'AbortError'));
        signal?.addEventListener('abort', abort, { once: true });
        if (signal?.aborted) abort();
        timer = setTimeout(
          () => reject(new Error('Texture image decode timed out.')),
          TEXTURE_REVIEW_LIMITS.decodeSeconds * 1_000,
        );
      }),
    ]);
  } finally {
    clearTimeout(timer);
    if (abort) signal?.removeEventListener('abort', abort);
  }
}

/**
 * An isolated review renderer. Owns every URL/image/source/subtexture/application; never calls
 * Assets.load, Texture.from, or global caches. Straight PNG alpha is premultiplied once on upload.
 * This exercises browser rendering and does not measure GPU time or peak GPU memory.
 */
export async function createTextureReviewPreview(
  host: HTMLElement,
  value: TextureReviewClientPackage,
  initialPlayback: TexturePreviewPlayback,
  options: {
    signal?: AbortSignal;
    onFrame?: (frameId: string) => void;
    onError?: (message: string) => void;
  } = {},
): Promise<TexturePreviewController> {
  let app: Application | undefined;
  let source: ImageSource | undefined;
  const textures = new Map<string, Texture>();
  let image: HTMLImageElement | undefined;
  let blobUrl: string | undefined;
  let initSettled = false;
  let disposed = false;
  let sprite: Sprite | undefined;
  let overlay: Graphics | undefined;
  let elapsedMs = 0;
  let dropNextDelta = true;
  let playback = { ...initialPlayback };
  let shownFrame = '';
  const signal = options.signal;

  function release() {
    signal?.removeEventListener('abort', dispose);
    document.removeEventListener('visibilitychange', visibilityChanged);
    if (image) {
      image.removeAttribute('src');
      image = undefined;
    }
    if (blobUrl) {
      URL.revokeObjectURL(blobUrl);
      blobUrl = undefined;
    }
    // Application.init cannot be cancelled safely mid-flight. Its settled continuation releases it.
    if (app && initSettled) {
      const owned = app;
      app = undefined;
      if (owned.renderer) {
        owned.canvas.removeEventListener('webglcontextlost', contextLost);
        owned.destroy(
          { removeView: true, releaseGlobalResources: false },
          {
            children: true,
            context: true,
            texture: false,
            textureSource: false,
          },
        );
      } else if (!owned.stage.destroyed) owned.stage.destroy({ children: true, context: true });
    }
    for (const texture of textures.values()) texture.destroy(false);
    textures.clear();
    source?.destroy();
    source = undefined;
    sprite = undefined;
    overlay = undefined;
  }
  function dispose() {
    disposed = true;
    release();
  }
  function fail(message: string) {
    dispose();
    options.onError?.(message);
  }
  function checkCancelled() {
    if (disposed || signal?.aborted)
      throw new DOMException('Texture preview cancelled.', 'AbortError');
  }
  function contextLost(event: Event) {
    event.preventDefault();
    fail('Texture preview stopped after graphics context loss. Reopen the package to retry.');
  }
  function visibilityChanged() {
    dropNextDelta = true;
    syncPlayback();
  }
  let draw: () => void = () => {};
  function syncPlayback() {
    if (!app || !initSettled || disposed) return;
    if (document.hidden || playback.paused || playback.reducedMotion) app.stop();
    else app.start();
    if (!document.hidden) {
      draw();
      app.render();
    }
  }
  signal?.addEventListener('abort', dispose, { once: true });
  try {
    const verified = await verifyTexturePreviewPackage(value, signal);
    checkCancelled();
    const manifest = verified.packageData.manifest;
    if (!manifest.clips.some((clip) => clip.id === playback.clipId))
      throw new Error('Selected texture clip is unavailable; no fallback clip is invented.');
    blobUrl = URL.createObjectURL(new Blob([verified.bytes.buffer], { type: 'image/png' }));
    image = new Image();
    image.decoding = 'async';
    image.src = blobUrl;
    await decodeImage(image, signal);
    checkCancelled();
    if (
      image.naturalWidth !== manifest.atlas.width ||
      image.naturalHeight !== manifest.atlas.height
    )
      throw new Error('Decoded texture atlas dimensions mismatch.');
    const { Application, ImageSource, Texture, Rectangle, Sprite, Graphics } =
      await import('pixi.js');
    checkCancelled();
    app = new Application();
    try {
      await app.init({
        width: WIDTH,
        height: HEIGHT,
        resolution: 1,
        autoDensity: false,
        autoStart: false,
        sharedTicker: false,
        preference: 'webgl',
        background: 0x14262d,
        antialias: false,
      });
    } finally {
      initSettled = true;
    }
    checkCancelled();
    source = new ImageSource({
      resource: image,
      alphaMode: 'premultiply-alpha-on-upload',
      scaleMode: 'nearest',
      autoGenerateMipmaps: false,
      resolution: 1,
    });
    for (const frame of manifest.frames) {
      const geometry = texturePreviewGeometry(frame);
      textures.set(
        frame.id,
        new Texture({
          source,
          frame: new Rectangle(
            geometry.frame.x,
            geometry.frame.y,
            geometry.frame.width,
            geometry.frame.height,
          ),
          orig: new Rectangle(0, 0, geometry.orig.width, geometry.orig.height),
          trim: new Rectangle(
            geometry.trim.x,
            geometry.trim.y,
            geometry.trim.width,
            geometry.trim.height,
          ),
        }),
      );
    }
    const first = textureReviewFrameAt(manifest, playback.clipId, 0);
    sprite = new Sprite({ texture: textures.get(first.id)! });
    overlay = new Graphics();
    const checker = new Graphics();
    app.stage.addChild(checker, sprite, overlay);
    let paintedBackground: TexturePreviewBackground | undefined;
    draw = () => {
      if (!sprite || !overlay || !source || !app) return;
      const background = playback.background ?? 'checkerboard';
      if (background !== paintedBackground) {
        checker.clear();
        if (background === 'checkerboard') {
          for (let y = 0; y < HEIGHT; y += 32)
            for (let x = 0; x < WIDTH; x += 32)
              checker.rect(x, y, 32, 32).fill((x / 32 + y / 32) % 2 ? 0x263b43 : 0x1b3038);
        } else checker.rect(0, 0, WIDTH, HEIGHT).fill(background === 'light' ? 0xf4f0e4 : 0x14262d);
        paintedBackground = background;
      }
      const filtering = playback.filtering ?? 'nearest';
      if (source.style.scaleMode !== filtering) {
        source.style.scaleMode = filtering;
        source.style.update();
      }
      const worldSize = playback.displayMode === 'world-1x';
      app.canvas.style.width = worldSize ? `${WIDTH}px` : '100%';
      app.canvas.style.height = worldSize ? `${HEIGHT}px` : 'auto';
      app.canvas.style.maxWidth = worldSize ? 'none' : '100%';
      const placement = texturePreviewLayout(manifest, playback.displayMode);

      const frame = textureReviewFrameAt(
        manifest,
        playback.clipId,
        playback.reducedMotion ? 0 : elapsedMs,
      );
      const geometry = texturePreviewGeometry(frame);
      sprite.texture = textures.get(frame.id)!;
      sprite.pivot.set(geometry.pivot.x, geometry.pivot.y);
      sprite.position.set(placement.x, placement.y);
      sprite.scale.set(placement.scale * geometry.sourceScale);
      overlay.clear();
      overlay
        .rect(
          placement.x + geometry.bounds.left * placement.scale,
          placement.y + geometry.bounds.top * placement.scale,
          frame.world.width * placement.scale,
          frame.world.height * placement.scale,
        )
        .stroke({ color: 0x91adb8, width: 1, alpha: 0.6 });
      overlay
        .moveTo(placement.x - 6, placement.y)
        .lineTo(placement.x + 6, placement.y)
        .moveTo(placement.x, placement.y - 6)
        .lineTo(placement.x, placement.y + 6)
        .stroke({ color: 0xff8590, width: 2 });
      for (const contact of geometry.contacts)
        overlay
          .circle(
            placement.x + contact.x * placement.scale,
            placement.y + contact.y * placement.scale,
            3,
          )
          .stroke({ color: 0xffdc83, width: 1.5 });
      if (shownFrame !== frame.id) {
        shownFrame = frame.id;
        options.onFrame?.(frame.id);
      }
    };
    app.canvas.setAttribute(
      'aria-label',
      'Unapproved isolated texture review animation with declared pivot and contacts',
    );
    app.canvas.style.width = '100%';
    app.canvas.style.height = 'auto';
    app.canvas.style.display = 'block';
    app.canvas.addEventListener('webglcontextlost', contextLost);
    host.append(app.canvas);
    document.addEventListener('visibilitychange', visibilityChanged);
    app.ticker.add((ticker) => {
      if (disposed) return;
      try {
        if (dropNextDelta) dropNextDelta = false;
        else
          elapsedMs = advanceTexturePreviewClock(elapsedMs, ticker.elapsedMS, {
            paused: playback.paused,
            reducedMotion: playback.reducedMotion,
            hidden: document.hidden,
          });
        draw();
      } catch (error) {
        fail(error instanceof Error ? error.message : 'Texture playback failed.');
      }
    });
    syncPlayback();
    return {
      update(next) {
        if (disposed) return;
        if (!manifest.clips.some((clip) => clip.id === next.clipId)) {
          fail('Selected texture clip is unavailable; no fallback clip is invented.');
          return;
        }
        if (next.clipId !== playback.clipId || next.replayRevision !== playback.replayRevision)
          elapsedMs = 0;
        if (
          next.paused !== playback.paused ||
          next.reducedMotion !== playback.reducedMotion ||
          next.clipId !== playback.clipId ||
          next.replayRevision !== playback.replayRevision
        )
          dropNextDelta = true;
        playback = { ...next };
        try {
          syncPlayback();
        } catch (error) {
          fail(error instanceof Error ? error.message : 'Texture playback failed.');
        }
      },
      destroy: dispose,
    };
  } catch (error) {
    dispose();
    throw error;
  }
}

