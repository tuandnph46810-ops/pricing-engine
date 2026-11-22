"""
╔══════════════════════════════════════════════════════════════════════╗
║  PRICING ENGINE v3.2 PRO — Unit Economics & Profit Architecture     ║
║  Dành cho Ban Điều Hành (CEO) Công ty Gia dụng (Bếp gas, Bếp từ)     ║
║  Thiết kế: White & Vibrant Red Theme (Độ tương phản cao, sắc nét)    ║
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
    page_title="Pricing Engine — Unit Economics Suite",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────── EXECUTIVE DESIGN SYSTEM ───────────────────────────
BRAND_RED = "#DC2626"       # Vibrant, modern executive red
BRAND_RED_HOVER = "#B91C1C"
BRAND_RED_LIGHT = "#FEE2E2"
BRAND_DARK = "#0F172A"      # Slate 900 (Deep, ultra-crisp text)
BRAND_MUTED = "#475569"     # Slate 600 (Secondary readable text)
BRAND_BORDER = "#E2E8F0"    # Crisp subtle border
BRAND_BG = "#F8FAFC"        # Clean off-white canvas

st.markdown(f"""
<style>
    /* ══════ TOÀN DIỆN HỆ THỐNG PHÔNG CHỮ & ĐỘ TƯƠNG PHẢN CAO ══════ */
    html, body, [class*="css"], .stMarkdown {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: {BRAND_DARK} !important;
    }}

    /* Nền ứng dụng chính */
    .stApp {{
        background-color: {BRAND_BG};
    }}

    /* ══════ SIDEBAR (THANH BÊN) ══════ */
    section[data-testid="stSidebar"] {{
        background-color: #FFFFFF !important;
        border-right: 1.5px solid {BRAND_BORDER} !important;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {{
        color: {BRAND_DARK} !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px !important;
    }}
    section[data-testid="stSidebar"] label,
    div[data-testid="stWidgetLabel"] label,
    div[data-testid="stWidgetLabel"] p {{
        color: {BRAND_DARK} !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }}
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] small {{
        color: {BRAND_MUTED} !important;
        font-weight: 500 !important;
    }}

    /* ══════ INPUTS VÀ SELECTBOX ══════ */
    .stTextInput input, 
    .stNumberInput input, 
    div[data-baseweb="select"] {{
        background-color: #FFFFFF !important;
        color: {BRAND_DARK} !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }}
    .stTextInput input:focus, 
    .stNumberInput input:focus {{
        border-color: {BRAND_RED} !important;
        box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.15) !important;
    }}
    div[data-baseweb="select"] * {{
        color: {BRAND_DARK} !important;
    }}

    /* ══════ METRIC CARDS (CHỈ SỐ TỔNG QUAN) ══════ */
    div[data-testid="stMetric"] {{
        background: #FFFFFF !important;
        border: 1.5px solid {BRAND_BORDER} !important;
        border-top: 4px solid {BRAND_RED} !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08) !important;
    }}
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] label {{
        color: {BRAND_MUTED} !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    div[data-testid="stMetricValue"] div {{
        color: {BRAND_DARK} !important;
        font-weight: 800 !important;
        font-size: 1.85rem !important;
    }}
    div[data-testid="stMetricDelta"] {{
        font-weight: 600 !important;
    }}

    /* ══════ TABS ══════ */
    button[data-baseweb="tab"] {{
        color: {BRAND_MUTED} !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 10px 20px !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {BRAND_RED} !important;
        border-bottom: 3px solid {BRAND_RED} !important;
        font-weight: 700 !important;
    }}

    /* ══════ EXPANDERS (KHUNG MỞ RỘNG) ══════ */
    div[data-testid="stExpander"] {{
        background-color: #FFFFFF !important;
        border: 1.5px solid {BRAND_BORDER} !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
    }}
    div[data-testid="stExpander"] summary {{
        color: {BRAND_DARK} !important;
        font-weight: 700 !important;
    }}
    div[data-testid="stExpander"] summary:hover {{
        color: {BRAND_RED} !important;
    }}

    /* ══════ NÚT BẤM (BUTTONS) ══════ */
    .stButton > button,
    .stDownloadButton > button {{
        background-color: {BRAND_RED} !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 8px 18px !important;
        box-shadow: 0 2px 4px rgba(220, 38, 38, 0.25) !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:hover,
    .stDownloadButton > button:hover {{
        background-color: {BRAND_RED_HOVER} !important;
        box-shadow: 0 4px 10px rgba(220, 38, 38, 0.35) !important;
    }}

    /* ══════ BẢNG DỮ LIỆU DATAFRAME ══════ */
    .stDataFrame {{
        border-radius: 8px;
        overflow: hidden;
        border: 1.5px solid {BRAND_BORDER};
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
    """Đại diện cho 1 nhân viên cụ thể."""
    role: str = ""
    name: str = ""
    salary: float = 0.0
    commission_pct: float = 0.0
    active: bool = False


@dataclass
class StaffTeam:
    """Đội ngũ nhân sự — từng vị trí độc lập."""
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

    def salary_breakdown_per_unit(self) -> list[tuple[str, float, float]]:
        result = []
        for m in self.members:
            if m.active and m.salary > 0:
                label = f"{m.role} ({m.name})" if m.name else m.role
                per_unit = m.salary / self.estimated_monthly_orders if self.estimated_monthly_orders > 0 else 0
                result.append((label, per_unit, m.salary))
        return result

    def commission_breakdown_per_unit(self, selling_price: float) -> list[tuple[str, float, float]]:
        result = []
        for m in self.members:
            if m.active and m.commission_pct > 0:
                label = f"{m.role} ({m.name})" if m.name else m.role
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

        result = {"Doanh thu (Giá bán)": selling_price}
        result.update(breakdown)
        result["⑪ Hoa hồng nhân viên"] = commission
        result["TỔNG CHI PHÍ"] = total_cost
        result["LỢI NHUẬN RÒNG"] = net_profit
        result["BIÊN LỢI NHUẬN (%)"] = margin_pct
        return result


# ─────────────────────────── PRESETS ───────────────────────────

SAMPLE_PRODUCTS = {
    "BG-001 — Bếp gas đôi kính cường lực": {
        "cogs": 850_000, "box": 35_000, "foam": 25_000, "glass": 15_000, "tape": 5_000,
    },
    "BG-002 — Bếp gas đơn inox": {
        "cogs": 420_000, "box": 25_000, "foam": 15_000, "glass": 0, "tape": 5_000,
    },
    "BT-001 — Bếp từ đôi âm": {
        "cogs": 1_500_000, "box": 45_000, "foam": 35_000, "glass": 20_000, "tape": 5_000,
    },
    "BT-002 — Bếp từ đơn di động": {
        "cogs": 650_000, "box": 20_000, "foam": 15_000, "glass": 10_000, "tape": 5_000,
    },
    "🔧 Nhập tùy chỉnh": {
        "cogs": 0, "box": 0, "foam": 0, "glass": 0, "tape": 0,
    },
}

DEFAULT_STAFF = [
    {"role": "NV Livestream 1", "name": "Thảo", "salary": 7_000_000, "commission": 1.0, "active": True},
    {"role": "NV Livestream 2", "name": "Minh", "salary": 7_000_000, "commission": 1.0, "active": True},
    {"role": "NV Chăm sóc KH", "name": "Hương", "salary": 6_000_000, "commission": 0.0, "active": True},
    {"role": "NV Quản lý",     "name": "Tùng",  "salary": 10_000_000, "commission": 0.0, "active": True},
    {"role": "NV Kỹ thuật / Kho", "name": "", "salary": 0, "commission": 0.0, "active": False},
    {"role": "Vị trí bổ sung 1", "name": "", "salary": 0, "commission": 0.0, "active": False},
    {"role": "Vị trí bổ sung 2", "name": "", "salary": 0, "commission": 0.0, "active": False},
]


def format_vnd(value: float) -> str:
    if value == float('inf') or value != value:
        return "∞ Không khả thi"
    return f"{value:,.0f} ₫"


# ─────────────────────────── UI RENDERERS ───────────────────────────

def render_executive_pnl_table(calc: PricingCalculator, bep: float, p15: float, p20: float, custom_p: float = 0):
    """Bảng so sánh P&L tổng thể đa kịch bản với độ tương phản cao."""
    scenarios = [
        ("🔴 Hòa vốn (BEP)", bep),
        ("🟡 Biên 15%", p15),
        ("🟢 Biên 20%", p20),
    ]
    if custom_p > 0:
        scenarios.append(("🎯 Giá tùy chọn", custom_p))

    pnls = [calc.pnl_at_price(price) for _, price in scenarios]

    items = [
        ("DOANH THU & GIÁ BÁN", [("Doanh thu (Giá bán)", lambda p: format_vnd(p["Doanh thu (Giá bán)"]))]),
        ("GIÁ VỐN & ĐÓNG GÓI CHỐNG VỠ", [
            ("① Giá nhập (COGS)", lambda p: format_vnd(p["① Giá nhập (COGS)"])),
            ("② Bao bì đóng gói chống sốc", lambda p: format_vnd(p["② Bao bì đóng gói chống sốc"])),
            ("③ Dự phòng hỏng / vỡ kính (5%)", lambda p: format_vnd(p["③ Dự phòng hàng hỏng / vỡ kính"])),
        ]),
        ("CHI PHÍ BÁN HÀNG & MARKETING", [
            ("④ Chi phí Ads Livestream", lambda p: format_vnd(p["④ Chi phí Ads Livestream"])),
            ("⑤ Chi phí Ads Page", lambda p: format_vnd(p["⑤ Chi phí Ads Page"])),
        ]),
        ("CHI PHÍ NHÂN SỰ TỪNG VỊ TRÍ", [
            ("⑥ Lương cố định nhân viên", lambda p: format_vnd(p["⑥ Lương nhân sự (phân bổ)"])),
            ("⑪ Hoa hồng bán hàng", lambda p: format_vnd(p["⑪ Hoa hồng nhân viên"])),
        ]),
        ("VẬN HÀNH & HẬU MÃI", [
            ("⑦ Chi phí mặt bằng phân bổ", lambda p: format_vnd(p["⑦ Chi phí mặt bằng (phân bổ)"])),
            ("⑧ Chi phí vận chuyển & hoàn hàng", lambda p: format_vnd(p["⑧ Chi phí vận chuyển"])),
            ("⑨ Chi phí bảo hành sản phẩm", lambda p: format_vnd(p["⑨ Chi phí bảo hành"])),
            ("⑩ Chi phí dự phòng phát sinh", lambda p: format_vnd(p["⑩ Chi phí phát sinh (phân bổ)"])),
        ]),
        ("KẾT QUẢ KINH DOANH DỰ KIẾN", [
            ("TỔNG CHI PHÍ / ĐƠN", lambda p: format_vnd(p["TỔNG CHI PHÍ"])),
            ("LỢI NHUẬN RÒNG / ĐƠN", lambda p: format_vnd(p["LỢI NHUẬN RÒNG"])),
            ("TỶ SUẤT BIÊN LN (%)", lambda p: f"{p['BIÊN LỢI NHUẬN (%)']:.1f}%"),
        ])
    ]

    html = f"""
    <div style="background:#FFFFFF; border:1.5px solid {BRAND_BORDER}; border-radius:12px; overflow:hidden; box-shadow:0 4px 6px -1px rgba(0,0,0,0.05); margin-top:10px;">
        <table style="width:100%; border-collapse:collapse; text-align:left; font-size:0.95rem;">
            <thead>
                <tr style="background:#0F172A; color:#FFFFFF;">
                    <th style="padding:14px 18px; font-weight:700; width:38%;">Khoản mục kinh tế (Unit Economics)</th>
    """
    for name, _ in scenarios:
        html += f"""<th style="padding:14px 18px; text-align:right; font-weight:700; color:#FFFFFF;">{name}</th>"""
    html += "</tr></thead><tbody>"

    for group_name, row_items in items:
        is_summary = group_name == "KẾT QUẢ KINH DOANH DỰ KIẾN"
        group_bg = "#FEF2F2" if is_summary else "#F1F5F9"
        group_color = BRAND_RED if is_summary else BRAND_DARK
        
        html += f"""
        <tr style="background:{group_bg};">
            <td colspan="{len(scenarios) + 1}" style="padding:10px 18px; font-weight:800; color:{group_color}; letter-spacing:0.3px; border-top:1px solid {BRAND_BORDER};">
                {group_name}
            </td>
        </tr>
        """
        for label, val_func in row_items:
            is_profit_row = "LỢI NHUẬN RÒNG" in label or "BIÊN LN" in label
            is_cost_row = "TỔNG CHI PHÍ" in label
            
            row_style = ""
            if is_profit_row:
                row_style = "background:#F0FDF4; font-weight:700;"
            elif is_cost_row:
                row_style = "background:#FFF1F2; font-weight:700;"
            
            html += f"""<tr style="border-bottom:1px solid #F1F5F9; {row_style}">
                <td style="padding:10px 18px; color:{BRAND_DARK};">{label}</td>
            """
            for p in pnls:
                val_text = val_func(p)
                text_color = BRAND_DARK
                if is_profit_row:
                    text_color = "#15803D" if p["LỢI NHUẬN RÒNG"] >= 0 else BRAND_RED
                elif is_cost_row:
                    text_color = BRAND_RED
                
                html += f"""<td style="padding:10px 18px; text-align:right; font-weight:{'800' if is_profit_row or is_cost_row else '600'}; color:{text_color};">{val_text}</td>"""
            html += "</tr>"

    html += "</tbody></table></div>"
    st.markdown(html, unsafe_allow_html=True)


def render_pnl_waterfall(pnl: dict, title: str):
    cost_keys = [k for k in pnl if k[0] in "①②③④⑤⑥⑦⑧⑨⑩⑪"]
    short_labels = {
        "①": "COGS", "②": "Bao bì", "③": "Hỏng/vỡ kính",
        "④": "Ads Live", "⑤": "Ads Page", "⑥": "Lương NS",
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

    labels.append("Lợi nhuận ròng")
    values.append(pnl["LỢI NHUẬN RÒNG"])
    measures.append("total")

    fig = go.Figure(go.Waterfall(
        x=labels, y=values, measure=measures,
        textposition="outside",
        text=[format_vnd(abs(v)) for v in values],
        connector={"line": {"color": "#94A3B8"}},
        increasing={"marker": {"color": "#16A34A"}},
        decreasing={"marker": {"color": BRAND_RED}},
        totals={"marker": {"color": "#16A34A" if pnl["LỢI NHUẬN RÒNG"] >= 0 else BRAND_RED}},
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(color=BRAND_DARK, size=15, weight=700)),
        showlegend=False, height=440,
        margin=dict(t=50, b=50, l=40, r=40),
        xaxis_tickangle=-30,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color=BRAND_DARK, family="sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_cost_pie(pnl: dict):
    short_labels = {
        "①": "COGS", "②": "Bao bì", "③": "Hỏng/vỡ",
        "④": "Ads Live", "⑤": "Ads Page", "⑥": "Lương NS",
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

    palette = [
        "#DC2626", "#EF4444", "#F87171", "#FCA5A5",
        "#0F172A", "#334155", "#64748B", "#94A3B8",
        "#EA580C", "#F59E0B", "#10B981"
    ]
    fig = px.pie(names=labels, values=values, title="Cơ cấu chi phí đơn hàng",
                 hole=0.45, color_discrete_sequence=palette)
    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
    fig.update_layout(
        height=440, margin=dict(t=50, b=20, l=20, r=20),
        plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        font=dict(color=BRAND_DARK, family="sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_margin_curve(calc: PricingCalculator, bep: float):
    if bep == float('inf') or bep <= 0:
        return
    prices = [bep * r / 100 for r in range(60, 201, 5)]
    margins = [calc.pnl_at_price(p)["BIÊN LỢI NHUẬN (%)"] for p in prices]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=prices, y=margins, mode='lines+markers',
        name='Biên LN Ròng (%)',
        line=dict(color=BRAND_RED, width=3),
        marker=dict(size=5, color=BRAND_RED)
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="#64748B", annotation_text="Hòa vốn (0%)")
    fig.add_hline(y=15, line_dash="dot", line_color="#F59E0B", annotation_text="Mục tiêu 15%")
    fig.add_hline(y=20, line_dash="dot", line_color="#10B981", annotation_text="Mục tiêu 20%")
    fig.add_vline(x=bep, line_dash="dash", line_color=BRAND_RED, annotation_text=f"BEP: {format_vnd(bep)}")
    fig.update_layout(
        title=dict(text="Đường cong độ co giãn Biên lợi nhuận theo Giá bán", font=dict(color=BRAND_DARK, size=15, weight=700)),
        xaxis_title="Giá bán ra thị trường (VNĐ)",
        yaxis_title="Biên lợi nhuận ròng (%)",
        height=400, plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
        font=dict(color=BRAND_DARK, family="sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────── MAIN APPLICATION ───────────────────────────

def main():
    # ── Executive Top Banner ──
    st.markdown(f"""
    <div style="background:#FFFFFF; border:1.5px solid {BRAND_BORDER}; border-left:6px solid {BRAND_RED};
                padding:20px 24px; border-radius:12px; margin-bottom:20px;
                box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div>
                <span style="font-size:1.8rem; font-weight:900; color:{BRAND_DARK}; letter-spacing:-0.5px;">
                    🔥 PRICING ENGINE <span style="color:{BRAND_RED};">PRO</span>
                </span>
                <span style="background:{BRAND_RED_LIGHT}; color:{BRAND_RED}; font-size:0.75rem; font-weight:700; padding:3px 8px; border-radius:6px; margin-left:8px; vertical-align:middle;">
                    v3.2 EXECUTIVE
                </span>
                <div style="font-size:0.95rem; font-weight:500; color:{BRAND_MUTED}; margin-top:4px;">
                    Hệ thống tính toán Unit Economics & Kiến trúc định giá sản phẩm Gia dụng (Bếp gas, Bếp từ)
                </div>
            </div>
            <div style="text-align:right; font-size:0.85rem; color:{BRAND_MUTED};">
                <b>Kênh bán:</b> Livestream · Page Ads · Showroom<br>
                <b>Cập nhật:</b> {datetime.now().strftime('%d/%m/%Y')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════ SIDEBAR (THAM SỐ ĐẦU VÀO) ══════════════════════
    with st.sidebar:
        st.markdown(f"### ⚙️ THIẾT LẬP THAM SỐ")

        # ── Sản phẩm ──
        st.markdown("#### 📦 1. Mã sản phẩm")
        selected = st.selectbox("Chọn mẫu sản phẩm gia dụng", options=list(SAMPLE_PRODUCTS.keys()))
        preset = SAMPLE_PRODUCTS[selected]
        sku = st.text_input("Mã SKU", value=selected.split(" — ")[0] if " — " in selected else "SKU-01")
        product_name = st.text_input("Tên sản phẩm", value=selected.split(" — ")[1] if " — " in selected else "Bếp Gia Dụng")

        st.markdown("---")
        # ── Sản lượng ──
        st.markdown("#### 📊 2. Sản lượng bán / tháng")
        monthly_orders = st.number_input("Tổng đơn hàng dự kiến / tháng", min_value=1, value=200, step=10,
                                          help="Dùng để chia đều chi phí cố định (mặt bằng, lương cơ bản, ads...)")

        st.markdown("---")
        # ── Giá vốn & Đóng gói ──
        st.markdown("#### 💰 3. Giá vốn & Đóng gói")
        cogs = st.number_input("Giá nhập kho (COGS) (₫)", min_value=0, value=preset["cogs"], step=10_000)

        c1, c2 = st.columns(2)
        with c1:
            box_cost = st.number_input("Thùng carton", min_value=0, value=preset["box"], step=5_000)
            glass_prot = st.number_input("Bảo vệ kính", min_value=0, value=preset["glass"], step=5_000)
        with c2:
            foam_cost = st.number_input("Xốp chống sốc", min_value=0, value=preset["foam"], step=5_000)
            tape_label = st.number_input("Băng keo, tem", min_value=0, value=preset["tape"], step=1_000)

        breakage = st.slider("Dự phòng bể vỡ / hỏng kính (%)", 0.0, 20.0, 5.0, 0.5,
                             help="Mặc định 5% giá trị COGS do đặc thù mặt kính cường lực bếp gas/từ")

        st.markdown("---")
        # ── Marketing & Ads ──
        st.markdown("#### 📺 4. Chi phí Marketing & Ads")
        ads_ls_daily = st.number_input("Ngân sách Ads mồi Live / ngày (₫)", min_value=0, value=500_000, step=50_000)
        c3, c4 = st.columns(2)
        with c3:
            ls_sessions = st.number_input("Phiên Live / tháng", min_value=1, value=20)
        with c4:
            ls_orders = st.number_input("Đơn TB / phiên", min_value=1, value=10)

        ads_page_monthly = st.number_input("Ngân sách Ads Page (FB/TikTok) / tháng (₫)", min_value=0, value=5_000_000, step=500_000)
        page_orders = st.number_input("Số đơn chốt từ Page / tháng", min_value=1, value=50, step=5)

        st.markdown("---")
        # ── Nhân sự (Tách biệt từng người) ──
        st.markdown("#### 👥 5. Chi phí Nhân sự (Từng vị trí)")
        st.caption("Cấu hình lương & hoa hồng độc lập cho từng bạn:")

    staff_members = []
    with st.sidebar:
        for i, default in enumerate(DEFAULT_STAFF):
            is_open = i < 4
            status_icon = "🟢" if default["active"] else "⚪"
            with st.expander(f"{status_icon} {default['role']}", expanded=is_open):
                active = st.checkbox("Kích hoạt tính lương", value=default["active"], key=f"st_act_{i}")
                role = st.text_input("Chức danh", value=default["role"], key=f"st_rol_{i}")
                name = st.text_input("Tên nhân sự", value=default["name"], key=f"st_nam_{i}", placeholder="Họ và tên...")
                salary = st.number_input("Lương cứng / tháng (₫)", min_value=0, value=default["salary"], step=500_000, key=f"st_sal_{i}")
                comm = st.number_input("Hoa hồng (% DT)", min_value=0.0, value=default["commission"], step=0.5, key=f"st_com_{i}")

                staff_members.append(StaffMember(role=role, name=name, salary=salary, commission_pct=comm, active=active))

        st.markdown("---")
        # ── Mặt bằng & Vận hành ──
        st.markdown("#### 🏠 6. Mặt bằng & Vận hành")
        c5, c6 = st.columns(2)
        with c5:
            warehouse = st.number_input("Thuê kho / tháng", min_value=0, value=5_000_000, step=500_000)
            showroom = st.number_input("Showroom / tháng", min_value=0, value=8_000_000, step=500_000)
        with c6:
            office = st.number_input("Văn phòng / tháng", min_value=0, value=0, step=500_000)
            utilities = st.number_input("Điện, nước, net", min_value=0, value=3_000_000, step=500_000)

        st.markdown("---")
        # ── Vận chuyển & Bảo hành ──
        st.markdown("#### 🚚 7. Vận chuyển, BH & Phát sinh")
        c7, c8 = st.columns(2)
        with c7:
            ship_in = st.number_input("Nhập kho / SP", min_value=0, value=10_000, step=5_000)
            ship_out = st.number_input("Ship đến KH / đơn", min_value=0, value=30_000, step=5_000)
        with c8:
            return_rate = st.number_input("Tỷ lệ hoàn (%)", min_value=0.0, value=3.0, step=0.5)
            return_ship = st.number_input("Phí hoàn / đơn", min_value=0, value=30_000, step=5_000)

        c9, c10 = st.columns(2)
        with c9:
            warranty_rate = st.number_input("Tỷ lệ BH (%)", min_value=0.0, value=3.0, step=0.5)
            repair_cost = st.number_input("Phí sửa / vụ", min_value=0, value=100_000, step=10_000)
        with c10:
            replace_cost = st.number_input("Phí đổi mới / vụ", min_value=0, value=0, step=50_000)
            replace_ratio = st.number_input("% Đổi mới", min_value=0.0, value=10.0, step=5.0)

        contingency = st.number_input("Dự phòng phát sinh / tháng (₫)", min_value=0, value=2_000_000, step=500_000)

    # ══════════════════════ OBJECT COMPILATION ══════════════════════
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
    bep = calc.breakeven_price()
    p15 = calc.price_for_margin(15)
    p20 = calc.price_for_margin(20)

    # ══════════════════════ EXECUTIVE KPI CARDS ══════════════════════
    st.markdown(f"#### 🎯 CHỈ SỐ GIÁ MỤC TIÊU: <span style='color:{BRAND_RED};'>{sku}</span> — {product_name}", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="🔴 ĐIỂM HÒA VỐN (BEP)",
            value=format_vnd(bep),
            help="Mức giá bán tối thiểu thu hồi đủ toàn bộ giá vốn, chi phí ads, mặt bằng và nhân sự."
        )
    with col2:
        diff_15 = p15 - bep if (p15 != float('inf') and bep != float('inf')) else 0
        st.metric(
            label="🟡 GIÁ ĐỀ XUẤT (BIÊN 15%)",
            value=format_vnd(p15),
            delta=f"+{format_vnd(diff_15)} chênh hòa vốn" if diff_15 > 0 else None,
            help="Mức giá an toàn đảm bảo biên lợi nhuận ròng 15% sau khi trừ hết chi phí."
        )
    with col3:
        diff_20 = p20 - bep if (p20 != float('inf') and bep != float('inf')) else 0
        st.metric(
            label="🟢 GIÁ ĐỀ XUẤT (BIÊN 20%)",
            value=format_vnd(p20),
            delta=f"+{format_vnd(diff_20)} chênh hòa vốn" if diff_20 > 0 else None,
            help="Mức giá mục tiêu tối ưu cho doanh nghiệp đạt biên ròng 20%."
        )
    with col4:
        profit_20 = calc.pnl_at_price(p20)["LỢI NHUẬN RÒNG"] if p20 != float('inf') else 0
        st.metric(
            label="💵 LỢI NHUẬN RÒNG / ĐƠN (@20%)",
            value=format_vnd(profit_20),
            help="Số tiền lãi ròng thực tế công ty giữ lại trên mỗi sản phẩm bán ra ở mức giá biên 20%."
        )

    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    # ══════════════════════ TABS PHÂN TÍCH CHUYÊN SÂU ══════════════════════
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Bảng P&L So Sánh Dự Kiến",
        "👥 Chi Tiết Từng Nhân Sự",
        "📊 Biểu Đồ Cơ Cấu & Xu Hướng",
        "🔍 Ma Trận Độ Nhạy Lợi Nhuận",
        "📤 Bảng So Sánh Toàn Bộ SKU",
    ])

    # ────────────────────────── TAB 1: P&L SO SÁNH ──────────────────────────
    with tab1:
        st.markdown("##### 💼 BẢNG CÂN ĐỐI LÃI LỖ ĐA KỊCH BẢN (P&L COMPARATIVE STATEMENT)")
        st.caption("Xem và đối soát trực tiếp các dòng chi phí giữa 3 kịch bản giá bán đề xuất.")

        # Thêm phần giả lập giá tùy chọn
        c_cust1, c_cust2 = st.columns([2, 5])
        with c_cust1:
            custom_input_price = st.number_input(
                "🎯 Nhập giá bán giả định của bạn (₫):",
                min_value=0,
                value=int(p15) if p15 != float('inf') else 0,
                step=10_000,
                key="custom_price_tab1"
            )
        with c_cust2:
            if custom_input_price > 0:
                custom_pnl = calc.pnl_at_price(custom_input_price)
                c_profit = custom_pnl["LỢI NHUẬN RÒNG"]
                c_margin = custom_pnl["BIÊN LỢI NHUẬN (%)"]
                badge_bg = "#DCFCE7" if c_profit >= 0 else "#FEE2E2"
                badge_color = "#15803D" if c_profit >= 0 else "#DC2626"
                st.markdown(f"""
                <div style="background:{badge_bg}; border:1px solid {badge_color}; border-radius:8px; padding:10px 16px; margin-top:24px;">
                    <span style="font-weight:700; color:{badge_color};">Kết quả giá giả định:</span>
                    Lợi nhuận ròng: <b>{format_vnd(c_profit)}/đơn</b> &nbsp;|&nbsp; Biên lợi nhuận: <b>{c_margin:.1f}%</b>
                </div>
                """, unsafe_allow_html=True)

        render_executive_pnl_table(calc, bep, p15, p20, custom_input_price)

    # ────────────────────────── TAB 2: CHI TIẾT NHÂN SỰ ──────────────────────────
    with tab2:
        st.markdown("##### 👥 CƠ CẤU CHI PHÍ LƯƠNG & HOA HỒNG TỪNG NHÂN SỰ")
        st.caption(f"Chi phí nhân sự được chia đều dựa trên tổng sản lượng dự kiến: **{monthly_orders} đơn / tháng**.")

        active_members = [m for m in staff_members if m.active]
        if active_members:
            # Grid of distinct staff cards
            cols = st.columns(len(active_members) if len(active_members) <= 4 else 4)
            for idx, m in enumerate(active_members):
                col = cols[idx % len(cols)]
                per_unit = m.salary / monthly_orders if monthly_orders > 0 else 0
                comm_at_p15 = p15 * (m.commission_pct / 100) if p15 != float('inf') else 0
                total_m_unit = per_unit + comm_at_p15

                with col:
                    st.markdown(f"""
                    <div style="background:#FFFFFF; border:1.5px solid {BRAND_BORDER}; border-top:4px solid {BRAND_RED};
                                border-radius:10px; padding:16px; margin-bottom:12px; box-shadow:0 2px 4px rgba(0,0,0,0.04);">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:800; font-size:1rem; color:{BRAND_DARK};">{m.role}</span>
                            <span style="background:#DCFCE7; color:#15803D; font-size:0.75rem; font-weight:700; padding:2px 6px; border-radius:4px;">🟢 Đang tính</span>
                        </div>
                        <div style="font-size:0.88rem; font-weight:600; color:{BRAND_MUTED}; margin-top:2px;">
                            Họ tên: <b style="color:{BRAND_DARK};">{m.name or 'Chưa nhập'}</b>
                        </div>
                        <div style="height:1px; background:{BRAND_BORDER}; margin:10px 0;"></div>
                        <div style="font-size:0.85rem; color:{BRAND_DARK};">
                            • Lương cơ bản: <b>{format_vnd(m.salary)}/th</b><br>
                            • Hoa hồng: <b style="color:{BRAND_RED};">{m.commission_pct:.1f}% DT</b><br>
                            • Lương chia đều: <b>{format_vnd(per_unit)}/đơn</b><br>
                            • HH tại giá 15%: <b>{format_vnd(comm_at_p15)}/đơn</b>
                        </div>
                        <div style="height:1px; background:{BRAND_BORDER}; margin:10px 0;"></div>
                        <div style="font-size:0.85rem; font-weight:700; color:{BRAND_DARK}; text-align:right;">
                            Tổng chi / đơn: <span style="color:{BRAND_RED}; font-size:0.95rem;">{format_vnd(total_m_unit)}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Executive Staff Total Bar
            tot_sal = product.staff.total_salary()
            tot_fix_unit = product.staff.fixed_cost_per_unit()
            tot_comm_pct = product.staff.total_commission_pct()
            tot_comm_unit = product.staff.commission_per_unit(p15) if p15 != float('inf') else 0

            st.markdown(f"""
            <div style="background:#0F172A; color:#FFFFFF; padding:16px 24px; border-radius:10px; margin-top:10px;
                        display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
                <div>
                    <span style="font-size:0.85rem; color:#94A3B8; text-transform:uppercase; font-weight:700;">Tổng quỹ lương cứng</span><br>
                    <span style="font-size:1.3rem; font-weight:800; color:#FFFFFF;">{format_vnd(tot_sal)} / tháng</span>
                </div>
                <div>
                    <span style="font-size:0.85rem; color:#94A3B8; text-transform:uppercase; font-weight:700;">Lương cứng / Đơn</span><br>
                    <span style="font-size:1.3rem; font-weight:800; color:#F87171;">{format_vnd(tot_fix_unit)}</span>
                </div>
                <div>
                    <span style="font-size:0.85rem; color:#94A3B8; text-transform:uppercase; font-weight:700;">Tổng % Hoa hồng</span><br>
                    <span style="font-size:1.3rem; font-weight:800; color:#38BDF8;">{tot_comm_pct:.1f}% ({format_vnd(tot_comm_unit)}/đơn)</span>
                </div>
                <div>
                    <span style="font-size:0.85rem; color:#94A3B8; text-transform:uppercase; font-weight:700;">Tổng chi phí nhân sự / đơn</span><br>
                    <span style="font-size:1.4rem; font-weight:900; color:#4ADE80;">{format_vnd(tot_fix_unit + tot_comm_unit)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Chưa có nhân sự nào được tích chọn kích hoạt ở thanh bên trái.")

    # ────────────────────────── TAB 3: BIỂU ĐỒ TRỰC QUAN ──────────────────────────
    with tab3:
        st.markdown("##### 📊 MÔ HÌNH HÓA DÒNG TIỀN & BIÊN LỢI NHUẬN")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            render_pnl_waterfall(calc.pnl_at_price(p15), f"Biểu đồ Thác Nước P&L tại Giá 15% ({format_vnd(p15)})")
        with col_g2:
            render_cost_pie(calc.pnl_at_price(p15))

        render_margin_curve(calc, bep)

    # ────────────────────────── TAB 4: ĐỘ NHẠY LỢI NHUẬN ──────────────────────────
    with tab4:
        st.markdown("##### 🔍 PHÂN TÍCH ĐỘ NHẠY VÀ KỊCH BẢN RỦI RO")
        
        if bep != float('inf') and bep > 0:
            st.markdown("###### 1. Bảng nhạy cảm: Giá bán thị trường tác động đến Lãi/Lỗ")
            step = max(10_000, round(bep * 0.05 / 10_000) * 10_000)
            price_range = [p for p in [bep + step * i for i in range(-4, 10)] if p > 0]

            rows_sen = []
            for p in price_range:
                pnl = calc.pnl_at_price(p)
                profit = pnl['LỢI NHUẬN RÒNG']
                margin = pnl['BIÊN LỢI NHUẬN (%)']
                status = "🟢 Lãi tốt" if margin >= 15 else "🟡 Lãi mỏng" if profit > 0 else "🔴 Lỗ vốn"
                rows_sen.append({
                    "Giá bán thị trường (₫)": f"{p:,.0f}",
                    "Tổng chi phí / đơn (₫)": f"{pnl['TỔNG CHI PHÍ']:,.0f}",
                    "Lợi nhuận ròng / đơn (₫)": f"{profit:,.0f}",
                    "Biên lợi nhuận ròng (%)": f"{margin:.1f}%",
                    "Đánh giá rủi ro": status,
                })
            st.dataframe(pd.DataFrame(rows_sen), use_container_width=True, hide_index=True)

            st.markdown("---")
            c_sen1, c_sen2 = st.columns(2)
            with c_sen1:
                st.markdown("###### 2. Tác động của Tỷ lệ Hỏng / Vỡ kính cường lực")
                st.caption(f"Khảo sát tại mức giá đề xuất {format_vnd(p15)} (Biên 15%)")
                br_rows = []
                for br in [1, 2, 3, 5, 7, 10, 15]:
                    tmp = ProductInput(
                        sku=sku, product_name=product_name, cogs=cogs,
                        packaging=product.packaging, breakage_rate_pct=br,
                        ads_livestream=product.ads_livestream,
                        ads_page=product.ads_page, staff=product.staff,
                        premises=product.premises, shipping=product.shipping,
                        warranty=product.warranty, contingency=product.contingency,
                    )
                    tmp_pnl = PricingCalculator(tmp).pnl_at_price(p15)
                    br_rows.append({
                        "Tỷ lệ vỡ kính": f"{br}%",
                        "Phí hỏng/đơn (₫)": f"{cogs * br / 100:,.0f}",
                        "Lãi ròng/đơn (₫)": f"{tmp_pnl['LỢI NHUẬN RÒNG']:,.0f}",
                        "Biên ròng (%)": f"{tmp_pnl['BIÊN LỢI NHUẬN (%)']:.1f}%",
                    })
                st.dataframe(pd.DataFrame(br_rows), use_container_width=True, hide_index=True)

            with c_sen2:
                st.markdown("###### 3. Hiệu ứng quy mô: Sản lượng bán / tháng")
                st.caption(f"Khi scale đơn hàng, chi phí cố định (lương, mặt bằng...) giảm mạnh")
                scale_rows = []
                for mo in [100, 200, 300, 500, 800, 1000]:
                    tmp = ProductInput(
                        sku=sku, product_name=product_name, cogs=cogs,
                        packaging=product.packaging, breakage_rate_pct=breakage,
                        ads_livestream=product.ads_livestream, ads_page=product.ads_page,
                        staff=StaffTeam(members=staff_members, estimated_monthly_orders=mo),
                        premises=PremisesCost(warehouse, showroom, office, utilities, mo),
                        shipping=product.shipping, warranty=product.warranty,
                        contingency=ContingencyCost(contingency, mo),
                    )
                    tc = PricingCalculator(tmp)
                    t_bep = tc.breakeven_price()
                    scale_rows.append({
                        "Sản lượng (đơn/tháng)": f"{mo:,}",
                        "Điểm hòa vốn (₫)": format_vnd(t_bep),
                        "Giá bán đạt 15% (₫)": format_vnd(tc.price_for_margin(15)),
                        "Giá bán đạt 20% (₫)": format_vnd(tc.price_for_margin(20)),
                    })
                st.dataframe(pd.DataFrame(scale_rows), use_container_width=True, hide_index=True)

    # ────────────────────────── TAB 5: ĐA SKU ──────────────────────────
    with tab5:
        st.markdown("##### 📤 MA TRẬN ĐỊNH GIÁ TOÀN BỘ DANH MỤC SẢN PHẨM MẪU")
        st.caption("Áp dụng đồng bộ cấu trúc chi phí vận hành, marketing và nhân sự cho từng mã hàng:")

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
                "Mã SKU": tmp.sku,
                "Dòng sản phẩm": tmp.product_name,
                "Giá nhập (COGS)": f"{pd_['cogs']:,.0f} ₫",
                "Điểm hòa vốn (BEP)": format_vnd(t_bep),
                "Giá đề xuất (Biên 15%)": format_vnd(t_15),
                "Giá đề xuất (Biên 20%)": format_vnd(t_20),
                "Lãi ròng / đơn (@20%)": format_vnd(t_20 * 0.2) if t_20 != float('inf') else "N/A",
            })
        st.dataframe(pd.DataFrame(multi_rows), use_container_width=True, hide_index=True)

    # ── Executive Footer ──
    st.markdown(f"""
    <div style="background:#0F172A; border-radius:10px; padding:14px 20px; margin-top:35px;
                display:flex; justify-content:space-between; align-items:center; color:#94A3B8; font-size:0.85rem;">
        <div>🔥 <b>Pricing Engine Executive Suite v3.2</b> · Thiết kế chuẩn thẩm mỹ cao cấp</div>
        <div>Lưu hành nội bộ Ban Giám Đốc Công ty Gia Dụng</div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
