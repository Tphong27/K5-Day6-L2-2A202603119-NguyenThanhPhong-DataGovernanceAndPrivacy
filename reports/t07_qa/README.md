# T07 QA và đánh giá nội bộ

Các test của Người 4 nằm trong `tests/test_t07_pipeline.py`,
`tests/test_t07_integration.py`, `tests/test_t07_policy_metrics.py`.
Test review dùng danh tính `SYNTHETIC_TEST_ONLY` trong thư mục tạm của pytest;
không phải bằng chứng human review thật.

Chạy tại thư mục gốc repo bằng Python của `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -ra -p no:cacheprovider --junitxml=reports/t07_qa/pytest.xml
.\.venv\Scripts\python.exe -m src.main --config configs/lab.yaml --track t07 --pipeline src.t07_baseline --output out/baseline --run-name baseline --offline --seed 42
.\.venv\Scripts\python.exe -m src.main --config configs/lab.yaml --track t07 --pipeline src.pipeline --output out/poc --run-name poc --offline --seed 42
.\.venv\Scripts\python.exe -m tools.t07_slice_report
```

Script sinh `reports/metrics_baseline.json`, `reports/metrics_poc.json`,
`reports/metrics_blur_all.json`, `reports/table1_baseline_vs_poc.md`;
slice, CI và ảnh minh chứng nằm trong thư mục này. JSON ghi hash nhãn,
prediction, commit/config của inference và trạng thái review để truy nguyên.
Các số liệu được tính bởi script, không sửa tay. Output inference và bản chuyển
đổi nhãn nằm trong `out/` đã gitignore.

## Giới hạn bắt buộc phải ghi khi dùng số liệu

- Nhãn `reports/gold/t07_cvat_coco.json` là CVAT nội bộ, **không phải GT chính thức**.
  Nhãn có thể thiếu, trùng hoặc sai. Giữ nguyên nhãn khi tính metric; không xóa
  trường hợp xấu để cải thiện số. Pipeline không được đọc bộ nhãn này.
- `poc_prereview` nghĩa là chưa hoàn tất human review. Nhận CSV thật từ Người 3,
  khớp đúng queue hiện tại, đặt vào `out/poc/review_queue_reviewed.csv`, chạy lại
  PoC rồi script báo cáo. Không tự approve hàng loạt để lấy GO.
- `GO / REVIEW_COMPLETE` của pipeline là kết quả policy review, không thay thế
  cho kết luận metric/guardrail hoặc kiểm tra nhãn.
- Mỗi slice ghi N vùng. Size được tính từ bbox nhãn CVAT: small <1024 px²,
  medium từ 1024 đến dưới 9216 px², large ≥9216 px². N=0 ghi N/A.
- Không có condition đáng tin cậy nên ghi `condition=unknown`.
- Wilson CI giả định vùng độc lập. Bootstrap theo cụm ảnh dùng 2000 lần, seed 42,
  giữ các vùng cùng ảnh trong một cụm. CI không khắc phục sai lệch nhãn.
- Runtime là một lần chạy toàn bộ pipeline trên tất cả ảnh đầu vào, chưa gồm
  thời gian người duyệt. PoC chưa ghi `n_items`; lớp báo cáo sử dụng `n_images`
  để quy đổi thời gian/100 ảnh, không sửa core pipeline. Blur-all chưa có runtime
  riêng nên để N/A.
- Case `pii_03 / cvat:14` được gán `face` nhưng khung nằm trên áo: đây là
  **nghi vấn chất lượng nhãn**, không phải bằng chứng đã xác nhận detector bỏ sót mặt.
- Hai case biển số trong `failure_analysis.md` có metadata và ảnh. Nguyên nhân
  ở bộ lọc cạnh/hình dạng vẫn là giả thuyết, chưa truy vết chính xác.

Khi có overlay GT chính thức, dùng `src.evaluate` và `src.compare` theo
`reports/README.md`; không trình bày số CVAT nội bộ như kết quả chính thức.
