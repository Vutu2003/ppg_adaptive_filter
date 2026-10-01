# Reconstruction Assumptions / Decisions — Phases 1B–2B

Bảng dưới đây ghi các chi tiết còn thiếu trong README dataset hoặc paper CPC và trạng thái quyết định hiện tại. Nguồn và phạm vi xem [báo cáo đối chiếu](../../reports/data/dataset_documentation_reconciliation.md). `OPEN` nghĩa là phải quyết định và ghi lý do trước khi code hoặc so sánh kết quả chịu ảnh hưởng. Phần Phase 2A/2B ở cuối ghi phân loại và trạng thái của các quyết định đã triển khai. `BASELINE-RESOLVED` chốt reconstruction có thể tái lập, không xác nhận cách tác giả đã triển khai.

| ID / item | Missing specification | Future implementation choice | Rationale | Risk | Status |
| --- | --- | --- | --- | --- | --- |
| A01 — Competition ACC axis order | TestData README chỉ nói rows 3–5 là ba kênh ACC; không gắn X/Y/Z. | OPEN: đối chiếu nguồn chính chủ bổ sung hoặc giữ tên `ACC_AXIS_1..3` khi dùng test. | Không biến phép suy “bỏ ECG” thành xác nhận tài liệu. | Gán sai trục có thể đổi thứ tự cascade nếu dùng Competition. | OPEN |
| A02 — Spectral mask implementation | CPC chỉ nêu loại coefficients ngoài 0.4–3.5 Hz, không nêu FFT length, padding, xử lý tần số âm, inverse và biên. | Phase 2B baseline: mỗi window 1000 samples độc lập; rFFT/irFFT; inclusive mask; không padding, detrend, taper, overlap-add. | Trực tiếp loại coefficients ngoài dải và khôi phục số thực, ít xử lý bổ sung; dùng nguyên analysis units Phase 2A. Đây là RECONSTRUCTION-ASSUMPTION, không phải thông tin xác nhận từ paper. | Tác giả có thể dùng global filtering, NFFT hoặc xử lý biên khác; bất định phương pháp gốc vẫn còn. | BASELINE-RESOLVED; AUTHOR IMPLEMENTATION UNRESOLVED |
| A03 — LMS initialization/update | Paper cho order 27 và step 0.0001, không nêu initial weights, error sign và update convention. | OPEN: ghi rõ khởi tạo và phương trình cập nhật khi implement LMS. | Cần một thuật toán xác định, có thể kiểm tra. | Hội tụ và đầu ra khác paper. | OPEN |
| A04 — RLS scalar 0.999 | §4.1 gọi cặp 0.0001/0.999 là “step size” cho LMS/RLS, không ghi rõ 0.999 là forgetting factor. | OPEN: xác minh hoặc ghi diễn giải được chọn với nguồn/lý do. | Tránh gán một tên tham số không được paper xác nhận. | Chọn sai ý nghĩa làm RLS không tương ứng kết quả paper. | OPEN |
| A05 — RLS initialization | Paper không nêu covariance `P(0)`, regularization hoặc initial weights. | OPEN: chọn và ghi giá trị/phương trình khởi tạo sau khi rà soát. | RLS không xác định duy nhất nếu thiếu khởi tạo. | Độ ổn định và transient khác biệt. | OPEN |
| A06 — Adaptive state policy | Paper không nói carry/reset LMS/RLS theo window hay subject. | OPEN: xác định ranh giới trạng thái trước khi chạy replication. | Cửa sổ chồng lắp có thể khiến carry state thay đổi đầu ra mạnh. | Khó so sánh AAE và dễ rò thông tin giữa bản ghi. | OPEN |
| A07 — Normalization/scaling | Paper không yêu cầu normalize PPG/ACC trước adaptive filtering. | OPEN: mặc định không thêm phép biến đổi; nếu cần vì ổn định phải ghi quyết định và lý do trước. | Scale ảnh hưởng bước LMS và RLS. | Thay đổi thuật toán được tái tạo. | OPEN |
| A08 — Periodogram details | `NF=4096` nhưng chưa nêu window function, detrend, scaling, one-sided bin và tie rule. | OPEN: định nghĩa toàn bộ quy ước periodogram/peak khi implement. | Cùng `NF` vẫn có thể ra peak khác nhau. | Sai HR ở các cửa sổ có nhiều đỉnh. | OPEN |
| A09 — Tracking initialization | Paper dùng vị trí HR cửa sổ trước và smoothing 90/5/5 nhưng không nêu `N0` đầu tiên hoặc hai cửa sổ đầu. | OPEN: chọn initialization và quy tắc biên, không dùng BPM0 để khởi tạo nếu không có nguồn. | Tránh ground-truth leakage; phải xử lý đầu chuỗi. | Error đầu bản ghi và toàn chuỗi bị thiên lệch. | OPEN |
| A10 — Offline post-processing | Paper nêu current + 4 trước + 3 sau, so `abs(HR−mean)>variance`; không nêu định nghĩa variance và biên đầu/cuối. | OPEN: định nghĩa ddof, số điểm thực tế ở biên và chỉ áp dụng offline khi phù hợp. | Cần công thức tái lập cho các window biên. | Sai khác AAE và rò tương lai vào chế độ online. | OPEN |
| A11 — Table 1 per-subject crosswalk | CPC Table 1 đánh số Subject 1–12 nhưng nguồn không cung cấp crosswalk tường minh tới `DATA_XX`. | OPEN: khi so sánh từng hàng Table 1, xác minh crosswalk hoặc chỉ báo cáo theo filename. | Bộ 12 file primary đã chốt, song thứ tự hàng kết quả chưa được xác nhận độc lập. | Gán nhầm chỉ số subject khi so sánh từng hàng. | OPEN |

