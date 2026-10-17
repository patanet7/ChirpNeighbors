import { dev } from '$app/environment';
import { env } from '$env/dynamic/private';
import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { requireOwner, readBoundedBytes } from '$lib/server/http';
import { requestBudgets, requestBudgetResponse } from '$lib/server/operations/request-budget';
import { reviewPackageErrorResponse } from '$lib/workbench/asset-package.server';
import { TEXTURE_REVIEW_LIMITS } from '$lib/workbench/texture-profile';
import {
  createSyntheticTextureReviewBaseline,
  textureReviewClientPackage,
  validateTextureReviewPng,
} from '$lib/workbench/texture-profile.server';

export const POST: RequestHandler = async (event) => {
  const owner = requireOwner(event);
  if (!dev || env.CHIRP_DEV_AUTH !== '1')
    error(404, 'The development texture experiment is unavailable.');
  if (event.locals.identity?.mode !== 'development' || !['dev:alice', 'dev:bob'].includes(owner))
    error(403, 'Choose a development test yard to review textures.');
  if (event.request.headers.get('origin') !== event.url.origin)
    error(403, 'A same-origin request is required.');
  const admission = requestBudgets.acquire('uploads', owner);
  if (!admission.accepted) return requestBudgetResponse(admission);
  try {
    const contentType = event.request.headers.get('content-type') ?? '';
    let pack;
    if (contentType === 'application/json') {
      const bytes = await readBoundedBytes(event.request, 100);
      let input: unknown;
      try {
        input = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes));
      } catch {
        error(400, 'Choose a bounded synthetic baseline.');
      }
      if (
        !input ||
        typeof input !== 'object' ||
        Object.keys(input).length !== 1 ||
        !('syntheticEdge' in input) ||
        (input.syntheticEdge !== 128 && input.syntheticEdge !== 256)
      )
        error(400, 'Choose a 128 or 256 pixel synthetic baseline.');
      const baseline = await createSyntheticTextureReviewBaseline(input.syntheticEdge);
      pack = baseline;
    } else {
      if (contentType.length > 200 || !/^multipart\/form-data;\s*boundary=/i.test(contentType))
        error(415, 'Use a PNG and its texture-review manifest.');
      const bytes = await readBoundedBytes(
        event.request,
        TEXTURE_REVIEW_LIMITS.encodedBytes + TEXTURE_REVIEW_LIMITS.manifestBytes + 65_536,
      );
      let form: FormData;
      try {
        form = await new Response(bytes, { headers: { 'content-type': contentType } }).formData();
      } catch {
        error(400, 'Supply a valid texture review form.');
      }
      if (
        [...form.entries()].length !== 2 ||
        form.getAll('manifest').length !== 1 ||
        form.getAll('file').length !== 1
      )
        error(400, 'Supply exactly one manifest and one PNG.');
      const text = form.get('manifest'),
        file = form.get('file');
      if (
        typeof text !== 'string' ||
        new TextEncoder().encode(text).byteLength > TEXTURE_REVIEW_LIMITS.manifestBytes ||
        !file ||
        typeof file === 'string' ||
        file.type !== 'image/png' ||
        file.size > TEXTURE_REVIEW_LIMITS.encodedBytes
      )
        error(400, 'The texture input exceeds the experiment bounds.');
      let manifest: unknown;
      try {
        manifest = JSON.parse(text);
      } catch {
        error(400, 'The texture manifest must be valid JSON.');
      }
      pack = await validateTextureReviewPng(new Uint8Array(await file.arrayBuffer()), manifest);
    }
    if (event.request.signal.aborted) error(408, 'The texture request was cancelled.');
    return json(textureReviewClientPackage(pack), {
      headers: { 'cache-control': 'private, no-store' },
    });
  } catch (cause) {
    return reviewPackageErrorResponse(cause);
  } finally {
    admission.release();
  }
};

