import { Container, Graphics, ImageSource, Rectangle, Sprite, Texture } from 'pixi.js';
import { textureReviewFrameAt, TEXTURE_REVIEW_LIMITS } from '../workbench/texture-profile';
import {
  verifyYardReviewTexture,
  projectReviewTextureFrame,
  type CheckedYardReviewTexture,
} from './review-texture';

export interface ReviewTextureView {
  readonly container: Container;
  sample(timeSeconds: number, reducedMotion?: boolean): void;
  diagnostics(): {
    frameId: string | null;
    animated: boolean;
    static: boolean;
    primitiveCount: number;
    decodedRgbaBytes: number;
    textureCount: number;
    disposed: boolean;
    depthY: number;
  };
  destroy(): void;
}

/**
 * One owned sprite in the existing yard depth layer, without a new application, clock,
 * cache, physics object, slot, resident or saved pin. All source pixels remain review-only.
 */
export async function createReviewTextureView(
  selection: CheckedYardReviewTexture,
  signal?: AbortSignal,
): Promise<ReviewTextureView> {
  let disposed = false;
  let url: string | undefined;
  let image: HTMLImageElement | undefined;
  let source: ImageSource | undefined;
  let container: Container | undefined;
  let sprite: Sprite | undefined;
  let overlay: Graphics | undefined;
  let frameId: string | null = null;
  const textures = new Map<string, Texture>();
  function dispose() {
    disposed = true;
    signal?.removeEventListener('abort', dispose);
    container?.destroy({ children: true, context: true, texture: false, textureSource: false });
    container = undefined;
    sprite = undefined;
    overlay = undefined;
    for (const texture of textures.values()) texture.destroy(false);
    textures.clear();
    source?.destroy();
    source = undefined;
    image?.removeAttribute('src');
    image = undefined;
    if (url) {
      URL.revokeObjectURL(url);
      url = undefined;
    }
  }
  function checkCancelled() {
    if (disposed || signal?.aborted)
      throw new DOMException('Review texture cancelled.', 'AbortError');
  }
  signal?.addEventListener('abort', dispose, { once: true });
  try {
    const verified = await verifyYardReviewTexture(selection, signal);
    checkCancelled();
    const manifest = verified.packageData.manifest;
    url = URL.createObjectURL(new Blob([verified.bytes.buffer], { type: 'image/png' }));
    image = new Image();
    image.decoding = 'async';
    image.src = url;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let abort: (() => void) | undefined;
    try {
      await Promise.race([
        image.decode(),
        new Promise<never>((_, reject) => {
          abort = () => reject(new DOMException('Review texture cancelled.', 'AbortError'));
          signal?.addEventListener('abort', abort, { once: true });
          if (signal?.aborted) abort();
          timer = setTimeout(
            () => reject(new Error('Review texture decode timed out.')),
            TEXTURE_REVIEW_LIMITS.decodeSeconds * 1_000,
          );
        }),
      ]);
    } finally {
      clearTimeout(timer);
      if (abort) signal?.removeEventListener('abort', abort);
    }
    checkCancelled();
    if (
      image.naturalWidth !== manifest.atlas.width ||
      image.naturalHeight !== manifest.atlas.height
    )
      throw new Error('Decoded review texture dimensions mismatch.');
    source = new ImageSource({
      resource: image,
      alphaMode: 'premultiply-alpha-on-upload',
      scaleMode: 'nearest',
      autoGenerateMipmaps: false,
      resolution: 1,
    });
    for (const id of new Set(selection.idleFrameIds)) {
      const geometry = projectReviewTextureFrame(selection, id);
      textures.set(
        id,
        new Texture({
          source,
          frame: new Rectangle(
            geometry.sourceRect.x,
            geometry.sourceRect.y,
            geometry.sourceRect.width,
            geometry.sourceRect.height,
          ),
          orig: new Rectangle(0, 0, geometry.canvas.width, geometry.canvas.height),
          trim: new Rectangle(
            geometry.trim.x,
            geometry.trim.y,
            geometry.sourceRect.width,
            geometry.sourceRect.height,
          ),
        }),
      );
    }
    container = new Container({ label: 'review-texture-unapproved' });
    container.eventMode = 'none';
    container.zIndex = selection.depthY;
    container.position.set(selection.placement.x, selection.placement.y);
    const first = textureReviewFrameAt(manifest, selection.clipId, 0);
    sprite = new Sprite({ texture: textures.get(first.id)! });
    container.addChild(sprite);
    if (selection.showContacts) {
      overlay = new Graphics();
      container.addChild(overlay);
    }
    const owned = container;
    const primitiveCount = selection.showContacts ? 4 + selection.contacts.length : 1;
    function sample(timeSeconds: number, reducedMotion = false) {
      if (disposed || !sprite) return;
      if (!Number.isFinite(timeSeconds) || timeSeconds < 0)
        throw new RangeError('Invalid review texture scene time.');
      const frame = textureReviewFrameAt(
        manifest,
        selection.clipId,
        reducedMotion ? 0 : timeSeconds * 1_000,
      );
      if (frameId === frame.id) return;
      frameId = frame.id;
      const geometry = projectReviewTextureFrame(selection, frame.id);
      sprite.texture = textures.get(frame.id)!;
      sprite.pivot.set(geometry.pivot.x, geometry.pivot.y);
      sprite.scale.set(geometry.sourceScale);
      if (overlay) {
        overlay.clear();
        overlay
          .rect(
            geometry.bounds.left - selection.placement.x,
            geometry.bounds.top - selection.placement.y,
            geometry.bounds.right - geometry.bounds.left,
            geometry.bounds.bottom - geometry.bounds.top,
          )
          .stroke({ color: 0x91adb8, width: 1, alpha: 0.7 });
        overlay
          .moveTo(-4, 0)
          .lineTo(4, 0)
          .moveTo(0, -4)
          .lineTo(0, 4)
          .stroke({ color: 0xff8590, width: 1 });
        for (const contact of geometry.contacts)
          overlay
            .circle(contact.x - selection.placement.x, contact.y - selection.placement.y, 2)
            .stroke({ color: 0xffdc83, width: 1 });
      }
    }
    sample(0);
    return {
      container: owned,
      sample,
      diagnostics() {
        return {
          frameId,
          animated: selection.animated,
          static: !selection.animated,
          primitiveCount: disposed ? 0 : primitiveCount,
          decodedRgbaBytes: disposed ? 0 : manifest.atlas.width * manifest.atlas.height * 4,
          textureCount: textures.size,
          disposed,
          depthY: selection.depthY,
        };
      },
      destroy: dispose,
    };
  } catch (error) {
    dispose();
    throw error;
  }
}

