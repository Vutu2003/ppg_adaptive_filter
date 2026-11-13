# Lecture 01 — Nhập môn DSP nâng cao

**Môn học:** ET6021 — Xử lý tín hiệu số nâng cao
**Mục tiêu:** Ôn nhanh kiến thức nền tảng phục vụ bảo vệ đồ án CPC PPG LMS/RLS.

---

## 1. Hệ thống LTI (Slide 7)

LTI = Linear Time-Invariant — hệ tuyến tính bất biến theo thời gian.

- **Tuyến tính:** Thỏa mãn tính chồng chất và tính đồng nhất.
- **Bất biến theo thời gian:** Dịch đầu vào bao nhiêu thì đầu ra dịch tương ứng bấy nhiêu.
- **Nhân quả:** Đầu ra hiện tại không phụ thuộc đầu vào tương lai.
- **Ổn định BIBO:** Đầu vào bị chặn thì đầu ra cũng bị chặn.

**Phép chập:**

$$
y[n] = (x*h)[n] = \sum_{k=-\infty}^{\infty} x[k]h[n-k]
$$

Trong đó $h[n]$ là đáp ứng xung của hệ thống và $*$ là phép chập.

**Điều kiện quan trọng:**

- Nhân quả: $h[n] = 0$ với mọi $n < 0$.
- Ổn định BIBO: đáp ứng xung phải khả tổng tuyệt đối:

$$
\sum_{n=-\infty}^{\infty} \lvert h[n] \rvert < \infty
$$

> Liên hệ đồ án: LMS/RLS sử dụng cấu trúc FIR, nhưng trọng số thay đổi theo thời gian nên toàn bộ bộ lọc thích nghi nói chung không phải hệ LTI cố định.

## 2. FIR và IIR (Slide 8, 26)

**Phương trình sai phân tổng quát** (đã chuẩn hóa $a_0 = 1$):

$$
y[n] = -\sum_{k=1}^{N} a_k y[n-k] + \sum_{k=0}^{M} b_k x[n-k]
$$

### FIR — Finite Impulse Response

- Đáp ứng xung hữu hạn.
- Cấu trúc thông thường không hồi tiếp đầu ra.
- Dễ triển khai và ổn định BIBO khi các hệ số hữu hạn.

$$
y[n] = \sum_{k=0}^{M} b_k x[n-k]
$$

Trong công thức này, FIR bậc $M$ có $M+1$ hệ số. Trong mã đồ án, `n_taps` là **số hệ số**: LMS dùng 27 và RLS dùng 55 hệ số.

### IIR — Infinite Impulse Response

- Đáp ứng xung vô hạn.
- Thường có nhánh hồi tiếp sử dụng các đầu ra trước.
- Tính ổn định phụ thuộc vào vị trí cực của hàm truyền đạt.

**Liên hệ đồ án:** LMS/RLS sử dụng cấu trúc FIR với các trọng số được cập nhật thích nghi, không phải IIR.

## 3. Biến đổi Z (Slide 10–14)

**Định nghĩa:**

$$
X(z) = \sum_{n=-\infty}^{\infty} x[n]z^{-n}
$$

**Hàm truyền đạt của hệ LTI:**

$$
H(z) = \frac{Y(z)}{X(z)}
= \frac{\displaystyle\sum_{k=0}^{M} b_k z^{-k}}{\displaystyle 1 + \sum_{k=1}^{N} a_k z^{-k}}
$$

Ghi nhớ:

- $z^{-1}$: trễ một mẫu.
- Zero: nghiệm của tử số.
- Pole (cực): nghiệm của mẫu số.
- ROC: miền hội tụ của biến đổi Z.
- Hệ LTI ổn định BIBO khi ROC của $H(z)$ chứa đường tròn đơn vị $|z|=1$.

**Bổ sung:** Hàm truyền đạt $H(z)=Y(z)/X(z)$ được xét với điều kiện đầu bằng không.

## 4. Fourier, DFT và FFT (Slide 17–22)

- **DTFT:** Biểu diễn phổ liên tục theo tần số của tín hiệu rời rạc.
- **DFT:** Biểu diễn một dãy $N$ mẫu bằng $N$ hệ số phổ tại các tần số rời rạc.
- **FFT:** Thuật toán tính DFT hiệu quả hơn, không phải phép biến đổi khác.

**DFT:**

$$
X[k] = \sum_{n=0}^{N-1} x[n]e^{-j\frac{2\pi kn}{N}},
\qquad k=0,1,\ldots,N-1
$$

**IDFT:**

$$
x[n] = \frac{1}{N}\sum_{k=0}^{N-1} X[k]e^{j\frac{2\pi kn}{N}},
\qquad n=0,1,\ldots,N-1
$$

Trong đó $j^2=-1$, $n$ là chỉ số mẫu thời gian và $k$ là chỉ số bin tần số.

Độ phức tạp:

- DFT trực tiếp: $\mathcal{O}(N^2)$.
- FFT: $\mathcal{O}(N\log N)$.

**Đổi chỉ số bin sang tần số:**

$$
f_k = \frac{kF_s}{N}
$$

Ở đây, $F_s$ là tần số lấy mẫu (Hz), $N$ là số điểm DFT/FFT và $k$ bắt đầu từ 0. Với phổ một phía của tín hiệu thực, chỉ giữ các bin từ 0 đến $\lfloor N/2\rfloor$.

**Liên hệ đồ án:**

- $F_s = 125\ \text{Hz}$.
- $N_F = 4096$ điểm FFT; $N_F$ đóng vai trò của $N$ trong công thức đổi bin ở trên.

