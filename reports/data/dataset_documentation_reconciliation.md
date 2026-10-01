# Phase 1B — Dataset Documentation Reconciliation

## 1. Scope

Đối chiếu 44 file MAT local với tài liệu của bộ dữ liệu và paper CPC để chốt hợp đồng đọc dữ liệu cho Phase 2. Đây là đặc tả tài liệu: không sửa MAT, không triển khai loader/thuật toán, không chạy thử nghiệm. Chỉ dùng các trạng thái `CONFIRMED_FROM_DATASET_DOC`, `CONFIRMED_FROM_CPC_PAPER`, `CONFIRMED_FROM_TROIKA_PAPER`, `CONFIRMED_FROM_MULTIPLE_SOURCES`, `INFERRED_FROM_DATA`, `UNRESOLVED`.

Đường dẫn của báo cáo đặt tại `reports/data/` theo chỉ dẫn hiện tại của người dùng. [Báo cáo Stage 1A](dataset_status_report.md) và hai manifest được giữ trong cùng thư mục.

## 2. Sources reviewed

| ID | Nguồn | Phạm vi và kiểm tra |
| --- | --- | --- |
| D1 | [Training Readme.pdf](../../data/Training_data/Readme.pdf), 2 trang | Channel order, Fs, TYPE01/02, BPM0 và cửa sổ. |
| D2 | [Training Readme.docx](../../data/Training_data/Readme.docx) | Đã đọc riêng; nội dung **giống D1 sau khi chuẩn hóa khoảng trắng**, không có khác biệt nội dung. Cả hai trùng byte với file trong archive tác giả. |
| D3 | [TestData.zip của tác giả](https://github.com/zhilinzhang/IEEE-SP-Cup-2015-PPG-Dataset/blob/main/TestData.zip), `TestData/Readme.pdf` và `Readme.docx`, 2 trang | Competition schema, T01/T02, Fs và vị trí cửa sổ. Hai bản cùng nội dung, khác ký hiệu bullet khi trích text. 10/10 MAT local trùng byte với archive. |
| D4 | [README repository dữ liệu của tác giả](https://github.com/zhilinzhang/IEEE-SP-Cup-2015-PPG-Dataset) | `competition_data.zip` là 12 training sets; `TestData.zip` là test; `TrueBPM.zip` là ground truth test. 24/24 MAT Training và 10/10 nhãn `True_*` local trùng byte với hai archive tương ứng. |
| P1 | [CPC paper local](<../../docs/Healthcare Tech Letters - 2018 - Islam - Cascade and parallel combination  CPC  of adaptive filters for estimating heart.pdf>), Islam et al., *Healthcare Technology Letters* 5(1), 2018, pp. 18–24, DOI 10.1049/htl.2017.0027 | §2–§4.3: cohort, preprocessing, CPC, tracking, parameters, evaluation. |
| T1 | [TROIKA paper gốc trong repository tác giả](https://github.com/zhilinzhang/IEEE-SP-Cup-2015-PPG-Dataset/blob/main/TROIKA_A_General_Framework_for_Heart_Rat.pdf), Zhang et al., *IEEE TBME* 62(2), 2015, pp. 522–531 | §III và §IV, nhất là ground truth p. 528 và cohort. |
| O1 | [Stage 1A report](dataset_status_report.md), [file inventory](mat_file_inventory.csv), [variable manifest](mat_variable_manifest.csv) | Quan sát local: 12+10 signal, 12+10 label, shape, 22/22 độ dài nhãn khớp công thức. |

Nguồn ngoài chỉ dùng khi README local không mô tả Competition hoặc quy trình ground truth đầy đủ. Không dùng blog/forum. Archive tải vào `/tmp` để đọc tài liệu và đối chiếu SHA256; không thêm hay sửa file trong `data/Training_data/` và `data/Competition_data/`. Chỉ tạo schema YAML tại `data/metadata/` theo yêu cầu.

## 3. Confirmed dataset schema

### 3.1 Training split

D1/D2 nói rõ `sig` có 6 hàng theo thứ tự dưới đây. O1 xác nhận 12 file `(6, N)`, kiểu `float64`, cùng một biến `sig`. Hàng đánh số **1-based**; Python index bằng row − 1. Mỗi file tín hiệu có file `DATA_XX_TYPEYY_BPMtrace.mat` cùng stem với biến `BPM0`.

| Split | Row (1-based) | Signal | Source | Confidence / status |
| --- | ---: | --- | --- | --- |
| Training | 1 | ECG (ngực) | D1/D2 p. 1; O1 | HIGH — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| Training | 2 | PPG1 (cổ tay) | D1/D2 p. 1; O1 | HIGH — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| Training | 3 | PPG2 (cổ tay) | D1/D2 p. 1; O1 | HIGH — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| Training | 4 | ACC-X | D1/D2 p. 1, “x-, y-, z-axis” theo thứ tự | HIGH — `CONFIRMED_FROM_DATASET_DOC` |
| Training | 5 | ACC-Y | D1/D2 p. 1 | HIGH — `CONFIRMED_FROM_DATASET_DOC` |
| Training | 6 | ACC-Z | D1/D2 p. 1 | HIGH — `CONFIRMED_FROM_DATASET_DOC` |

### 3.2 Competition split

D3 nói `TEST_Sxx_Tyy.mat` có `sig` 5 hàng: hai hàng đầu là hai PPG, ba hàng cuối là ACC; ECG có được ghi nhưng **không cấp cho người dự thi**. O1 xác nhận 10 file `(5, N)`; SHA256 của cả 10 tín hiệu trùng archive TestData. D3 không gắn tên X/Y/Z cho từng hàng ACC; không điền trục bằng suy đoán.

| Split | Row (1-based) | Signal | Source | Confidence / status |
| --- | ---: | --- | --- | --- |
| Competition | 1 | PPG1 | D3 p. 1; O1 | HIGH — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| Competition | 2 | PPG2 | D3 p. 1; O1 | HIGH — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| Competition | 3 | ACC axis 1; tên X/Y/Z chưa xác nhận | D3 p. 1; O1 | HIGH cho vai trò ACC — `CONFIRMED_FROM_DATASET_DOC`; tên trục `UNRESOLVED` |
| Competition | 4 | ACC axis 2; tên X/Y/Z chưa xác nhận | D3 p. 1; O1 | HIGH cho vai trò ACC — `CONFIRMED_FROM_DATASET_DOC`; tên trục `UNRESOLVED` |
| Competition | 5 | ACC axis 3; tên X/Y/Z chưa xác nhận | D3 p. 1; O1 | HIGH cho vai trò ACC — `CONFIRMED_FROM_DATASET_DOC`; tên trục `UNRESOLVED` |

`True_Sxx_Tyy.mat` chứa `BPM0` và trùng 10/10 file trong archive TrueBPM của D4. Đây là nhãn test được công bố riêng; không phải ECG waveform. Việc ba hàng ACC Competition có đúng thứ tự X–Y–Z như Training là **hợp lý nhưng chưa được D3 xác nhận rõ**; không chốt trong schema.

## 4. Sampling rates and signal metadata

| Item | Kết luận | Nguồn | Status |
| --- | --- | --- | --- |
| Fs PPG/ACC/ECG Training | 125 Hz, các tín hiệu lấy mẫu đồng thời | D1/D2 p. 1; P1 §2 p. 19; T1 §IV.A p. 528 | `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| Fs PPG/ACC/ECG ghi ở Competition | 125 Hz; ECG không nằm trong `TEST_*` công khai | D3 p. 1 | `CONFIRMED_FROM_DATASET_DOC` |
| Orientation | `sig`: channels × samples; `BPM0`: vector cột trong MAT local | D1/D3 mô tả rows; O1 shape | `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| PPG/ACC/ECG physical units, calibration | Không công bố trong README/paper đã đọc | D1/D3/P1/T1 | `UNRESOLVED` (`UNKNOWN`) |
| PPG thiết bị | Hai pulse oximeter LED xanh 515 nm, cách 2 cm trong README Training/Test | D1/D3 | `CONFIRMED_FROM_DATASET_DOC` cho gói MAT này |

Mâu thuẫn nguồn: T1 §IV.A p. 528 mô tả **một** PPG và LED **609 nm**, còn D1/D3 mô tả **hai** PPG và LED **515 nm**. Đối với schema các MAT local, ưu tiên README dataset và shape thực tế; không dùng mô tả thiết bị của T1 để thay đổi channel mapping. P1 §2 p. 19 cũng nói hai PPG và ba ACC. T1 còn mô tả phần đầu/cuối vận động ở 1–2 km/h, trong khi D1 ghi “rest”; schedule cụ thể của `TYPE01/TYPE02` lấy theo D1.

## 5. Ground-truth BPM0 generation and alignment

**GROUND TRUTH GENERATION AND ALIGNMENT**

- Training: D1/D2 p. 1 xác nhận `BPM0` trong `*_BPMtrace.mat` là HR ground truth tính từ ECG hàng 1, mỗi giá trị ứng với cửa sổ 8 s; hai cửa sổ liền nhau chồng 6 s, tức shift 2 s. P1 §2 p. 19 cũng xác nhận nhãn ECG-derived, 8 s và overlap 6 s. Status: `CONFIRMED_FROM_MULTIPLE_SOURCES`.
- Cách tính trong nghiên cứu TROIKA: T1 §IV.C p. 528 nói đếm H chu kỳ tim và thời lượng D trong một cửa sổ ECG, rồi lấy `60H/D` BPM; không dùng thuật toán ước lượng HR tự động từ ECG. Status cho **phương pháp paper TROIKA**: `CONFIRMED_FROM_TROIKA_PAPER`. Việc mỗi phần tử `BPM0` local được sinh chính xác bằng quy trình đánh dấu chu kỳ/biên D nào không được README xác nhận; status cho chi tiết đó: `UNRESOLVED`. Phase 2 dùng nhãn cung cấp, không tái tạo nhãn từ ECG.
- Competition: D4 gọi `TrueBPM.zip` là ground truth test; 10 file `True_*` local trùng byte archive, ghép với `TEST_*` bằng cùng `Sxx_Tyy`. Vai trò nhãn: `CONFIRMED_FROM_MULTIPLE_SOURCES`; nguồn ECG và cách dựng từng giá trị test chưa được D3 nói trực tiếp: `UNRESOLVED`. ECG đã được ghi nhưng bị ẩn trong test theo D3.
- Vị trí cửa sổ: D1/D2 p. 1 nói nhãn đầu cho 8 giây đầu; nhãn thứ hai cho giây 3–10. D3 p. 2 ghi cụ thể cửa sổ 1 là sample 1–1000, cửa sổ 2 là sample 251–1250 theo **1-based inclusive**. Với Python: `[0:1000]`, `[250:1250]`; cửa sổ i (0-based) là `[250*i : 250*i+1000]`. Status: `CONFIRMED_FROM_MULTIPLE_SOURCES` cho window/shift/alignment theo index.
- O1: 22/22 cặp có `len(BPM0) = floor((N−1000)/250)+1`; đây là kiểm tra dữ liệu, không phải nguồn độc lập cho Fs. P1 §4.3 p. 22 nói CPC dùng **mọi cửa sổ** (khác JOSS/TROIKA trong so sánh). Status: `CONFIRMED_FROM_CPC_PAPER` cho quy tắc đánh giá CPC; O1 nhất quán với không loại cửa sổ đầu/cuối đã có nhãn. Phần mẫu cuối ngắn hơn 1000 không tạo cửa sổ đầy đủ; không có nhãn tương ứng. Trọng tâm Phase 2 là bảo toàn thứ tự và số lượng `BPM0`.

## 6. Dataset split semantics

| Item | Ý nghĩa | Nguồn / status |
| --- | --- | --- |
| `Training_data` | 12 bản ghi công khai từ tập training trong archive tác giả tên gây nhầm `competition_data.zip`; mỗi bản ghi có ECG, 2 PPG, 3 ACC và nhãn BPM0 | D1/D4/O1 — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| `DATA_XX` | Mã bản ghi 01–12; các file có 12 mã khác nhau. README nói “mỗi subject” nhưng **không xuất bản crosswalk rõ** giữa mã và hàng Subject 1–12 của CPC Table 1 | D1/O1/P1 — tập 12 file `CONFIRMED_FROM_MULTIPLE_SOURCES`; đối chiếu từng hàng Table 1 `UNRESOLVED` |
| `TYPE01` | Treadmill: rest 30 s → 8 km/h 1 min → 15 km/h 1 min → 8 km/h 1 min → 15 km/h 1 min → rest 30 s. Local chỉ `DATA_01_TYPE01.mat` | D1 p. 1/O1 — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| `TYPE02` | Treadmill: rest 30 s → 6 km/h 1 min → 12 km/h 1 min → 6 km/h 1 min → 12 km/h 1 min → rest 30 s. Local `DATA_02`–`DATA_12` | D1 p. 1/O1 — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| `Competition_data` | 10 test trials từ 8 subjects của TestData; 5 kênh công khai, ECG ẩn; `True_*` là nhãn test công bố riêng | D3/D4/O1 — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| `Sxx` | Subject 01–08 của test cohort; `S02`, `S06` có 2 trials local | D3 p. 1/O1 — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| `T01` | Kiểu vận động gồm cử động tay/cẳng tay, chạy, nhảy, chống đẩy | D3 p. 1 — `CONFIRMED_FROM_DATASET_DOC` |
| `T02` | Chủ yếu cử động tay/cẳng tay cường độ cao, ví dụ boxing | D3 p. 1 — `CONFIRMED_FROM_DATASET_DOC` |
| Cohort | Training/CPC: 12 nam, 18–35 tuổi. Test: 8 người, 19–58 tuổi; D3 có nữ 58 tuổi ở S08 | P1 §2/T1 §IV.A/D3 p. 1 — `CONFIRMED_FROM_MULTIPLE_SOURCES` cho cohort Training, `CONFIRMED_FROM_DATASET_DOC` cho Test |

Không gộp 8 test subjects vào 12 subjects của CPC Table 1. D4 phân biệt `TestData.zip` với archive 12 training sets; P1 Table 1 nêu rõ 12 subjects của TROIKA. Việc hai cohort có người trùng nhau không có crosswalk, nhưng test được mô tả là tập riêng. Thời lượng local theo 125 Hz khoảng 287.912–326.424 s cho Training, 206.032–320.176 s cho Test; câu “5 phút” ở P1 là mô tả gần đúng, không ép cắt/chèn mẫu.

## 7. CPC replication set

**CPC PRIMARY REPLICATION SET: 12 signal–label pairs trong `data/Training_data/`; không dùng `TEST_*` hoặc `True_*` để tái tạo Table 1.** Cơ sở: P1 §2 và Table 1/§4.3 (12 subjects TROIKA), D4 (12 training sets của TROIKA), D1 và O1 (đúng 12 signal–label pairs local). Status ở cấp **tập file**: `CONFIRMED_FROM_MULTIPLE_SOURCES`. Ánh xạ từng số hàng Subject 1–12 của Table 1 sang `DATA_XX` vẫn `UNRESOLVED`; không chọn dựa trên metric.

| Signal file | Label file |
| --- | --- |
| `data/Training_data/DATA_01_TYPE01.mat` | `data/Training_data/DATA_01_TYPE01_BPMtrace.mat` |
| `data/Training_data/DATA_02_TYPE02.mat` | `data/Training_data/DATA_02_TYPE02_BPMtrace.mat` |
| `data/Training_data/DATA_03_TYPE02.mat` | `data/Training_data/DATA_03_TYPE02_BPMtrace.mat` |
| `data/Training_data/DATA_04_TYPE02.mat` | `data/Training_data/DATA_04_TYPE02_BPMtrace.mat` |
| `data/Training_data/DATA_05_TYPE02.mat` | `data/Training_data/DATA_05_TYPE02_BPMtrace.mat` |
| `data/Training_data/DATA_06_TYPE02.mat` | `data/Training_data/DATA_06_TYPE02_BPMtrace.mat` |
| `data/Training_data/DATA_07_TYPE02.mat` | `data/Training_data/DATA_07_TYPE02_BPMtrace.mat` |
| `data/Training_data/DATA_08_TYPE02.mat` | `data/Training_data/DATA_08_TYPE02_BPMtrace.mat` |
| `data/Training_data/DATA_09_TYPE02.mat` | `data/Training_data/DATA_09_TYPE02_BPMtrace.mat` |
| `data/Training_data/DATA_10_TYPE02.mat` | `data/Training_data/DATA_10_TYPE02_BPMtrace.mat` |
| `data/Training_data/DATA_11_TYPE02.mat` | `data/Training_data/DATA_11_TYPE02_BPMtrace.mat` |
| `data/Training_data/DATA_12_TYPE02.mat` | `data/Training_data/DATA_12_TYPE02_BPMtrace.mat` |

## 8. CPC paper protocol reconciliation

| Property | CPC paper P1 | Dataset docs D1/D3/D4 | Local observed O1 | Final decision / status |
| --- | --- | --- | --- | --- |
| Dataset / subjects | §2 p. 19: public TROIKA, 12 nam 18–35 | D4: 12 training sets gốc của TROIKA; D3: test cohort 8 người khác mục đích | 12 Training, 10 Test signal files | Training 12 cho primary — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| PPG / ACC / ECG | §2 p. 19: 2 PPG, 3 ACC, HR từ ECG | D1: ECG/PPG1/PPG2/ACC X/Y/Z; D3: 2 PPG+3 ACC, ECG ẩn | `(6,N)` / `(5,N)` | Training mapping như §3.1; Test role như §3.2 — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| Fs | §2 p. 19: 125 Hz | D1/D3: tất cả 125 Hz | MAT không có biến Fs | 125 Hz từ tài liệu — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| Duration / activity | §2 p. 19: ~5 phút treadmill | D1: TYPE01/02 schedules; D3: test T01/T02 khác | Training 287.912–326.424 s; Test 206.032–320.176 s nếu Fs=125 | Dùng nguyên bản ghi; không ép 5 phút — `CONFIRMED_FROM_MULTIPLE_SOURCES` cho Fs, `INFERRED_FROM_DATA` cho thời lượng |
| Window / labels | §2 p. 19: 8 s, overlap 6 s, ECG GT | D1: BPM0 ECG-derived, first/second window; D3: sample 1–1000, 251–1250 | 22/22 lengths khớp | 1000 samples, shift 250, pair theo tên — `CONFIRMED_FROM_MULTIPLE_SOURCES` |
| All windows | §4.3 p. 22: CPC dùng mọi cửa sổ | D1/D3 không nói bỏ cửa sổ nào | Có nhãn cho mọi full window theo công thức | Không bỏ cửa sổ đầu — `CONFIRMED_FROM_CPC_PAPER` |
| Spectral filtering | §3.1 p. 19: mask 0.4–3.5 Hz trên từng PPG và từng ACC, rồi average PPG | D1/D3 không quy định preprocessing | Raw chưa xử lý ở stage này | Theo CPC 0.4–3.5 Hz — `CONFIRMED_FROM_CPC_PAPER`; chi tiết FFT `UNRESOLVED` |
| TROIKA preprocessing khác CPC | T1 §III p. 525: 0.4–5 Hz | D1 không nêu dải lọc | — | Không thay 0.4–3.5 Hz của CPC bằng 0.4–5 Hz của TROIKA — `CONFIRMED_FROM_CPC_PAPER` |
| ECG GT method | §2 p. 19 chỉ nói ECG-derived | D1 nói ECG-derived; T1 §IV.C p. 528 nêu `60H/D` | BPM0 hiện hữu | Dùng BPM0; exact file-generation details `UNRESOLVED` |

**Preprocessing specification ở mức tài liệu:** P1 §3.1 p. 19 nói loại bỏ spectral coefficients ngoài **0.4–3.5 Hz** cho **từng PPG** và **từng trục ACC**; sau đó lấy trung bình hai PPG đã lọc. P1 §3.2 p. 20 đưa ACC-X → ACC-Y → ACC-Z qua ba adaptive noise cancelers mắc tầng; một nhánh LMS, một nhánh RLS, cuối cùng trộn lồi. Không có chỉ dẫn normalize; không nêu FFT mask implementation, padding, phase, periodogram window function hoặc kiểu detrend. P1 §3.3 p. 21 chỉ nói ước lượng spectral peak/periodogram từ đầu ra đã khử nhiễu. Các chi tiết không ghi rõ được đánh `UNRESOLVED`, không chọn Butterworth hoặc cách FFT cụ thể ở Phase 1B.

## 9. Paper-reported parameters

Bảng này ghi **đúng cách paper trình bày**, không chuyển một tham số chưa rõ tên thành cấu hình thuật toán đã chốt.

| Block / item | Value in P1 | Source | Status / caveat |
| --- | --- | --- | --- |
| LMS filter order | 27 coefficients | §4.1 p. 21 | `CONFIRMED_FROM_CPC_PAPER` |
| LMS step size | 0.0001 | §4.1 p. 21 | `CONFIRMED_FROM_CPC_PAPER` |
| RLS filter order | 55 coefficients | §4.1 p. 21 | `CONFIRMED_FROM_CPC_PAPER` |
| RLS-associated scalar | 0.999; paper gọi chung cặp 0.0001/0.999 là “step size” cho LMS/RLS | §4.1 p. 21 | Giá trị gắn RLS `CONFIRMED_FROM_CPC_PAPER`; **nghĩa là forgetting factor chưa được paper viết rõ** — `UNRESOLVED` |
| RLS covariance/weights initialization | Không nêu | §3.2–§4.1 pp. 20–21 | `UNRESOLVED` |
| CPC mixing λ | 0.5, hai nhánh trọng số bằng nhau; `y=λy1+(1−λ)y2` | §3.2 eq. (2) p. 20; §4.1 p. 21 | `CONFIRMED_FROM_CPC_PAPER` |
| Spectral periodogram points `NF` | 4096 | §4.1 p. 21 | `CONFIRMED_FROM_CPC_PAPER` |
| Tracking search half-range `Ds` | 10 frequency bins quanh vị trí cửa sổ trước; paper nói toàn dải xấp xỉ 37 BPM | §3.3–§4.1 p. 21 | `CONFIRMED_FROM_CPC_PAPER`; khởi tạo cửa sổ đầu `UNRESOLVED` |
| BPM from spectral bin | `bin × 60 × Fs / NF` theo eq. (3), với quy ước bin của paper | §3.3 eq. (3) p. 21 | `CONFIRMED_FROM_CPC_PAPER`; ánh xạ 0/1-based bin khi code `UNRESOLVED` |
| Online smoothing | 90% ước lượng hiện tại + 5% mỗi một trong hai ước lượng trước | §3.3 p. 21 | `CONFIRMED_FROM_CPC_PAPER`; hai cửa sổ đầu `UNRESOLVED` |
| Offline post-processing | Mean và variance của HR hiện tại, 4 trước, 3 sau; nếu `abs(HR−mean)>variance`, thay HR bằng mean | §3.3 p. 21 | Quy tắc nêu `CONFIRMED_FROM_CPC_PAPER`; định nghĩa variance/biên chuỗi `UNRESOLVED` |
| Evaluation window policy | Dùng mọi time window | §4.3 p. 22 | `CONFIRMED_FROM_CPC_PAPER` |

## 10. Paper-specified vs reconstruction assumptions

| Item | Paper specified? | Exact detail | Implementation consequence |
| --- | --- | --- | --- |
| Training channel order | Dataset README specified | ECG, PPG1, PPG2, ACC-X/Y/Z — D1 p. 1 | Phase 2 dùng index 0–5 tương ứng. |
| Competition ACC axis order | Không chỉ rõ trong D3 | Chỉ xác nhận ba hàng cuối là ACC | Giữ `ACC_AXIS_1..3`; chưa gắn X/Y/Z. |
| Spectral filtering | Một phần — P1 §3.1 | Mask ngoài 0.4–3.5 Hz, từng PPG/ACC, PPG average sau lọc | Cần quyết định FFT length, masking, inverse/edge handling khi implement. |
| LMS initial weights/update convention | Không | Chỉ order và step size | Cần assumption có ghi rõ, không âm thầm dùng mặc định. |
| RLS 0.999 / `P(0)` | Một phần — P1 §4.1 | 0.999 được gắn RLS nhưng gọi “step size”; covariance init không nêu | Cần xác minh ý nghĩa scalar và chọn init. |
| Adaptive state reset | Không | Không nói reset theo window/subject hay carry state | Có thể ảnh hưởng mạnh kết quả; phải định nghĩa trước thực nghiệm. |
| Normalize/scale | Không | Không có normalization trong §3.1–§4.1 | Không thêm normalization theo thói quen; nếu cần sẽ ghi assumption. |
| Periodogram window/detrend/bin ties | Không | Chỉ `NF=4096`, spectral peak và eq. (3) | Cần chốt khi implement HR estimator. |
| Tracking initialization | Không | Chỉ tìm quanh `N0` của cửa sổ trước và smoothing 90/5/5 | Cần xử lý cửa sổ đầu/đầu thứ hai. |
| Offline post-processing edges/variance | Một phần — P1 §3.3 | 4 trước, 3 sau; ngưỡng variance | Cần định nghĩa variance và các đầu/cuối bản ghi; không áp dụng cho online nếu không muốn dùng tương lai. |

## 11. Remaining ambiguities

1. Competition rows 3–5 là ACC chắc chắn, nhưng tên trục X/Y/Z từng hàng chưa được D3 nói rõ. Có thể suy từ Training bỏ ECG, song vẫn là giả định.
2. P1 gọi 0.999 là “step size” của RLS; việc diễn giải nó là forgetting factor chưa được tác giả xác nhận. Không viết cấu hình `forgetting_factor: 0.999` với status confirmed.
3. `BPM0` Training có vai trò ECG-derived rõ, song phương pháp tạo từng giá trị và beat-boundary/rounding của file cụ thể không được D1 mô tả. Với Competition, nguồn ECG của `True_*` cũng chưa nói trực tiếp.
4. Crosswalk `DATA_XX` ↔ đúng thứ tự Subject 1–12 của CPC Table 1 chưa công bố trong các nguồn đã đọc. Primary **set** xác nhận, per-subject comparison cần chú thích rõ.
5. Units/calibration của PPG, ACC, ECG; FFT mask chi tiết; filter state, init, normalization, periodogram window/tie rule, tracking first windows và offline post-processing edges chưa được P1/D1/D3 quy định.
6. Mâu thuẫn T1 với D1/D3 về một/hai PPG và 609/515 nm, và khác biệt “slow walk”/“rest” ở đoạn đầu/cuối được ghi ở §4/§8. Ưu tiên dataset README cho gói MAT hiện có và P1 cho pipeline CPC.

## 12. Implementation contract for Phase 2

- Dataset raw giữ nguyên tại `data/Training_data/` và `data/Competition_data/`; MAT v5 đọc `sig` / `BPM0` như O1. Schema [dataset_schema.yaml](../../data/metadata/dataset_schema.yaml) là manifest đã có nguồn. Không dùng dữ liệu test để tái tạo Table 1.
- Primary: đúng 12 cặp trong §7; Training Python indices: ECG 0, PPG1 1, PPG2 2, ACC-X 3, ACC-Y 4, ACC-Z 5. Competition Python indices: PPG1 0, PPG2 1, ACC 2–4; tên từng trục ACC Competition còn OPEN.
- Fs=125 Hz cho các kênh; orientation `channels × samples`. Mỗi window dài 1000 samples, shift 250 samples, index Python `[250*i:250*i+1000]`; ghép nhãn `BPM0[i]` cùng file stem; dùng mọi full window có nhãn, giữ nguyên thứ tự.
- Theo CPC §3.1: spectral filtering 0.4–3.5 Hz trên **mỗi** PPG và ACC trước khi average PPG; không tự đưa TROIKA band 0.4–5 Hz, không tự thêm normalization. Cách mask/FFT vẫn OPEN như [assumptions](../../docs/assumptions/reconstruction_assumptions.md).
- Phase 2 chỉ triển khai loader/preprocessing khi các lựa chọn OPEN cần cho code được ghi lại; RLS/CPC/tracking vẫn ngoài phạm vi Phase 2. Không dùng GT để chọn channel mapping.

## 13. Final decision

Các channel Training, Fs, window/shift, vai trò `BPM0` và bộ 12 cặp primary đã có nguồn; Competition PPG/ACC role có nguồn nhưng ACC axis order chưa chốt. Những chỗ chưa được paper/docs chỉ định được giữ OPEN, không điền giá trị giả vào schema. SHA256 44/44 MAT giữ nguyên so với [inventory Stage 1A](mat_file_inventory.csv); không sửa raw data.

**PHASE 1B STATUS: PASS** — specification đủ để xây loader và preprocessing cho **primary Training set** với các quyết định triển khai OPEN cần ghi rõ khi sang Phase 2. Không bắt đầu Phase 2 trong nhiệm vụ này.
