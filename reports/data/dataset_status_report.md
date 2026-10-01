# Dataset Status Inspection Report

## 1. Scope

Stage 1A (2026-10-01): kiểm kê và đọc cấu trúc dữ liệu IEEE SPC/TROIKA hiện có. Chỉ đọc file gốc; không tiền xử lý, chuyển đổi, sửa dữ liệu, chạy thuật toán hoặc dùng nhãn HR để chọn hàng tín hiệu. Các thông số “paper expected” bên dưới lấy từ yêu cầu Stage 1A, **chưa được audit độc lập từ paper**.

Phương pháp: SHA256 trước khi đọc; `scipy.io.loadmat` trên từng file, thử `h5py` nếu SciPy lỗi; thống kê trên mảng số; đối chiếu filename và chiều dài; SHA256 lại sau khi đọc. Thống kê min/max/mean/std dùng phần tử hữu hạn; độ lệch chuẩn là population std (`ddof=0`).

## 2. Dataset location

- Project root: `/home/vutu/Desktop/XLTHNC`
- Raw path dự kiến `data/raw/ieee_spc2015/`: **không tồn tại**.
- Raw path thực tế: `data/Training_data/` và `data/Competition_data/`; không di chuyển file.
- Tổng: **48 files**, gồm **44 `.mat`** và **4 file khác**; 12,825,765 bytes toàn bộ, 12,693,446 bytes MAT.
- File khác: `data/Training_data/Readme.pdf`, `Readme.docx`, `data/nomi_tracce_BPM.txt`, `data/nomi_tracce_tot.txt`. Chúng được kiểm kê, không dùng để suy diễn thứ tự kênh trong Stage 1A.

## 3. Raw file inventory

Đường dẫn trong bảng là tương đối từ project root. Tất cả MAT có đúng 1 biến người dùng và không phát sinh warning khi đọc. CSV [mat_file_inventory.csv](mat_file_inventory.csv) ghi thêm SHA256, số biến và warning/error cho từng file.