Các thông số đã có nguồn (Training rows, Fs=125 Hz, cửa sổ 8 s/shift 2 s, bộ 12 cặp primary, band 0.4–3.5 Hz) không được lặp lại ở đây như giả định.

## Phase 2A — Loader/alignment decisions

Các giá trị đã xác nhận sau đây được ghi lại để truy vết triển khai, **không phải giả định mới**. Nguồn đã được đối chiếu ở Phase 1B, bao gồm schema `data/metadata/dataset_schema.yaml`.

| Decision | Classification | Source / rationale | Status |
| --- | --- | --- | --- |
| `Fs=125 Hz`, window 8 s, overlap 6 s, shift 2 s | PAPER-SPECIFIED; đồng thời DATASET-CONFIRMED | CPC §2 p.19; Training Readme p.1. Shift là 8−6. | CONFIRMED / IMPLEMENTED |
| Dùng mọi cửa sổ có nhãn, gồm cửa sổ đầu tiên | PAPER-SPECIFIED | CPC §4.3 p.22; README quy định cửa sổ đầu 8 s. | CONFIRMED / IMPLEMENTED |
| Ground truth ECG-derived được cung cấp theo cửa sổ | PAPER-SPECIFIED; đồng thời DATASET-CONFIRMED | CPC §2; Training README; `BPM0`. Loader chỉ đọc nhãn cung cấp. | CONFIRMED / IMPLEMENTED |
| 12 Training pairs; `sig=(6,N)`; rows ECG, PPG1, PPG2, ACC-X, ACC-Y, ACC-Z | DATASET-CONFIRMED | Training Readme.pdf / Readme.docx; audit Phase 1A. | CONFIRMED / IMPLEMENTED |
| Pair theo cùng `DATA_NN_TYPENN`; `BPM0[i]` ứng với window i | DATASET-CONFIRMED | Training filename patterns và README; kiểm chứng đủ 12 cặp bằng validator Phase 2A. | CONFIRMED / IMPLEMENTED |
| Python chỉ số 0; slice `[start:end]`; thời gian đầu/cuối tính từ sample/Fs | RECONSTRUCTION-ASSUMPTION — quy ước triển khai đã chốt | Quy ước Python biểu diễn nguyên vẹn các cửa sổ README, không thay đổi dữ liệu hay protocol. | RESOLVED / IMPLEMENTED |
| `window_samples=1000`, `hop_samples=250`; `M=0` khi `N<1000`, ngược lại `(N−1000)//250+1` | PAPER-SPECIFIED / DATASET-CONFIRMED — hệ quả toán học | 125×8 và 125×2; đếm mọi slice đầy đủ. Đây là phép suy xác định, không có bất định cần giả định. | DERIVED / IMPLEMENTED |
| Frozen dataclasses; array views chỉ đọc; sort theo ID; tên file không phân biệt hoa/thường và từ chối alias trùng; mặc định kiểm tra 12 cặp | RECONSTRUCTION-ASSUMPTION — lựa chọn kỹ thuật đã chốt | Bảo vệ raw buffers khỏi ghi vô ý, tránh sao chép kênh/window; discovery xác định và phát hiện ghép cặp mơ hồ. Có thể đặt `expected_count` cho subset/test. | RESOLVED / IMPLEMENTED |
| Mọi mismatch, NaN/Inf, dtype không phải số thực hoặc shape sai đều báo lỗi; giữ nguyên −1024 và dtype | RECONSTRUCTION-ASSUMPTION — chính sách validation theo yêu cầu Phase 2A | Không sửa, shift, pad hoặc truncate dữ liệu/nhãn; error kèm ID/path, expected/observed. | RESOLVED / IMPLEMENTED |