$$
\begin{aligned}
\operatorname{BPM}(k) &= 60f_k = \frac{60kF_s}{N_F}, \\
\Delta f &= \frac{F_s}{N_F} = \frac{125}{4096}
\approx 0{,}03052\ \text{Hz}, \\
\Delta\operatorname{BPM} &= \frac{60F_s}{N_F}
\approx 1{,}831\ \text{BPM/bin}.
\end{aligned}
$$

**Vì sao dùng 4096 điểm?** Nhịp tim thô được tính từ bin đỉnh phổ nên bị rời rạc theo bước $\Delta\operatorname{BPM}=60F_s/N_F$. Zero-padding từ 1000 lên 4096 điểm giảm bước này từ $7{,}5$ xuống khoảng $1{,}831\ \text{BPM/bin}$, giúp biểu diễn nhịp tim chi tiết hơn và có thể giảm **sai số rời rạc hóa khi quy vị trí đỉnh phổ sang BPM**. Việc này không thêm thông tin đo; tổng sai số vẫn phụ thuộc nhiễu, khả năng phân giải của cửa sổ và việc chọn đúng đỉnh.

## 5. Phân tích phổ theo cửa sổ (Slide 23)

Các bước cơ bản:

1. Chia tín hiệu thành những đoạn hữu hạn.
2. Có thể nhân hàm cửa sổ $w[n]$.
3. Tính FFT trên từng đoạn.
4. Phân tích biên độ/công suất phổ.

**Các khái niệm cần nhớ:**

- Windowing: nhân hàm cửa sổ để kiểm soát rò rỉ phổ.
- Spectral leakage: năng lượng phổ bị trải sang các tần số lân cận.
- Overlap: các đoạn liên tiếp chia sẻ một phần mẫu.
- Zero-padding: thêm số 0 để tăng mật độ lưới FFT, không làm tăng độ phân giải vật lý của dữ liệu gốc.

**Liên hệ đồ án:**

- Cửa sổ: 8 giây = 1000 mẫu.
- Bước dịch: 2 giây = 250 mẫu.
- Chồng lấn: 6 giây = 750 mẫu (75%).
- FFT 4096 điểm dùng zero-padding.
- Cấu hình tái hiện không nhân thêm hàm cửa sổ taper.

## 6. Bộ lọc số và các chỉ tiêu (Slide 24–26)

Hệ thống LTI có đáp ứng tần số:

$$
Y(e^{j\omega}) = H(e^{j\omega})X(e^{j\omega})
$$

Trong đó $\omega$ là tần số góc chuẩn hóa, tính bằng rad/mẫu, với $\omega = 2\pi f/F_s$.

Các chỉ tiêu bộ lọc thực tế:

- Tần số cắt: xác định vùng chuyển giữa dải thông và dải chắn.
- Độ rộng dải chuyển tiếp: khoảng tần số chuyển từ thông sang chắn.
- Độ gợn dải thông: sai lệch biên độ trong dải thông.
- Độ gợn dải chắn: mức đáp ứng còn lại trong dải chắn.
- Chi phí triển khai: tính toán, bộ nhớ và sai số lượng tử hóa.

**Liên hệ đồ án:** Lọc phổ 0,4–3,5 Hz chỉ loại các thành phần ngoài dải; nhiễu chuyển động nằm trong dải vẫn có thể tồn tại.

---

## 7. Ba câu hỏi phản biện phải trả lời được

### Câu 1. Vì sao LMS/RLS sử dụng FIR?

FIR biểu diễn đầu ra bằng tích vô hướng giữa vector mẫu tham chiếu và vector trọng số. LMS/RLS cập nhật trực tiếp các trọng số này để ước lượng thành phần nhiễu liên quan đến ACC. Cấu trúc không có hồi tiếp đầu ra nên đơn giản hơn trong việc kiểm soát tính ổn định của phần lọc.

### Câu 2. Vì sao FFT 4096 điểm khi chỉ có 1000 mẫu?

FFT 4096 điểm giảm bước lưới BPM từ $7{,}5$ xuống khoảng $1{,}831\ \text{BPM/bin}$, nên có thể giảm sai số rời rạc hóa khi ước lượng nhịp tim từ bin đỉnh phổ. Dữ liệu thực vẫn chỉ có 1000 mẫu trong 8 giây; zero-padding không bổ sung thông tin đo hay bảo đảm tổng sai số ước lượng luôn giảm.

### Câu 3. Vì sao lọc thông dải chưa đủ để khử nhiễu PPG?

Vì nhiễu chuyển động có thể nằm trong cùng dải tần số với thành phần nhịp tim. Bộ lọc thông dải không phân biệt được hai thành phần chỉ dựa vào tần số; LMS/RLS khai thác tham chiếu gia tốc để ước lượng phần nhiễu tương quan.

---

## 8. Checklist trước khi chuyển lecture

- [ ] Giải thích được LTI, nhân quả, ổn định và phép chập.
- [ ] Phân biệt FIR và IIR.
- [ ] Hiểu $z^{-1}$ là phép trễ một mẫu.
- [ ] Phân biệt DTFT, DFT và FFT.
- [ ] Hiểu zero-padding, windowing, leakage và overlap.
- [ ] Giải thích được lý do dùng FIR và FFT trong CPC PPG.

**Ưu tiên ôn:** FIR/IIR → DFT/FFT → Windowing → LTI → Biến đổi Z.

**Nguồn:** Lecture 01 — Nhập môn, ET6021, 26 slide.
**Lưu ý:** Các điều kiện ổn định, độ phức tạp FFT và liên hệ CPC là phần giải thích bổ sung trên cơ sở slide và đồ án.
