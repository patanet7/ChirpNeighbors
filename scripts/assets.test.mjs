// node --test scripts/assets.test.mjs — the id grammar, the state-suffix parser and the art/evidence
// split, on fixtures (never the real tree).
import test from 'node:test';
import assert from 'node:assert/strict';
import { parseId, isValidId, slotOf, parseStateSuffix, classifyImage, imageInfo, reviewToSlot, candidateVersion } from './lib/layout.mjs';
import { encodePng } from './lib/png.mjs';

test('id grammar: valid ids parse into their parts', () => {
  assert.deepEqual(
    { ...parseId('birds/house_finch/clips/hop/v2') },
    { id: 'birds/house_finch/clips/hop/v2', kind: 'birds', name: 'house_finch', subject: 'birds/house_finch', slot: 'clips/hop', version: 'v2', act: 'hop' },
  );
  assert.equal(parseId('birds/common_raven/canon').act, 'canon');
  const plant = parseId('plants/coast_live_oak/mature.winter.bare/c1a2b3c4d');
  assert.deepEqual([plant.form, plant.season, plant.state, plant.version], ['mature', 'winter', 'bare', 'c1a2b3c4d']);
  assert.equal(parseId('plants/monstera_deliciosa/potted.all').state, null);
  assert.equal(parseId('objects/bench/v3').slot, null);
  assert.equal(parseId('objects/bench/wet').state, 'wet');
  const scene = parseId('scenes/inland/winter.snow/composite');
  assert.deepEqual([scene.season, scene.state, scene.layer], ['winter', 'snow', 'composite']);
  assert.equal(parseId('inbox/c0123abcd').kind, 'inbox');
  assert.equal(slotOf('scenes/coastal/autumn/composite/v1'), 'scenes/coastal/autumn/composite');
  assert.equal(slotOf('objects/bench/v1'), 'objects/bench');
  assert.equal(candidateVersion('885fc45c96046d6b'), 'c885fc45c');
});

test('id grammar: bad ids are refused', () => {
  for (const bad of [
    'trees/oak', // unknown kind
    'birds/House_Finch', // not snake_case
    'birds/house_finch/clips/dance', // unknown act
    'birds/house_finch/hop', // clips/ missing
    'plants/oak/big.all', // unknown form
    'plants/oak/mature.monsoon', // unknown season
    'plants/oak/mature.all.glowing', // unknown state
    'scenes/coastal/autumn', // layer missing
    'scenes/coastal/autumn/sky', // unknown layer
    'objects/bench/v0', // versions start at 1
    'inbox/abc', // inbox needs c<sha8>
    'packs/sage/canon', // packs have no slots
  ])
    assert.equal(isValidId(bad), false, bad);
});

test('state suffixes: the first state word after __ wins; seasons are read too', () => {
  assert.equal(parseStateSuffix('arrowwood__dry_spent.png').state, 'dry');
  assert.equal(parseStateSuffix('coyote_brush__mild_dry_stress.png').state, 'dry');
  assert.equal(parseStateSuffix('purple_needlegrass__healthy_seed_morphology_r01.png').state, 'base');
  assert.equal(parseStateSuffix('toyon__fruiting.png').state, 'fruit');
  assert.equal(parseStateSuffix('fuchsia__flowering_r2.png').state, 'bloom');
  assert.deepEqual(parseStateSuffix('maple__autumn_foliage.png'), { state: null, season: 'autumn', suffix: 'autumn_foliage' });
  // without __ only a final word that is exactly a state or season counts
  assert.equal(parseStateSuffix('arrowwood-dry.png').state, 'dry');
  assert.equal(parseStateSuffix('maple-autumn-foliage.png').season, null);
  assert.deepEqual(parseStateSuffix('house-finch-hop-03.png'), { state: null, season: null, suffix: null });
});

