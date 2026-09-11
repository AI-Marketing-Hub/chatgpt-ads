# Synthetic workflow acceptance

This directory exercises five advisory workflows against one deliberately invented business, Mossline Desk Goods. The fixture is not a real advertiser, the destination uses the reserved `.invalid` domain, and every account observation is absent. No account, browser, API, network write, paid generation, scheduling, or external action is part of this acceptance scope.

The cases test whether the workflows produce useful work while preserving blockers:

| Workflow | Produced decision | Why that decision is correct in this fixture |
| --- | --- | --- |
| Readiness | `blocked` | Business inputs exist, but country eligibility, account identity, role, billing, currency, timezone, destination, and measurement are not observed. |
| Plan | `provisional` | Supplied economics support break-even math and a bounded spend scenario, while platform objective, bid mode, targeting, and account controls remain unset. |
| Creative | `blocked` | Two substantiated copy directions are drafted, but actual format support, rendering, destination behavior, and asset rights are unverified. |
| Experiment | `needs_input` | A fixed feasibility pilot is useful, but no power or efficacy claim is possible without a baseline and a verified assignment method. |
| Monitor | `blocked` | Comparable complete days can be calculated, but one missing day and one stale incomplete day prevent a whole-window pacing conclusion. |

Platform-dependent statements are limited to claim IDs returned by the repository's bounded guarded retrieval. [source-query-ledger.json](source-query-ledger.json) records the exact queries, expected returned claims, guarded withheld claims, and source IDs used. The query output is explicitly documentation evidence with `live_verification: false`.

The machine-readable [case-ledger.json](case-ledger.json) binds each case to its fixture slice, output, rubric criteria, and last executed outcome. [rubric.json](rubric.json) defines the acceptance criteria. Each JSON file under `cases/` contains the brief input, reasoning-rich produced output, and an advisory result conforming to the repository result schema.

Run the independent acceptance check from the repository root:

```bash
python3 acceptance/workflows/verify.py
```

The verifier validates the five advisory results against `skills/chatgpt-ads/references/result.schema.json`, reruns all guarded queries, checks the cited source dates as of the frozen case date, verifies evidence references, recomputes economics and monitor arithmetic with Python `Decimal`, checks the creative claim manifest, and confirms the experiment does not invent a power result. Its pass does not establish source truth after the frozen date, native account access, campaign execution, destination behavior, platform performance, or human approval.
