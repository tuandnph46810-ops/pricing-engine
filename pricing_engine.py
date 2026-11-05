"""
╔══════════════════════════════════════════════════════════════════════╗
║  PRICING ENGINE v2.0 — Unit Economics Calculator                   ║
║  Dành cho ngành Gia dụng (Bếp gas, Bếp từ)                        ║
║  Bán hàng trực tiếp: Livestream, Page, Showroom                   ║
║  Tính toán: Break-even, Giá bán đề xuất, P&L dự kiến              ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass, field
from datetime import datetime

# ─────────────────────────── CONFIG ───────────────────────────
st.set_page_config(
    page_title="Pricing Engine v2 — Unit Economics",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────── DATA CLASSES ───────────────────────────

@dataclass
class PackagingCost:
    """Chi phí bao bì đóng gói chống sốc / chống vỡ kính."""
    box_cost: float = 0.0             # Thùng carton (VNĐ)
    foam_cost: float = 0.0            # Xốp chống sốc (VNĐ)
    glass_protection: float = 0.0     # Bảo vệ kính cường lực (VNĐ)
    tape_label: float = 0.0           # Băng keo, nhãn (VNĐ)

    def total(self) -> float:
        return self.box_cost + self.foam_cost + self.glass_protection + self.tape_label


@dataclass
class AdsLivestreamCost:
    """Chi phí chạy ads mồi livestream."""
    daily_budget: float = 0.0         # Ngân sách ads / ngày (VNĐ)
    sessions_per_month: int = 20      # Số phiên live / tháng
    avg_orders_per_session: int = 10  # Đơn TB mỗi phiên

    def cost_per_unit(self) -> float:
        total_monthly = self.daily_budget * 30
        total_orders = self.sessions_per_month * self.avg_orders_per_session
        if total_orders == 0:
            return 0
        return total_monthly / total_orders


@dataclass
class AdsPageCost:
    """Chi phí chạy ads Page (Facebook, Zalo, TikTok…)."""
    monthly_budget: float = 0.0       # Ngân sách ads page / tháng (VNĐ)
    orders_from_page: int = 50        # Số đơn từ page / tháng

    def cost_per_unit(self) -> float:
        if self.orders_from_page == 0:
            return 0
        return self.monthly_budget / self.orders_from_page


@dataclass
class StaffCost:
    """Chi phí nhân sự tổng hợp."""
    # Nhân viên livestream
    ls_salary_per_person: float = 0.0
    ls_num_staff: int = 2
    ls_commission_pct: float = 0.0        # % hoa hồng trên doanh thu

    # Nhân viên khác (kho, CSKH, kế toán, quản lý…)
    other_staff_total_salary: float = 0.0  # Tổng lương NV khác / tháng

    estimated_monthly_orders: int = 200

    def fixed_cost_per_unit(self) -> float:
        total = (self.ls_salary_per_person * self.ls_num_staff
                 + self.other_staff_total_salary)
        if self.estimated_monthly_orders == 0:
            return 0
        return total / self.estimated_monthly_orders

    def commission_per_unit(self, selling_price: float) -> float:
        return selling_price * self.ls_commission_pct / 100


@dataclass
class PremisesCost:
    """Chi phí mặt bằng (kho, showroom, văn phòng)."""
    warehouse_rent: float = 0.0       # Tiền thuê kho / tháng
    showroom_rent: float = 0.0        # Tiền thuê showroom / tháng
    office_rent: float = 0.0          # Tiền thuê VP / tháng
    utilities: float = 0.0            # Điện nước, internet / tháng
    estimated_monthly_orders: int = 200

    def total_monthly(self) -> float:
        return self.warehouse_rent + self.showroom_rent + self.office_rent + self.utilities

    def cost_per_unit(self) -> float:
        if self.estimated_monthly_orders == 0:
            return 0
        return self.total_monthly() / self.estimated_monthly_orders


@dataclass
class ShippingCost:
    """Chi phí vận chuyển."""
    inbound_per_unit: float = 0.0     # Vận chuyển nhập kho / SP (VNĐ)
    outbound_per_unit: float = 0.0    # Ship đến khách (shop chịu) / đơn (VNĐ)
    return_rate_pct: float = 0.0      # Tỷ lệ hoàn hàng (%)
    return_shipping: float = 0.0      # Phí ship hoàn / đơn hoàn (VNĐ)

    def total_per_unit(self) -> float:
        return (self.inbound_per_unit
                + self.outbound_per_unit
                + self.return_rate_pct / 100 * self.return_shipping)


@dataclass
class WarrantyCost:
    """Chi phí bảo hành."""
    warranty_rate_pct: float = 0.0     # Tỷ lệ BH / tổng đơn (%)
    avg_repair_cost: float = 0.0       # Chi phí sửa chữa TB / case (VNĐ)
    avg_replace_cost: float = 0.0      # Chi phí đổi mới TB / case (VNĐ)
    replace_ratio_pct: float = 0.0     # % case phải đổi mới (trong số BH)

    def cost_per_unit(self) -> float:
        if self.warranty_rate_pct == 0:
            return 0
        rate = self.warranty_rate_pct / 100
        repair_portion = (1 - self.replace_ratio_pct / 100) * self.avg_repair_cost
        replace_portion = (self.replace_ratio_pct / 100) * self.avg_replace_cost
        return rate * (repair_portion + replace_portion)


@dataclass
class ContingencyCost:
    """Chi phí phát sinh."""
    monthly_contingency: float = 0.0   # Dự phòng phát sinh / tháng (VNĐ)
    estimated_monthly_orders: int = 200

    def cost_per_unit(self) -> float:
        if self.estimated_monthly_orders == 0:
            return 0
        return self.monthly_contingency / self.estimated_monthly_orders


@dataclass
class ProductInput:
    """Tổng hợp thông số đầu vào cho 1 mã sản phẩm."""
    sku: str = ""
    product_name: str = ""
    cogs: float = 0.0
    packaging: PackagingCost = field(default_factory=PackagingCost)
    breakage_rate_pct: float = 5.0
    ads_livestream: AdsLivestreamCost = field(default_factory=AdsLivestreamCost)
    ads_page: AdsPageCost = field(default_factory=AdsPageCost)
    staff: StaffCost = field(default_factory=StaffCost)
    premises: PremisesCost = field(default_factory=PremisesCost)
    shipping: ShippingCost = field(default_factory=ShippingCost)
    warranty: WarrantyCost = field(default_factory=WarrantyCost)
    contingency: ContingencyCost = field(default_factory=ContingencyCost)


# ─────────────────────────── CALCULATION ENGINE ───────────────────────────

class PricingCalculator:
    """Core calculation engine."""

    def __init__(self, product: ProductInput):
        self.p = product

    def _cost_breakdown_fixed(self) -> dict:
        """Chi tiết từng khoản chi phí cố định / đơn."""
        return {
            "① Giá nhập (COGS)": self.p.cogs,
            "② Bao bì đóng gói chống sốc": self.p.packaging.total(),
            "③ Dự phòng hàng hỏng / vỡ kính": self.p.cogs * self.p.breakage_rate_pct / 100,
            "④ Chi phí Ads Livestream": self.p.ads_livestream.cost_per_unit(),
            "⑤ Chi phí Ads Page": self.p.ads_page.cost_per_unit(),
            "⑥ Nhân sự (lương cố định phân bổ)": self.p.staff.fixed_cost_per_unit(),
            "⑦ Chi phí mặt bằng (phân bổ)": self.p.premises.cost_per_unit(),
            "⑧ Chi phí vận chuyển": self.p.shipping.total_per_unit(),
            "⑨ Chi phí bảo hành": self.p.warranty.cost_per_unit(),
            "⑩ Chi phí phát sinh (phân bổ)": self.p.contingency.cost_per_unit(),
        }

    def _total_fixed_cost(self) -> float:
        return sum(self._cost_breakdown_fixed().values())

    def _total_variable_pct(self) -> float:
        """Tổng % chi phí biến đổi (theo giá bán) — chỉ còn hoa hồng NV."""
        return self.p.staff.ls_commission_pct

    def breakeven_price(self) -> float:
        fixed = self._total_fixed_cost()
        var_pct = self._total_variable_pct()
        if var_pct >= 100:
            return float('inf')
        return fixed / (1 - var_pct / 100)

    def price_for_margin(self, target_margin_pct: float) -> float:
        fixed = self._total_fixed_cost()
        var_pct = self._total_variable_pct()
        denominator = 1 - (var_pct + target_margin_pct) / 100
        if denominator <= 0:
            return float('inf')
        return fixed / denominator

    def pnl_at_price(self, selling_price: float) -> dict:
        breakdown = self._cost_breakdown_fixed()
        commission = self.p.staff.commission_per_unit(selling_price)

        total_cost = sum(breakdown.values()) + commission
        net_profit = selling_price - total_cost
        margin_pct = (net_profit / selling_price * 100) if selling_price > 0 else 0

        result = {"Doanh thu (Giá bán)": selling_price, "─── CHI PHÍ ───": ""}
        result.update(breakdown)
        result["⑪ Hoa hồng NV livestream"] = commission
        result["─── TỔNG KẾT ───"] = ""
        result["TỔNG CHI PHÍ"] = total_cost
        result["LỢI NHUẬN RÒNG"] = net_profit
        result["BIÊN LỢI NHUẬN (%)"] = margin_pct
        return result


# ─────────────────────────── PRESET DATA ───────────────────────────

SAMPLE_PRODUCTS = {
    "BG-001 — Bếp gas đôi kính cường lực": {
        "cogs": 850_000, "box": 35_000, "foam": 25_000,
        "glass": 15_000, "tape": 5_000,
    },
    "BG-002 — Bếp gas đơn inox": {
        "cogs": 420_000, "box": 25_000, "foam": 15_000,
        "glass": 0, "tape": 5_000,
    },
    "BT-001 — Bếp từ đôi âm": {
        "cogs": 1_500_000, "box": 45_000, "foam": 35_000,
        "glass": 20_000, "tape": 5_000,
    },
    "BT-002 — Bếp từ đơn di động": {
        "cogs": 650_000, "box": 20_000, "foam": 15_000,
        "glass": 10_000, "tape": 5_000,
    },
    "🔧 Nhập tùy chỉnh": {
        "cogs": 0, "box": 0, "foam": 0, "glass": 0, "tape": 0,
    },
}


# ─────────────────────────── HELPERS ───────────────────────────

def format_vnd(value: float) -> str:
    if value == float('inf'):
        return "∞ (Không khả thi)"
    return f"{value:,.0f} ₫"


def render_pnl_waterfall(pnl: dict, title: str):
    cost_keys = [k for k in pnl if k.startswith("①") or k.startswith("②")
                 or k.startswith("③") or k.startswith("④") or k.startswith("⑤")
                 or k.startswith("⑥") or k.startswith("⑦") or k.startswith("⑧")
                 or k.startswith("⑨") or k.startswith("⑩") or k.startswith("⑪")]

    short_labels = {
        "①": "COGS", "②": "Đóng gói", "③": "Hỏng/vỡ",
        "④": "Ads Live", "⑤": "Ads Page", "⑥": "Nhân sự",
        "⑦": "Mặt bằng", "⑧": "Vận chuyển", "⑨": "Bảo hành",
        "⑩": "Phát sinh", "⑪": "Hoa hồng",
    }

    labels = ["Doanh thu"]
    values = [pnl["Doanh thu (Giá bán)"]]
    measures = ["absolute"]

    for k in cost_keys:
        prefix = k[:1]
        labels.append(short_labels.get(prefix, k[:10]))
        values.append(-pnl[k])
        measures.append("relative")

    labels.append("Lợi nhuận")
    values.append(pnl["LỢI NHUẬN RÒNG"])
    measures.append("total")

    fig = go.Figure(go.Waterfall(
        x=labels, y=values, measure=measures,
        textposition="outside",
        text=[format_vnd(abs(v)) for v in values],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#2ecc71"}},
        decreasing={"marker": {"color": "#e74c3c"}},
        totals={"marker": {"color": "#3498db" if pnl["LỢI NHUẬN RÒNG"] >= 0 else "#e74c3c"}},
    ))
    fig.update_layout(title=title, showlegend=False, height=450,
                      margin=dict(t=60, b=60), yaxis_title="VNĐ",
                      xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)


def render_cost_pie(pnl: dict):
    short_labels = {
        "①": "COGS", "②": "Đóng gói", "③": "Hỏng/vỡ",
        "④": "Ads Live", "⑤": "Ads Page", "⑥": "Nhân sự",
        "⑦": "Mặt bằng", "⑧": "Vận chuyển", "⑨": "Bảo hành",
        "⑩": "Phát sinh", "⑪": "Hoa hồng",
    }
    labels, values = [], []
    for k, v in pnl.items():
        prefix = k[:1]
        if prefix in short_labels and isinstance(v, (int, float)) and v > 0:
            labels.append(short_labels[prefix])
            values.append(v)

    if not values:
        return

    fig = px.pie(names=labels, values=values, title="Cơ cấu chi phí",
                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=420, margin=dict(t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)


def render_margin_curve(calc: PricingCalculator, bep: float):
    if bep == float('inf') or bep <= 0:
        return

    prices = [bep * r / 100 for r in range(60, 201, 5)]
    margins = []
    for p in prices:
        pnl = calc.pnl_at_price(p)
        margins.append(pnl["BIÊN LỢI NHUẬN (%)"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prices, y=margins, mode='lines+markers',
                              name='Biên LN (%)',
                              line=dict(color='#3498db', width=2),
                              marker=dict(size=4)))
    fig.add_hline(y=0, line_dash="dash", line_color="red",
                  annotation_text="Hòa vốn")
    fig.add_hline(y=15, line_dash="dot", line_color="orange",
                  annotation_text="Mục tiêu 15%")
    fig.add_hline(y=20, line_dash="dot", line_color="green",
                  annotation_text="Mục tiêu 20%")
    fig.add_vline(x=bep, line_dash="dash", line_color="red",
                  annotation_text=f"BEP: {format_vnd(bep)}")
    fig.update_layout(title="Biên lợi nhuận theo giá bán",
                      xaxis_title="Giá bán (VNĐ)",
                      yaxis_title="Biên lợi nhuận (%)",
                      height=420, margin=dict(t=60, b=40))
    st.plotly_chart(fig, use_container_width=True)


def render_pnl_column(pnl: dict, title: str):
    st.markdown(f"#### {title}")
    for k, v in pnl.items():
        if isinstance(v, str) and v == "":
            st.markdown(f"**{k}**")
        elif isinstance(v, (int, float)):
            if "%" in k:
                st.markdown(f"&nbsp;&nbsp;&nbsp;{k}: **{v:.1f}%**")
            else:
                color = ""
                if "LỢI NHUẬN" in k:
                    color = "red" if v < 0 else "green"
                formatted = format_vnd(v)
                suffix = f" :{color}[●]" if color else ""
                st.markdown(f"&nbsp;&nbsp;&nbsp;{k}: **{formatted}**{suffix}")


# ─────────────────────────── MAIN UI ───────────────────────────

def main():
    st.markdown("""
    # 🔥 Pricing Engine v2 — Unit Economics
    ### Phân tích giá & lãi lỗ cho sản phẩm Gia dụng (Bếp gas, Bếp từ)
    > Kênh bán: **Livestream · Page · Showroom** — Không qua sàn TMĐT
    ---
    """)

    # ══════════════════════ SIDEBAR ══════════════════════
    with st.sidebar:
        st.header("⚙️ Thông số đầu vào")

        # ── Chọn sản phẩm ──
        st.subheader("📦 Sản phẩm")
        selected = st.selectbox("Chọn mã sản phẩm mẫu",
                                 options=list(SAMPLE_PRODUCTS.keys()))
        preset = SAMPLE_PRODUCTS[selected]

        sku = st.text_input("Mã SKU",
                             value=selected.split(" — ")[0] if " — " in selected else "")
        product_name = st.text_input("Tên sản phẩm",
                                      value=selected.split(" — ")[1] if " — " in selected else "")

        # ── Đơn hàng ước tính ──
        st.subheader("📊 Tổng đơn ước tính / tháng")
        monthly_orders = st.number_input("Tổng đơn / tháng (tất cả kênh)",
                                          min_value=1, value=200, step=10,
                                          help="Dùng để phân bổ chi phí cố định hàng tháng")

        # ── 1. COGS ──
        st.subheader("💰 1. Giá nhập (COGS)")
        cogs = st.number_input("Giá nhập / sản phẩm (₫)", min_value=0,
                                value=preset["cogs"], step=10_000)

        # ── 2. Bao bì ──
        st.subheader("📦 2. Bao bì đóng gói")
        c1, c2 = st.columns(2)
        with c1:
            box_cost = st.number_input("Thùng carton (₫)", min_value=0,
                                        value=preset["box"], step=5_000)
            glass_prot = st.number_input("Bảo vệ kính (₫)", min_value=0,
                                          value=preset["glass"], step=5_000)
        with c2:
            foam_cost = st.number_input("Xốp chống sốc (₫)", min_value=0,
                                         value=preset["foam"], step=5_000)
            tape_label = st.number_input("Băng keo, nhãn (₫)", min_value=0,
                                          value=preset["tape"], step=1_000)

        # ── 3. Hàng hỏng ──
        st.subheader("💔 3. Dự phòng hàng hỏng")
        breakage = st.slider("Tỷ lệ hỏng / vỡ kính (%)", 0.0, 20.0, 5.0, 0.5,
                              help="Mặc định 5% — tính trên giá nhập")

        # ── 4. Ads Livestream ──
        st.subheader("📺 4. Chi phí Ads Livestream")
        ads_ls_daily = st.number_input("Ngân sách ads live / ngày (₫)",
                                        min_value=0, value=500_000, step=50_000)
        c3, c4 = st.columns(2)
        with c3:
            ls_sessions = st.number_input("Phiên live / tháng", min_value=1,
                                           value=20, step=1)
        with c4:
            ls_orders = st.number_input("Đơn TB / phiên", min_value=1,
                                         value=10, step=1)

        # ── 5. Ads Page ──
        st.subheader("📱 5. Chi phí Ads Page")
        ads_page_monthly = st.number_input("Ngân sách ads page / tháng (₫)",
                                            min_value=0, value=5_000_000,
                                            step=500_000,
                                            help="Facebook, Zalo, TikTok Ads…")
        page_orders = st.number_input("Đơn từ page / tháng", min_value=1,
                                       value=50, step=5)

        # ── 6. Nhân sự ──
        st.subheader("👥 6. Chi phí nhân sự")
        st.markdown("**Nhân viên Livestream**")
        c5, c6 = st.columns(2)
        with c5:
            ls_salary = st.number_input("Lương / người / tháng (₫)",
                                         min_value=0, value=7_000_000,
                                         step=500_000)
            ls_num = st.number_input("Số NV livestream", min_value=0,
                                      value=2, step=1)
        with c6:
            ls_comm = st.number_input("Hoa hồng NV livestream (%)",
                                       min_value=0.0, value=1.0, step=0.5,
                                       help="% trên doanh thu / đơn")

        st.markdown("**Nhân viên khác (kho, CSKH, kế toán, quản lý…)**")
        other_staff_salary = st.number_input("Tổng lương NV khác / tháng (₫)",
                                              min_value=0, value=15_000_000,
                                              step=1_000_000)

        # ── 7. Mặt bằng ──
        st.subheader("🏠 7. Chi phí mặt bằng")
        c7, c8 = st.columns(2)
        with c7:
            warehouse = st.number_input("Tiền thuê kho / tháng (₫)",
                                         min_value=0, value=5_000_000,
                                         step=500_000)
            showroom = st.number_input("Tiền thuê showroom / tháng (₫)",
                                        min_value=0, value=8_000_000,
                                        step=500_000)
        with c8:
            office = st.number_input("Tiền thuê VP / tháng (₫)",
                                      min_value=0, value=0, step=500_000)
            utilities = st.number_input("Điện nước, internet / tháng (₫)",
                                         min_value=0, value=3_000_000,
                                         step=500_000)

        # ── 8. Vận chuyển ──
        st.subheader("🚚 8. Chi phí vận chuyển")
        c9, c10 = st.columns(2)
        with c9:
            ship_in = st.number_input("Vận chuyển nhập kho / SP (₫)",
                                       min_value=0, value=10_000, step=5_000)
            ship_out = st.number_input("Ship đến khách / đơn (₫)",
                                        min_value=0, value=30_000, step=5_000,
                                        help="Phần shop chịu")
        with c10:
            return_rate = st.number_input("Tỷ lệ hoàn hàng (%)", min_value=0.0,
                                           value=3.0, step=0.5)
            return_ship = st.number_input("Phí ship hoàn / đơn hoàn (₫)",
                                           min_value=0, value=30_000, step=5_000)

        # ── 9. Bảo hành ──
        st.subheader("🔧 9. Chi phí bảo hành")
        c11, c12 = st.columns(2)
        with c11:
            warranty_rate = st.number_input("Tỷ lệ BH / tổng đơn (%)",
                                             min_value=0.0, value=3.0, step=0.5)
            repair_cost = st.number_input("Chi phí sửa chữa TB / case (₫)",
                                           min_value=0, value=100_000, step=10_000)
        with c12:
            replace_cost = st.number_input("Chi phí đổi mới TB / case (₫)",
                                            min_value=0, value=0, step=50_000,
                                            help="= COGS nếu đổi nguyên sản phẩm")
            replace_ratio = st.number_input("% case phải đổi mới", min_value=0.0,
                                             value=10.0, step=5.0)

        # ── 10. Phát sinh ──
        st.subheader("⚡ 10. Chi phí phát sinh")
        contingency = st.number_input("Dự phòng phát sinh / tháng (₫)",
                                       min_value=0, value=2_000_000,
                                       step=500_000,
                                       help="Hao hụt kho, quà tặng, xử lý khiếu nại…")

    # ══════════════════════ BUILD PRODUCT ══════════════════════

    product = ProductInput(
        sku=sku,
        product_name=product_name,
        cogs=cogs,
        packaging=PackagingCost(box_cost, foam_cost, glass_prot, tape_label),
        breakage_rate_pct=breakage,
        ads_livestream=AdsLivestreamCost(ads_ls_daily, ls_sessions, ls_orders),
        ads_page=AdsPageCost(ads_page_monthly, page_orders),
        staff=StaffCost(ls_salary, ls_num, ls_comm, other_staff_salary, monthly_orders),
        premises=PremisesCost(warehouse, showroom, office, utilities, monthly_orders),
        shipping=ShippingCost(ship_in, ship_out, return_rate, return_ship),
        warranty=WarrantyCost(warranty_rate, repair_cost, replace_cost, replace_ratio),
        contingency=ContingencyCost(contingency, monthly_orders),
    )

    calc = PricingCalculator(product)

    # ══════════════════════ KEY METRICS ══════════════════════

    bep = calc.breakeven_price()
    price_15 = calc.price_for_margin(15)
    price_20 = calc.price_for_margin(20)

    st.markdown(f"## 📊 Kết quả: **{sku}** — {product_name}")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🔴 Điểm hòa vốn (BEP)", format_vnd(bep))
    with m2:
        delta_15 = f"+{format_vnd(price_15 - bep)} vs BEP" if price_15 != float('inf') else None
        st.metric("🟡 Giá đề xuất (Biên 15%)", format_vnd(price_15), delta=delta_15)
    with m3:
        delta_20 = f"+{format_vnd(price_20 - bep)} vs BEP" if price_20 != float('inf') else None
        st.metric("🟢 Giá đề xuất (Biên 20%)", format_vnd(price_20), delta=delta_20)
    with m4:
        if price_20 != float('inf'):
            profit_20 = calc.pnl_at_price(price_20)["LỢI NHUẬN RÒNG"]
            st.metric("💵 LN ròng / đơn @20%", format_vnd(profit_20))

    st.markdown("---")

    # ══════════════════════ TABS ══════════════════════

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Bảng P&L chi tiết",
        "📊 Biểu đồ phân tích",
        "🔍 Phân tích độ nhạy",
        "📤 So sánh đa SKU",
    ])

    # ────── TAB 1: P&L ──────
    with tab1:
        c_a, c_b, c_c = st.columns(3)
        with c_a:
            render_pnl_column(calc.pnl_at_price(bep), "🔴 Tại điểm hòa vốn")
        with c_b:
            render_pnl_column(calc.pnl_at_price(price_15), "🟡 Biên lợi nhuận 15%")
        with c_c:
            render_pnl_column(calc.pnl_at_price(price_20), "🟢 Biên lợi nhuận 20%")

        st.markdown("---")
        st.subheader("🎯 Nhập giá bán tùy chỉnh")
        custom_price = st.number_input(
            "Giá bán tùy chỉnh (₫)", min_value=0,
            value=int(price_15) if price_15 != float('inf') else 0,
            step=10_000, key="custom_price",
        )
        if custom_price > 0:
            pnl_c = calc.pnl_at_price(custom_price)
            rows = [{"Khoản mục": k,
                      "Giá trị": format_vnd(v) if "%" not in k else f"{v:.1f}%"}
                     for k, v in pnl_c.items() if isinstance(v, (int, float))]
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ────── TAB 2: Charts ──────
    with tab2:
        ch1, ch2 = st.columns(2)
        with ch1:
            render_pnl_waterfall(calc.pnl_at_price(price_15),
                                  f"Waterfall P&L — Biên 15% ({format_vnd(price_15)})")
        with ch2:
            render_cost_pie(calc.pnl_at_price(price_15))
        render_margin_curve(calc, bep)

    # ────── TAB 3: Sensitivity ──────
    with tab3:
        st.subheader("🔍 Phân tích độ nhạy giá bán")

        if bep != float('inf') and bep > 0:
            step = max(10_000, round(bep * 0.05 / 10_000) * 10_000)
            price_range = [p for p in [bep + step * i for i in range(-5, 11)] if p > 0]

            rows = []
            for p in price_range:
                pnl = calc.pnl_at_price(p)
                profit = pnl['LỢI NHUẬN RÒNG']
                rows.append({
                    "Giá bán (₫)": f"{p:,.0f}",
                    "Tổng CP (₫)": f"{pnl['TỔNG CHI PHÍ']:,.0f}",
                    "LN ròng (₫)": f"{profit:,.0f}",
                    "Biên LN (%)": f"{pnl['BIÊN LỢI NHUẬN (%)']:.1f}%",
                    "": "🟢 Lãi" if profit > 0 else "🔴 Lỗ" if profit < 0 else "🟡 Hòa vốn",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            # Sensitivity trên tỷ lệ hỏng
            st.markdown("---")
            st.subheader("📉 Tác động tỷ lệ hàng hỏng")
            st.caption(f"Tại mức giá {format_vnd(price_15)} (biên 15%)")

            br_rows = []
            for br in [0, 1, 2, 3, 5, 7, 10, 15]:
                tmp = ProductInput(
                    sku=sku, product_name=product_name, cogs=cogs,
                    packaging=product.packaging, breakage_rate_pct=br,
                    ads_livestream=product.ads_livestream,
                    ads_page=product.ads_page, staff=product.staff,
                    premises=product.premises, shipping=product.shipping,
                    warranty=product.warranty, contingency=product.contingency,
                )
                tmp_pnl = PricingCalculator(tmp).pnl_at_price(price_15)
                br_rows.append({
                    "Tỷ lệ hỏng (%)": f"{br}%",
                    "CP hỏng / đơn (₫)": f"{cogs * br / 100:,.0f}",
                    "LN ròng (₫)": f"{tmp_pnl['LỢI NHUẬN RÒNG']:,.0f}",
                    "Biên LN (%)": f"{tmp_pnl['BIÊN LỢI NHUẬN (%)']:.1f}%",
                })
            st.dataframe(pd.DataFrame(br_rows), use_container_width=True,
                         hide_index=True)

            # Sensitivity trên số đơn/tháng
            st.markdown("---")
            st.subheader("📦 Tác động số đơn / tháng đến chi phí phân bổ")
            st.caption(f"Tại mức giá {format_vnd(price_15)} (biên 15%)")

            ord_rows = []
            for mo in [50, 100, 150, 200, 300, 500, 800, 1000]:
                tmp = ProductInput(
                    sku=sku, product_name=product_name, cogs=cogs,
                    packaging=product.packaging, breakage_rate_pct=breakage,
                    ads_livestream=product.ads_livestream,
                    ads_page=product.ads_page,
                    staff=StaffCost(ls_salary, ls_num, ls_comm, other_staff_salary, mo),
                    premises=PremisesCost(warehouse, showroom, office, utilities, mo),
                    shipping=product.shipping,
                    warranty=product.warranty,
                    contingency=ContingencyCost(contingency, mo),
                )
                tmp_calc = PricingCalculator(tmp)
                tmp_bep = tmp_calc.breakeven_price()
                tmp_pnl = tmp_calc.pnl_at_price(price_15)
                ord_rows.append({
                    "Đơn / tháng": f"{mo:,}",
                    "BEP (₫)": format_vnd(tmp_bep),
                    "LN ròng (₫)": f"{tmp_pnl['LỢI NHUẬN RÒNG']:,.0f}",
                    "Biên LN (%)": f"{tmp_pnl['BIÊN LỢI NHUẬN (%)']:.1f}%",
                })
            st.dataframe(pd.DataFrame(ord_rows), use_container_width=True,
                         hide_index=True)
        else:
            st.warning("Không thể tính BEP — hãy kiểm tra thông số đầu vào.")

    # ────── TAB 4: Multi-SKU ──────
    with tab4:
        st.subheader("📤 So sánh nhanh các SKU mẫu")
        st.info("Cùng thông số chi phí chung — chỉ khác COGS và đóng gói.")

        multi_rows = []
        for name, pd_ in SAMPLE_PRODUCTS.items():
            if "Nhập tùy chỉnh" in name:
                continue
            tmp = ProductInput(
                sku=name.split(" — ")[0],
                product_name=name.split(" — ")[1] if " — " in name else name,
                cogs=pd_["cogs"],
                packaging=PackagingCost(pd_["box"], pd_["foam"], pd_["glass"], pd_["tape"]),
                breakage_rate_pct=breakage,
                ads_livestream=product.ads_livestream,
                ads_page=product.ads_page, staff=product.staff,
                premises=product.premises, shipping=product.shipping,
                warranty=product.warranty, contingency=product.contingency,
            )
            tc = PricingCalculator(tmp)
            t_bep = tc.breakeven_price()
            t_15 = tc.price_for_margin(15)
            t_20 = tc.price_for_margin(20)
            multi_rows.append({
                "SKU": tmp.sku,
                "Sản phẩm": tmp.product_name,
                "COGS (₫)": f"{pd_['cogs']:,.0f}",
                "BEP (₫)": format_vnd(t_bep),
                "Giá 15% (₫)": format_vnd(t_15),
                "Giá 20% (₫)": format_vnd(t_20),
                "LN/đơn @20%": format_vnd(t_20 * 20 / 100) if t_20 != float('inf') else "N/A",
            })
        st.dataframe(pd.DataFrame(multi_rows), use_container_width=True,
                     hide_index=True)

    # ── Footer ──
    st.markdown("---")
    st.markdown(
        f"<div style='text-align:center; color:gray; font-size:0.85em'>"
        f"Pricing Engine v2.0 · {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
        f"Dành cho nội bộ Công ty Gia dụng</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
