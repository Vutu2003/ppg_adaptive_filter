# Phase 2A — Production Loader + Segmentation/Alignment

**Status: PASS.** Báo cáo và manifest lưu trực tiếp trong `reports/`, dùng tiền tố `phase_2a_` theo yêu cầu.

Tóm tắt kiểm tra repository trước khi sửa:

- Đã xem cây thư mục, `src/cpc_ppg/__init__.py`, tests hiện có, `README.md`, `.gitignore`, `pyproject.toml`, `requirements.txt`, `data/metadata/dataset_schema.yaml`, `docs/assumptions/reconstruction_assumptions.md`, các báo cáo/inventory Phase 1 trong `reports/data/` và nội dung Training MAT. Chưa có data implementation hay script skeleton để tái sử dụng; tests chỉ có placeholder.
- Tạo 8 module trong `src/cpc_ppg/data/`, script validator, 4 test modules và fixture, báo cáo này, CSV alignment. Danh sách đầy đủ ở §3.
- Sửa `pyproject.toml` để khai báo integration marker và cập nhật assumptions/decisions. Không thêm dependency.
- Chọn frozen dataclasses, NumPy views chỉ đọc, một nơi định nghĩa protocol, discovery có thứ tự xác định, validation nghiêm ngặt trước khi trả record/windows. Các kênh giữ nguyên giá trị và dtype.

## 1. Scope

Triển khai Training MAT v5 loading, ghép signal/BPMtrace, tách 6 kênh raw, cửa sổ đầy đủ 8 s/shift 2 s, ánh xạ BPM0, validation, automated tests và báo cáo.

Phase 2A chỉ xuất raw channels. Không triển khai spectral filtering, detrend, normalization, resampling, PPG averaging, artifact rejection, LMS/RLS, cascade/CPC, periodogram, HR tracking, post-processing hoặc evaluation metrics. Competition_data không được đưa vào API xử lý của phase này.

## 2. Source-of-truth protocol

Nguồn đã được đối chiếu ở [Phase 1B](data/dataset_documentation_reconciliation.md) và [dataset schema](../data/metadata/dataset_schema.yaml): Training Readme.pdf/Readme.docx; CPC paper §2 p.19 và §4.3 p.22. Phase 2A kiểm chứng lại bằng 12 cặp dữ liệu thực.

| Protocol | Value | Classification |
| --- | --- | --- |
| Sampling rate | Fs = 125 Hz | PAPER-SPECIFIED; DATASET-CONFIRMED |
| Window | 8 s = 1000 samples | PAPER-SPECIFIED; số samples là hệ quả toán học |
| Overlap / shift | 6 s / 2 s = 250-sample hop | PAPER-SPECIFIED; DATASET-CONFIRMED |
| Signal | `sig`, channels × samples, `(6,N)` | DATASET-CONFIRMED |
| Rows Python 0–5 | ECG, PPG1, PPG2, ACC-X, ACC-Y, ACC-Z | DATASET-CONFIRMED |
| Labels | `BPM0`, ECG-derived ground truth per window | PAPER-SPECIFIED; DATASET-CONFIRMED |
| Label mapping | Window i ↔ BPM0[i], first window starts at sample 0 | DATASET-CONFIRMED |
| Evaluation windows | All supplied labelled windows | PAPER-SPECIFIED, CPC §4.3 |

## 3. Implementation

Files created:

| File | Role |
| --- | --- |
| `src/cpc_ppg/data/protocol.py` | Fs/window/hop/channel constants; full-window count |
| `src/cpc_ppg/data/models.py` | TrainingPair, TrainingRecord, TrainingWindow, AlignmentSummary |
| `src/cpc_ppg/data/errors.py` | DatasetValidationError, PairingError, FiniteDataError, AlignmentError |
| `src/cpc_ppg/data/discovery.py` | Parse IDs, reject ambiguous/missing pairs, deterministic sort |
| `src/cpc_ppg/data/loader.py` | scipy.io.loadmat, shape/dtype/finite checks, raw extraction |
| `src/cpc_ppg/data/segmentation.py` | Exact full raw views with label/time metadata |
| `src/cpc_ppg/data/validation.py` | Record checks and complete window/value/index verification |
| `src/cpc_ppg/data/__init__.py` | Public loading, segmentation, validation and model API |
| `scripts/validate_phase2a_loader.py` | 12-record table, aggregates, CSV option, PASS/FAIL exit code |
| `tests/data/conftest.py` | Identifiable synthetic raw data and temporary MAT fixtures |
| `tests/data/test_discovery.py` | Pairing/count/order/error tests |
| `tests/data/test_loader.py` | Channel map, vectors, raw dtype/values, invalid input tests |
| `tests/data/test_segmentation.py` | Boundaries, labels, memory sharing, integrity, mismatch tests |
| `tests/data/test_phase2a_integration.py` | Real dataset/schema/integrity and CLI success/failure tests |
| `reports/phase_2a_alignment_manifest.csv` | 12 rows of machine-readable alignment metadata |
| `reports/phase_2a_loader_alignment_report.md` | This report |

