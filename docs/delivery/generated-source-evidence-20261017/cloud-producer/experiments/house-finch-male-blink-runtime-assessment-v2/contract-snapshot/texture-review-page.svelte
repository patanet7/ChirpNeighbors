<script lang="ts">
  import { onMount } from 'svelte';
  import { resolve } from '$app/paths';
  import { checkedRequest } from '$lib/client/service';
  import TextureReviewPreview from '$lib/components/TextureReviewPreview.svelte';
  import { createTextureReviewExport } from '$lib/workbench/texture-review-export';
  import {
    textureReviewClientPackageSchema,
    TEXTURE_REVIEW_LIMITS,
    type TextureReviewClientPackage,
  } from '$lib/workbench/texture-profile';

  let packageData = $state.raw<TextureReviewClientPackage | null>(null);
  let manifestFile = $state<File | null>(null);
  let pngFile = $state<File | null>(null);
  let busy = $state(false);
  let error = $state('');
  let notice = $state(
    'Load a synthetic baseline or deliberately supply a compatible experimental package.',
  );
  let clipId = $state('idle');
  let paused = $state(true);
  let reducedMotion = $state(false);
  let replayRevision = $state(0);
  let originalPng = $state.raw<Uint8Array | null>(null);
  let exporting = $state(false);
  let exportDigest = $state('');
  let exportController: AbortController | null = null;
  let generation = 0;
  let disposed = false;
  let controller: AbortController | null = null;
  const receipt = $derived(packageData?.receipt);
  onMount(() => {
    reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    return () => {
      disposed = true;
      generation++;
      controller?.abort();
      exportController?.abort();
    };
  });
  function clear() {
    generation++;
    controller?.abort();
    controller = null;
    exportController?.abort();
    exportController = null;
    exporting = false;
    originalPng = null;
    exportDigest = '';
    packageData = null;
    busy = false;
    notice = 'Experiment cleared. Saved yard assets, pins and current limits were unchanged.';
  }
  async function load(edge?: 128 | 256) {
    if (busy || disposed || (!edge && (!manifestFile || !pngFile))) return;
    const capturedManifest = manifestFile,
      capturedPng = pngFile;
    const revision = ++generation;
    const requestController = new AbortController();
    controller = requestController;
    busy = true;
    error = '';
    packageData = null;
    originalPng = null;
    exportDigest = '';
    exportController?.abort();
    exportController = null;
    exporting = false;
    try {
      let capturedOriginal: Uint8Array | null = null;
      let body: BodyInit;
      let headers: HeadersInit | undefined;
      if (edge) {
        body = JSON.stringify({ syntheticEdge: edge });
        headers = { 'content-type': 'application/json' };
      } else {
        if (
          !capturedManifest ||
          !capturedPng ||
          capturedManifest.size > TEXTURE_REVIEW_LIMITS.manifestBytes ||
          capturedPng.size > TEXTURE_REVIEW_LIMITS.encodedBytes
        )
          throw new Error('The texture experiment input exceeds its explicit bounds.');
        const text = await capturedManifest.text();
        capturedOriginal = new Uint8Array(await capturedPng.arrayBuffer());
        if (disposed || generation !== revision) return;
        const form = new FormData();
        form.append('manifest', text);
        form.append('file', capturedPng, capturedPng.name);
        body = form;
      }
      const response = await checkedRequest(
        '/api/texture-review',
        textureReviewClientPackageSchema,
        { method: 'POST', body, ...(headers ? { headers } : {}) },
        (input, init) =>
          fetch(input, {
            ...init,
            signal: AbortSignal.any([
              requestController.signal,
              ...(init?.signal ? [init.signal] : []),
            ]),
          }),
      );
      if (disposed || generation !== revision) return;
      if (!response.ok)
        throw new Error(response.message ?? 'The texture experiment rejected this input.');
      packageData = response.data;
      originalPng = capturedOriginal;
      clipId = response.data.manifest.clips[0]!.id;
      paused = true;
      replayRevision++;
      notice = edge
        ? 'Synthetic technical pixels only. They establish allocation and transport behavior, not bird fidelity.'
        : 'Supplied texture accepted for this isolated review only. Rights, identity, contacts and appearance remain unapproved.';
    } catch (cause) {
      if (!disposed && generation === revision)
        error =
          cause instanceof Error ? cause.message : 'The texture experiment could not complete.';
    } finally {
      if (!disposed && generation === revision) {
        busy = false;
        controller = null;
      }
    }
  }
  async function downloadReview() {
    if (!packageData || !originalPng || busy || exporting || disposed) return;
    const capturedPackage = packageData;
    const capturedOriginal = originalPng;
    const revision = generation;
    const taskController = new AbortController();
    exportController = taskController;
    exporting = true;
    error = '';
    let url: string | undefined;
    try {
      const result = await createTextureReviewExport(
        capturedPackage,
        capturedOriginal,
        [],
        taskController.signal,
      );
      if (disposed || generation !== revision || packageData !== capturedPackage) return;
      url = URL.createObjectURL(new Blob([result.json], { type: 'application/json' }));
      const link = document.createElement('a');
      link.href = url;
      link.download = `unapproved-texture-review-${result.contentDigest.slice(0, 12)}.json`;
      link.click();
      exportDigest = result.contentDigest;
      notice =
        'Exported the supplied PNG, exact manifest and canonical validation receipt for private review. Artwork and contacts remain unapproved; nothing was activated.';
    } catch (cause) {
      if (!disposed && generation === revision && !taskController.signal.aborted)
        error = cause instanceof Error ? cause.message : 'The review export could not complete.';
    } finally {
      if (url) URL.revokeObjectURL(url);
      if (!disposed && generation === revision) {
        exporting = false;
        if (exportController === taskController) exportController = null;
      }
    }
  }
