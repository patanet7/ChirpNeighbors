# Illustrative behavior ontology boundaries

This additive slice extends the existing simulator. It does not add biological
knowledge, recognize observed individual birds or replace fixture artwork.
`illustrative-species-profile-v1` and `simulation-options-v1` remain unchanged.

| Boundary | Meaning | Authority and limits |
| --- | --- | --- |
| `species-behavior-traits-v1` | Size, speed/hop bias, ground/perch/roost affinities, feed/bath/nest/play/sing priorities, spacing and caution | Product-authored illustrative defaults, version 1, explicitly biologically unvalidated and never observation-derived. Known display-catalog species only. Zero activity weight disables eligibility; at least one location affinity remains. |
| `fictional-personality-v1` | Curiosity, sociability and boldness | Versioned deterministic fiction seeded only by decorative resident identity. Session variation, display names, owner data, location and evidence must not alter this identity. The schema describes provenance; engine tests establish derivation. |
| `behavior-experiment-v1` | Six closed developer comparison presets | Transient opt-in input only: ground-only, perch-only, no-bathing, no-routines, cautious or sociable. No arbitrary weights, persistence request or authority over reviewed geometry. |
| `behavior-decision-trace-v1` | Selected intent, candidate eligibility/priorities, available/rejected slot counts, locomotion and actual transition | Transient decorative diagnostics. Selected intent may be feeding while the actual transition is moving toward a feeder. Populated elections require unique candidate behaviors and an eligible selection with the same priority; placement/cancellation overrides may have no election. |

Actual observations remain in the existing private evidence store. No observation,
recording, source path, owner, geographic location or free-form private note is
accepted by these strict contracts. A developer trace can include the existing
derived scene-slot identifier, whose 167-character bound accommodates a valid
160-character object ID plus `:center`. Diagnostic reason strings are bounded
lowercase rule codes, not free-form evidence.

An ineligible candidate may retain a positive diagnostic priority when its
preferred activity has no usable location. Eligibility remains separate and the
selected candidate must be eligible. A positive weight alone does not grant an
object capability, a free slot or physical clearance.

The ontology provides eligibility and priority inputs. Existing simulation
navigation, object capabilities, slot reservations and physical clearance remain
authoritative. Reviewed shape geometry overrides illustrative size defaults.
Actual sampled clips, missing-animation fallbacks and support/contact geometry
belong to the renderer and are not inferred from a behavior label. The workbench
must present those actual renderer results separately from the decision trace.

The exported JSON Schemas intentionally cover structural rules. Known-catalog
membership, nonzero aggregate affinities, unique candidate behavior and selected
candidate coherence remain source refinements. Golden and mutation differential
gates distinguish these semantic rejections from structural acceptance. Changes to
the reviewed semantic and compatibility baselines require independent review.

The contract goldens cover unvalidated/fictional provenance, unknown species,
zero eligibility, bounded weights/seeds, strict private-field exclusion, the
closed experiment presets, intent versus travel transitions, maximal slot IDs,
and invalid candidate elections. These fixtures establish mechanics only;
species science, observed personality and approved visual fidelity remain absent.

## Focused contract verification

The additive boundary checks passed on 2026-10-09: 393 cross-language goldens
(44 new ontology cases), 12,242 deterministic mutations with Ajv/Python agreement,
789 source-valid inputs, 235 explicitly separate semantic rejections, and five
focused contract tests. Export checking passes for both repositories. The 197
structural digest entries match the reviewed compatibility baseline.

Independent review approved only four new schema digests per repository and eight
new semantic exceptions. No existing digest changed; all 227 prior semantic
entries retained their exact relative order. The new exceptions cover unknown
catalog species, selected-priority coherence and duplicate candidates. The
first roundtrip attempt identified the missing explicit Python allowlist entries;
adding those four names made the subsequent run pass. Full engine, renderer and
browser acceptance belongs to the integration evidence, not these contract counts.