| File | Size (bytes) | MAT reader | Status |
| --- | ---: | --- | --- |
| `data/Competition_data/TEST_S01_T01.mat` | 472,572 | scipy.io.loadmat | OK |
| `data/Competition_data/TEST_S02_T01.mat` | 457,781 | scipy.io.loadmat | OK |
| `data/Competition_data/TEST_S02_T02.mat` | 546,264 | scipy.io.loadmat | OK |
| `data/Competition_data/TEST_S03_T02.mat` | 529,544 | scipy.io.loadmat | OK |
| `data/Competition_data/TEST_S04_T02.mat` | 381,948 | scipy.io.loadmat | OK |
| `data/Competition_data/TEST_S05_T02.mat` | 592,342 | scipy.io.loadmat | OK |
| `data/Competition_data/TEST_S06_T01.mat` | 450,976 | scipy.io.loadmat | OK |
| `data/Competition_data/TEST_S06_T02.mat` | 559,057 | scipy.io.loadmat | OK |
| `data/Competition_data/TEST_S07_T02.mat` | 464,964 | scipy.io.loadmat | OK |
| `data/Competition_data/TEST_S08_T01.mat` | 340,413 | scipy.io.loadmat | OK |
| `data/Competition_data/True_S01_T01.mat` | 930 | scipy.io.loadmat | OK |
| `data/Competition_data/True_S02_T01.mat` | 915 | scipy.io.loadmat | OK |
| `data/Competition_data/True_S02_T02.mat` | 928 | scipy.io.loadmat | OK |
| `data/Competition_data/True_S03_T02.mat` | 952 | scipy.io.loadmat | OK |
| `data/Competition_data/True_S04_T02.mat` | 752 | scipy.io.loadmat | OK |
| `data/Competition_data/True_S05_T02.mat` | 926 | scipy.io.loadmat | OK |
| `data/Competition_data/True_S06_T01.mat` | 894 | scipy.io.loadmat | OK |
| `data/Competition_data/True_S06_T02.mat` | 895 | scipy.io.loadmat | OK |
| `data/Competition_data/True_S07_T02.mat` | 821 | scipy.io.loadmat | OK |
| `data/Competition_data/True_S08_T01.mat` | 738 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_01_TYPE01.mat` | 663,124 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_01_TYPE01_BPMtrace.mat` | 1,188 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_02_TYPE02.mat` | 655,302 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_02_TYPE02_BPMtrace.mat` | 1,238 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_03_TYPE02.mat` | 630,349 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_03_TYPE02_BPMtrace.mat` | 1,132 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_04_TYPE02.mat` | 603,118 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_04_TYPE02_BPMtrace.mat` | 1,152 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_05_TYPE02.mat` | 622,859 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_05_TYPE02_BPMtrace.mat` | 1,118 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_06_TYPE02.mat` | 687,192 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_06_TYPE02_BPMtrace.mat` | 1,100 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_07_TYPE02.mat` | 651,912 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_07_TYPE02_BPMtrace.mat` | 1,190 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_08_TYPE02.mat` | 674,257 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_08_TYPE02_BPMtrace.mat` | 1,196 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_09_TYPE02.mat` | 667,175 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_09_TYPE02_BPMtrace.mat` | 1,142 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_10_TYPE02.mat` | 683,027 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_10_TYPE02_BPMtrace.mat` | 1,082 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_11_TYPE02.mat` | 668,737 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_11_TYPE02_BPMtrace.mat` | 1,060 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_12_TYPE02.mat` | 668,021 | scipy.io.loadmat | OK |
| `data/Training_data/DATA_12_TYPE02_BPMtrace.mat` | 1,163 | scipy.io.loadmat | OK |
| `data/Training_data/Readme.docx` | 12,601 | — | NOT_MAT |
| `data/Training_data/Readme.pdf` | 118,950 | — | NOT_MAT |
| `data/nomi_tracce_BPM.txt` | 438 | — | NOT_MAT |
| `data/nomi_tracce_tot.txt` | 330 | — | NOT_MAT |

## 4. MAT structures

Tất cả 44 file có header `MATLAB 5.0 MAT-file` (`matfile_version=(1,0)`), đọc bằng `scipy.io.loadmat`; không cần `h5py`. Mỗi file chỉ có một `numpy.ndarray` kiểu `float64` sau khi bỏ metadata `__header__`, `__version__`, `__globals__`. **Không có MATLAB struct, cell/object array, nested group hoặc biến lồng nhau** trong các file hiện có.

| Group | Files | Variable | Shape pattern | Python type / dtype |
| --- | ---: | --- | --- | --- |
| Training signal | 12 | `sig` | `(6, N)`, N=35,989–40,803 | ndarray / float64 |
| Training label | 12 | `BPM0` | `(L, 1)`, L=140–160 | ndarray / float64 |
| Competition signal | 10 | `sig` | `(5, N)`, N=25,754–40,022 | ndarray / float64 |
| Competition label | 10 | `BPM0` | `(L, 1)`, L=100–157 | ndarray / float64 |

Bảng dưới ghi thống kê **mọi biến thực tế**; mọi phần tử đều hữu hạn nên `finite = elements`, `nonfinite = 0` ở tất cả hàng. CSV [mat_variable_manifest.csv](mat_variable_manifest.csv) lưu chính xác dtype, shape, ndim, số phần tử, NaN/+Inf/-Inf, min/max/mean/std, first/last 10 và thống kê từng hàng `sig`.

| File | Variable | Shape | Finite | Min | Max | Mean | Std |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `TEST_S01_T01.mat` | `sig` | `(5, 36452)` | 182,260 | -555.000 | 551.000 | 0.352 | 35.502 |
| `TEST_S02_T01.mat` | `sig` | `(5, 35212)` | 176,060 | -233.500 | 386.500 | 0.114 | 19.291 |
| `TEST_S02_T02.mat` | `sig` | `(5, 36859)` | 184,295 | -1024.000 | 946.500 | -0.246 | 39.307 |
| `TEST_S03_T02.mat` | `sig` | `(5, 38752)` | 193,760 | -382.000 | 453.500 | 0.583 | 19.722 |
| `TEST_S04_T02.mat` | `sig` | `(5, 26000)` | 130,000 | -176.500 | 222.000 | 0.817 | 22.491 |
| `TEST_S05_T02.mat` | `sig` | `(5, 40022)` | 200,110 | -1024.000 | 939.500 | 0.569 | 47.918 |
| `TEST_S06_T01.mat` | `sig` | `(5, 33832)` | 169,160 | -185.000 | 256.000 | 0.394 | 23.296 |
| `TEST_S06_T02.mat` | `sig` | `(5, 36425)` | 182,125 | -1024.000 | 943.500 | 0.351 | 61.467 |
| `TEST_S07_T02.mat` | `sig` | `(5, 31152)` | 155,760 | -200.000 | 254.000 | 0.414 | 27.263 |
| `TEST_S08_T01.mat` | `sig` | `(5, 25754)` | 128,770 | -555.000 | 877.000 | 0.551 | 44.047 |
| `True_S01_T01.mat` | `BPM0` | `(142, 1)` | 142 | 59.055 | 101.925 | 74.731 | 9.997 |
| `True_S02_T01.mat` | `BPM0` | `(137, 1)` | 137 | 60.624 | 101.237 | 76.126 | 10.826 |
| `True_S02_T02.mat` | `BPM0` | `(144, 1)` | 144 | 76.923 | 147.668 | 127.693 | 17.822 |
| `True_S03_T02.mat` | `BPM0` | `(152, 1)` | 152 | 107.973 | 172.775 | 156.774 | 14.867 |
| `True_S04_T02.mat` | `BPM0` | `(101, 1)` | 101 | 101.036 | 147.975 | 122.814 | 12.572 |
| `True_S05_T02.mat` | `BPM0` | `(157, 1)` | 157 | 112.179 | 146.004 | 135.317 | 7.326 |
| `True_S06_T01.mat` | `BPM0` | `(132, 1)` | 132 | 64.655 | 117.188 | 90.607 | 14.135 |
| `True_S06_T02.mat` | `BPM0` | `(142, 1)` | 142 | 115.031 | 165.615 | 143.439 | 11.910 |
| `True_S07_T02.mat` | `BPM0` | `(121, 1)` | 121 | 112.903 | 146.756 | 127.340 | 8.529 |
| `True_S08_T01.mat` | `BPM0` | `(100, 1)` | 100 | 79.957 | 92.688 | 85.997 | 3.706 |
| `DATA_01_TYPE01.mat` | `sig` | `(6, 37937)` | 227,622 | -1024.000 | 914.000 | -45.423 | 139.837 |
| `DATA_01_TYPE01_BPMtrace.mat` | `BPM0` | `(148, 1)` | 148 | 69.588 | 165.615 | 133.406 | 30.185 |
| `DATA_02_TYPE02.mat` | `sig` | `(6, 37850)` | 227,100 | -1024.000 | 227.500 | -45.818 | 120.111 |
| `DATA_02_TYPE02_BPMtrace.mat` | `BPM0` | `(148, 1)` | 148 | 69.516 | 148.592 | 120.967 | 21.551 |
| `DATA_03_TYPE02.mat` | `sig` | `(6, 35989)` | 215,934 | -1024.000 | 596.500 | -45.866 | 127.902 |
| `DATA_03_TYPE02_BPMtrace.mat` | `BPM0` | `(140, 1)` | 140 | 83.705 | 160.428 | 131.283 | 21.209 |
| `DATA_04_TYPE02.mat` | `sig` | `(6, 37250)` | 223,500 | -613.000 | 1008.500 | -45.484 | 122.154 |
| `DATA_04_TYPE02_BPMtrace.mat` | `BPM0` | `(146, 1)` | 146 | 78.947 | 164.062 | 133.026 | 23.146 |
| `DATA_05_TYPE02.mat` | `sig` | `(6, 37328)` | 223,968 | -726.500 | 1007.500 | -45.474 | 125.523 |
| `DATA_05_TYPE02_BPMtrace.mat` | `BPM0` | `(146, 1)` | 146 | 101.237 | 166.843 | 141.931 | 19.088 |
| `DATA_06_TYPE02.mat` | `sig` | `(6, 38373)` | 230,238 | -1024.000 | 476.000 | -42.465 | 153.890 |
| `DATA_06_TYPE02_BPMtrace.mat` | `BPM0` | `(150, 1)` | 150 | 68.728 | 153.061 | 131.500 | 24.456 |
| `DATA_07_TYPE02.mat` | `sig` | `(6, 36650)` | 219,900 | -1024.000 | 458.000 | -42.264 | 154.216 |
| `DATA_07_TYPE02_BPMtrace.mat` | `BPM0` | `(143, 1)` | 143 | 92.119 | 157.563 | 134.614 | 20.194 |
| `DATA_08_TYPE02.mat` | `sig` | `(6, 40803)` | 244,818 | -970.500 | 312.000 | -45.440 | 120.225 |
| `DATA_08_TYPE02_BPMtrace.mat` | `BPM0` | `(160, 1)` | 160 | 74.534 | 150.794 | 125.125 | 19.326 |
| `DATA_09_TYPE02.mat` | `sig` | `(6, 38121)` | 228,726 | -834.500 | 385.000 | -45.247 | 129.245 |
| `DATA_09_TYPE02_BPMtrace.mat` | `BPM0` | `(149, 1)` | 149 | 74.257 | 151.274 | 126.071 | 22.616 |
| `DATA_10_TYPE02.mat` | `sig` | `(6, 38042)` | 228,252 | -1024.000 | 1013.000 | -45.548 | 149.276 |
| `DATA_10_TYPE02_BPMtrace.mat` | `BPM0` | `(149, 1)` | 149 | 121.359 | 176.742 | 160.505 | 14.512 |
| `DATA_11_TYPE02.mat` | `sig` | `(6, 36500)` | 219,000 | -1024.000 | 1014.000 | -46.777 | 181.103 |
| `DATA_11_TYPE02_BPMtrace.mat` | `BPM0` | `(143, 1)` | 143 | 110.063 | 170.639 | 152.492 | 18.099 |
| `DATA_12_TYPE02.mat` | `sig` | `(6, 37316)` | 223,896 | -1024.000 | 711.000 | -46.227 | 149.144 |
| `DATA_12_TYPE02_BPMtrace.mat` | `BPM0` | `(146, 1)` | 146 | 96.831 | 170.279 | 141.662 | 21.882 |

## 5. Cross-file schema

Có hai schema tín hiệu theo split: 6 hàng ở Training, 5 hàng ở Competition. Mọi cặp signal–label tìm thấy theo tên file. `N / 125` và số cửa sổ kỳ vọng bên dưới **chỉ là suy ra nếu lấy Fs=125 Hz, window=8 s, shift=2 s từ mô tả paper trong yêu cầu**; chúng không chứng minh Fs hay cách tạo nhãn. `Delta = observed BPM0 length − expected windows`.

| Signal file | Candidate subject / trial từ tên | `sig` shape | `BPM0` shape | Duration candidate (s) | Expected windows | Delta |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `TEST_S01_T01.mat` | Competition `S01` / `T01` | `(5, 36452)` | `(142, 1)` | 291.616 | 142 | +0 |
| `TEST_S02_T01.mat` | Competition `S02` / `T01` | `(5, 35212)` | `(137, 1)` | 281.696 | 137 | +0 |
| `TEST_S02_T02.mat` | Competition `S02` / `T02` | `(5, 36859)` | `(144, 1)` | 294.872 | 144 | +0 |
| `TEST_S03_T02.mat` | Competition `S03` / `T02` | `(5, 38752)` | `(152, 1)` | 310.016 | 152 | +0 |
| `TEST_S04_T02.mat` | Competition `S04` / `T02` | `(5, 26000)` | `(101, 1)` | 208.000 | 101 | +0 |
| `TEST_S05_T02.mat` | Competition `S05` / `T02` | `(5, 40022)` | `(157, 1)` | 320.176 | 157 | +0 |
| `TEST_S06_T01.mat` | Competition `S06` / `T01` | `(5, 33832)` | `(132, 1)` | 270.656 | 132 | +0 |
| `TEST_S06_T02.mat` | Competition `S06` / `T02` | `(5, 36425)` | `(142, 1)` | 291.400 | 142 | +0 |
| `TEST_S07_T02.mat` | Competition `S07` / `T02` | `(5, 31152)` | `(121, 1)` | 249.216 | 121 | +0 |
| `TEST_S08_T01.mat` | Competition `S08` / `T01` | `(5, 25754)` | `(100, 1)` | 206.032 | 100 | +0 |
| `DATA_01_TYPE01.mat` | Training `01` / `TYPE01` | `(6, 37937)` | `(148, 1)` | 303.496 | 148 | +0 |
| `DATA_02_TYPE02.mat` | Training `02` / `TYPE02` | `(6, 37850)` | `(148, 1)` | 302.800 | 148 | +0 |
| `DATA_03_TYPE02.mat` | Training `03` / `TYPE02` | `(6, 35989)` | `(140, 1)` | 287.912 | 140 | +0 |
| `DATA_04_TYPE02.mat` | Training `04` / `TYPE02` | `(6, 37250)` | `(146, 1)` | 298.000 | 146 | +0 |
| `DATA_05_TYPE02.mat` | Training `05` / `TYPE02` | `(6, 37328)` | `(146, 1)` | 298.624 | 146 | +0 |
| `DATA_06_TYPE02.mat` | Training `06` / `TYPE02` | `(6, 38373)` | `(150, 1)` | 306.984 | 150 | +0 |
| `DATA_07_TYPE02.mat` | Training `07` / `TYPE02` | `(6, 36650)` | `(143, 1)` | 293.200 | 143 | +0 |
| `DATA_08_TYPE02.mat` | Training `08` / `TYPE02` | `(6, 40803)` | `(160, 1)` | 326.424 | 160 | +0 |
| `DATA_09_TYPE02.mat` | Training `09` / `TYPE02` | `(6, 38121)` | `(149, 1)` | 304.968 | 149 | +0 |
| `DATA_10_TYPE02.mat` | Training `10` / `TYPE02` | `(6, 38042)` | `(149, 1)` | 304.336 | 149 | +0 |
| `DATA_11_TYPE02.mat` | Training `11` / `TYPE02` | `(6, 36500)` | `(143, 1)` | 292.000 | 143 | +0 |
| `DATA_12_TYPE02.mat` | Training `12` / `TYPE02` | `(6, 37316)` | `(146, 1)` | 298.528 | 146 | +0 |

22/22 cặp có `Delta=0`. Đây là kiểm tra tính nhất quán của giả thuyết, **không phải bằng chứng độc lập** cho Fs/window/shift. Training có mã `01`–`12`, 12 trial; Competition có mã `S01`–`S08`, 10 trial (S02 và S06 có hai trial). Mã subject/trial được trích trực tiếp từ filename: **HIGH** cho cách đọc tên file, nhưng danh tính người tham gia và quan hệ giữa hai split **UNKNOWN** vì không có biến metadata.

Orientation recommendation: vì `sig` có 5/6 hàng nhưng 25,754–40,803 cột, mỗi hàng là một chuỗi dài với dải giá trị nhất quán, dạng **channels × samples** là cách đọc hợp lý (**MEDIUM**). Thời lượng suy ra với 125 Hz củng cố cách đọc này nhưng không chứng minh sampling rate. Không transpose hay lưu lại ma trận. `BPM0` được quan sát là vector cột `(L, 1)`.

Bảng nhận diện mã subject/trial theo **tên gốc**; HIGH chỉ là độ tin cậy của việc đọc chuỗi filename, không xác nhận danh tính người tham gia. File nhãn tương ứng dùng cùng mã theo quy tắc `DATA_*_BPMtrace` hoặc `True_*`.

| Raw signal filename | Candidate subject | Trial | Confidence | Evidence |
| --- | --- | --- | --- | --- |
| `TEST_S01_T01.mat` | `S01` | `T01` | HIGH (mã tên file) | `TEST_S01_T01` trong filename |
| `TEST_S02_T01.mat` | `S02` | `T01` | HIGH (mã tên file) | `TEST_S02_T01` trong filename |
| `TEST_S02_T02.mat` | `S02` | `T02` | HIGH (mã tên file) | `TEST_S02_T02` trong filename |
| `TEST_S03_T02.mat` | `S03` | `T02` | HIGH (mã tên file) | `TEST_S03_T02` trong filename |
| `TEST_S04_T02.mat` | `S04` | `T02` | HIGH (mã tên file) | `TEST_S04_T02` trong filename |
| `TEST_S05_T02.mat` | `S05` | `T02` | HIGH (mã tên file) | `TEST_S05_T02` trong filename |
| `TEST_S06_T01.mat` | `S06` | `T01` | HIGH (mã tên file) | `TEST_S06_T01` trong filename |
| `TEST_S06_T02.mat` | `S06` | `T02` | HIGH (mã tên file) | `TEST_S06_T02` trong filename |
| `TEST_S07_T02.mat` | `S07` | `T02` | HIGH (mã tên file) | `TEST_S07_T02` trong filename |
| `TEST_S08_T01.mat` | `S08` | `T01` | HIGH (mã tên file) | `TEST_S08_T01` trong filename |
| `DATA_01_TYPE01.mat` | `01` | `TYPE01` | HIGH (mã tên file) | `DATA_01_TYPE01` trong filename |
| `DATA_02_TYPE02.mat` | `02` | `TYPE02` | HIGH (mã tên file) | `DATA_02_TYPE02` trong filename |
| `DATA_03_TYPE02.mat` | `03` | `TYPE02` | HIGH (mã tên file) | `DATA_03_TYPE02` trong filename |
| `DATA_04_TYPE02.mat` | `04` | `TYPE02` | HIGH (mã tên file) | `DATA_04_TYPE02` trong filename |
| `DATA_05_TYPE02.mat` | `05` | `TYPE02` | HIGH (mã tên file) | `DATA_05_TYPE02` trong filename |
| `DATA_06_TYPE02.mat` | `06` | `TYPE02` | HIGH (mã tên file) | `DATA_06_TYPE02` trong filename |
| `DATA_07_TYPE02.mat` | `07` | `TYPE02` | HIGH (mã tên file) | `DATA_07_TYPE02` trong filename |
| `DATA_08_TYPE02.mat` | `08` | `TYPE02` | HIGH (mã tên file) | `DATA_08_TYPE02` trong filename |
| `DATA_09_TYPE02.mat` | `09` | `TYPE02` | HIGH (mã tên file) | `DATA_09_TYPE02` trong filename |
| `DATA_10_TYPE02.mat` | `10` | `TYPE02` | HIGH (mã tên file) | `DATA_10_TYPE02` trong filename |
| `DATA_11_TYPE02.mat` | `11` | `TYPE02` | HIGH (mã tên file) | `DATA_11_TYPE02` trong filename |
| `DATA_12_TYPE02.mat` | `12` | `TYPE02` | HIGH (mã tên file) | `DATA_12_TYPE02` trong filename |

Ngoại lệ về thời lượng theo giả thuyết 125 Hz: `TEST_S04_T02.mat` 208.000 s và `TEST_S08_T01.mat` 206.032 s, ngắn hơn đáng kể so với mô tả “khoảng 5 phút”; `TEST_S07_T02.mat` là 249.216 s. Không đánh dấu các file này là hỏng.

## 6. Candidate signal mapping

Chỉ dựa vào tên biến, shape, dải giá trị và sự nhất quán giữa file. Các số hàng dùng chỉ số **1-based** như khi đọc ma trận; không dùng `BPM0` để thử hoặc tối ưu mapping.

| Candidate | Variable/row | Evidence | Confidence |
| --- | --- | --- | --- |
| PPG1/PPG2, Training | Hai hàng nào đó trong `sig` rows 1–3 | Ba hàng này có biên độ cỡ hàng trăm và giá trị lượng tử kiểu nửa đơn vị; 3 hàng còn lại có dải cỡ ±4. Không có nhãn từng hàng. | LOW |
| PPG1/PPG2, Competition | `sig` rows 1–2 là ứng viên cặp kênh | Ma trận 5 hàng; hai hàng đầu có dải cỡ hàng trăm, ba hàng cuối cỡ ±4. Thứ tự PPG1/PPG2 chưa biết. | MEDIUM |
| ACC-X/Y/Z, Training | `sig` rows 4–6 là ứng viên bộ ba | Dải gộp −3.502 đến 3.986, khác rõ rows 1–3 và nhất quán 12 file. Trục X/Y/Z chưa được gắn nhãn. | MEDIUM |
| ACC-X/Y/Z, Competition | `sig` rows 3–5 là ứng viên bộ ba | Dải gộp −3.994 đến 3.986, nhất quán 10 file. Trục X/Y/Z chưa được gắn nhãn. | MEDIUM |
| ECG, Training | Một hàng trong `sig` rows 1–3 có thể là kênh khác PPG | Training có thêm một hàng so với Competition; chỉ shape/dải giá trị không đủ chứng minh đó là ECG hay xác định hàng. | LOW |
| Ground-truth HR/BPM | `BPM0` trong các file `*_BPMtrace.mat` và `True_*.mat` | Tên biến/tên file, giá trị 59.055–176.742 và 22/22 độ dài khớp công thức cửa sổ giả định. | HIGH |
| Subject metadata | Không có biến riêng; chỉ có filename | Có mã `DATA_XX`, `SXX_TYY`; chưa xác minh danh tính. | UNKNOWN |

## 7. Ground-truth inspection

22 file ứng viên nhãn đều chứa `BPM0` dạng vector cột `float64`, dài 100–160 phần tử; mọi giá trị hữu hạn, không NaN/Inf. Dải chung 59.055–176.742 BPM. Bảng sau có min/max/mean và 10 giá trị đầu/cuối **làm tròn 3 chữ số**; CSV manifest giữ số gốc với độ chính xác của `float64`.

| Label file | Shape | Min | Max | Mean | First 10 | Last 10 |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `True_S01_T01.mat` | `(142, 1)` | 59.055 | 101.925 | 74.731 | 62.696, 60.206, 59.055, 59.389, 59.659, 59.389, 59.863, 60.554, 62.574, 67.797 | 101.925, 100.000, 96.266, 93.458, 91.931, 92.975, 94.439, 95.819, 94.394, 90.361 |
| `True_S02_T01.mat` | `(137, 1)` | 60.624 | 101.237 | 76.126 | 70.239, 69.686, 69.686, 68.493, 66.288, 65.217, 64.655, 63.898, 64.725, 64.417 | 77.240, 76.444, 76.609, 75.928, 75.843, 75.928, 75.588, 76.185, 76.444, 76.271 |
| `True_S02_T02.mat` | `(144, 1)` | 76.923 | 147.668 | 127.693 | 76.923, 77.765, 79.693, 82.057, 82.873, 84.356, 85.670, 86.605, 87.209, 85.616 | 139.040, 137.195, 134.636, 132.743, 130.502, 127.932, 125.654, 123.330, 120.321, 118.644 |
| `True_S03_T02.mat` | `(152, 1)` | 107.973 | 172.775 | 156.774 | 110.544, 109.551, 110.063, 110.169, 109.375, 108.583, 107.973, 111.465, 117.925, 123.220 | 172.414, 171.518, 170.824, 170.455, 170.279, 169.903, 169.579, 169.057, 168.919, 168.630 |
| `True_S04_T02.mat` | `(101, 1)` | 101.036 | 147.975 | 122.814 | 101.036, 101.580, 101.987, 102.389, 109.428, 113.391, 116.796, 119.427, 122.449, 124.481 | 113.759, 111.702, 110.643, 110.294, 107.497, 106.441, 105.178, 105.386, 105.978, 105.634 |
| `True_S05_T02.mat` | `(157, 1)` | 112.179 | 146.004 | 135.317 | 112.179, 115.639, 118.922, 122.574, 124.352, 125.261, 125.523, 124.861, 124.861, 125.261 | 144.385, 144.695, 144.817, 144.670, 144.231, 142.706, 140.919, 139.650, 139.032, 139.463 |
| `True_S06_T01.mat` | `(132, 1)` | 64.655 | 117.188 | 90.607 | 72.816, 73.350, 73.171, 70.021, 67.873, 67.114, 64.655, 64.655, 66.225, 66.815 | 109.948, 111.940, 112.847, 112.299, 111.940, 112.661, 114.379, 116.339, 117.188, 116.796 |
| `True_S06_T02.mat` | `(142, 1)` | 115.031 | 165.615 | 143.439 | 115.031, 119.554, 123.626, 125.558, 126.263, 125.523, 124.352, 123.077, 121.581, 120.064 | 164.749, 165.615, 165.441, 164.577, 163.892, 163.551, 163.892, 164.577, 164.921, 165.268 |
| `True_S07_T02.mat` | `(121, 1)` | 112.903 | 146.756 | 127.340 | 129.705, 127.389, 128.894, 130.635, 133.185, 135.638, 137.195, 137.689, 136.778, 135.350 | 135.678, 135.638, 135.815, 135.638, 134.831, 133.648, 132.890, 132.674, 133.185, 133.648 |
| `True_S08_T01.mat` | `(100, 1)` | 79.957 | 92.688 | 85.997 | 86.934, 88.997, 90.263, 90.759, 90.959, 91.060, 91.261, 91.667, 91.769, 91.463 | 87.311, 86.505, 84.555, 82.508, 81.522, 81.967, 82.317, 83.241, 83.927, 85.052 |
| `DATA_01_TYPE01_BPMtrace.mat` | `(148, 1)` | 69.588 | 165.615 | 133.406 | 74.339, 76.357, 77.143, 74.668, 72.581, 71.685, 72.894, 73.449, 75.335, 76.844 | 163.892, 163.043, 161.871, 160.772, 159.067, 157.398, 156.413, 155.602, 154.959, 154.221 |
| `DATA_02_TYPE02_BPMtrace.mat` | `(148, 1)` | 69.516 | 148.592 | 120.967 | 84.746, 89.771, 92.593, 88.997, 84.364, 81.257, 76.099, 72.904, 72.115, 70.922 | 147.363, 146.004, 144.540, 143.464, 142.405, 141.509, 140.333, 138.462, 136.803, 135.207 |
| `DATA_03_TYPE02_BPMtrace.mat` | `(140, 1)` | 83.705 | 160.428 | 131.283 | 104.055, 104.278, 102.041, 98.253, 94.286, 94.340, 95.643, 96.257, 95.238, 91.769 | 159.736, 160.085, 160.428, 160.387, 159.744, 158.898, 157.729, 157.068, 156.904, 156.576 |
| `DATA_04_TYPE02_BPMtrace.mat` | `(146, 1)` | 78.947 | 164.062 | 133.026 | 82.873, 82.508, 82.965, 85.812, 87.209, 87.766, 84.876, 82.237, 79.872, 80.214 | 154.321, 151.596, 149.842, 148.129, 146.907, 145.317, 145.474, 145.631, 145.788, 146.154 |
| `DATA_05_TYPE02_BPMtrace.mat` | `(146, 1)` | 101.237 | 166.843 | 141.931 | 109.718, 109.797, 111.583, 111.583, 108.817, 106.599, 103.723, 104.614, 107.803, 109.674 | 164.577, 163.551, 162.539, 161.290, 160.061, 158.730, 158.158, 157.895, 157.563, 157.398 |
| `DATA_06_TYPE02_BPMtrace.mat` | `(150, 1)` | 68.728 | 153.061 | 131.500 | 68.728, 69.803, 69.767, 69.284, 69.444, 70.755, 73.052, 73.690, 74.834, 75.167 | 152.284, 152.594, 152.733, 152.733, 152.570, 152.570, 152.733, 152.733, 153.061, 153.061 |
| `DATA_07_TYPE02_BPMtrace.mat` | `(143, 1)` | 92.119 | 157.563 | 134.614 | 97.720, 96.567, 94.828, 95.597, 96.051, 95.949, 95.745, 94.178, 93.964, 94.142 | 157.398, 157.563, 157.068, 156.413, 155.568, 154.639, 154.004, 153.061, 152.284, 151.757 |
| `DATA_08_TYPE02_BPMtrace.mat` | `(160, 1)` | 74.534 | 150.794 | 125.125 | 74.534, 75.928, 77.801, 80.906, 82.599, 85.324, 86.207, 85.911, 83.756, 80.645 | 119.174, 117.188, 115.132, 112.661, 110.670, 109.261, 107.803, 108.093, 108.025, 107.497 |
| `DATA_09_TYPE02_BPMtrace.mat` | `(149, 1)` | 74.257 | 151.274 | 126.071 | 86.505, 85.421, 83.149, 80.453, 77.231, 76.358, 74.257, 75.605, 77.320, 79.787 | 150.158, 149.215, 148.129, 146.421, 144.231, 142.105, 140.573, 139.607, 138.587, 136.656 |
| `DATA_10_TYPE02_BPMtrace.mat` | `(149, 1)` | 121.359 | 176.742 | 160.505 | 123.491, 127.932, 130.293, 131.715, 132.261, 132.450, 131.443, 129.590, 128.342, 125.918 | 176.094, 175.159, 173.867, 172.594, 170.984, 170.454, 169.720, 169.405, 168.712, 168.090 |
| `DATA_11_TYPE02_BPMtrace.mat` | `(143, 1)` | 110.063 | 170.639 | 152.492 | 115.385, 116.796, 117.450, 117.188, 116.796, 115.622, 114.329, 113.147, 111.702, 110.994 | 170.270, 170.454, 169.753, 169.643, 170.103, 169.928, 169.355, 168.024, 166.139, 164.956 |
| `DATA_12_TYPE02_BPMtrace.mat` | `(146, 1)` | 96.831 | 170.279 | 141.662 | 97.933, 99.119, 99.558, 100.223, 98.584, 96.831, 97.720, 99.186, 102.623, 104.278 | 167.343, 165.790, 163.721, 162.539, 160.428, 159.067, 157.398, 156.250, 155.440, 154.004 |

## 8. Paper-expected vs dataset-observed

| Property | Paper expected (theo yêu cầu, chưa audit) | Dataset observed | Status |
| --- | --- | --- | --- |
| Subjects | Không có số lượng cụ thể trong yêu cầu Stage 1A | 12 mã Training; 8 mã Competition với 10 trial; không có metadata danh tính | NOT VERIFIED |
| PPG channels | PPG1 + PPG2 | `sig` không đặt tên hàng; ứng viên như §6 | AMBIGUOUS |
| ACC channels | ACC-X/Y/Z | Bộ ba hàng biên độ nhỏ là ứng viên; không có tên trục | AMBIGUOUS |
| Sampling rate | 125 Hz | Không có biến Fs/time; chỉ có số mẫu | NOT ENCODED / NOT VERIFIED |
| Recording duration | Khoảng 5 phút | Nếu Fs=125 Hz: 206.032–326.424 s; có trial ngắn hơn | INFERRED ONLY |
| HR labels | HR ground truth theo window | 22 vector `BPM0`, ghép tên được với 22 `sig` | CANDIDATE FOUND |
| Window | 8 s | Không có metadata window; 22/22 chiều dài nhãn khớp công thức giả định | NOT ENCODED / NOT VERIFIED |
| Shift / overlap | shift 2 s / overlap 6 s | Không có metadata shift/overlap; chiều dài nhãn khớp công thức giả định | NOT ENCODED / NOT VERIFIED |

## 9. Data-quality checks

- 44/44 biến số không rỗng, không NaN, không +Inf/−Inf; không biến hoặc hàng `sig` nào toàn zero hay constant. Chi tiết từng hàng ở CSV manifest.
- Dải toàn cục `sig`: −1024.000 đến 1014.000; `BPM0`: 59.055 đến 176.742. Không có đơn vị/range hợp lệ được mã hóa trong MAT, nên không thể kết luận giá trị nào là sai chỉ từ biên độ.
- Giá trị biên `−1024` lặp lại trong một số hàng waveform; đây là **ứng viên bão hòa/giới hạn lượng tử**, chưa xác nhận nguyên nhân. Không chỉnh sửa dữ liệu:

| File | `sig` row (1-based) | Count of −1024 | Fraction of row |
| --- | ---: | ---: | ---: |
| `TEST_S02_T02.mat` | 2 | 13 | 0.04% |
| `TEST_S05_T02.mat` | 2 | 11 | 0.03% |
| `TEST_S06_T02.mat` | 2 | 14 | 0.04% |
| `DATA_01_TYPE01.mat` | 1 | 1 | 0.00% |
| `DATA_02_TYPE02.mat` | 1 | 4 | 0.01% |
| `DATA_03_TYPE02.mat` | 1 | 10 | 0.03% |
| `DATA_06_TYPE02.mat` | 1 | 1,599 | 4.17% |
| `DATA_07_TYPE02.mat` | 1 | 1,598 | 4.36% |
| `DATA_10_TYPE02.mat` | 1 | 180 | 0.47% |
| `DATA_11_TYPE02.mat` | 1 | 477 | 1.31% |
| `DATA_12_TYPE02.mat` | 1 | 28 | 0.08% |

## 10. Ambiguities

- Thứ tự PPG1/PPG2/ECG (nếu có) trong `sig` chưa được xác minh; nhãn trục ACC cũng chưa có.
- Không có sampling rate, timestamp, đơn vị đo, calibration hoặc protocol window trong các biến MAT.
- `BPM0` là ứng viên ground truth mạnh từ tên và giá trị, nhưng cách tính/đồng bộ chính xác chưa được xác minh.
- `DATA_XX`, `SXX_TYY`, `TYPE01/02` cho mã file/trial; quan hệ danh tính giữa Training và Competition chưa được xác minh.
- Sự lặp lại của −1024 và các trial ngắn là quan sát; nguyên nhân và tính hợp lệ cần tài liệu nguồn.

## 11. Questions requiring external documentation

- TROIKA paper, IEEE SPC documentation và README đi kèm: `sig` row nào là PPG1, PPG2, ACC-X/Y/Z, ECG? Có khác biệt giữa Training và Competition không?
- Sampling rate, đơn vị và thứ tự trục được công bố chính thức là gì? `−1024` có là giới hạn ADC/sensor không?
- `BPM0` được tạo từ ECG như thế nào, window đặt mốc thời gian ở đâu, và alignment với `sig` ra sao?
- `TYPE01/02` và `SXX_TYY` có ý nghĩa gì; các mã subject giữa hai split có trùng người không?
- CPC paper quy định chính xác tập subject/trial và cách dùng Training/Competition nào?

## 12. Recommended next step

Đối chiếu README dataset, tài liệu TROIKA/IEEE và paper CPC để xác nhận mapping kênh, Fs, nhãn và protocol; ghi nguồn cho từng kết luận. **Chưa thực hiện bước đó ở Stage 1A.**

## 13. Final status

44/44 MAT đọc được; hai schema tín hiệu, nhãn và các ngoại lệ đã được ghi nhận. SHA256 của 44 MAT sau khi đọc trùng baseline trước khi đọc; không thêm file nào vào `data/`.

**DATASET INSPECTION STATUS: PASS**
