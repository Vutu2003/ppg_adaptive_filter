# Mục 3.2 — Hiểu kiến trúc CPC từ ANC, LMS và RLS

**Nguồn:** Islam và cộng sự, *Healthcare Technology Letters* (2018), mục 3.2, Hình 2–5, công thức (1)–(2); tham số đối chiếu mục 4.1. [Mở paper](<../../Healthcare Tech Letters - 2018 - Islam - Cascade and parallel combination  CPC  of adaptive filters for estimating heart.pdf>).

**Ý tưởng:** mỗi nhánh khử nhiễu lần lượt theo ba trục gia tốc; hai nhánh dùng LMS/RLS rồi phối hợp đầu ra để làm rõ thành phần nhịp tim.

## 1. Vì sao cần tham chiếu gia tốc?

Đỉnh nhiễu chuyển động có thể mạnh hơn và nằm sát đỉnh nhịp tim trong phổ PPG. Mục 3.2 dùng mô hình đơn giản:

$$
\boxed{m[n]=a_xm_x[n]+a_ym_y[n]+a_zm_z[n]}\tag{1}
$$

- $m[n]$: nhiễu chuyển động trong PPG; $m_x[n],m_y[n],m_z[n]$: ba tín hiệu gia tốc.
- $a_x,a_y,a_z$: hệ số biểu diễn mức đóng góp của chuyển động từng hướng.

Mô hình này giải thích vì sao ACC cung cấp thông tin về nhiễu. Tác giả chọn **xử lý riêng từng trục, nối tiếp các tầng ANC**, nhằm hạn chế làm suy giảm đỉnh tim khi khử nhiễu gần nó.

## 2. Một tầng ANC làm gì?

![Một tầng ANC theo ký hiệu paper: gia tốc qua F_i tạo nhiễu ước lượng; phép trừ tạo y_i1 và hồi tiếp để cập nhật hệ số](images/paper/01-anc-core.svg)

*Minh họa tầng đầu của nhánh $i$. $d[n]$ là PPG đã tiền xử lý; $F_i$ là loại bộ lọc thích nghi. Ký hiệu $\widehat m_{i1}[n]$ được thêm để chỉ nhiễu ước lượng.*

Một tầng thực hiện hai việc:

1. **Lọc ACC:** tạo ước lượng phần nhiễu liên quan đến tham chiếu.
2. **Trừ khỏi đầu vào chính:** giữ lại tín hiệu đưa sang tầng kế tiếp; dùng chính phần còn lại để cập nhật bộ lọc.

Với ký hiệu nền tảng bổ trợ:

$$
\widehat m[n]=\mathbf w^T[n]\mathbf u[n],
\qquad e[n]=\text{đầu vào chính}-\widehat m[n].
$$

$\mathbf u[n]$ gồm các mẫu ACC hiện tại và quá khứ; $\mathbf w[n]$ là các hệ số FIR; $T$ là chuyển vị. Số phần tử của hai véc-tơ bằng nhau.

**Điểm dễ nhầm:** đầu ra ANC thường gọi là $e[n]$, nhưng Hình 3 gọi chúng là **$y_{i1}[n],y_{i2}[n],y_i[n]$**. Đây là PPG còn lại sau phép trừ, còn nhiễu ước lượng nằm ở đầu ra của khối $F_i$ trước phép trừ.

ANC cần tham chiếu liên quan đến nhiễu và ít liên quan đến thành phần tim cần giữ. Vì vậy, giảm năng lượng đầu ra chỉ hữu ích khi vẫn bảo toàn thông tin nhịp tim.

## 3. LMS và RLS nằm ở đâu trong ANC?

Chúng là **hai cách cập nhật hệ số của $F_i$**; cùng dùng phép lọc và phép trừ ở trên.

| Core | Cách điều chỉnh hệ số | Vai trò trong CPC |
|---|---|---|
| LMS | Theo gradient từ sai số tức thời | Ba tầng của nhánh $F_1$ |
| RLS | Bình phương tối thiểu có trọng số, cập nhật đệ quy | Ba tầng của nhánh $F_2$ |

**LMS:**

$$
\mathbf w[n+1]=\mathbf w[n]+\mu e[n]\mathbf u[n].
$$

