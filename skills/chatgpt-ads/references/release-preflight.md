# Preflight for defaults, drafts and reporting

Use before converting a reviewed campaign plan into account actions. These are review requirements for observed capabilities, not assertions that the platform exposes every control.

| Item | Required observation and decision |
| --- | --- |
| Account | Exact client/account identity; access, billing, verification and delivery states separately |
| Automated creative | Available controls, observed state, intended state, approved source assets and extent of generated changes; unknown is not disabled |
| Spend | Campaign budget semantics, relevant account limits, explicit owner maximum effect, currency and schedule; defaults are not spending authority |
| Drafts | Existing IDs, whether entering the flow may create state, observed post-exit state and reconciliation before retry |
| Reporting | Reporting export versus edit template, entity/time grain, locale, timezone identity, event definition, attribution window and time basis |

Put effective settings into the existing action-plan `before`/`after` objects and the reviewed campaign artifact. Do not invent native API property names: these are local record fields until a native mapping is verified. The browser guard compares the complete supplied objects and approval hashes, but cannot discover omitted controls, verify truth or authenticate an owner.

An unavailable control needs observed evidence of unavailability. An unknown material default needs investigation before launch. If toggling a control is required, include that change in the exact reviewed batch; do not silently turn it off under read-only authority.

For an interrupted flow, record saved, draft, under review, published and delivering as distinct states. Inspect existing objects and the available audit history before another creation attempt. A lack of visible evidence is not proof of absence.

Use the normalized analyzer only where a reviewed mapping preserves the source meaning. Keep click and view attribution separate. A UI column selector does not prove that the underlying event-attribution configuration changed.
