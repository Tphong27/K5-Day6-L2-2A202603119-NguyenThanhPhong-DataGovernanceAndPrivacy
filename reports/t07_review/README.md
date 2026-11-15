# T07 human-review evidence

- Initial reviewer: `han` (Huỳnh Ngọc Gia Hân)
- Initial review timestamp: `2026-11-15T05:19:49.021Z`
- Follow-up decision owner: `han` (Huỳnh Ngọc Gia Hân)
- Decision relayed/recorded by: Nguyễn Nhật Minh (Lead integration)
- Recorded resolution timestamp: `2026-11-15T06:21:00Z`

The reviewed queue contains exactly 15 current queue IDs:

- approve: 5
- reject: 10
- edit: 0
- escalate: 0
- skip/pending/stale: 0

The following IDs were initially escalated and subsequently approved by Hân in
a follow-up relayed by Minh. Both boxes remain redacted:

- `poc:pii_54:000` (initial review note: `plate`)
- `poc:pii_45:003`

The final production decision is `GO / REVIEW_COMPLETE`. This operational GO
only states that review is complete and the output contract passes. It does not
override the internal CVAT over-redaction guardrail, which still fails.

Integrity:

- original handoff CSV SHA-256: `C6C163EE88B82D2D3B4967C56AF595048107953E8DC2E5D5428E8B5520E4F205`
- final reviewed CSV SHA-256: `78C11E7DBB0329A020A2F4BD3437068EDA3293DC2B10CB743DED9EA4DDFF84A7`
- original handoff archive SHA-256: `63B76E65DCD30C4272772E071B4737A10A3B33D6727E9B55DE46CC27D5CBCAC6`
- all image paths refer to the public synthetic fixture; no real PII is included here.

Running the PoC with this CSV produced 341 final regions, zero invalid boxes,
60 exported images, `pending=0`, `escalated=0`, and operational decision `GO`.