$\mu$ là bước cập nhật: quyết định mức thay đổi hệ số từ sai số hiện tại.

**RLS chuẩn có hệ số quên:**

$$
\begin{aligned}
\mathbf k[n]&=\frac{\mathbf P[n]\mathbf u[n]}
{f+\mathbf u^T[n]\mathbf P[n]\mathbf u[n]},\\
\mathbf w[n+1]&=\mathbf w[n]+\mathbf k[n]e[n],\\
\mathbf P[n+1]&=\frac{\mathbf P[n]-\mathbf k[n]\mathbf u^T[n]\mathbf P[n]}{f}.
\end{aligned}
$$

$f$ giảm trọng số của dữ liệu cũ; $\mathbf P$ là nghịch đảo ma trận tương quan đầu vào có trọng số; $\mathbf k$ là véc-tơ điều chỉnh hệ số. **Mỗi tầng có hệ số và trạng thái riêng.**

*Các công thức core và ký hiệu $\mathbf u,\mathbf w,e,\mu,f,\mathbf P,\mathbf k,\widehat m$ là phần giải thích bổ trợ; mục 3.2 không viết các phương trình cập nhật này.*

## 4. Cascade: ba tầng khử nhiễu nối tiếp

![Hình 3 nguyên bản trích trực tiếp từ PDF của paper: hai chuỗi ANC, các phép trừ và hồi tiếp, khối trễ trên tham chiếu Y/Z, lớp phối hợp lambda](images/paper/02-paper-original-fig3.jpg)

*Hình 3 nguyên bản, trang 20; ảnh được trích trực tiếp từ PDF, giữ nguyên ký hiệu và đường nối. Mỗi tầng ANC gồm $F_i$, phép trừ và nhánh cập nhật. Trong cấu hình thí nghiệm, nhánh trên dùng LMS, nhánh dưới dùng RLS.*

Luồng trong **mỗi nhánh $i\in\{1,2\}$**:

| Tầng | Đầu vào chính | Tham chiếu tại bộ lọc theo Hình 3 | Đầu ra sau phép trừ |
|---|---|---|---|
| X | $d[n]$ | $m_x[n]$ | $y_{i1}[n]=d[n]-\widehat m_{i1}[n]$ |
| Y | $y_{i1}[n]$ | $m_y[n-l_i]$ | $y_{i2}[n]=y_{i1}[n]-\widehat m_{i2}[n]$ |
| Z | $y_{i2}[n]$ | $m_z[n-2l_i]$ | $y_i[n]=y_{i2}[n]-\widehat m_{i3}[n]$ |

**Cách đọc:** tầng Y tiếp tục xử lý phần còn lại của tầng X; tầng Z tiếp tục xử lý phần còn lại của tầng Y. Ba tầng cùng học quan hệ giữa ACC và nhiễu trong đầu vào của mình.

Hình 3 đặt $z^{-l_i}$ trước tham chiếu Y và $z^{-2l_i}$ trước tham chiếu Z: đây là các phép trễ $l_i$ và $2l_i$ mẫu. Paper gọi $l_i$ là **order** của bộ lọc; chưa mô tả đầy đủ cách xử lý căn chỉnh và biên mẫu. Vì vậy, cần giữ các khối này khi đọc sơ đồ, tránh tự suy ra quy tắc triển khai từ bậc lọc.

## 5. Parallel: phối hợp hai đầu ra đã khử nhiễu

Hai nhánh nhận **cùng $d[n]$ và ba kênh ACC**, nhưng có cách thích nghi khác nhau. Các đầu ra cuối là $y_1[n]$ và $y_2[n]$:

$$
\boxed{y[n]=\lambda y_1[n]+(1-\lambda)y_2[n]},
\qquad \lambda\in[0,1].\tag{2}
$$

| $\lambda$ | Đóng góp vào $y[n]$ |
|---|---|
| $1$ | Chỉ nhánh 1 |
| $0$ | Chỉ nhánh 2 |
| $0{,}5$ | Hai nhánh có trọng số bằng nhau |

