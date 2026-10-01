# CPC PPG Heart-Rate Replication

Tái tạo phương pháp trong paper “Cascade and parallel combination (CPC) of adaptive filters for estimating heart rate during intensive physical exercise from photoplethysmographic signal”.

Pipeline dự kiến: PPG/ACC → tiền xử lý → LMS và RLS mắc tầng → kết hợp CPC → ước lượng và theo dõi nhịp tim → đánh giá. Các bước này **chưa được triển khai**.

## Cấu trúc

```text
data/           Dataset gốc; giữ nguyên Training_data/ và Competition_data/
docs/           Paper gốc và ghi chú tái tạo
src/cpc_ppg/    Mã nguồn khi bắt đầu triển khai
tests/          Kiểm thử khi có mã nguồn
results/        Kết quả được sinh ra sau này
```

Không đổi tên hay sửa các file trong `data/`. Paper PDF hiện ở `docs/`. Trước khi viết thuật toán, ghi thông số từ paper, đặc điểm dữ liệu quan sát được và các giả định vào [docs/replication.md](docs/replication.md).
