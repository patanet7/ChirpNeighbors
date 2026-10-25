# Privacy, companionship and sustainability

Canonical requirements and acceptance for this topic. Stable IDs, decisions, dependencies and named evidence are retained from the [task index](../delivery/product-behavior-and-ideas.md). U: paths refer to the UI repository; M: paths refer to ChirpNeighbors. Evidence labels resolve through the [verification ledger](../delivery/verification-ledger.md). Current GitHub publication is tracked separately in the [release record](../archive/publication/20261011/README.md).

### PB-006 — Earned companionship and levels should support attachment without pressure.

**Source / decision:** user decision; Agreed. **Implementation:** Planned. **Integration:** Not integrated. **Release / production:** See [current release status](../archive/publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/domain/yard.ts future progression boundary; no progression storage/API.

**Behavioral acceptance:** Before implementation define earning events, bounded rewards, migrations and accessible equivalent interactions; enforce no missed-day punishment, starvation, guilt, paid affection or lost birds.

**Tests and evidence:** No executable acceptance test for this requested outcome. No passing outcome evidence or tested implementation commit.

**Dependencies:** PB-002, PB-005, EN-001. **Remaining gap:** No executable progression acceptance tests, rates, levels, reward rules or storage exist. **Next action:** Specify a bounded progression contract and behavioral tests before implementation.

### PB-013 — Private accounts, media and owner data are the default; optional shares are safe view-only projections.

**Source / decision:** user decision; Agreed. **Implementation:** Private defaults and opt-in projection implemented. **Integration:** Local integrated checkpoint. **Release / production:** See [current release status](../archive/publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/auth/session-binding.ts; U:src/lib/server/sharing; U:src/lib/sharing/display.ts; U:src/lib/server/storage.

**Behavioral acceptance:** Cookie/session authority defeats owner-ID spoofing and old-tab account replacement; shared capability is opt-in, frozen, view-only and revoke/expiry/restore-fenced. Projection omits names/location/Findings/recordings/private pins; shared renderer uses builtin safe fixtures and no owner ontology workbench.

**Tests and evidence:** [U:src/lib/server/auth/session-binding.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/auth/session-binding.test.ts); [U:src/lib/server/sharing/sharing.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/sharing/sharing.test.ts); [U:src/lib/server/sharing/egress.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/sharing/egress.test.ts); [U:scripts/session-binding-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/session-binding-browser-checks.py); [U:scripts/share-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/share-browser-checks.py). [E-CAT:session-binding/session-binding-browser-results.json](../archive/delivery/LOCAL-EVIDENCE.md); [E-CAT:sharing/share-browser-results.json](../archive/delivery/LOCAL-EVIDENCE.md); [E-ONT:ontology-browser-results.json](../archive/delivery/LOCAL-EVIDENCE.md).

**Representative exact assertions:** sharing.test.ts: “invalidates every capability in an older backup without changing owner yard data”; E-CAT browser result: “public view performs no API or private image requests”; E-CAT catalog browser result: “Shared view still excludes private resident names, observations, local source job and location”.

**Dependencies:** EN-001, EN-002. **Remaining gap:** Production provider/account policies and account-wide erasure remain external; shared views do not show private reviewed artwork or live owner ontology. The 2026-10-12 review also found unsafe configured storage roots and wildcard fixture startup. **Next action:** [EN-003-A](../archive/engineering-roadmap.md#en-003-a--reject-served-private-data-roots) and [EN-003-B](../archive/engineering-roadmap.md#en-003-b--repeatable-loopback-development-lifecycle) own those repairs; preserve narrow share projection and use EN-011 for erasure scope.

**Current audit fixes and limits:** A present signed Google `azp` must match the sole configured client. Supported browser origins now normalize consistently before Python Origin/session admission. The [connection audit](../archive/delivery/product-audit-20261009.md) distinguishes local signed-provider/SMTP fixtures from unverified live sign-in, baseline transport gaps (superseded by the bounded transport slice) and missing account-wide recovery/erasure.

### PB-015 — First-party analytics answer coarse product-use questions only after explicit consent.

**Source / decision:** user decision; Agreed. **Implementation:** Default-off consented analytics foundation implemented. **Integration:** Local integrated checkpoint; operational activation absent. **Release / production:** See [current release status](../archive/publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/analytics; U:src/lib/server/analytics; U:src/lib/server/auth/session-binding.ts.

**Behavioral acceptance:** No collection without explicit current consent; closed coarse events omit identity/species/evidence/media/location/URLs/IP/referrer/free text; separate stores, bounded admission, revoke/regrant fences and purge/retention fail safely; collector failure never blocks yard/login.

**Tests and evidence:** [U:src/lib/server/analytics/analytics.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/analytics/analytics.test.ts); [U:src/lib/analytics/client.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/analytics/client.test.ts); [U:scripts/analytics-browser-checks.py](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/analytics-browser-checks.py). [E-CAT:analytics/results.json](../archive/delivery/LOCAL-EVIDENCE.md); [E-CAT:ui-unit.log](../archive/delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-013, EN-001. **Remaining gap:** No real-user activation, external collector, unique-user retention claim or legal-compliance claim. Final policy/retention/operator review and real web-vitals dependency remain open. **Next action:** Review operating policy and retention before any activation; keep default off.

### PB-016 — Minimal restricted security audit is separate from optional product analytics.

**Source / decision:** user decision; Agreed. **Implementation:** Disabled fixed-code helper and tests implemented. **Integration:** Helper verified; operational hooks/policy not integrated. **Release / production:** See [current release status](../archive/publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/analytics/security-audit.ts; U:src/lib/server/analytics/maintenance.ts.

**Behavioral acceptance:** Security purpose remains separate from consented product analytics; fixed-code records exclude raw identity/evidence/request payloads and are disabled by default; independent retention/maintenance cannot imply consent.

**Tests and evidence:** [U:src/lib/server/analytics/analytics.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/analytics/analytics.test.ts). [E-CAT:ui-unit.log](../archive/delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-013, PB-015. **Remaining gap:** No selected operational hook set or approved retention/access policy. Helper tests do not demonstrate deployed security monitoring. **Next action:** Specify reviewed events/operator policy before enabling concrete hooks.

### PB-017 — Sustainability may include voluntary support, paid/premium themes, daily credits, small ads or monetized customization.

**Source / decision:** tentative user idea; Tentative; no option selected. **Implementation:** Not implemented. **Integration:** Not integrated. **Release / production:** See [current release status](../archive/publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** Future product/economic boundary; no billing/ad/currency routes.

**Behavioral acceptance:** If selected later, assess costs, accessibility, control and privacy before technical design; no credits, currency, ads, billing or paid affection is authorized by this idea.

**Tests and evidence:** No executable acceptance test for this requested outcome. No passing outcome evidence or tested implementation commit.

**Dependencies:** PB-006, PB-015, PB-018. **Remaining gap:** Voluntary support, premium themes, daily credits, small ads and monetized customization are unselected ideas, not approved implementation. **Next action:** Obtain a product decision before selecting any economic mechanism.

### PB-019 — Protect progress against restored consent and presentation rollback.

**Source / decision:** assistant proposal; Assistant proposal implemented locally; not recorded as new user decision. **Implementation:** Implemented. **Integration:** Local integrated checkpoint. **Release / production:** See [current release status](../archive/publication/20261011/README.md); historical local integration is not production validation.

**Architecture:** U:src/lib/server/operations/restore-optional-state.test.ts; U:scripts/private_backup.py; U:src/lib/server/analytics/recovery.ts.

**Behavioral acceptance:** Restore to a new directory cancels copied pending arrival notices, revokes copied analytics consent and discards optional aggregates while preserving original backup/evidence; cover stores with and without deletion ledger.

**Tests and evidence:** [U:src/lib/server/operations/restore-optional-state.test.ts](https://github.com/patanet7/birdsong-yard-sprites/blob/main/src/lib/server/operations/restore-optional-state.test.ts); [U:scripts/tests/test_private_backup.py](https://github.com/patanet7/birdsong-yard-sprites/blob/main/scripts/tests/test_private_backup.py). [E-CAT:ui-unit.log](../archive/delivery/LOCAL-EVIDENCE.md); [E-CAT:private-recovery-tests.log](../archive/delivery/LOCAL-EVIDENCE.md).

**Dependencies:** PB-010, PB-015, EN-003. **Remaining gap:** Does not erase offline copies or guarantee the supplied deletion ledger is newest. **Next action:** Retain explicit offline-copy/operator limits under EN-011.
