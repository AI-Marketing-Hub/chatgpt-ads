# Monitor pacing, anomalies and operational drift

## Inputs

Account profile, authorized read scope, baseline, explicit monitoring window and alert criteria.

## Procedure

1. Check evidence freshness and report completeness before diagnosing a trend. Missing or failed reports are data incidents, not healthy zero-spend days.

2. Compare pacing with effective budget semantics and elapsed schedule, accounting for lag, timezone and pending charges. Use client-agreed thresholds, not invented universal alerts.

3. Inspect delivery, policy, destination, tracking and feed health within authorized scope. Classify account incidents separately from documentation or browser drift.

4. Emit actionable findings with evidence and proposed response. A monitor cannot automatically spend, pause or edit without authorization covering that action. Scheduling is disabled until the user requests a cadence.

5. Capture candidate lessons privately. Promote only reviewed, appropriately anonymized insights with evidence and limitations. Stay quiet on unchanged scheduled checks unless the user requests status updates.

## Output

Pacing/incident report, prioritized proposals, checkpoint and candidate lessons.

## Evidence and failure behavior

Use current source IDs from `sources.json` and check `capabilities.md` and conflicts before making platform claims. Missing decisions return `needs_input`; missing evidence returns `no_data`; unavailable tools return `capability_unavailable`; external effects lacking approval return `needs_approval`. Keep partial work and observed failures explicit.

See [learning and privacy](learning.md) before promoting any lesson.

Use the monitor section of [workflow output templates](workflow-outputs.md) to structure the deliverable.

Compare each reporting date with the explicit as-of date, account timezone and reporting lag. An old row labeled partial is a stale completeness incident once its lag window has passed, not an open day to wait out. Exclude missing and incomplete days from comparable pacing. Existing authorization for read-only reporting also covers routine repulls and checking currency/timezone within that scope. Lack of account access is a capability or evidence gap; do not request fresh approval merely because automatic account changes are prohibited.

For daily rows, measure lag from the end of the reporting day in its timezone, not from its start. A September 7 daily row with 24-hour lag matures at the start of September 9. If as-of time is only a date, disclose boundary uncertainty rather than inventing an exact timestamp.