Khi cả hai nhánh cùng giữ thành phần tim, tổng trọng số bằng 1 giữ nguyên phần đó. Các sai lệch khác nhau có thể giảm khi phối hợp. Paper **cộng hai tín hiệu theo thời gian**; không lấy trung bình hai nhịp tim đã ước lượng hay hai phổ công suất.

**Ký hiệu cần phân biệt:** $y_{11},y_{12},y_1$ thuộc nhánh 1; $y_{21},y_{22},y_2$ thuộc nhánh 2; $y$ là đầu ra CPC. $\lambda$ là trọng số phối hợp, độc lập với hệ số quên $f$ trong công thức RLS bổ trợ.

## 6. Tham số paper công bố và giới hạn diễn giải

Mục 4.1 báo cáo cấu hình dùng cho kết quả:

| Nhánh / lớp | Ký hiệu kiến trúc | Giá trị công bố |
|---|---|---|
| LMS | $F_1$, order $l_1$ | Order **27**; “step size” **0.0001** |
| RLS | $F_2$, order $l_2$ | Order **55**; “step size” **0.999** |
| Phối hợp | $\lambda$ | Cố định **0.5** |

Paper gọi cả **0.0001 và 0.999** là “step size”, không đưa quy tắc cập nhật chi tiết. Gắn $\mu=0.0001$ cho LMS và diễn giải $f=0.999$ là hệ số quên RLS là cách liên hệ với core chuẩn; riêng diễn giải RLS cần được ghi rõ. Paper cũng chưa xác định đầy đủ quy ước **order / số hệ số**, khởi tạo $\mathbf P$ và trạng thái giữa các cửa sổ.

**Phần thích nghi nằm trong sáu bộ lọc; $\lambda=0.5$ không được tự cập nhật trong cấu hình công bố.**

## 7. Đọc minh họa hiệu quả trong mục 3.2

![Hình 4 trích từ paper: phổ PPG sau tiền xử lý, sau nhánh LMS, sau nhánh RLS và sau phối hợp với lambda bằng 0.5](images/paper/03-paper-fig4.png)

*Hình 4, trang 21: vòng tròn xanh đánh dấu nhịp tim tham chiếu; hình thoi đỏ đánh dấu đỉnh phổ lớn nhất. Đọc sự trùng vị trí hai dấu; các hàng có thang công suất khác nhau.*

| Phổ | Quan sát trong ví dụ |
|---|---|
| (a) Sau tiền xử lý | Đỉnh nhiễu mạnh hơn đỉnh tim. |
| (b) LMS | Nhiễu giảm nhưng đỉnh nhiễu vẫn trội. |
| (c) RLS | Đỉnh tim chưa tách rõ khỏi đỉnh lân cận. |
| (d) CPC, $\lambda=0.5$ | Đỉnh lớn nhất trùng vị trí nhịp tim tham chiếu. |

Ví dụ cho thấy **phối hợp hai nhánh giúp chọn đúng đỉnh tim trong cửa sổ này**. Đây là minh chứng thực nghiệm; kiến trúc không bảo đảm luôn khử hết nhiễu. Sau khối CPC, $y[n]$ mới được đưa sang ước lượng và theo dõi nhịp tim ở mục 3.3.

## 8. Motivation — Vì sao ba tầng nối tiếp và hai nhánh song song?

**Hai phần giải quyết hai vấn đề khác nhau:** nối tiếp khai thác **ba hướng chuyển động**; song song khai thác **hai cách thích nghi**. Đây là lựa chọn thiết kế của paper, được thực nghiệm hỗ trợ; chưa phải cấu trúc bắt buộc hay tối ưu đã được chứng minh.

### 8.1. Vì sao ba tầng ANC nối tiếp?

- **Ba tầng tương ứng ba trục ACC.** Theo mô hình (1), nhiễu có đóng góp từ $m_x,m_y,m_z$. Chỉ dùng một trục có thể bỏ sót thông tin chuyển động ở các hướng còn lại.
- **Mỗi tầng xử lý phần còn lại.** Tầng X tạo $y_{i1}$; tầng Y học quan hệ giữa tham chiếu Y và phần nhiễu còn trong $y_{i1}$; tầng Z tiếp tục trên $y_{i2}$. Ba tầng có tham chiếu và hệ số riêng.
- **Giữ riêng thông tin từng hướng.** Cộng cố định ba kênh ACC trước khi lọc có thể làm mất thông tin do các thành phần triệt tiêu nhau. Mục 3.2 còn nêu nguy cơ làm suy giảm đỉnh tim khi khử nhiễu có đỉnh gần nó. Tác giả vì vậy chọn khử nhiễu từng hướng theo chuỗi.