const png = (w, h, alphaAt) => {
  const data = new Uint8Array(w * h * 4);
  for (let i = 0; i < w * h; i++) {
    data.set([120, 90, 60, alphaAt(i % w, Math.floor(i / w))], i * 4);
  }
  return Buffer.from(encodePng({ width: w, height: h, data }));
};
const cutout = png(8, 8, (x, y) => (x > 1 && x < 6 && y > 1 ? 255 : 0)); // sprite with clear surround
const solid = png(8, 8, () => 255); // RGBA but every pixel opaque

test('art vs evidence: decided by type, alpha and name, with a reason', () => {
  assert.equal(imageInfo(cutout).hasAlphaChannel, true);
  assert.ok(imageInfo(cutout).transparentFraction > 0.4);
  assert.equal(imageInfo(solid).transparentFraction, 0);

  const art = classifyImage('assets/generated/packs/x/sprites/toyon.png', imageInfo(cutout));
  assert.deepEqual(art, { class: 'art', why: 'transparent PNG (RGBA cut-out)' });
  // opaque render of a sprite: evidence
  assert.equal(classifyImage('packs/x/renders/toyon.png', imageInfo(solid)).class, 'evidence');
  assert.match(classifyImage('packs/x/renders/toyon.png', imageInfo(solid)).why, /opaque/);
  // opaque background: art (scenes are opaque by nature)
  assert.equal(classifyImage('packs/x/backgrounds/coastal/originals/autumn-r1.png', imageInfo(solid)).class, 'art');
  // contact sheets and previews by name, even when transparent
  assert.equal(classifyImage('packs/x/toyon-contact-sheet.png', imageInfo(cutout)).class, 'evidence');
  assert.equal(classifyImage('packs/x/qa/toyon.png', imageInfo(cutout)).class, 'evidence');
  assert.equal(classifyImage('packs/x/toyon_compare.png', imageInfo(cutout)).class, 'evidence');
  // non-PNG formats
  assert.equal(classifyImage('packs/x/hop.gif').class, 'evidence');
  assert.equal(classifyImage('packs/x/hop.apng').class, 'evidence');
  assert.equal(classifyImage('packs/x/photo.jpg').class, 'evidence');
  assert.equal(classifyImage('packs/x/broken.png', imageInfo(Buffer.from('nope'))).class, 'evidence');
  // a sprite whose name merely contains a word like "background" stays art
  assert.equal(classifyImage('packs/x/sprites/sagebrush.png', imageInfo(cutout)).class, 'art');
});

test('legacy review slot ids map to the new grammar', () => {
  assert.equal(reviewToSlot('house_finch.canon'), 'birds/house_finch/canon');
  assert.equal(reviewToSlot('house_finch.hop'), 'birds/house_finch/clips/hop');
  assert.equal(reviewToSlot('object.feeder.cedar'), 'objects/feeder_cedar');
  assert.equal(reviewToSlot('object.misc.hose_reel'), 'objects/misc_hose_reel');
  assert.equal(reviewToSlot('plant.toyon_evergreen'), 'plants/toyon_evergreen/mature.all');
  assert.equal(reviewToSlot('plant.monstera_deliciosa', () => 'potted'), 'plants/monstera_deliciosa/potted.all');
  assert.equal(reviewToSlot('plant.maple_autumn'), 'plants/maple/mature.autumn');
  assert.equal(reviewToSlot('plant.healthy'), 'plants/coast_live_oak/mature.all'); // a mislabelled oak canopy
  assert.equal(reviewToSlot('scene.coastal.autumn'), 'scenes/coastal/autumn/composite');
  assert.equal(reviewToSlot('scene.coastal_urban.ground'), 'scenes/coastal/all/ground');
  assert.equal(reviewToSlot('weather.snow'), 'scenes/weather/all.snow/overlay');
  assert.equal(reviewToSlot('season.winter'), 'scenes/seasonal/winter/composite');
  assert.equal(reviewToSlot('nonsense'), null);
});
