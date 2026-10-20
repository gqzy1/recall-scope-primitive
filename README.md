# RecallScope Primitive

Compare a consumer product with the scope of one official CPSC recall notice. Preserve the exact source snapshot, the supplied product facts, four independent findings, and an immutable result that another application can read.

A matching brand or model may still require a manufacturer serial-number check. RecallScope keeps that uncertainty visible instead of treating keyword similarity as confirmation.

## How it works

1. `assess(request_id, payload)` validates a bounded product description and an exact `https://www.cpsc.gov/Recalls/YYYY/notice` URL.
2. A `strict_eq` nondeterministic boundary fetches the official notice as text. Missing recall sections, inaccessible pages, oversized pages and disagreement fail without writing a result. Notice text is never silently truncated.
3. The leader assesses identity, variant, original sale/manufacturing period, and region. Each validator independently assesses the same sealed facts and agreed notice. All four labels must agree. An additional validator audit checks that the proposed quotations and explanations support their assigned findings.
4. Deterministic code computes the aggregate result and stores the accepted assessment with both input and notice SHA256 hashes. The exact notice is retained for later review.

This is a shared, consensus-controlled record rather than an application server's private model answer. Models still can make mistakes; consensus and quotation checks do not authenticate user-supplied product facts.

| Result | Meaning |
| --- | --- |
| `POTENTIAL_MATCH` | Every dimension is matched or explicitly unrestricted. Follow the official notice and manufacturer process. |
| `NEEDS_DETAILS` | At least one dimension is uncertain and none explicitly excludes this notice. |
| `OUTSIDE_THIS_NOTICE` | At least one explicit mismatch excludes this particular notice. Other notices may still apply. |

Per-dimension labels are `MATCH`, `MISMATCH`, `UNKNOWN`, `UNRESTRICTED`. Identity cannot be unrestricted. Missing restrictions are unknown, not automatically unrestricted. Reasons and quotations may vary between validators; material labels must match exactly. A correct label with unsupported reasoning is rejected by the audit.

## Interface

| Method | Arguments | Returns |
| --- | --- | --- |
| `assess` | `request_id: str`, `payload: str` | JSON record; write |
| `get_record` | `owner: str`, `request_id: str` | Stored JSON or empty string; view |
| `get_count` | `owner: str` | Record count; view |

A request ID is 1–48 lowercase letters, digits or dashes. Records are namespaced by the actual transaction sender. Repeating an ID with identical canonical input returns the existing record without another fetch or model call. Different input under that ID is rejected. Each owner can create at most 64 records; a new ID creates a new snapshot, not an update.

Payload:

```json
{"notice_url":"https://www.cpsc.gov/Recalls/2025/Example-Notice","product":{"brand":"Example","model":"ABC-123","batch":"","original_sale":"","region":"United States","details":""}}
```

Use a real notice URL. Brand, model and region are required. Other missing details may remain empty. Product fields are limited to 120 characters, except details (800). Payload limit: 5,000 characters. Source limit: 60,000 characters. There is no administrator or overwrite method.

## Run tests

Python 3.12+:

```sh
python -m unittest discover -s tests -v
```

The 25 tests use a small CPython harness with substituted SDK, network and model outputs. They verify boundaries, grounding, owner isolation, idempotence, disagreement rejection and write ordering. They are not a GenVM runtime test or proof of network consensus.

## Deploy and reuse

Open `contracts/recall_scope.py` in GenLayer Studio on Stable Studionet (chain 61999). The constructor takes no arguments. Deploy through your browser wallet, then supply its address to the companion app. The app checks the deployed source against its SHA256 before permitting a submission.

No deployment address or successful network transaction is claimed by this release. GenVM compatibility, real CPSC retrieval from validators, model agreement, resource usage and wallet execution still require live verification. Dynamic CPSC text can cause strict snapshot equality to reject; this is a failed assessment, not an accepted approximation. Do not repeatedly send writes to force a preferred outcome.

A record is specific to the notice snapshot and supplied facts. It does not certify safety, authorize resale, search all recalls or confirm a manufacturer's serial-number lookup. Inputs and results are public; do not submit confidential information.

MIT License.