Không có giả định khoa học chưa giải quyết nào cản trở Phase 2A Training loader/alignment. Tại thời điểm hoàn tất Phase 2A, A01–A11 giữ trạng thái `OPEN`; không dùng chúng để thay đổi pipeline trong phase đó. Chi tiết kiểm chứng xem [báo cáo Phase 2A](../../reports/phase_2a_loader_alignment_report.md).

## Phase 2B — Spectral preprocessing baseline

Nguồn trực tiếp: CPC paper local, **§3.1 p.19**, đã đọc lại trong Phase 2B; Phase 1B không cung cấp bằng chứng mạnh hơn về FFT implementation. Các quyết định dưới đây được chốt theo paper và baseline người dùng yêu cầu, không dựa trên HR error hay AAE. Không resolve A01, A03–A11.

| Decision | Classification | Rationale / consequence | Status |
| --- | --- | --- | --- |
| Eliminate spectral coefficients ngoài desired band 0.4–3.5 Hz | PAPER-SPECIFIED | CPC §3.1; không thay bằng Butterworth/FIR/IIR hoặc đổi band. | CONFIRMED / IMPLEMENTED |
| Lọc riêng PPG1 và PPG2; cùng filter áp dụng riêng cho ACC-X/Y/Z | PAPER-SPECIFIED | CPC §3.1; đủ năm inputs. | CONFIRMED / IMPLEMENTED |
| Lấy arithmetic mean của hai PPG sau khi từng kênh đã lọc | PAPER-SPECIFIED | CPC §3.1 và mô tả Fig.1; không average raw trước. | CONFIRMED / IMPLEMENTED |
| Fs=125, 8 s=1000 samples, các kênh và BPM0/index/bounds từ Phase 2A | DATASET-CONFIRMED; length là DERIVED | Reuse loader/segmentation, giữ đủ 1768 windows và nhãn như metadata. ECG không là input; BPM0 không ảnh hưởng transforms. | CONFIRMED / IMPLEMENTED |
| Filtering độc lập từng window; NFFT=L=1000; không zero-padding | RECONSTRUCTION-ASSUMPTION | Dùng đúng analysis units 8 s và ít xử lý bổ sung. Paper không chốt global hay per-window/NFFT. | BASELINE-RESOLVED / IMPLEMENTED |
| NumPy rFFT, mask inclusive `f>=0.4 & f<=3.5`, irFFT với `n=L` | RECONSTRUCTION-ASSUMPTION | rFFT biểu diễn Hermitian spectrum của input số thực; irFFT tránh output imaginary residual. Không nói tác giả dùng rFFT. | BASELINE-RESOLVED / IMPLEMENTED |
| Không spectral taper, detrend, normalization, resampling, overlap-add hoặc state giữa windows | RECONSTRUCTION-ASSUMPTION | Không thêm phép biến đổi không được chỉ định. DC bị loại vì ngoài band, không subtract mean riêng. Filtering hữu hạn có quy ước periodic/circular trên từng window, không nối lại full record. | BASELINE-RESOLVED / IMPLEMENTED |
| df=125/1000=0.125 Hz; first retained=0.5 Hz, last=3.5 Hz; retained bin count được tính từ frequency mask | DERIVED | 0.375<0.4; 0.5>=0.4; 3.5 là bin chính xác. Requested paper band vẫn 0.4–3.5, không đổi thành 0.5–3.5. | DERIVED / VERIFIED |
| Frozen typed config/output; output float64 riêng, chỉ đọc; raw model không thay đổi | ENGINEERING-DECISION | Giữ data boundary rõ, kiểm chứng numerical precision nhất quán; không giữ raw copies trong output. | RESOLVED / IMPLEMENTED |
| Second-FFT leakage tolerance: `tau=64*eps_float64*L`; max out-of-band magnitude/max FFT magnitude ≤tau; energy fraction ≤tau² | ENGINEERING-DECISION | Tolerance roundoff theo scale, không đòi exact zero. Magnitudes normalize chỉ trong metric để tránh overflow khi bình phương, không normalize signals. Zero output có leakage=0. Không tune tolerance theo HR/AAE. | RESOLVED / IMPLEMENTED |
| Diagnostic coefficient power `abs(rFFT(x))²/L²`, không taper/padding, Hz axis; chọn record đầu tiên theo sort và window 0 | ENGINEERING-DECISION | Các plot được chọn xác định, không chọn theo nhãn/error; không implement HR periodogram/peak/tracking hoặc claim trùng paper Fig.1. | RESOLVED / IMPLEMENTED |

Bất định về cách lọc thật của tác giả (global/per-window, FFT length, padding, boundaries, taper/inverse/edge handling) **vẫn unresolved**. Baseline đóng băng cho replication có thể tái lập, không suy ra các lựa chọn này đã được paper xác nhận. Kết quả kiểm chứng xem [báo cáo Phase 2B](../../reports/phase_2b_preprocessing_report.md).
