"""
╔══════════════════════════════════════════════════════════════════════╗
║  PRICING ENGINE v3.0 — Unit Economics Calculator                   ║
║  Dành cho ngành Gia dụng (Bếp gas, Bếp từ)                        ║
║  Bán hàng trực tiếp: Livestream, Page, Showroom                   ║
║  Chi phí nhân sự tách biệt từng người                             ║
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
    page_title="Pricing Engine v3 — Unit Economics",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────── THEME: WHITE + RED ───────────────────────────

BRAND_RED = "#E8192C"
BRAND_RED_LIGHT = "#FF4D5E"
BRAND_RED_BG = "#FFF0F1"
BRAND_RED_DARK = "#B71525"

st.markdown(f"""
<style>
    /* ══════ GLOBAL ══════ */
    .stApp {{
        background-color: #FFFFFF;
        color: #222222;
    }}
    header[data-testid="stHeader"] {{
        background-color: {BRAND_RED};
    }}

    /* ══════ SIDEBAR — nền trắng, accent đỏ ══════ */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #FFFFFF 0%, {BRAND_RED_BG} 100%);
        border-right: 3px solid {BRAND_RED};
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {{
        color: {BRAND_RED} !important;
        font-weight: 700 !important;
    }}
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .stCaption {{
        color: #333333 !important;
    }}
    section[data-testid="stSidebar"] .stNumberInput input,
    section[data-testid="stSidebar"] .stTextInput input {{
        background-color: #FFFFFF !important;
        color: #222222 !important;
        border: 1.5px solid #DDDDDD !important;
        border-radius: 6px !important;
    }}
    section[data-testid="stSidebar"] .stNumberInput input:focus,
    section[data-testid="stSidebar"] .stTextInput input:focus {{
        border-color: {BRAND_RED} !important;
        box-shadow: 0 0 0 2px {BRAND_RED_BG} !important;
    }}
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {{
        background-color: #FFFFFF !important;
        color: #222222 !important;
        border-color: #DDDDDD !important;
    }}
    section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {{
        color: #222222 !important;
    }}
    section[data-testid="stSidebar"] .stCheckbox label span {{
        color: #333333 !important;
    }}
    section[data-testid="stSidebar"] .stSlider label {{
        color: #333333 !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: {BRAND_RED_LIGHT} !important;
        opacity: 0.4;
    }}
    /* Sidebar expanders */
    section[data-testid="stSidebar"] details {{
        background-color: #FFFFFF !important;
        border: 1.5px solid #EEEEEE !important;
        border-radius: 8px !important;
        margin-bottom: 6px;
    }}
    section[data-testid="stSidebar"] details[open] {{
        border-color: {BRAND_RED} !important;
    }}
    section[data-testid="stSidebar"] details summary {{
        color: {BRAND_RED_DARK} !important;
        font-weight: 600;
    }}

    /* ══════ METRIC CARDS ══════ */
    div[data-testid="stMetric"] {{
        background-color: {BRAND_RED_BG};
        border-left: 4px solid {BRAND_RED};
        padding: 12px 16px;
        border-radius: 8px;
    }}
    div[data-testid="stMetric"] label {{
        color: {BRAND_RED_DARK} !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
        color: {BRAND_RED} !important;
        font-weight: 700 !important;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {{
        color: #555555 !important;
    }}

    /* ══════ TABS ══════ */
    button[data-baseweb="tab"] {{
        color: #666666 !important;
        font-weight: 500 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {BRAND_RED} !important;
        border-bottom: 3px solid {BRAND_RED} !important;
        font-weight: 700 !important;
    }}

    /* ══════ EXPANDERS (main area) ══════ */
    .main details summary {{
        color: {BRAND_RED_DARK} !important;
        font-weight: 600;
    }}
    .main details[open] {{
        border-color: {BRAND_RED} !important;
    }}

    /* ══════ BUTTONS ══════ */
    .stButton > button {{
        background-color: {BRAND_RED} !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px;
        font-weight: 600;
    }}
    .stButton > button:hover {{
        background-color: {BRAND_RED_DARK} !important;
    }}

    /* ══════ HEADINGS ══════ */
    .main h1, .main h2 {{
        color: {BRAND_RED} !important;
    }}
    .main h3 {{
        color: {BRAND_RED_DARK} !important;
    }}

    /* ══════ BODY TEXT ══════ */
    .main .stMarkdown p,
    .main .stMarkdown li,
    .main .stMarkdown span {{
        color: #333333 !important;
    }}

    /* ══════ DATAFRAME ══════ */
    .stDataFrame thead tr th {{
        background-color: {BRAND_RED} !important;
        color: #FFFFFF !important;
    }}

    /* ══════ INPUTS (main area) ══════ */
    .main .stNumberInput input,
    .main .stTextInput input {{
        border: 1.5px solid #DDDDDD !important;
        color: #222222 !important;
    }}
    .main .stNumberInput input:focus,
    .main .stTextInput input:focus {{
        border-color: {BRAND_RED} !important;
        box-shadow: 0 0 0 2px {BRAND_RED_BG} !important;
    }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────── DATA CLASSES ───────────────────────────

@dataclass
class PackagingCost:
    box_cost: float = 0.0
    foam_cost: float = 0.0
    glass_protection: float = 0.0
    tape_label: float = 0.0

    def total(self) -> float:
        return self.box_cost + self.foam_cost + self.glass_protection + self.tape_label


@dataclass
class AdsLivestreamCost:
    daily_budget: float = 0.0
    sessions_per_month: int = 20
    avg_orders_per_session: int = 10

    def cost_per_unit(self) -> float:
        total_monthly = self.daily_budget * 30
        total_orders = self.sessions_per_month * self.avg_orders_per_session
        if total_orders == 0:
            return 0
        return total_monthly / total_orders


@dataclass
class AdsPageCost:
    monthly_budget: float = 0.0
    orders_from_page: int = 50

    def cost_per_unit(self) -> float:
        if self.orders_from_page == 0:
            return 0
        return self.monthly_budget / self.orders_from_page


@dataclass
class StaffMember:
    """Một nhân viên cụ thể."""
    role: str = ""                    # Vị trí
    name: str = ""                    # Tên
    salary: float = 0.0              # Lương / tháng
    commission_pct: float = 0.0      # Hoa hồng % trên doanh thu
    active: bool = False             # Có đang làm việc không


@dataclass
class StaffTeam:
    """Toàn bộ đội ngũ nhân sự — từng người riêng biệt."""
    members: list = field(default_factory=list)
    estimated_monthly_orders: int = 200

    def total_salary(self) -> float:
        return sum(m.salary for m in self.members if m.active)

    def total_commission_pct(self) -> float:
        return sum(m.commission_pct for m in self.members if m.active)

    def fixed_cost_per_unit(self) -> float:
        if self.estimated_monthly_orders == 0:
            return 0
        return self.total_salary() / self.estimated_monthly_orders

    def commission_per_unit(self, selling_price: float) -> float:
        return selling_price * self.total_commission_pct() / 100

    def salary_breakdown_per_unit(self) -> list[tuple[str, float]]:
        """Chi tiết lương phân bổ / đơn từng người."""
        result = []
        for m in self.members:
            if m.active and m.salary > 0:
                label = f"{m.role}: {m.name}" if m.name else m.role
                per_unit = m.salary / self.estimated_monthly_orders if self.estimated_monthly_orders > 0 else 0
                result.append((label, per_unit, m.salary))
        return result

    def commission_breakdown_per_unit(self, selling_price: float) -> list[tuple[str, float]]:
        """Chi tiết hoa hồng / đơn từng người."""
        result = []
        for m in self.members:
            if m.active and m.commission_pct > 0:
                label = f"{m.role}: {m.name}" if m.name else m.role
                per_unit = selling_price * m.commission_pct / 100
                result.append((label, per_unit, m.commission_pct))
        return result


@dataclass
class PremisesCost:
    warehouse_rent: float = 0.0
    showroom_rent: float = 0.0
    office_rent: float = 0.0
    utilities: float = 0.0
    estimated_monthly_orders: int = 200

    def total_monthly(self) -> float:
        return self.warehouse_rent + self.showroom_rent + self.office_rent + self.utilities

    def cost_per_unit(self) -> float:
        if self.estimated_monthly_orders == 0:
            return 0
        return self.total_monthly() / self.estimated_monthly_orders


@dataclass
class ShippingCost:
    inbound_per_unit: float = 0.0
    outbound_per_unit: float = 0.0
    return_rate_pct: float = 0.0
    return_shipping: float = 0.0

    def total_per_unit(self) -> float:
        return (self.inbound_per_unit
                + self.outbound_per_unit
                + self.return_rate_pct / 100 * self.return_shipping)


@dataclass
class WarrantyCost:
    warranty_rate_pct: float = 0.0
    avg_repair_cost: float = 0.0
    avg_replace_cost: float = 0.0
    replace_ratio_pct: float = 0.0

    def cost_per_unit(self) -> float:
        if self.warranty_rate_pct == 0:
            return 0
        rate = self.warranty_rate_pct / 100
        repair_portion = (1 - self.replace_ratio_pct / 100) * self.avg_repair_cost
        replace_portion = (self.replace_ratio_pct / 100) * self.avg_replace_cost
        return rate * (repair_portion + replace_portion)


@dataclass
class ContingencyCost:
    monthly_contingency: float = 0.0
    estimated_monthly_orders: int = 200

    def cost_per_unit(self) -> float:
        if self.estimated_monthly_orders == 0:
            return 0
        return self.monthly_contingency / self.estimated_monthly_orders


@dataclass
class ProductInput:
    sku: str = ""
    product_name: str = ""
    cogs: float = 0.0
    packaging: PackagingCost = field(default_factory=PackagingCost)
    breakage_rate_pct: float = 5.0
    ads_livestream: AdsLivestreamCost = field(default_factory=AdsLivestreamCost)
    ads_page: AdsPageCost = field(default_factory=AdsPageCost)
    staff: StaffTeam = field(default_factory=StaffTeam)
    premises: PremisesCost = field(default_factory=PremisesCost)
    shipping: ShippingCost = field(default_factory=ShippingCost)
    warranty: WarrantyCost = field(default_factory=WarrantyCost)
    contingency: ContingencyCost = field(default_factory=ContingencyCost)


# ─────────────────────────── CALCULATION ENGINE ───────────────────────────

class PricingCalculator:
    def __init__(self, product: ProductInput):
        self.p = product

    def _cost_breakdown_fixed(self) -> dict:
        return {
            "① Giá nhập (COGS)": self.p.cogs,
            "② Bao bì đóng gói chống sốc": self.p.packaging.total(),
            "③ Dự phòng hàng hỏng / vỡ kính": self.p.cogs * self.p.breakage_rate_pct / 100,
            "④ Chi phí Ads Livestream": self.p.ads_livestream.cost_per_unit(),
            "⑤ Chi phí Ads Page": self.p.ads_page.cost_per_unit(),
            "⑥ Lương nhân sự (phân bổ)": self.p.staff.fixed_cost_per_unit(),
            "⑦ Chi phí mặt bằng (phân bổ)": self.p.premises.cost_per_unit(),
            "⑧ Chi phí vận chuyển": self.p.shipping.total_per_unit(),
            "⑨ Chi phí bảo hành": self.p.warranty.cost_per_unit(),
            "⑩ Chi phí phát sinh (phân bổ)": self.p.contingency.cost_per_unit(),
        }

    def _total_fixed_cost(self) -> float:
        return sum(self._cost_breakdown_fixed().values())

    def _total_variable_pct(self) -> float:
        return self.p.staff.total_commission_pct()

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
        result["⑪ Hoa hồng nhân viên"] = commission
        result["─── TỔNG KẾT ───"] = ""
        result["TỔNG CHI PHÍ"] = total_cost
        result["LỢI NHUẬN RÒNG"] = net_profit
        result["BIÊN LỢI NHUẬN (%)"] = margin_pct
        return result

    def staff_pnl_detail(self, selling_price: float) -> list[dict]:
        """P&L chi tiết từng nhân viên."""
        rows = []
        for label, per_unit, monthly in self.p.staff.salary_breakdown_per_unit():
            rows.append({
                "Nhân viên": label,
                "Lương / tháng": monthly,
                "Phân bổ / đơn": per_unit,
                "Loại": "Lương cố định",
            })
        for label, per_unit, pct in self.p.staff.commission_breakdown_per_unit(selling_price):
            rows.append({
                "Nhân viên": label,
                "Hoa hồng (%)": pct,
                "Phân bổ / đơn": per_unit,
                "Loại": "Hoa hồng",
            })
        return rows


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

# Default staff roster
DEFAULT_STAFF = [
    {"role": "NV Livestream 1", "name": "", "salary": 7_000_000, "commission": 1.0, "active": True},
    {"role": "NV Livestream 2", "name": "", "salary": 7_000_000, "commission": 1.0, "active": True},
    {"role": "NV Chăm sóc KH", "name": "", "salary": 6_000_000, "commission": 0.0, "active": True},
    {"role": "NV Quản lý",     "name": "", "salary": 10_000_000, "commission": 0.0, "active": True},
    {"role": "Vị trí 5",       "name": "", "salary": 0, "commission": 0.0, "active": False},
    {"role": "Vị trí 6",       "name": "", "salary": 0, "commission": 0.0, "active": False},
    {"role": "Vị trí 7",       "name": "", "salary": 0, "commission": 0.0, "active": False},
]


# ─────────────────────────── HELPERS ───────────────────────────

def format_vnd(value: float) -> str:
    if value == float('inf'):
        return "∞ (Không khả thi)"
    return f"{value:,.0f} ₫"


def render_pnl_waterfall(pnl: dict, title: str):
    cost_keys = [k for k in pnl if k[0] in "①②③④⑤⑥⑦⑧⑨⑩⑪"]
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
        connector={"line": {"color": "#ccc"}},
        increasing={"marker": {"color": "#2ecc71"}},
        decreasing={"marker": {"color": BRAND_RED}},
        totals={"marker": {"color": "#2ecc71" if pnl["LỢI NHUẬN RÒNG"] >= 0 else BRAND_RED}},
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(color=BRAND_RED_DARK)),
        showlegend=False, height=450,
        margin=dict(t=60, b=60), yaxis_title="VNĐ",
        xaxis_tickangle=-35, plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
    )
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
        prefix = k[:1] if k else ""
        if prefix in short_labels and isinstance(v, (int, float)) and v > 0:
            labels.append(short_labels[prefix])
            values.append(v)
    if not values:
        return

    red_palette = [
        "#E8192C", "#FF4D5E", "#FF7A87", "#FFB3BA", "#C0392B",
        "#E74C3C", "#F1948A", "#FADBD8", "#D35400", "#E67E22", "#F39C12",
    ]
    fig = px.pie(names=labels, values=values, title="Cơ cấu chi phí",
                 hole=0.4, color_discrete_sequence=red_palette)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=420, margin=dict(t=60, b=20),
                      plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
    st.plotly_chart(fig, use_container_width=True)


def render_margin_curve(calc: PricingCalculator, bep: float):
    if bep == float('inf') or bep <= 0:
        return
    prices = [bep * r / 100 for r in range(60, 201, 5)]
    margins = [calc.pnl_at_price(p)["BIÊN LỢI NHUẬN (%)"] for p in prices]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prices, y=margins, mode='lines+markers',
                              name='Biên LN (%)',
                              line=dict(color=BRAND_RED, width=3),
                              marker=dict(size=4, color=BRAND_RED)))
    fig.add_hline(y=0, line_dash="dash", line_color="#999", annotation_text="Hòa vốn")
    fig.add_hline(y=15, line_dash="dot", line_color="#f39c12", annotation_text="Mục tiêu 15%")
    fig.add_hline(y=20, line_dash="dot", line_color="#2ecc71", annotation_text="Mục tiêu 20%")
    fig.add_vline(x=bep, line_dash="dash", line_color=BRAND_RED,
                  annotation_text=f"BEP: {format_vnd(bep)}")
    fig.update_layout(
        title=dict(text="Biên lợi nhuận theo giá bán", font=dict(color=BRAND_RED_DARK)),
        xaxis_title="Giá bán (VNĐ)", yaxis_title="Biên lợi nhuận (%)",
        height=420, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
    )
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
                st.markdown(f"&nbsp;&nbsp;&nbsp;{k}: **{format_vnd(v)}**"
                            + (f" :{color}[●]" if color else ""))


