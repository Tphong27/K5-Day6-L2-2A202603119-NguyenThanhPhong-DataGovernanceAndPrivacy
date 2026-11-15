> INTERNAL CVAT EVALUATION ONLY. Check run_name/review status; not official GT.

Baseline: `baseline` (git 594d092, seed 42) · PoC: `poc_reviewed` (git 594d092, seed 42)

| Metric (unit) | Slice | Baseline | PoC | Δ abs | Δ rel | Better | N |
|---|---|---|---|---|---|---|---|
| **PII Miss Rate** (GT regions with coverage < 0.9 / GT regions) | all | 0.3304 | 0.3304 | 0.0000 | +0.0% | lower | 115 |
| Region recall (1 - miss rate) | all | 0.6696 | 0.6696 | 0.0000 | +0.0% | higher | 115 |
| Over-redaction rate (redacted px outside GT / redacted px) | all | 0.6601 | 0.6465 | -0.0135 | -2.1% | lower | None |
| Guardrail: Over-redaction rate <= 0.3 (1 = pass, 0 = fail (constrained primary)) | all | 0.0000 | 0.0000 | 0.0000 | baseline=0 | higher | None |
| PII Miss Rate (fraction) | type=face | 0.0704 | 0.0704 | 0.0000 | +0.0% | lower | 71 |
| PII Miss Rate (fraction) | type=plate | 0.7500 | 0.7500 | 0.0000 | +0.0% | lower | 44 |
| PII Miss Rate (fraction) | condition=unknown | 0.3304 | 0.3304 | 0.0000 | +0.0% | lower | 115 |
| PII Miss Rate (fraction) | size=small | 0.3426 | 0.3426 | 0.0000 | +0.0% | lower | 108 |
| PII Miss Rate (fraction) | size=medium | 0.1429 | 0.1429 | 0.0000 | +0.0% | lower | 7 |
| PII Miss Rate (fraction) | size=large | n/a | n/a | n/a | n/a | lower | 0 |
| Runtime / 100 items (s) | all | 0.7628 | 2.1835 | | | lower | |
