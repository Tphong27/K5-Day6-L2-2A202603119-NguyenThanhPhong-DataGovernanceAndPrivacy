# Bàn giao code tham khảo để viết báo cáo t07

Gói này chỉ trích phần logic liên quan từ autolabel_yolov. Đây không phải báo cáo hoàn chỉnh hoặc toàn bộ ứng dụng. Không kèm checkpoint, dữ liệu CVAT, thông tin đăng nhập, giao diện hay code upload.

## Nguồn

- Repo: https://github.com/AnhTuan2003ml/autolabel_yolov
- Commit tham chiếu: 438358d1bc865e1d845ecfad056b7b0f8d48b064.
- yolo_agent/infer.py: resolve_device, scalar, to_list, box_points, class_name, mapped_label và nhánh bbox trong infer.
- cvat_agent/job_runner.py: cấu trúc prediction JSON và ý tưởng tổng hợp số đối tượng.
- Các hàm trợ giúp trong src/detector.py được trích nguyên văn; detect là nhánh bbox rút gọn, run_pipeline là lớp đóng gói bàn giao, không phải bản sao nguyên hàm của repo.

## File bàn giao

| File | Nội dung |
| --- | --- |
| src/pipeline.py | Gọi detect, gom kết quả, tùy chọn ghi JSON; chỉ là phần detect của pipeline t07. |
| src/detector.py | Gọi model.predict, đọc bbox/confidence/class, ánh xạ tên và lọc label. |
| configs/lab.yaml | Mẫu lựa chọn t07 và tham số; thông tin nhóm để người viết bổ sung. |
| requirements.txt | Thư viện khi tích hợp với YOLO; không cần cài để chạy test dùng model giả. |
| tests/test_pipeline.py | Success và edge/failure, dùng dữ liệu giả; không tải model. |

## Điểm cần nói đúng trong báo cáo

- Repo gốc hiện có nhận diện và xuất annotation. Chưa có logic làm mờ (blur/redaction), duyệt ảnh nhạy cảm (review) và quyết định phát hành ảnh (decide).
- review_id trong UI gốc là mã kiểm tra/chọn label, không phải bước human review của bài redaction.
- Không trình bày pipeline detect → blur → review → decide là đã hoàn thành chỉ từ các đoạn code này.
- Chưa có kết quả precision, recall, coverage, latency hoặc đánh giá t07 thực tế trong gói bàn giao.
- YOLO với trọng số COCO mặc định không có riêng class face/plate; muốn nhận diện hai class này cần model phù hợp do người dùng cung cấp. Đổi tên class hoặc đổi prompt không tạo ra khả năng nhận diện mới.

## Đầu vào / đầu ra

Người tích hợp truyền model đã được nạp vào run_pipeline. Gói này không gọi YOLO(...) để tải hoặc nạp model.

Mỗi detection giữ format của repo gốc:
{"type":"rectangle","label":"face","confidence":0.9,"points":[x1,y1,x2,y2]}

Tọa độ bbox là pixel theo ảnh đầu vào. Các tham số confidence, device, label_map và allowed_labels được truyền vào hàm; lab.yaml chỉ là cấu hình tham khảo, chưa có bộ đọc YAML trong đoạn code trích.

## Sử dụng để tham khảo

Chạy kiểm thử tại thư mục gói:
python -B -m unittest discover -s tests -v

Tích hợp trong chương trình đã có model:
from src.pipeline import run_pipeline
result = run_pipeline(model, "images", confidence=0.25, allowed_labels=("face", "plate"))

## Người viết báo cáo bổ sung

Theo bảng yêu cầu ban đầu, còn cần tự viết reports/metric_contract.md, reports/group_report.md, reports/team_contributions.csv và chuẩn bị slide/minh chứng trong demo/. Tên thành viên, nhiệm vụ, commit cá nhân, số liệu thực nghiệm và kết quả phải lấy từ công việc thực tế. Nếu cần gói nộp đủ detect/blur/review/decide thì phần redaction và quy trình review/decide còn phải triển khai.
