# Lifecycle wave local commit ledger

Baseline UI `83837529722ce48e210ed224e74cfbaf2f72881b`; companion `084b33dfac1160e1cc9b2db9336b0a16b9c4a831`. All changes are local. Documentation-only evidence commits follow the tested code heads.

## UI/application

Tested code head: `70a04886cc03c05556cf8380b412b9b618d20829`.

- `79c7cf982f9635606769e222e93a2c3660f5b044` — feat(recordings): define versioned lifecycle and deletion ledger contracts
- `dfaad261668cc40e412390c6c61a6312c84d9669` — test: exercise account auth through real app and local providers
- `0f9efa64c5aa6da46f56cc3238a61c34710e1f94` — fix(audio): retain one canonical frame for short recordings
- `776968af68cb05fa4840bf6db71f618ebdf54738` — feat(recordings): persist fenced deletion cleanup and derived output admission
- `973972c81a649c44ec1e34830e1806f5867fc766` — test(audio): preserve channel literal in frame boundary fixture
- `e0e4ff10d650a2403caef498772b28b8b32cc81d` — test(audio): exercise real local ONNX lifecycle and review journey
- `da0aed81ef8ec1280dfdfb5c406bb4f5482539b0` — feat: add private source and license bundle intake to workshop
- `a1006180415da6c928296e6af45986bfd89614c0` — test: verify uploaded asset review and pin lifecycle through the browser
- `f5804281d27c47c66a2f0004eef53bd3e34da9aa` — feat(audio): persist private analysis and atomically confirm reviewed Findings
- `460e42fac45259b5d537477aeec958f47bf9b8e6` — test(audio): cover saved review reload and deletion receipt semantics
- `9bb92434cc4a62bd870415f0e8bcd93b9c08f826` — feat(recordings): show durable owner lifecycle history
- `d8b4fe862a5d9408c0a78bf44891ca0a5a2a4bb5` — test(recordings): exercise durable cleanup failures and restarts
- `cbaac3611dfd1385be3b8975c1bd6509d48570de` — fix(audio): validate restored candidate semantics and refresh lifecycle counts
- `47283f1492f2b3082fae6a63bf637780f62cf0cf` — feat(ops): reconcile retained deletions during isolated backup recovery
- `a25b830d1d9962086baab8149965bfdd2ffe4fc2` — test: validate confirmation correlation and saved candidate semantics
- `3328160cf8232e5c551d87b57ec5641c3e84a4ba` — chore: expose lifecycle regression gates and reviewed model digest configuration
- `5a9486ab855c9003cbf0bc3a75defb21f429e037` — fix(recordings): verify derived integrity and defer cleanup during live writes
- `70a04886cc03c05556cf8380b412b9b618d20829` — test(contracts): mirror lifecycle and confirmation schemas with semantic goldens

## Post-run UI test correction and documentation

- `86e4e187b8c6d2bdc0ab39a8c38e705255b94872` — scope status assertions to recording feedback; affected suite passed 26/26 on this revision.
- `4365c20b9efb61fc185737a58002f8dd8efc40a1` — format the scoped assertion; no behavioral change.
- `3205490aac50347614355820445d584cad2de1e4` — document integrated lifecycle, confirmation and recovery boundaries; final UI head.

## Companion/service

Tested code head: `633bcbeb34aa6ad77aad74cf653d58e186d81b23`.

- `1cdbe54f072a731d0fbb7d6716ce1e414eb7159a` — docs: define durable lifecycle wave ownership and acceptance gates
- `5c15f9da6067112086b637f972083de86e25af2a` — test(audio): generate explicit arithmetic ONNX mechanics bundle
- `a38581c91305a7d0c2e37442514073abb7d4c388` — docs(audio): explain generated cross-process mechanics fixture
- `510c0490ffe59a18cb541deec547c45fc6e2cd23` — docs(audio): record actual model lifecycle acceptance evidence
- `05338e7886bbbf8bfafd6a9138acbba3e64ca0c6` — test: expand local system gate to durable lifecycle and actual owner journeys
- `fbc563ac7af1386908c5e4dbcc47bfae4a4e6c03` — docs(ops): record retained deletion recovery acceptance and limits
- `633bcbeb34aa6ad77aad74cf653d58e186d81b23` — test(contracts): verify lifecycle and confirmation structural mirrors