def render_staff_detail_table(calc: PricingCalculator, selling_price: float):
    """Bảng chi tiết từng nhân viên."""
    rows = calc.staff_pnl_detail(selling_price)
    if not rows:
        st.info("Chưa có nhân viên nào được kích hoạt.")
        return

    df = pd.DataFrame(rows)
    for col in ["Lương / tháng", "Phân bổ / đơn"]:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: format_vnd(x) if pd.notna(x) else "—")
    if "Hoa hồng (%)" in df.columns:
        df["Hoa hồng (%)"] = df["Hoa hồng (%)"].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "—")
    st.dataframe(df, use_container_width=True, hide_index=True)


# ─────────────────────────── MAIN UI ───────────────────────────

def main():
    st.markdown(f"""
    <div style="text-align:center; padding: 10px 0 5px 0;">
        <span style="font-size:2.5em; font-weight:800; color:{BRAND_RED};">🔥 PRICING ENGINE</span>
        <br>
        <span style="font-size:1.1em; color:{BRAND_RED_DARK};">
        Phân tích giá & lãi lỗ · Gia dụng (Bếp gas, Bếp từ) · Livestream · Page · Showroom</span>
    </div>
    <hr style="border: 2px solid {BRAND_RED}; margin: 10px 0 20px 0;">
    """, unsafe_allow_html=True)

    # ══════════════════════ SIDEBAR ══════════════════════
    with st.sidebar:
        st.markdown(f"### ⚙️ THÔNG SỐ ĐẦU VÀO")

        # ── Sản phẩm ──
        st.markdown("#### 📦 Sản phẩm")
        selected = st.selectbox("Chọn mã sản phẩm mẫu",
                                 options=list(SAMPLE_PRODUCTS.keys()))
        preset = SAMPLE_PRODUCTS[selected]
        sku = st.text_input("Mã SKU",
                             value=selected.split(" — ")[0] if " — " in selected else "")
        product_name = st.text_input("Tên sản phẩm",
                                      value=selected.split(" — ")[1] if " — " in selected else "")

        # ── Đơn hàng ──
        st.markdown("---")
        st.markdown("#### 📊 Đơn hàng ước tính")
        monthly_orders = st.number_input("Tổng đơn / tháng", min_value=1,
                                          value=200, step=10)

        # ── 1. COGS ──
        st.markdown("---")
        st.markdown("#### 💰 1. Giá nhập (COGS)")
        cogs = st.number_input("Giá nhập / SP (₫)", min_value=0,
                                value=preset["cogs"], step=10_000)

        # ── 2. Bao bì ──
        st.markdown("---")
        st.markdown("#### 📦 2. Bao bì đóng gói")
        c1, c2 = st.columns(2)
        with c1:
            box_cost = st.number_input("Thùng carton", min_value=0,
                                        value=preset["box"], step=5_000)
            glass_prot = st.number_input("Bảo vệ kính", min_value=0,
                                          value=preset["glass"], step=5_000)
        with c2:
            foam_cost = st.number_input("Xốp chống sốc", min_value=0,
                                         value=preset["foam"], step=5_000)
            tape_label = st.number_input("Băng keo, nhãn", min_value=0,
                                          value=preset["tape"], step=1_000)

        # ── 3. Hàng hỏng ──
        st.markdown("---")
        st.markdown("#### 💔 3. Dự phòng hàng hỏng")
        breakage = st.slider("Tỷ lệ hỏng / vỡ kính (%)", 0.0, 20.0, 5.0, 0.5)

        # ── 4. Ads Livestream ──
        st.markdown("---")
        st.markdown("#### 📺 4. Ads Livestream")
        ads_ls_daily = st.number_input("Budget ads live / ngày (₫)",
                                        min_value=0, value=500_000, step=50_000)
        c3, c4 = st.columns(2)
        with c3:
            ls_sessions = st.number_input("Phiên / tháng", min_value=1, value=20)
        with c4:
            ls_orders = st.number_input("Đơn / phiên", min_value=1, value=10)

        # ── 5. Ads Page ──
        st.markdown("---")
        st.markdown("#### 📱 5. Ads Page")
        ads_page_monthly = st.number_input("Budget ads page / tháng (₫)",
                                            min_value=0, value=5_000_000, step=500_000)
        page_orders = st.number_input("Đơn từ page / tháng", min_value=1,
                                       value=50, step=5)

        # ── 6. NHÂN SỰ — TÁCH BIỆT TỪNG NGƯỜI ──
        st.markdown("---")
        st.markdown(f"#### 👥 6. Chi phí nhân sự (từng người)")
        st.caption("Mỗi nhân viên 1 cột riêng — bật/tắt theo nhu cầu")

    # Build staff members from sidebar
    staff_members = []
    with st.sidebar:
        for i, default in enumerate(DEFAULT_STAFF):
            is_preset = i < 4  # 4 vị trí mặc định
            with st.expander(
                f"{'🟢' if default['active'] else '⚪'} {default['role']}",
                expanded=is_preset,
            ):
                active = st.checkbox("Đang làm việc", value=default["active"],
                                      key=f"staff_active_{i}")
                role = st.text_input("Vị trí", value=default["role"],
                                      key=f"staff_role_{i}")
                name = st.text_input("Họ tên", value=default["name"],
                                      key=f"staff_name_{i}",
                                      placeholder="Nhập tên nhân viên…")
                salary = st.number_input("Lương / tháng (₫)", min_value=0,
                                          value=default["salary"], step=500_000,
                                          key=f"staff_salary_{i}")
                comm = st.number_input("Hoa hồng (%)", min_value=0.0,
                                        value=default["commission"], step=0.5,
                                        key=f"staff_comm_{i}",
                                        help="% trên doanh thu / đơn")

                staff_members.append(StaffMember(
                    role=role, name=name, salary=salary,
                    commission_pct=comm, active=active,
                ))

    with st.sidebar:
        # ── 7. Mặt bằng ──
        st.markdown("---")
        st.markdown("#### 🏠 7. Mặt bằng")
        c7, c8 = st.columns(2)
        with c7:
            warehouse = st.number_input("Thuê kho / tháng", min_value=0,
                                         value=5_000_000, step=500_000)
            showroom = st.number_input("Thuê showroom / tháng", min_value=0,
                                        value=8_000_000, step=500_000)
        with c8:
            office = st.number_input("Thuê VP / tháng", min_value=0,
                                      value=0, step=500_000)
            utilities = st.number_input("Điện nước, net / tháng", min_value=0,
                                         value=3_000_000, step=500_000)

        # ── 8. Vận chuyển ──
        st.markdown("---")
        st.markdown("#### 🚚 8. Vận chuyển")
        c9, c10 = st.columns(2)
        with c9:
            ship_in = st.number_input("Nhập kho / SP", min_value=0,
                                       value=10_000, step=5_000)
            ship_out = st.number_input("Ship đến KH / đơn", min_value=0,
                                        value=30_000, step=5_000)
        with c10:
            return_rate = st.number_input("Tỷ lệ hoàn (%)", min_value=0.0,
                                           value=3.0, step=0.5)
            return_ship = st.number_input("Ship hoàn / đơn", min_value=0,
                                           value=30_000, step=5_000)

        # ── 9. Bảo hành ──
        st.markdown("---")
        st.markdown("#### 🔧 9. Bảo hành")
        c11, c12 = st.columns(2)
        with c11:
            warranty_rate = st.number_input("Tỷ lệ BH (%)", min_value=0.0,
                                             value=3.0, step=0.5)
            repair_cost = st.number_input("CP sửa chữa / case", min_value=0,
                                           value=100_000, step=10_000)
        with c12:
            replace_cost = st.number_input("CP đổi mới / case", min_value=0,
                                            value=0, step=50_000)
            replace_ratio = st.number_input("% đổi mới", min_value=0.0,
                                             value=10.0, step=5.0)

        # ── 10. Phát sinh ──
        st.markdown("---")
        st.markdown("#### ⚡ 10. Phát sinh")
        contingency = st.number_input("Dự phòng / tháng (₫)", min_value=0,
                                       value=2_000_000, step=500_000)

    # ══════════════════════ BUILD PRODUCT ══════════════════════

    product = ProductInput(
        sku=sku, product_name=product_name, cogs=cogs,
        packaging=PackagingCost(box_cost, foam_cost, glass_prot, tape_label),
        breakage_rate_pct=breakage,
        ads_livestream=AdsLivestreamCost(ads_ls_daily, ls_sessions, ls_orders),
        ads_page=AdsPageCost(ads_page_monthly, page_orders),
        staff=StaffTeam(members=staff_members, estimated_monthly_orders=monthly_orders),
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

    st.markdown(f"### 📊 Kết quả: **{sku}** — {product_name}")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🔴 Điểm hòa vốn (BEP)", format_vnd(bep))
    with m2:
        st.metric("🟡 Giá đề xuất (Biên 15%)", format_vnd(price_15))
    with m3:
        st.metric("🟢 Giá đề xuất (Biên 20%)", format_vnd(price_20))
    with m4:
        if price_20 != float('inf'):
            profit_20 = calc.pnl_at_price(price_20)["LỢI NHUẬN RÒNG"]
            st.metric("💵 LN ròng / đơn @20%", format_vnd(profit_20))

    st.markdown(f'<hr style="border: 1px solid {BRAND_RED};">', unsafe_allow_html=True)

    # ══════════════════════ TABS ══════════════════════

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 P&L chi tiết",
        "👥 Chi tiết nhân sự",
        "📊 Biểu đồ",
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

        st.markdown(f'<hr style="border: 1px solid {BRAND_RED_LIGHT};">', unsafe_allow_html=True)
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

    # ────── TAB 2: Staff Detail ──────
    with tab2:
        st.subheader("👥 Bảng chi phí nhân sự — từng người")
        st.caption(f"Phân bổ trên {monthly_orders} đơn / tháng")

        # Summary cards per person
        active_staff = [m for m in staff_members if m.active]
        if active_staff:
            cols = st.columns(min(len(active_staff), 4))
            for idx, member in enumerate(active_staff):
                col = cols[idx % len(cols)]
                label = f"{member.role}"
                if member.name:
                    label += f"\n({member.name})"
                per_unit = member.salary / monthly_orders if monthly_orders > 0 else 0
                with col:
                    st.markdown(f"""
                    <div style="background:{BRAND_RED_BG}; border:2px solid {BRAND_RED};
                                border-radius:10px; padding:15px; text-align:center; margin-bottom:10px;">
                        <div style="font-weight:700; color:{BRAND_RED_DARK}; font-size:0.9em;">
                            {member.role}</div>
                        <div style="color:#666; font-size:0.8em;">{member.name or '—'}</div>
                        <hr style="margin:8px 0; border-color:{BRAND_RED_LIGHT};">
                        <div style="font-size:0.85em;">Lương: <b>{format_vnd(member.salary)}</b></div>
                        <div style="font-size:0.85em;">Hoa hồng: <b>{member.commission_pct:.1f}%</b></div>
                        <hr style="margin:8px 0; border-color:{BRAND_RED_LIGHT};">
                        <div style="font-size:0.85em;">Phân bổ/đơn: <b style="color:{BRAND_RED};">{format_vnd(per_unit)}</b></div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### 📊 Bảng tổng hợp")
            ref_price = price_15 if price_15 != float('inf') else bep
            render_staff_detail_table(calc, ref_price)

            # Total row
            total_salary = product.staff.total_salary()
            total_per_unit = product.staff.fixed_cost_per_unit()
            total_comm_pct = product.staff.total_commission_pct()
            total_comm = product.staff.commission_per_unit(ref_price)

            st.markdown(f"""
            <div style="background:{BRAND_RED}; color:white; padding:12px 20px;
                        border-radius:8px; display:flex; justify-content:space-between;">
                <span><b>TỔNG LƯƠNG:</b> {format_vnd(total_salary)}/tháng</span>
                <span><b>PHÂN BỔ/ĐƠN:</b> {format_vnd(total_per_unit)}</span>
                <span><b>HOA HỒNG:</b> {total_comm_pct:.1f}% = {format_vnd(total_comm)}/đơn</span>
                <span><b>TỔNG NS/ĐƠN:</b> {format_vnd(total_per_unit + total_comm)}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Chưa có nhân viên nào được kích hoạt. Hãy bật ở sidebar.")

        # Staff cost as % of revenue
        st.markdown("---")
        st.subheader("📊 Tỷ trọng chi phí nhân sự trong giá bán")
        if price_15 != float('inf') and active_staff:
            staff_total_per_unit = total_per_unit + total_comm
            other_cost = calc._total_fixed_cost() - product.staff.fixed_cost_per_unit()

            fig_staff = go.Figure(go.Pie(
                labels=["Nhân sự (lương+HH)", "Chi phí khác", "Lợi nhuận"],
                values=[staff_total_per_unit, other_cost, price_15 * 15 / 100],
                marker=dict(colors=[BRAND_RED, "#FFB3BA", "#2ecc71"]),
                hole=0.5,
            ))
            fig_staff.update_layout(
                title="Cơ cấu giá bán (Biên 15%)",
                height=350, paper_bgcolor="#FFFFFF",
            )
            st.plotly_chart(fig_staff, use_container_width=True)

    # ────── TAB 3: Charts ──────
    with tab3:
        ch1, ch2 = st.columns(2)
        with ch1:
            render_pnl_waterfall(calc.pnl_at_price(price_15),
                                  f"Waterfall P&L — Biên 15% ({format_vnd(price_15)})")
        with ch2:
            render_cost_pie(calc.pnl_at_price(price_15))
        render_margin_curve(calc, bep)

    # ────── TAB 4: Sensitivity ──────
    with tab4:
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

            # Sensitivity on breakage
            st.markdown("---")
            st.subheader("📉 Tác động tỷ lệ hàng hỏng")
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
                    "Tỷ lệ hỏng": f"{br}%",
                    "CP hỏng / đơn": f"{cogs * br / 100:,.0f}",
                    "LN ròng": f"{tmp_pnl['LỢI NHUẬN RÒNG']:,.0f}",
                    "Biên LN": f"{tmp_pnl['BIÊN LỢI NHUẬN (%)']:.1f}%",
                })
            st.dataframe(pd.DataFrame(br_rows), use_container_width=True, hide_index=True)

            # Sensitivity on monthly orders
            st.markdown("---")
            st.subheader("📦 Tác động số đơn / tháng")
            ord_rows = []
            for mo in [50, 100, 150, 200, 300, 500, 800, 1000]:
                tmp = ProductInput(
                    sku=sku, product_name=product_name, cogs=cogs,
                    packaging=product.packaging, breakage_rate_pct=breakage,
                    ads_livestream=product.ads_livestream,
                    ads_page=product.ads_page,
                    staff=StaffTeam(members=staff_members, estimated_monthly_orders=mo),
                    premises=PremisesCost(warehouse, showroom, office, utilities, mo),
                    shipping=product.shipping, warranty=product.warranty,
                    contingency=ContingencyCost(contingency, mo),
                )
                tc = PricingCalculator(tmp)
                t_bep = tc.breakeven_price()
                tmp_pnl = tc.pnl_at_price(price_15)
                ord_rows.append({
                    "Đơn / tháng": f"{mo:,}",
                    "BEP": format_vnd(t_bep),
                    "LN ròng": f"{tmp_pnl['LỢI NHUẬN RÒNG']:,.0f}",
                    "Biên LN": f"{tmp_pnl['BIÊN LỢI NHUẬN (%)']:.1f}%",
                })
            st.dataframe(pd.DataFrame(ord_rows), use_container_width=True, hide_index=True)
        else:
            st.warning("Không thể tính BEP — hãy kiểm tra thông số đầu vào.")

    # ────── TAB 5: Multi-SKU ──────
    with tab5:
        st.subheader("📤 So sánh nhanh các SKU mẫu")
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
                "COGS": f"{pd_['cogs']:,.0f}",
                "BEP": format_vnd(t_bep),
                "Giá 15%": format_vnd(t_15),
                "Giá 20%": format_vnd(t_20),
                "LN/đơn @20%": format_vnd(t_20 * 20 / 100) if t_20 != float('inf') else "N/A",
            })
        st.dataframe(pd.DataFrame(multi_rows), use_container_width=True, hide_index=True)

    # ── Footer ──
    st.markdown(f"""
    <hr style="border: 2px solid {BRAND_RED};">
    <div style='text-align:center; color:{BRAND_RED_DARK}; font-size:0.85em; padding:10px 0;'>
    🔥 Pricing Engine v3.0 · {datetime.now().strftime('%d/%m/%Y %H:%M')} ·
    Dành cho nội bộ Công ty Gia dụng
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