**Cách nói chính xác:** “Dùng ba tầng vì có ba tham chiếu theo ba trục; mỗi tầng tiếp tục giảm phần nhiễu liên quan đến tham chiếu của mình.” Mục tiêu không phải lặp cùng một bộ lọc ba lần.

### 8.2. Vì sao thêm hai nhánh LMS/RLS song song?

Một chuỗi ba tầng vẫn phụ thuộc vào thuật toán cập nhật: LMS dùng sai số tức thời, RLS dùng thông tin tương quan và bình phương tối thiểu có trọng số. Vì thế, hai chuỗi có thể còn những sai lệch khác nhau.

**RLS không luôn tốt hơn LMS trong dữ liệu paper:** ở người số 3, AAE của LMS là **0,66**, RLS là **1,03 BPM** (Bảng 1). Đây là cơ sở thực nghiệm để cân nhắc phối hợp thay vì chỉ giữ một thuật toán.

Hai nhánh cùng nhận $d[n]$, tạo $y_1[n],y_2[n]$ để phối hợp theo (2). Khi cả hai giữ được thành phần tim, tổng trọng số bằng 1 giữ nguyên phần chung đó; phần nhiễu còn lại có thể giảm nếu các sai lệch bổ trợ nhau. Hình 4 minh họa trường hợp đầu ra phối hợp làm rõ đỉnh tim hơn từng nhánh riêng.

**Bằng chứng của paper — Bảng 1, trang 22:**

| Cấu hình | AAE trung bình (BPM) |
|---|---:|
| Chỉ chuỗi LMS ba tầng | 13,95 |
| Chỉ chuỗi RLS ba tầng | 2,43 |
| CPC phối hợp hai chuỗi | **1,12** |

Các kết quả này hỗ trợ lợi ích của **phối hợp hai chuỗi đã chọn** trên bộ dữ liệu thử nghiệm; chưa tách riêng lợi ích của số tầng và thứ tự trục.

### 8.3. Nếu giảng viên hỏi sâu hơn

| Câu hỏi | Trả lời có căn cứ |
|---|---|
| Ba tầng và thứ tự X → Y → Z có tối ưu không? | Paper chọn theo ba trục ACC, chưa so sánh đầy đủ số tầng hoặc các thứ tự khác để kết luận tối ưu. |
| Có thể dùng một ANC nhận cả ba trục không? | Có, đó là một kiến trúc khác. Giữ riêng ba tham chiếu không bắt buộc phải mắc nối tiếp; paper chưa chứng minh CPC vượt mọi ANC đa đầu vào. |
| Càng nhiều tầng hoặc nhánh càng tốt? | Cần thực nghiệm kiểm chứng. Thêm bộ lọc tăng chi phí; tham chiếu không phù hợp còn có thể làm suy giảm thành phần tim. |
| Phối hợp luôn tốt hơn từng nhánh? | Hiệu quả phụ thuộc các sai lệch còn lại và $\lambda$; Bảng 1 cho thấy lợi ích trung bình, không bảo đảm cho mọi cửa sổ. |

### 8.4. Câu trả lời ngắn khi bảo vệ

> Ba tầng tương ứng với ba trục gia tốc. Mỗi tầng ANC dùng một trục để ước lượng nhiễu và truyền phần PPG còn lại cho tầng sau. Hai chuỗi LMS và RLS chạy song song vì có cách thích nghi khác nhau; phối hợp đầu ra giúp giảm phụ thuộc vào hạn chế của từng thuật toán. Trong paper, CPC đạt AAE trung bình thấp hơn hai chuỗi riêng. Đây là lựa chọn thiết kế có thực nghiệm hỗ trợ, chưa phải bằng chứng rằng cấu trúc này tối ưu trong mọi trường hợp.
