# 🔥 Pricing Engine — Unit Economics Calculator

## Tổng quan

Công cụ tính giá & phân tích lãi lỗ (P&L) theo **từng mã sản phẩm (SKU)** dành cho ngành Gia dụng — Bếp gas, Bếp từ. Ứng dụng Streamlit với giao diện trực quan, biểu đồ tương tác.

---

## Công thức tính toán

### Tổng chi phí cố định / đơn (Fixed Cost)

```
FC = COGS + Phí sàn CĐ + Voucher + Đóng gói + (COGS × Tỷ lệ hỏng%)
   + Ads/đơn + Lương NV/đơn + Ship + Khác
```

### Tổng % chi phí biến đổi (Variable Cost %)

```
VC% = Phí thanh toán% + Hoa hồng sàn% + Hoa hồng NV%
```

### Điểm hòa vốn (Break-even Price)

```
BEP = FC / (1 − VC%)
```

### Giá bán đạt biên lợi nhuận M%

```
Price(M%) = FC / (1 − VC% − M%)
```

### Lợi nhuận ròng tại mức giá P

```
Net Profit = P − FC − (P × VC%)
Margin%    = Net Profit / P × 100
```

---

## Cách chạy

```bash
cd C:\Users\admin\.gemini\antigravity\scratch\pricing-engine
pip install -r requirements.txt
streamlit run pricing_engine.py
```

Mở trình duyệt tại `http://localhost:8501`

---

## Thông số đầu vào

| # | Nhóm | Mô tả |
|---|------|--------|
| 1 | **COGS** | Giá nhập từ nhà cung cấp |
| 2 | **Phí sàn TMĐT** | Phí cố định, phí thanh toán %, hoa hồng sàn %, voucher shop chịu |
| 3 | **Bao bì đóng gói** | Thùng carton, xốp chống sốc, bảo vệ kính, băng keo/nhãn |
| 4 | **Dự phòng hàng hỏng** | Mặc định 5% — tính trên giá nhập |
| 5 | **Ads mồi livestream** | Ngân sách ads/ngày, số phiên live/tháng, đơn TB/phiên |
| 6 | **Nhân viên livestream** | Lương cơ bản × 2 người, hoa hồng %, tổng đơn/tháng |
| 7 | **Chi phí khác** | Phí ship shop chịu, chi phí khác |

## Kết quả đầu ra

- 🔴 **Điểm hòa vốn (BEP)** — Giá tối thiểu không lỗ
- 🟡 **Giá đề xuất biên 15%** — Mức giá an toàn
- 🟢 **Giá đề xuất biên 20%** — Mức giá mục tiêu
- 📋 **Bảng P&L chi tiết** — 10 khoản mục chi phí
- 📊 **Waterfall chart + Pie chart + Margin curve**
- 🔍 **Phân tích độ nhạy** — Giá bán & tỷ lệ hỏng
- 📤 **So sánh đa SKU** — Tất cả sản phẩm mẫu

## Sản phẩm mẫu có sẵn

| SKU | Tên | COGS |
|-----|-----|------|
| BG-001 | Bếp gas đôi kính cường lực | 850,000₫ |
| BG-002 | Bếp gas đơn inox | 420,000₫ |
| BT-001 | Bếp từ đôi âm | 1,500,000₫ |
| BT-002 | Bếp từ đơn di động | 650,000₫ |
