import { z } from 'zod';
import type { WeatherCondition } from '../weather/contracts.ts';
export const REGIONAL_VARIANT_IDS = [
  'sd-coastal-spring-v1',
  'sd-coastal-summer-v1',
  'sd-coastal-autumn-v1',
  'sd-coastal-winter-v1',
  'sd-oak-spring-v1',
  'sd-oak-summer-v1',
  'sd-oak-autumn-v1',
  'sd-oak-winter-v1',
  'sd-courtyard-spring-v1',
  'sd-courtyard-summer-v1',
  'sd-courtyard-autumn-v1',
  'sd-courtyard-winter-v1',
  'sd-inland-spring-v1',
  'sd-inland-summer-v1',
  'sd-inland-autumn-v1',
  'sd-inland-winter-v1',
  'sd-patio-spring-v1',
  'sd-patio-summer-v1',
  'sd-patio-autumn-v1',
  'sd-patio-winter-v1',
] as const;
export const regionalBackgroundSchema = z.enum([
  'coastal',
  'oak',
  'courtyard',
  ...REGIONAL_VARIANT_IDS,
]);
export type RegionalBackground = z.infer<typeof regionalBackgroundSchema>;
/** Fixed candidate source selection. These are paint identities, not navigation scenes. */
export const REGIONAL_BACKGROUNDS = [
  { id: 'coastal', label: 'Coastal garden', subjectId: 'scene.san_diego_coastal_urban' },
  { id: 'oak', label: 'Oak shade pocket', subjectId: 'scene.san_diego_oak_riparian_shade_pocket' },
  {
    id: 'courtyard',
    label: 'Marine courtyard',
    subjectId: 'scene.san_diego_compact_marine_courtyard',
  },
] as const;
/** Authored experiment presets, not measurements or a weather provider. Core water remains SI. */
export function physicalForSavedWeather(condition: WeatherCondition) {
  return condition === 'snow'
    ? { precipitationMmPerHour: 12, snowFraction: 1, temperatureC: -2 }
    : condition === 'rain'
      ? { precipitationMmPerHour: 24, snowFraction: 0, temperatureC: 10 }
      : { precipitationMmPerHour: 0, snowFraction: 0, temperatureC: 18 };
}

export const regionalAssetIdSchema = z.enum([...regionalBackgroundSchema.options, 'sunflower']);