</script>

<svelte:head
  ><title>Texture profile experiment · ChirpNeighbors</title><meta
    name="robots"
    content="noindex,nofollow"
  /></svelte:head
>
<main>
  <nav>
    <a href={resolve('/candidate-yard')}>Candidate yard preview</a>
    <a href={resolve('/art-lab')}>Art & engine lab</a><a href={resolve('/asset-review')}
      >Existing rectangle review</a
    ><a href={resolve('/')}>Your yard</a>
  </nav>
  <h1>Detailed texture profile experiment</h1>
  <p>
    This private isolated canvas evaluates bounded straight-RGBA textures using Pixi. It creates no
    resident, approval, saved pin or replacement default. Current rectangle contracts and yard
    layout remain unchanged.
  </p>
  <section aria-label="Synthetic texture baselines">
    <h2>Measure technical capacity</h2>
    <button disabled={busy} onclick={() => load(128)}>Load 16 × 128px synthetic frames</button>
    <button disabled={busy} onclick={() => load(256)}>Load 16 × 256px synthetic frames</button>
    <p>
      These generated test patterns exercise dense color and partial alpha. They are not bird
      artwork.
    </p>
  </section>
  <section aria-label="Supplied texture review">
    <h2>Review a deliberately prepared candidate</h2>
    <label
      >Experimental manifest JSON<input
        type="file"
        accept="application/json,.json"
        disabled={busy}
        onchange={(event) => (manifestFile = event.currentTarget.files?.[0] ?? null)}
      /></label
    >
    <label
      >Declared atlas PNG<input
        type="file"
        accept="image/png,.png"
        disabled={busy}
        onchange={(event) => (pngFile = event.currentTarget.files?.[0] ?? null)}
      /></label
    >
    <button disabled={busy || !manifestFile || !pngFile} onclick={() => load()}
      >Validate for isolated review</button
    >
    <p>
      Experimental ceiling: 4 MiB encoded PNG, 1024px atlas edge, 1,048,576 decoded pixels / 4 MiB
      RGBA, 64 stored frames, 512px frame edge, 256 sequence steps. This is an evaluation envelope,
      not an approved production default.
    </p>
  </section>
  <button disabled={!packageData && !busy} onclick={clear}
    >{busy ? 'Cancel experiment' : 'Clear experiment'}</button
  >
  <p role="status">{notice}</p>
  {#if error}<p role="alert">{error}</p>{/if}
  {#if packageData && receipt}
    <section aria-label="Texture playback">
      <label
        >Clip<select bind:value={clipId}
          >{#each packageData.manifest.clips as clip (clip.id)}<option value={clip.id}
              >{clip.id}</option
            >{/each}</select
        ></label
      >
      <button onclick={() => (paused = !paused)}>{paused ? 'Play review clip' : 'Pause'}</button>
      <button onclick={() => replayRevision++}>Replay</button>
      <label><input type="checkbox" bind:checked={reducedMotion} />Reduced motion</label>
      <TextureReviewPreview {packageData} {clipId} {paused} {reducedMotion} {replayRevision} />
    </section>
    <section aria-label="Measured texture receipt">
      <h2>Observed CPU receipt</h2>
      <button
        onclick={downloadReview}
        disabled={busy || exporting || !originalPng}
        data-testid="export-texture-review"
        >{exporting ? 'Preparing export…' : 'Export supplied texture review'}</button
      >
      <p>
        Export retains the supplied PNG, exact manifest and canonical validation receipt. Choose a
        supplied PNG to enable export; synthetic baselines do not retain an original upload.
      </p>
      {#if exportDigest}<p>Export content SHA-256: <code>{exportDigest}</code></p>{/if}
      <dl>
        <dt>Atlas / stored frames</dt>
        <dd>{receipt.canonical.width} × {receipt.canonical.height} / {receipt.metrics.frames}</dd>
        <dt>Decoded RGBA allocation</dt>
        <dd>{receipt.metrics.knownDecodedRgbaBytes.toLocaleString()} bytes</dd>
        <dt>Canonical PNG / visible colors</dt>
        <dd>
          {receipt.canonical.bytes.toLocaleString()} bytes / {receipt.metrics.visibleRgbColors.toLocaleString()}
        </dd>
        <dt>Partial-alpha pixels</dt>
        <dd>{receipt.metrics.partialAlphaPixels.toLocaleString()}</dd>
        <dt>CPU decode / validation / encode / total</dt>
        <dd>
          {receipt.timings.decodeMs.toFixed(2)} / {receipt.timings.validationMs.toFixed(2)} / {receipt.timings.encodeMs.toFixed(
            2,
          )} / {receipt.timings.totalMs.toFixed(2)} ms
        </dd>
        <dt>Canonical SHA-256</dt>
        <dd><code>{receipt.canonical.sha256}</code></dd>
      </dl>
      <p>
        Buffer counts are known allocations, not peak process memory or GPU/VRAM measurements.
        Timing is one CPU wall-time sample. Contact checks establish a nonzero-alpha source pixel,
        not physical support or species fidelity. Playback and actual GPU appearance still require
        visual review.
      </p>
    </section>
  {/if}
</main>

<style>
  main {
    max-width: 64rem;
    margin: 2rem auto;
    padding: 0 1rem;
  }
  nav,
  section {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }
  section {
    align-items: center;
    padding: 1rem;
    border: 1px solid #cdd8cf;
  }
  section h2,
  section p,
  section dl {
    flex-basis: 100%;
  }
  label {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    align-items: center;
  }
  section > label {
    min-width: 0;
    max-width: 100%;
  }
  input[type='file'] {
    min-width: 0;
    max-width: 100%;
  }
  dl {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) 2fr;
    gap: 0.5rem;
  }
  dd {
    margin: 0;
    overflow-wrap: anywhere;
  }
  code {
    overflow-wrap: anywhere;
  }
</style>

