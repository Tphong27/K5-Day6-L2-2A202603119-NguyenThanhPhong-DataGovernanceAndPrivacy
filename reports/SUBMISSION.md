# T07 submission status

## CẦN NGUYỄN NHẬT MINH XÁC NHẬN

- [ ] Hân approve cả `poc:pii_54:000` và `poc:pii_45:003`.
- [ ] Chấp nhận ghi lý do hai approval là giữ redaction theo hướng fail-safe; chưa có
  lời giải thích chi tiết khác trực tiếp từ Hân.
- [ ] Nguyễn Thanh Phong là Data Owner/người ký quyết định cuối.
- [ ] Đồng ý cách ghi đóng góp của Phạm Anh Tuấn: commit `a7e889a` là prototype/materials,
  production detector fallback do Nguyễn Nhật Minh tích hợp.
- [ ] Điền deadline chính xác theo giờ Việt Nam.
- [ ] Chốt người thuyết trình/demo.
- [ ] Xác nhận có cần hai tag `demo-180m`, `final-24h` hay không.
- [ ] Xác nhận giảng viên có cần `SUBMISSION.md` riêng hay chỉ cần `group_report.md`.

Những số liệu kỹ thuật còn lại đã được script/test xác minh, không cần xác nhận thủ công.

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

## Chưa chắc chắn / chưa hoàn thành

1. **Official/hidden GT:** chưa có kết quả chính thức của giảng viên. Các metric
   hiện tại dùng nhãn CVAT nội bộ, có thể thiếu/trùng/sai.
2. **Guardrail chất lượng:** over-redaction nội bộ vẫn vượt 0.3; không được ghi
   model quality PASS dù operational decision là GO.
3. **Tag:** chưa tạo `demo-180m` và `final-24h`.
4. **Deadline:** nhóm chưa cung cấp deadline giờ Việt Nam.
5. **Merge:** nhánh hoàn thiện phải được merge vào `main` trước khi nộp.
6. **Dữ liệu thật:** detector fixture-oriented, chưa được xác nhận trên ảnh thật.
7. **Presentation owner:** cột presenter trong contribution table chưa được nhóm chốt.