Files modified:

- `pyproject.toml`: declare the `integration` pytest marker.
- `docs/assumptions/reconstruction_assumptions.md`: add classified Phase 2A decisions/statuses; preserve A01–A11 as OPEN.

Public usage from the configured source environment:

```python
from cpc_ppg.data import load_training_record, segment_training_record

record = load_training_record(
    "data/Training_data/DATA_01_TYPE01.mat",
    "data/Training_data/DATA_01_TYPE01_BPMtrace.mat",
)
windows = segment_training_record(record)
# windows[0].ppg1 is record.ppg1[0:1000]; windows[0].bpm is record.bpm[0].
```

## 4. Data model

`TrainingRecord` lưu record ID, hai paths, Fs, sáu kênh 1-D và BPM0 1-D; cung cấp `n_samples` và `duration_s`. Các kênh là views của `sig`, không sao chép riêng từng kênh. MAT row/column BPM0 được reshape thành vector, giữ dtype và giá trị.

`TrainingWindow` lưu record ID, index, start/end samples, start/end seconds, sáu views 1000 samples và nhãn BPM dạng float. End sample/time là biên exclusive. Dataclasses frozen; các arrays do loader/segmentation xuất ra được đặt chỉ đọc để tránh ghi vô ý. Caller cần buffer có thể ghi phải tạo bản copy rõ ràng.

`AlignmentSummary` cung cấp N, label/window counts và first/final bounds. Với zero windows, các bounds là `None`.

## 5. Pairing logic

Discover trực tiếp các file khớp `DATA_<NN>_TYPE<NN>.mat` và `DATA_<NN>_TYPE<NN>_BPMtrace.mat`. Ghép theo canonical base ID, sort theo ID, mặc định yêu cầu 12 cặp. Không hard-code 12 filenames trong loader. Test integration đối chiếu tập đã discover với schema Phase 1B.

Tên được match không phân biệt hoa/thường; nếu có hai case variants cùng vai trò/ID, raise `PairingError`. Missing labels, orphan labels, matching directory entries và số cặp sai đều báo lỗi. File không thuộc pattern được bỏ qua. `expected_count` có thể được chỉ định hoặc đặt `None` cho fixture/subset; script production dùng mặc định 12.

## 6. Segmentation logic

```text
start_i = 250 * i
end_i   = start_i + 1000
M       = floor((N - 1000) / 250) + 1, if N >= 1000
M       = 0, if N < 1000
label_i = BPM0[i]
channel_i = channel[start_i:end_i]
```

Window 0 là `[0:1000]`; window 1 là `[250:1250]`. Chỉ lấy cửa sổ đầy đủ; mọi complete final window đều được giữ. Không pad phần đuôi. Label count phải bằng M ngay trong loader và trước segmentation; thiếu/thừa một nhãn đều raise `AlignmentError`.

Reusable `validate_segmented_windows` kiểm tra số cửa sổ, toàn bộ metadata, shape 1000 samples, dtype, từng giá trị raw và BPM0 index của mọi cửa sổ. Error chứa record/path, expected và observed.

## 7. Dataset validation results

Chạy bằng `.venv/bin/python scripts/validate_phase2a_loader.py --manifest reports/phase_2a_alignment_manifest.csv`; exit code **0**. Duration dưới đây là `N/125`, không phải tổng thời lượng các cửa sổ chồng lắp.

| Record ID | N | Duration s | BPM0 | Expected | Actual | First bounds | Last bounds | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| DATA_01_TYPE01 | 37937 | 303.496 | 148 | 148 | 148 | [0:1000] | [36750:37750] | PASS |
| DATA_02_TYPE02 | 37850 | 302.800 | 148 | 148 | 148 | [0:1000] | [36750:37750] | PASS |
| DATA_03_TYPE02 | 35989 | 287.912 | 140 | 140 | 140 | [0:1000] | [34750:35750] | PASS |
| DATA_04_TYPE02 | 37250 | 298.000 | 146 | 146 | 146 | [0:1000] | [36250:37250] | PASS |
| DATA_05_TYPE02 | 37328 | 298.624 | 146 | 146 | 146 | [0:1000] | [36250:37250] | PASS |
| DATA_06_TYPE02 | 38373 | 306.984 | 150 | 150 | 150 | [0:1000] | [37250:38250] | PASS |
| DATA_07_TYPE02 | 36650 | 293.200 | 143 | 143 | 143 | [0:1000] | [35500:36500] | PASS |
| DATA_08_TYPE02 | 40803 | 326.424 | 160 | 160 | 160 | [0:1000] | [39750:40750] | PASS |
| DATA_09_TYPE02 | 38121 | 304.968 | 149 | 149 | 149 | [0:1000] | [37000:38000] | PASS |
| DATA_10_TYPE02 | 38042 | 304.336 | 149 | 149 | 149 | [0:1000] | [37000:38000] | PASS |
| DATA_11_TYPE02 | 36500 | 292.000 | 143 | 143 | 143 | [0:1000] | [35500:36500] | PASS |
| DATA_12_TYPE02 | 37316 | 298.528 | 146 | 146 | 146 | [0:1000] | [36250:37250] | PASS |

