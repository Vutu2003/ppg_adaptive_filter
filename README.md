# Giảm nhiễu PPG và ước lượng nhịp tim bằng LMS/RLS–CPC

Mã nguồn đồ án triển khai bộ lọc thích nghi LMS, RLS và cấu trúc Cascade and Parallel Combination (CPC) để giảm nhiễu chuyển động trong tín hiệu PPG. Repository giữ mã xử lý chính, dữ liệu gốc, bài báo, bài giảng và báo cáo để phục vụ trình bày, bảo vệ đồ án.

## Tìm nhanh phần cài đặt

| Nội dung cần giải thích | Mã nguồn |
| --- | --- |
| Công thức cập nhật LMS | [lms.py](src/cpc_ppg/adaptive_filters/lms.py) — `lms_filter()` |
| Công thức cập nhật RLS | [rls.py](src/cpc_ppg/adaptive_filters/rls.py) — `rls_filter()` |
| Số hệ số, bước học, hệ số quên | [config.py](src/cpc_ppg/adaptive_filters/config.py) |
| Ba tầng ACC-X → ACC-Y → ACC-Z | [cascade.py](src/cpc_ppg/adaptive_filters/cascade.py) |
| Phối hợp hai nhánh bằng λ | [cpc.py](src/cpc_ppg/adaptive_filters/cpc.py) — `combine_cpc()` |
| Lọc phổ PPG/ACC trước bộ lọc thích nghi | [spectral.py](src/cpc_ppg/preprocessing/spectral.py), [pipeline.py](src/cpc_ppg/preprocessing/pipeline.py) |
| Chọn và theo dõi đỉnh phổ | [spectral_peak.py](src/cpc_ppg/hr/spectral_peak.py) |
| Làm mượt nhịp tim | [postprocessing.py](src/cpc_ppg/hr/postprocessing.py) |
| Đọc dữ liệu và chia cửa sổ | [loader.py](src/cpc_ppg/data/loader.py), [segmentation.py](src/cpc_ppg/data/segmentation.py) |
| Công thức AAE, Pearson, Bland–Altman | [metrics.py](src/cpc_ppg/evaluation/metrics.py), [bland_altman.py](src/cpc_ppg/evaluation/bland_altman.py) |

[scripts/demo.py](scripts/demo.py) thể hiện thứ tự gọi các hàm trong bảng trên để chạy luồng xử lý hoàn chỉnh.

## Luồng xử lý

```text
PPG1, PPG2 và ACC-X/Y/Z (125 Hz)
  → cửa sổ 8 giây, dịch 2 giây
  → lọc phổ 0,4–3,5 Hz riêng từng kênh
  → trung bình hai PPG đã lọc
  → hai nhánh LMS/RLS, mỗi nhánh nối tầng X → Y → Z
  → CPC: λ·e_LMS + (1−λ)·e_RLS, λ = 0,5
  → FFT 4096 điểm → chọn/theo dõi đỉnh → BPM → làm mượt nhân quả
```

LMS dùng 27 hệ số và μ = 0,0001. RLS dùng 55 hệ số, hệ số quên 0,999 và P0 = I. Trọng số được khởi tạo lại theo từng cửa sổ. BPM0 từ ECG chỉ dùng đối chiếu sau khi ước lượng, không điều khiển bộ lọc hoặc chọn đỉnh.

Các tham số được khai báo trực tiếp trong các file `config.py` của mã nguồn. Một số quy ước triển khai của tác giả chưa được xác nhận; mã này thể hiện cấu hình thực hiện trong đồ án, với các lựa chọn và giới hạn được trình bày trong báo cáo.

## Cài đặt và chạy demo

Dùng Python 3.12 trở lên. Mã chạy chỉ cần NumPy và SciPy.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/demo.py
```

Mặc định chạy 10 cửa sổ đầu của `DATA_01_TYPE01` và in HR cùng AAE của ba phương pháp. Chạy toàn bộ một bản ghi hoặc đổi bản ghi:

```bash
.venv/bin/python scripts/demo.py --full-record
.venv/bin/python scripts/demo.py --record DATA_02_TYPE02 --windows 20
```

Có thể dùng `--data-dir /duong/dan/Training_data` nếu dữ liệu ở vị trí khác. Mỗi bản ghi cần cặp `DATA_XX_TYPEXX.mat` và `DATA_XX_TYPEXX_BPMtrace.mat` như trong [dữ liệu Training](data/Training_data/).

Demo chỉ in kết quả ra terminal. AAE hiển thị được tính trên các cửa sổ vừa chạy; chỉ số tổng hợp 12 bản ghi và các phân tích đầy đủ nằm trong báo cáo. Hậu xử lý ngoại tuyến vẫn có trong mã, nhưng demo dùng đầu ra nhân quả.

## Tài liệu và báo cáo

- [Báo cáo PDF](reports/final/Bao_cao_mon_hoc_CPC_PPG_LMS_RLS.pdf) · [Bản Word](reports/final/Bao_cao_mon_hoc_CPC_PPG_LMS_RLS.docx).
- [Slide PowerPoint](reports/final/Bao_ve_mon_hoc_CPC_PPG_LMS_RLS.pptx) · [Slide PDF](reports/final/Bao_ve_mon_hoc_CPC_PPG_LMS_RLS.pdf).
- [Bài báo CPC gốc](<docs/Healthcare Tech Letters - 2018 - Islam - Cascade and parallel combination  CPC  of adaptive filters for estimating heart.pdf>).
- [Bài giảng](docs/lecture/) · [Mẫu bìa và slide gốc](template/).

## Cấu trúc repository

```text
data/                         Dữ liệu và hướng dẫn gốc
src/cpc_ppg/
  adaptive_filters/           LMS, RLS, ba tầng ANC và CPC
  preprocessing/              Lọc phổ và lấy trung bình PPG
  hr/                         Phổ, theo dõi đỉnh và làm mượt
  data/                       Đọc MAT, chia cửa sổ, kiểm tra đầu vào
  evaluation/                 Các công thức đo sai số
scripts/demo.py               Ví dụ gọi luồng xử lý hoàn chỉnh
docs/                         Chỉ gồm bài báo CPC gốc và lecture/
reports/final/                Chỉ gồm 4 file DOCX/PDF báo cáo, PPTX/PDF slide
template/                     Mẫu tài liệu gốc
```

Các bộ test, trình validation, mã vẽ hình và kết quả xuất trung gian đã được lược bỏ. Các kiểm tra kích thước, dữ liệu hữu hạn và trạng thái bộ lọc vẫn nằm trong mã lõi để phát hiện đầu vào sai. Môi trường `.venv/`, cache và các thư mục cấu hình cục bộ được loại khỏi Git bằng `.gitignore`.
