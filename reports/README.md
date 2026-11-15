# reports/

| File | Ai tạo | Cách tạo |
|---|---|---|
| `group_report.md` | nhóm | điền template |
| `metric_contract.md` | nhóm | điền ở phút 30 |
| `metrics_baseline.json` | **script** | `python -m src.evaluate --track tXX --pred out/baseline/<file> --run-name baseline --out reports/metrics_baseline.json` |
| `metrics_poc.json` | **script** | `python -m src.evaluate --track tXX --pred out/poc/<file> --run-name poc --out reports/metrics_poc.json` |
| `table1_baseline_vs_poc.md` | **script** | `python -m src.compare reports/metrics_baseline.json reports/metrics_poc.json --out reports/table1_baseline_vs_poc.md` |
| `review_queue.csv` | pipeline + reviewer | copy từ `out/poc/review_queue.csv` sau khi review (có cột reviewer/decision) |
| `decision_log.csv` | pipeline | copy từ `out/poc/decision_log.csv` |
| `team_contributions.csv` | nhóm | khớp với `git shortlog -sne --all` |

Các file metrics/table **không được sửa tay** — giảng viên sẽ chạy lại lệnh để đối chiếu.

## T07: QA và kiểm tra bằng nhãn nội bộ

Xem [t07_qa/README.md](t07_qa/README.md) để chạy test, Baseline, PoC và
`python -m tools.t07_slice_report`. Script sinh các file metrics/table chuẩn ở
thư mục này, còn slice/CI và ảnh minh chứng nằm trong `t07_qa/`.

Các file có `evaluation_status=INTERNAL_CVAT_NOT_OFFICIAL` dùng nhãn CVAT của
nhóm, không phải GT chính thức. `run_name=poc_prereview` nghĩa là chưa hoàn tất
human review. Không dùng các kết quả này để tuyên bố đã đạt đánh giá chính thức.
