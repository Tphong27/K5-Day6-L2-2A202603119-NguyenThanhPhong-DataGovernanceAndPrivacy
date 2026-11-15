# T07 human-review evidence

Reviewer: `han` (Huỳnh Ngọc Gia Hân)  
Review timestamp from exported CSV: `2026-11-15T05:19:49.021Z`

The reviewed queue contains exactly 15 current queue IDs:

- approve: 3
- reject: 10
- edit: 0
- escalate: 2
- skip/pending/stale: 0

Escalated IDs:

- `poc:pii_54:000` (review note: `plate`)
- `poc:pii_45:003`

The production decision is therefore correctly `REWORK / REVIEW_ESCALATED`.
The team must not rewrite an escalation as approval merely to obtain `GO`.

Integrity:

- `review_queue_reviewed.csv` SHA-256: `C6C163EE88B82D2D3B4967C56AF595048107953E8DC2E5D5428E8B5520E4F205`
- original handoff archive SHA-256: `63B76E65DCD30C4272772E071B4737A10A3B33D6727E9B55DE46CC27D5CBCAC6`
- all image paths refer to the public synthetic fixture; no real PII is included here.

Running the PoC with this CSV produced 341 final regions, zero invalid boxes,
60 exported images, `pending=0`, and two escalations.