export const regionalSeasonSchema = z.enum(['spring', 'summer', 'autumn', 'winter']);
export const regionalYardTypeSchema = z.enum(['coastal', 'oak', 'courtyard', 'inland', 'patio']);
export const REGIONAL_YARD_TYPES = [
  { id: 'coastal', label: 'Coastal garden', subjectId: 'scene.san_diego_coastal_urban' },
  { id: 'oak', label: 'Oak shade pocket', subjectId: 'scene.san_diego_oak_riparian_shade_pocket' },
  {
    id: 'courtyard',
    label: 'Marine courtyard',
    subjectId: 'scene.san_diego_compact_marine_courtyard',
  },
  { id: 'inland', label: 'Inland canyon', subjectId: 'scene.san_diego_inland_canyon' },
  { id: 'patio', label: 'Managed patio', subjectId: 'scene.san_diego_managed_patio' },
] as const;
/** PR24 exact originals; static seasonal paint only, never automatic climate or plant simulation. */
export const REGIONAL_SEASONAL_BACKGROUNDS = [
  {
    id: 'sd-coastal-spring-v1',
    yardType: 'coastal',
    season: 'spring',
    subjectId: 'scene.san_diego_coastal_urban',
    sourceVariantId: 'wave04_coastal_garden_v1.season_spring_v1',
    sourceSha256: 'c777cbc06a9cb28865953116b8ce1c69db0bd94d99094f7b52555a4020f9b292',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-coastal-summer-v1',
    yardType: 'coastal',
    season: 'summer',
    subjectId: 'scene.san_diego_coastal_urban',
    sourceVariantId: 'wave04_coastal_garden_v1.season_summer_v1',
    sourceSha256: 'aae94e6c83e5d0d9396f79fe4c3f9144b9769747e15ac2485dbe09bc461d133c',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-coastal-autumn-v1',
    yardType: 'coastal',
    season: 'autumn',
    subjectId: 'scene.san_diego_coastal_urban',
    sourceVariantId: 'wave04_coastal_garden_v1.season_autumn_v1',
    sourceSha256: '885fc45c96046d6b950e9e5dcc028ab0e4bf1d6d4aa77d603fd3ab3b7df83847',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-coastal-winter-v1',
    yardType: 'coastal',
    season: 'winter',
    subjectId: 'scene.san_diego_coastal_urban',
    sourceVariantId: 'wave04_coastal_garden_v1.season_winter_v1',
    sourceSha256: '7a2f9252394c915dab3efdc7e9c2ba774609f52a68eba10937bc1bcd0c664e52',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-oak-spring-v1',
    yardType: 'oak',
    season: 'spring',
    subjectId: 'scene.san_diego_oak_riparian_shade_pocket',
    sourceVariantId: 'wave04_shaded_oak_garden_v1.season_spring_v1',
    sourceSha256: '3e505fd584cc77037e359a99e5eca8ada7d5062c82012ff4678e280fda2e30d7',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-oak-summer-v1',
    yardType: 'oak',
    season: 'summer',
    subjectId: 'scene.san_diego_oak_riparian_shade_pocket',
    sourceVariantId: 'wave04_shaded_oak_garden_v1.season_summer_v1',
    sourceSha256: '0e9418353d4026980fa70651782189a72556a65fca266abdfe9fbcaec370aef2',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-oak-autumn-v1',
    yardType: 'oak',
    season: 'autumn',
    subjectId: 'scene.san_diego_oak_riparian_shade_pocket',
    sourceVariantId: 'wave04_shaded_oak_garden_v1.season_autumn_v1',
    sourceSha256: 'b4278bce52436534aba56d315bf7db142a77017aa6c793d0833b415c6f4eeb02',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-oak-winter-v1',
    yardType: 'oak',
    season: 'winter',
    subjectId: 'scene.san_diego_oak_riparian_shade_pocket',
    sourceVariantId: 'wave04_shaded_oak_garden_v1.season_winter_v1',
    sourceSha256: '55a4bd6c74091f293873f8458936899ab6930efc3e83c40d539ceb2b3c7655db',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-courtyard-spring-v1',
    yardType: 'courtyard',
    season: 'spring',
    subjectId: 'scene.san_diego_compact_marine_courtyard',
    sourceVariantId: 'wave04_mediterranean_courtyard_v1.season_spring_v1',
    sourceSha256: '19032eece1ec17b119532029e78f43d49bc8f3eae5593a395b18c21baae5d9ab',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-courtyard-summer-v1',
    yardType: 'courtyard',
    season: 'summer',
    subjectId: 'scene.san_diego_compact_marine_courtyard',
    sourceVariantId: 'wave04_mediterranean_courtyard_v1.season_summer_v1',
    sourceSha256: '0b3999342ea1a54d813082c3292b38391830429ebdf983d76b761ab2cf2f73a3',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-courtyard-autumn-v1',
    yardType: 'courtyard',
    season: 'autumn',
    subjectId: 'scene.san_diego_compact_marine_courtyard',
    sourceVariantId: 'wave04_mediterranean_courtyard_v1.season_autumn_v1',
    sourceSha256: '20c89a58e484f02c989e42cb9aded052a5160eea6c0c567c2266f2c1faca56e7',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-courtyard-winter-v1',
    yardType: 'courtyard',
    season: 'winter',
    subjectId: 'scene.san_diego_compact_marine_courtyard',
    sourceVariantId: 'wave04_mediterranean_courtyard_v1.season_winter_v1',
    sourceSha256: '4080cbf1bae374ac47fa4ccb501d61ca41e8e95323e83d110eb480ea725f47bf',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-inland-spring-v1',
    yardType: 'inland',
    season: 'spring',
    subjectId: 'scene.san_diego_inland_canyon',
    sourceVariantId: 'san_diego_20261017_candidate_v1.season_spring_v1',
    sourceSha256: '47850cdeaeb88d3cf37a7f42cc67da1662abbc7308ee13e0ef1cf48c9452108a',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-inland-summer-v1',
    yardType: 'inland',
    season: 'summer',
    subjectId: 'scene.san_diego_inland_canyon',
    sourceVariantId: 'san_diego_20261017_candidate_v1.season_summer_v1',
    sourceSha256: '8ffbe697b0e4ff90f6033172d01a455d7f3fb503bcf7d53a1c70f92ca8fe9182',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-inland-autumn-v1',
    yardType: 'inland',
    season: 'autumn',
    subjectId: 'scene.san_diego_inland_canyon',
    sourceVariantId: 'san_diego_20261017_candidate_v1.season_autumn_v1',
    sourceSha256: 'fa92e219de328087b4b49b1b4c1ae4507efb3abacd95f9ce2888540fe7c02caf',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-inland-winter-v1',
    yardType: 'inland',
    season: 'winter',
    subjectId: 'scene.san_diego_inland_canyon',
    sourceVariantId: 'san_diego_20261017_candidate_v1.season_winter_v1',
    sourceSha256: '6cdd7d0ac6acca8139a47b631abd9997c84628ba7781309fb3df961021e4f622',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-patio-spring-v1',
    yardType: 'patio',
    season: 'spring',
    subjectId: 'scene.san_diego_managed_patio',
    sourceVariantId: 'san_diego_20261017_candidate_v1.season_spring_v1',
    sourceSha256: '81bc62e5b8a5ba7f57d3215fe258c41e9fcf0d3d7be57754c05515ae195a0e1c',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-patio-summer-v1',
    yardType: 'patio',
    season: 'summer',
    subjectId: 'scene.san_diego_managed_patio',
    sourceVariantId: 'san_diego_20261017_candidate_v1.season_summer_v1',
    sourceSha256: 'c2b77c08ef654c4277f82a4246353bcd79414dc7fd8b8d708b0fdcbcd7efcf1e',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-patio-autumn-v1',
    yardType: 'patio',
    season: 'autumn',
    subjectId: 'scene.san_diego_managed_patio',
    sourceVariantId: 'san_diego_20261017_candidate_v1.season_autumn_v1',
    sourceSha256: '076a1c837ddf19a7bc53f10d3b4c182db05ada62e38e7928cf22628acc7691f6',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
  {
    id: 'sd-patio-winter-v1',
    yardType: 'patio',
    season: 'winter',
    subjectId: 'scene.san_diego_managed_patio',
    sourceVariantId: 'san_diego_20261017_candidate_v1.season_winter_v1',
    sourceSha256: '4caebd048e47f47de74b9a6a069a790d3fbda51e36afa569652f444707d44988',
    sourceCommit: '28566c7012eeae322553682d44873b0df64f73d6',
  },
] as const;
export function regionalVariantId(yard: unknown, season: unknown) {
  const [yardType, seasonType] = z
    .tuple([regionalYardTypeSchema, regionalSeasonSchema])
    .parse([yard, season]);
  const found = REGIONAL_SEASONAL_BACKGROUNDS.find(
    (item) => item.yardType === yardType && item.season === seasonType,
  );
  if (!found) throw new Error('The selected yard and season are unavailable.');
  return found.id;
}

/** Frozen retained adaptation revisions. Source identity only; never geometry review. */
export const regionalSourceExportDigests: Readonly<
  Record<z.infer<typeof regionalAssetIdSchema>, string>
> = {
  coastal: '4e55a97f6365088ef33c3fdafa89605ec6fab71033e84a794de1b79fa5c8b90a',
  oak: 'f55afd6c46164adbf7a1942b869999405f327275554f68462ef60e98680d5444',
  courtyard: '17c4918c0221356d597d6e2c9c8f1d46f4592e711b50faaf6e7b1113711c6710',
  sunflower: '432323ada20ba1058277c396c36b50f84c99c0d0a2f6e6e8976b4f1142bb370a',
  'sd-coastal-spring-v1': 'd3f400262544a0df9d71475bd596b82ab20be9cdfc24440bf8352f0d60216dd9',
  'sd-coastal-summer-v1': 'c0757aad59c21fc762f83e594824a1534d99a46a69308e7adc09b3270f09b9ce',
  'sd-coastal-autumn-v1': 'bb4121100ac49dd116430c6a200369a27a54170fe14eabdc4691c8bd91c8f0e3',
  'sd-coastal-winter-v1': 'fa0a2118e19a468536c39e1946a48fba3193c04adbfda848371b8a3e79e127f6',
  'sd-oak-spring-v1': '11f9f04dc506ae440390e05145b3ec536250a8763135dbd21fcbf16251fab0c6',
  'sd-oak-summer-v1': '69f92ae04e73b145e9f57a28a6e50306ca3375cc6fb26181f3f8345927efefb8',
  'sd-oak-autumn-v1': '34bdb8a1d96a3af42c046a765856d6b8c911662161e618f18b12bb39b8fd8e48',
  'sd-oak-winter-v1': '93a7fbd3c220bfb216ac1e3bb03fa0555008e061bdf9259e1b22540d90321ea9',
  'sd-courtyard-spring-v1': '9ef274d2e2c7340e75b1bb79e5b5f50a67c0dc90ea7df83c345a027835b1d8e6',
  'sd-courtyard-summer-v1': 'a28f71b868f1fe9e8c2c74abeeb7dfcd15f2cfccd42e13cfbd063dd14a10168d',
  'sd-courtyard-autumn-v1': '0486c1f4e544da7b7a0d153e435e2054f0354fd3abab89dd1f611682fce41449',
  'sd-courtyard-winter-v1': '584f1b57efc7a06392b5e90d623d26572cb5e8f69ad07148c49f8a8b85e3d347',
  'sd-inland-spring-v1': 'f3a93710c3e0245d76f722b900b4e33449765d135d522bfb928ab4cf3be2da2a',
  'sd-inland-summer-v1': 'fc7c5e293a324799f8f4a6eff771b98e06134671042ccf5ffd6ccf3bce914b53',
  'sd-inland-autumn-v1': 'cadc865480cce6795ed1871bfc353a181a8a0bc5c3962028e226c32108d387c2',
  'sd-inland-winter-v1': '3f6b51af6b2e51360607a22137a5b5243363027c66a2db3a9891003cd2874a3a',
  'sd-patio-spring-v1': '1ec5aa3dbea6f9718df7926d93984188a244f51f4824e59f2b4090d20a137ec3',
  'sd-patio-summer-v1': '20b8701641875ead37956552f769ebd108d87e00eb0a18d1486ef0e57f94d528',
  'sd-patio-autumn-v1': '3fe1151e0b8954f93742248f38caf9e5e59df4b26f3fc032556ef2d40807b177',
  'sd-patio-winter-v1': '2470ada38619bf9f543e69f4b819e3068af837fea05292c37beef74f7562b125',
};