```text
Training pairs found: 12
Records loaded: 12
Total windows: 1768
Alignment failures: 0
Finite-data failures: 0
Other failures: 0
Overall status: PASS
```

CSV chi tiết: [phase_2a_alignment_manifest.csv](phase_2a_alignment_manifest.csv).

## 8. Test results

Environment: existing `.venv`, Python 3.12.10, pytest 9.1.1, pytest-cov 7.1.0. Không cài package mới trong Phase 2A.

```bash
.venv/bin/python -m pytest
COVERAGE_FILE=/tmp/cpc_phase2a.coverage .venv/bin/python -m pytest \
  --cov=cpc_ppg.data --cov-report=term-missing \
  --cov-report=json:/tmp/cpc_phase2a_coverage.json \
  --junitxml=/tmp/cpc_phase2a_tests.xml
```

- Plain pytest: **76 passed in 1.65 s**; 0 failed, 0 skipped.
- Coverage run: **76 passed in 1.93 s**; 0 failed, 0 skipped.
- Statement coverage riêng `cpc_ppg.data`: **229/229 = 100%**, 0 missing. Không tuyên bố coverage 100% cho script hoặc toàn repository.
- 10 discovery tests; 34 loader tests; 26 segmentation/validator tests; 6 integration/CLI tests. Hai test dataset thực đã chạy, không skip; chỉ skip nếu Training directory không hiện diện trên máy khác.
- Test đủ N=0,999,1000,1250,1499,1500; mapping từng kênh với distinct row values; labels row/column; 1-D sig, 5/7 rows, transpose/3-D sai; missing variables; NaN/Inf; nonnumeric/complex; thiếu/thừa labels; off-by-one; dữ liệu/dtype/bounds/labels bị đổi; CLI exit nonzero và thống kê đúng khi bản ghi lỗi.
- Lượt đầu có một lỗi test so sánh basename với schema chứa relative path; đã sửa phép đối chiếu dùng relative path và chạy lại toàn bộ thành công.

## 9. Integrity checks

- So sánh SHA-256 của **44 MAT files** toàn dataset trước và sau triển khai/validation: 44/44 giữ nguyên; 0 changed/missing; 0 added. Baseline và kết quả kiểm tra phiên này: `/tmp/cpc_phase2a_raw_before.json`, `/tmp/cpc_phase2a_raw_integrity.json`.
- Real integration test kiểm tra lại SHA-256 của 24 Training MAT files trước/sau loading và segmentation, đồng thời so sánh từng raw channel/BPM0 với kết quả `loadmat` độc lập.
- Không normalization, filtering, detrend, interpolation, resampling, PPG averaging hoặc loại −1024. Tests xác nhận −1024 được giữ nguyên, raw dtype không bị đổi.
- Segmentation không sửa arrays/labels gốc; windows chia sẻ memory với channels và được đặt chỉ đọc.
- Cửa sổ đầu `[0:1000]` giữ nguyên cho cả 12 records; final complete window không bị bỏ. Không silent label truncation, padding, offset hay suy nhãn từ ECG.

## 10. Assumptions

Chi tiết trạng thái đã cập nhật tại [reconstruction_assumptions.md](../docs/assumptions/reconstruction_assumptions.md).

| Decision group | Classification / status |
| --- | --- |
| Fs, 8 s windows, 6 s overlap, per-window ground truth, all windows used | PAPER-SPECIFIED / CONFIRMED, IMPLEMENTED |
| Training six rows/order, signal-label filenames, BPM0 vector/mapping | DATASET-CONFIRMED / CONFIRMED, IMPLEMENTED |
| 1000/250 samples; full-window count formula | Hệ quả xác định của PAPER-SPECIFIED / DATASET-CONFIRMED; DERIVED, IMPLEMENTED; không phải giả định bất định |
| Zero-based indexing, half-open slices, frozen dataclasses/read-only views, deterministic case-insensitive discovery, strict errors | RECONSTRUCTION-ASSUMPTION — quy ước/lựa chọn kỹ thuật / RESOLVED, IMPLEMENTED |

Không thêm giả định sinh lý hoặc thuật toán HR. A01–A11 từ Phase 1B vẫn OPEN, không được dùng trong loader/alignment này.

## 11. Open issues

Không có vấn đề chưa giải quyết trong phạm vi Phase 2A Training loader/alignment. API chủ đích chỉ hỗ trợ Training MAT v5 theo schema đã xác nhận; không tự đoán schema khác.

## 12. Phase conclusion

**PASS.** Đủ 12 Training pairs và 24 MAT files được load; channel mapping chính xác; BPM0 trở thành vector; toàn bộ 1768 windows có boundaries/labels/raw values đúng; tests và script đều pass; raw MAT hashes không đổi. Báo cáo, manifest và assumptions update đã hoàn thành.

**Phase 2B preprocessing was NOT implemented.**
