# T07 submission status

## Thông tin owner đã xác nhận

- Hân approve cả `poc:pii_54:000` và `poc:pii_45:003`; ghi nhận lý do giữ redaction theo hướng fail-safe.
- Nguyễn Thanh Phong là Data Owner/người ký quyết định cuối.
- Contribution của Phạm Anh Tuấn được ghi là prototype/materials tại `a7e889a`; production fallback do Nguyễn Nhật Minh tích hợp.
- Deadline: 12:00 ngày 15/11/2026 (UTC+7).
- Nhóm đã demo và được bonus point; không cung cấp tên presenter cá nhân.
- Không yêu cầu tag và không yêu cầu submission riêng. File này chỉ là checklist bổ sung nội bộ.

## Nhóm

| Vai trò | Thành viên | Mã học viên |
|---|---|---|
| Detector prototype/materials | Phạm Anh Tuấn | 2A202603232 |
| Baseline/data protocol | Nguyễn Thanh Phong | 2A202603119 |
| Human review/audit/export | Huỳnh Ngọc Gia Hân | 2A202603128 |
| QA/metric/failure analysis | Lương Văn Quyến | 2A202603226 |
| Integration/decision/report/demo | Nguyễn Nhật Minh | 2A202603210 |

## Kết quả có thể tái tạo

- Track: T07 Automatic Face/Plate Redaction + Review Queue.
- Input: 60 ảnh synthetic; không có PII thật.
- Seed: 42; offline: true; review budget: 15.
- Preflight: 0 FAIL, 2 cảnh báo tài nguyên tùy chọn.
- Pytest: exit code 0; test tùy chọn không có overlay được skip.
- Baseline: exit code 0; 351 redactions; 0 invalid boxes.
- PoC cuối: exit code 0; 351 candidates; 341 final regions; 0 invalid boxes.
- Human review cuối: 5 approve, 10 reject, 0 edit/escalate/skip/pending/stale.
- Operational decision: `GO / REVIEW_COMPLETE`.
- Internal CVAT PII Miss Rate: 0.3304347826 (38/115).
- Internal CVAT over-redaction: 0.6465120026; guardrail <=0.3 **FAIL**.
- Blur-all miss rate: 0, nhưng over-redaction khoảng 0.9893 nên guardrail FAIL.

Operational GO chỉ xác nhận workflow/review/schema/audit hoàn tất. Nó không có
nghĩa chất lượng model đã PASS và không thay thế đánh giá GT chính thức.

## Lệnh chấm/tái tạo

```powershell
.\.venv\Scripts\python.exe -m tools.preflight
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m src.main --config configs/lab.yaml --track t07 --pipeline src.t07_baseline --output out/baseline --run-name baseline --offline --seed 42
.\.venv\Scripts\python.exe -m src.main --config configs/lab.yaml --track t07 --output out/poc --run-name poc_reviewed --offline --seed 42
.\.venv\Scripts\python.exe -m tools.t07_slice_report
```

Để tái tạo đúng quyết định cuối, copy
`reports/t07_review/review_queue_reviewed.csv` sang
`out/poc/review_queue_reviewed.csv` trước khi chạy PoC lần cuối.

## Artifacts

- `reports/group_report.md`
- `reports/team_contributions.csv`
- `reports/metrics_baseline.json`
- `reports/metrics_poc.json`
- `reports/metrics_blur_all.json`
- `reports/table1_baseline_vs_poc.md`
- `reports/t07_qa/`
- `reports/t07_review/`
- `demo/T07_DEMO_PLAN.md`

## Hạn chế và việc còn lại

1. **Official/hidden GT:** chưa có kết quả chính thức của giảng viên. Các metric
   hiện tại dùng nhãn CVAT nội bộ, có thể thiếu/trùng/sai.
2. **Guardrail chất lượng:** over-redaction nội bộ vẫn vượt 0.3; không được ghi
   model quality PASS dù operational decision là GO.
3. **Hai approval cần second review trước release thật:** metadata/box của `poc:pii_54:000` và `poc:pii_45:003` không khớp rõ với loại `face`; hiện giữ approve theo xác nhận của Hân để hoàn tất workflow.
4. **Merge:** nhánh hoàn thiện phải được merge vào `main` trước khi nộp.
5. **Dữ liệu thật:** detector fixture-oriented, chưa được xác nhận trên ảnh thật.
6. **Presenter cá nhân:** nhóm chỉ xác nhận đã demo và được bonus; không cung cấp tên người trình bày.
