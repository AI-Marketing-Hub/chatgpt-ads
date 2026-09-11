# Measurement workflow acceptance

Synthetic business: a fictional household-goods shop. This is an offline business-event contract exercise, not an implementation of the OpenAI Pixel/CAPI protocol. No events are sent. Account event mapping, accepted payloads and attribution remain unverified.

Business definition: one paid, non-refunded order is one purchase. Currency is USD; value is merchandise revenue excluding tax and shipping. Browser/server records for the same order carry the same opaque business event ID. The local fixture requires explicit consent state `granted`; unknown or denied states suppress sending. This conservative fixture choice is not a jurisdiction-wide legal conclusion.

The real implementation must map these business fields into the current documented native payload and verify consent, data purpose, click identifier handling, event time, browser/server identifier parity and account data-source identity. Receipt of an event does not prove attribution. Match backend eligible orders, accepted events and platform conversions as separate populations.

## Test protocol

| Case | Expected local behavior | Required native evidence later |
| --- | --- | --- |
| One valid paid order | Eligible once | Accepted event and validation diagnostics |
| Browser and server duplicate | One business event | Platform deduplication demonstrated with matching event ID |
| Duplicate ID, conflicting value | Hold group for reconciliation (ineligible until resolved) | Correct source-of-truth value before any resend |
| Unknown or denied consent | Suppress | Actual tag/network inspection confirms no unauthorized emission |
| Missing ID or invalid value | Reject | Native validation response, with no real personal data |
| Refund/non-purchase event | Exclude from this purchase metric | Separately reviewed refund treatment and reporting meaning |
| Currency mismatch | Reject | Correct account/event currency mapping |

Run `python3 acceptance/measurement/run_offline_cases.py`. Its output includes only synthetic event IDs. These checks validate the business-side preparation rules; they do not simulate server acceptance or a native attribution window.
