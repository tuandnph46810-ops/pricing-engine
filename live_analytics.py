"""
╔══════════════════════════════════════════════════════════════════════╗
║  LIVE ANALYTICS DASHBOARD                                          ║
║  Phân tích số liệu phòng Livestream                                ║
║  Dành cho ngành Gia dụng (Bếp gas, Bếp từ)                        ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
import io

# ─────────────────────────── CONFIG ───────────────────────────
st.set_page_config(
    page_title="Live Analytics Dashboard",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

ALERT_THRESHOLD_PCT = 8.0  # Ngưỡng cảnh báo hủy đơn / hoàn hàng (%)

SAMPLE_CSV = os.path.join(os.path.dirname(__file__), "sample_live_data.csv")

EXPECTED_COLUMNS = [
    "date", "session_id", "staff_name", "start_time", "end_time",
    "duration_minutes", "total_viewers", "peak_ccu", "avg_ccu",
    "cart_clicks", "total_orders", "completed_orders",
    "cancelled_orders", "returned_orders", "revenue",
    "products_sold", "new_followers", "comments", "shares", "likes",
    "platform",
]


# ─────────────────────────── HELPERS ───────────────────────────

def format_vnd(v: float) -> str:
    if abs(v) >= 1_000_000_000:
        return f"{v / 1_000_000_000:,.1f} tỷ"
    if abs(v) >= 1_000_000:
        return f"{v / 1_000_000:,.1f} tr"
    return f"{v:,.0f} ₫"


def format_number(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"{v / 1_000_000:,.1f}M"
    if abs(v) >= 1_000:
        return f"{v / 1_000:,.1f}K"
    return f"{v:,.0f}"


def safe_pct(numerator, denominator) -> float:
    return (numerator / denominator * 100) if denominator > 0 else 0.0


def load_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean data."""
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        st.error(f"❌ File CSV thiếu các cột: {', '.join(missing)}")
        st.info(f"Các cột cần có: {', '.join(EXPECTED_COLUMNS)}")
        st.stop()

    df["date"] = pd.to_datetime(df["date"])
    for col in ["duration_minutes", "total_viewers", "peak_ccu", "avg_ccu",
                 "cart_clicks", "total_orders", "completed_orders",
                 "cancelled_orders", "returned_orders", "revenue",
                 "products_sold", "new_followers", "comments", "shares", "likes"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Computed columns
    df["duration_hours"] = df["duration_minutes"] / 60
    df["revenue_per_hour"] = df.apply(
        lambda r: r["revenue"] / r["duration_hours"] if r["duration_hours"] > 0 else 0, axis=1
    )
    df["ctr_pct"] = df.apply(
        lambda r: safe_pct(r["cart_clicks"], r["total_viewers"]), axis=1
    )
    df["cr_pct"] = df.apply(
        lambda r: safe_pct(r["completed_orders"], r["cart_clicks"]), axis=1
    )
    df["cancel_rate_pct"] = df.apply(
        lambda r: safe_pct(r["cancelled_orders"], r["total_orders"]), axis=1
    )
    df["return_rate_pct"] = df.apply(
        lambda r: safe_pct(r["returned_orders"], r["total_orders"]), axis=1
    )
    df["cancel_return_rate_pct"] = df["cancel_rate_pct"] + df["return_rate_pct"]
    df["avg_order_value"] = df.apply(
        lambda r: r["revenue"] / r["completed_orders"] if r["completed_orders"] > 0 else 0, axis=1
    )

    return df.sort_values("date").reset_index(drop=True)


# ─────────────────────────── ALERT ENGINE ───────────────────────────

def render_alerts(df: pd.DataFrame, threshold: float):
    """Cảnh báo tự động khi tỷ lệ hủy/hoàn vượt ngưỡng."""
    flagged = df[df["cancel_return_rate_pct"] > threshold].copy()

    if flagged.empty:
        st.success(f"✅ Tất cả phiên live đều có tỷ lệ hủy + hoàn **dưới {threshold}%**. Tuyệt vời!")
        return

    st.error(f"🚨 **{len(flagged)} phiên live** có tỷ lệ hủy đơn + hoàn hàng **vượt ngưỡng {threshold}%**")

    for _, row in flagged.iterrows():
        cancel_pct = row["cancel_rate_pct"]
        return_pct = row["return_rate_pct"]
        total_pct = row["cancel_return_rate_pct"]

        severity = "🔴" if total_pct > threshold * 1.5 else "🟡"

        with st.expander(
            f"{severity} {row['session_id']} — {row['staff_name']} "
            f"({row['date'].strftime('%d/%m/%Y')}) — "
            f"Hủy+Hoàn: {total_pct:.1f}%",
            expanded=(total_pct > threshold * 1.5),
        ):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Tỷ lệ hủy đơn", f"{cancel_pct:.1f}%",
                       delta=f"{cancel_pct - threshold:.1f}% vs ngưỡng",
                       delta_color="inverse")
            c2.metric("Tỷ lệ hoàn hàng", f"{return_pct:.1f}%",
                       delta=f"{return_pct - threshold:.1f}% vs ngưỡng",
                       delta_color="inverse")
            c3.metric("Tổng đơn", f"{int(row['total_orders'])}")
            c4.metric("Đơn bị hủy+hoàn",
                       f"{int(row['cancelled_orders'] + row['returned_orders'])}")

            # Root cause hints
            hints = []
            if cancel_pct > 5:
                hints.append("• Tỷ lệ hủy cao → Kiểm tra chất lượng tư vấn, mô tả SP chính xác")
            if return_pct > 3:
                hints.append("• Tỷ lệ hoàn cao → Kiểm tra đóng gói, vận chuyển, kỳ vọng khách")
            if row["avg_ccu"] > 600 and cancel_pct > 5:
                hints.append("• CCU cao nhưng hủy nhiều → Có thể ads thu hút sai đối tượng")
            if hints:
                st.markdown("**💡 Gợi ý kiểm tra:**")
                st.markdown("\n".join(hints))


# ─────────────────────────── CHARTS ───────────────────────────

def chart_revenue_trend(df: pd.DataFrame):
    """Xu hướng doanh thu theo ngày."""
    daily = df.groupby("date").agg(
        revenue=("revenue", "sum"),
        orders=("completed_orders", "sum"),
        sessions=("session_id", "count"),
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily["date"], y=daily["revenue"],
        name="Doanh thu",
        marker_color="#3498db",
        text=[format_vnd(v) for v in daily["revenue"]],
        textposition="outside",
    ))
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["revenue"].rolling(3, min_periods=1).mean(),
        name="Trung bình 3 ngày",
        line=dict(color="#e74c3c", width=2, dash="dot"),
        yaxis="y",
    ))

    fig.update_layout(
        title="📈 Xu hướng doanh thu theo ngày",
        xaxis_title="Ngày", yaxis_title="Doanh thu (VNĐ)",
        height=420, margin=dict(t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)


def chart_revenue_by_staff(df: pd.DataFrame):
    """Doanh số theo nhân viên livestream."""
    staff = df.groupby("staff_name").agg(
        revenue=("revenue", "sum"),
        orders=("completed_orders", "sum"),
        sessions=("session_id", "count"),
        total_hours=("duration_hours", "sum"),
        avg_ccu=("avg_ccu", "mean"),
    ).reset_index()
    staff["revenue_per_hour"] = staff["revenue"] / staff["total_hours"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=staff["staff_name"], y=staff["revenue"],
        name="Tổng doanh thu",
        marker_color="#2ecc71",
        text=[format_vnd(v) for v in staff["revenue"]],
        textposition="outside",
    ))

    fig.update_layout(
        title="👥 Doanh thu theo nhân viên Livestream",
        xaxis_title="Nhân viên", yaxis_title="Doanh thu (VNĐ)",
        height=400, margin=dict(t=60, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    return staff


def chart_staff_comparison_radar(df: pd.DataFrame):
    """So sánh năng lực nhân viên bằng radar chart."""
    staff = df.groupby("staff_name").agg(
        avg_revenue_per_hour=("revenue_per_hour", "mean"),
        avg_ccu=("avg_ccu", "mean"),
        avg_ctr=("ctr_pct", "mean"),
        avg_cr=("cr_pct", "mean"),
        avg_cancel_return=("cancel_return_rate_pct", "mean"),
        avg_orders=("completed_orders", "mean"),
    ).reset_index()

    categories = ["Doanh thu/Giờ", "CCU TB", "CTR (%)", "CR (%)",
                   "Đơn/Phiên", "Chất lượng đơn"]

    fig = go.Figure()
    for _, row in staff.iterrows():
        # Normalize to 0-100 scale for radar
        max_rev = staff["avg_revenue_per_hour"].max()
        max_ccu = staff["avg_ccu"].max()

        quality = 100 - row["avg_cancel_return"] * 5  # Invert: lower cancel = higher quality

        values = [
            row["avg_revenue_per_hour"] / max_rev * 100 if max_rev > 0 else 0,
            row["avg_ccu"] / max_ccu * 100 if max_ccu > 0 else 0,
            min(row["avg_ctr"] * 10, 100),
            min(row["avg_cr"] * 5, 100),
            min(row["avg_orders"] * 1.5, 100),
            max(quality, 0),
        ]
        values.append(values[0])  # Close the polygon

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=row["staff_name"],
            opacity=0.6,
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="🎯 So sánh năng lực nhân viên",
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)


def chart_hourly_pattern(df: pd.DataFrame):
    """Phân tích hiệu quả theo khung giờ."""
    df_copy = df.copy()
    df_copy["start_hour"] = pd.to_datetime(df_copy["start_time"], format="%H:%M").dt.hour

    hourly = df_copy.groupby("start_hour").agg(
        avg_revenue=("revenue", "mean"),
        avg_ccu=("avg_ccu", "mean"),
        sessions=("session_id", "count"),
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=hourly["start_hour"], y=hourly["avg_revenue"],
        name="DT trung bình / phiên",
        marker_color="#9b59b6",
        text=[format_vnd(v) for v in hourly["avg_revenue"]],
        textposition="outside",
    ))
    fig.add_trace(go.Scatter(
        x=hourly["start_hour"], y=hourly["avg_ccu"],
        name="CCU trung bình",
        yaxis="y2",
        line=dict(color="#e67e22", width=3),
        mode="lines+markers",
    ))

    fig.update_layout(
        title="⏰ Hiệu quả theo khung giờ bắt đầu live",
        xaxis=dict(title="Giờ bắt đầu", dtick=1),
        yaxis=dict(title="Doanh thu TB (VNĐ)"),
        yaxis2=dict(title="CCU TB", overlaying="y", side="right"),
        height=400, margin=dict(t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)


def chart_funnel(df: pd.DataFrame):
    """Phễu chuyển đổi."""
    total_viewers = df["total_viewers"].sum()
    cart_clicks = df["cart_clicks"].sum()
    total_orders = df["total_orders"].sum()
    completed = df["completed_orders"].sum()

    stages = ["Lượt xem", "Bấm giỏ hàng", "Đặt đơn", "Hoàn thành"]
    values = [total_viewers, cart_clicks, total_orders, completed]
    pcts = [100] + [safe_pct(v, total_viewers) for v in values[1:]]

    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial",
        marker=dict(color=["#3498db", "#f39c12", "#e74c3c", "#2ecc71"]),
    ))
    fig.update_layout(title="🔻 Phễu chuyển đổi Livestream", height=400)
    st.plotly_chart(fig, use_container_width=True)


def chart_cancel_return_trend(df: pd.DataFrame, threshold: float):
    """Xu hướng tỷ lệ hủy/hoàn theo ngày."""
    daily = df.groupby("date").agg(
        total_orders=("total_orders", "sum"),
        cancelled=("cancelled_orders", "sum"),
        returned=("returned_orders", "sum"),
    ).reset_index()
    daily["cancel_pct"] = safe_pct(daily["cancelled"], daily["total_orders"])
    daily["return_pct"] = safe_pct(daily["returned"], daily["total_orders"])
    daily["total_pct"] = daily["cancel_pct"] + daily["return_pct"]

    # Vectorized percentage calculation
    daily["cancel_pct"] = daily.apply(lambda r: safe_pct(r["cancelled"], r["total_orders"]), axis=1)
    daily["return_pct"] = daily.apply(lambda r: safe_pct(r["returned"], r["total_orders"]), axis=1)
    daily["total_pct"] = daily["cancel_pct"] + daily["return_pct"]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=daily["date"], y=daily["cancel_pct"],
                          name="Tỷ lệ hủy (%)", marker_color="#e74c3c"))
    fig.add_trace(go.Bar(x=daily["date"], y=daily["return_pct"],
                          name="Tỷ lệ hoàn (%)", marker_color="#f39c12"))
    fig.add_hline(y=threshold, line_dash="dash", line_color="red",
                  annotation_text=f"Ngưỡng cảnh báo {threshold}%")

    fig.update_layout(
        title="📉 Tỷ lệ hủy đơn & hoàn hàng theo ngày",
        barmode="stack",
        xaxis_title="Ngày", yaxis_title="%",
        height=400, margin=dict(t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)


def chart_platform_comparison(df: pd.DataFrame):
    """So sánh hiệu quả theo nền tảng."""
    if "platform" not in df.columns:
        return

    plat = df.groupby("platform").agg(
        sessions=("session_id", "count"),
        revenue=("revenue", "sum"),
        avg_ccu=("avg_ccu", "mean"),
        avg_cr=("cr_pct", "mean"),
        avg_orders=("completed_orders", "mean"),
    ).reset_index()

    fig = px.bar(plat, x="platform", y="revenue", color="platform",
                 text=[format_vnd(v) for v in plat["revenue"]],
                 title="🌐 Doanh thu theo nền tảng",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(height=380, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    return plat


# ─────────────────────────── MAIN UI ───────────────────────────

def main():
    st.markdown("""
    # 📺 Live Analytics Dashboard
    ### Phân tích số liệu phòng Livestream — Ngành Gia dụng
    ---
    """)

    # ══════════════════════ SIDEBAR ══════════════════════
    with st.sidebar:
        st.header("📂 Nguồn dữ liệu")

        data_source = st.radio(
            "Chọn nguồn dữ liệu:",
            ["📋 Dữ liệu mẫu (30 phiên)", "📤 Upload file CSV"],
            index=0,
        )

        if data_source == "📤 Upload file CSV":
            uploaded = st.file_uploader("Chọn file CSV", type=["csv"])
            if uploaded is not None:
                df_raw = pd.read_csv(uploaded)
            else:
                st.info("⬆️ Hãy upload file CSV hoặc chọn dữ liệu mẫu.")
                st.markdown("---")
                st.markdown("**📥 Tải file CSV mẫu:**")
                if os.path.exists(SAMPLE_CSV):
                    with open(SAMPLE_CSV, "r", encoding="utf-8") as f:
                        st.download_button(
                            "⬇️ Download sample_live_data.csv",
                            f.read(),
                            file_name="sample_live_data.csv",
                            mime="text/csv",
                        )
                st.markdown("**Các cột cần có:**")
                st.code(", ".join(EXPECTED_COLUMNS), language=None)
                st.stop()
        else:
            if os.path.exists(SAMPLE_CSV):
                df_raw = pd.read_csv(SAMPLE_CSV)
            else:
                st.error("❌ Không tìm thấy file sample_live_data.csv")
                st.stop()

        df = load_and_validate(df_raw)

        st.markdown("---")
        st.header("🎚️ Bộ lọc")

        # Date range
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()
        date_range = st.date_input("Khoảng ngày",
                                    value=(min_date, max_date),
                                    min_value=min_date,
                                    max_value=max_date)
        if isinstance(date_range, tuple) and len(date_range) == 2:
            df = df[(df["date"].dt.date >= date_range[0]) &
                     (df["date"].dt.date <= date_range[1])]

        # Staff filter
        staff_list = ["Tất cả"] + sorted(df["staff_name"].unique().tolist())
        selected_staff = st.selectbox("Nhân viên", staff_list)
        if selected_staff != "Tất cả":
            df = df[df["staff_name"] == selected_staff]

        # Platform filter
        if "platform" in df.columns:
            platforms = ["Tất cả"] + sorted(df["platform"].unique().tolist())
            selected_platform = st.selectbox("Nền tảng", platforms)
            if selected_platform != "Tất cả":
                df = df[df["platform"] == selected_platform]

        # Alert threshold
        st.markdown("---")
        st.header("🚨 Ngưỡng cảnh báo")
        alert_threshold = st.slider(
            "Ngưỡng hủy + hoàn (%)", 1.0, 20.0, ALERT_THRESHOLD_PCT, 0.5,
            help="Cảnh báo khi tỷ lệ hủy đơn + hoàn hàng vượt mức này",
        )

    if df.empty:
        st.warning("⚠️ Không có dữ liệu trong khoảng lọc. Hãy điều chỉnh bộ lọc.")
        st.stop()

    # ══════════════════════ KPI CARDS ══════════════════════

    total_sessions = len(df)
    total_revenue = df["revenue"].sum()
    total_hours = df["duration_hours"].sum()
    total_orders = df["total_orders"].sum()
    total_completed = df["completed_orders"].sum()
    total_cancelled = df["cancelled_orders"].sum()
    total_returned = df["returned_orders"].sum()
    total_viewers = df["total_viewers"].sum()
    total_cart = df["cart_clicks"].sum()
    avg_ccu = df["avg_ccu"].mean()
    overall_ctr = safe_pct(total_cart, total_viewers)
    overall_cr = safe_pct(total_completed, total_cart)
    rev_per_hour = total_revenue / total_hours if total_hours > 0 else 0
    cancel_return_pct = safe_pct(total_cancelled + total_returned, total_orders)

    # Row 1
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("📺 Phiên live", f"{total_sessions}")
    k2.metric("💰 Tổng doanh thu", format_vnd(total_revenue))
    k3.metric("⏱️ Tổng giờ live", f"{total_hours:.1f}h")
    k4.metric("📦 Đơn hoàn thành", f"{int(total_completed)}")
    k5.metric("👁️ CCU trung bình", f"{avg_ccu:,.0f}")
    k6.metric("💵 Doanh thu / Giờ", format_vnd(rev_per_hour))

    # Row 2
    k7, k8, k9, k10, k11, k12 = st.columns(6)
    k7.metric("🛒 CTR (Bấm giỏ)", f"{overall_ctr:.2f}%")
    k8.metric("🎯 CR (Chuyển đổi)", f"{overall_cr:.1f}%")
    k9.metric("🧾 Giá trị TB/đơn",
              format_vnd(total_revenue / total_completed if total_completed > 0 else 0))
    k10.metric("❌ Đơn hủy", f"{int(total_cancelled)}")
    k11.metric("↩️ Đơn hoàn", f"{int(total_returned)}")

    alert_color = "🔴" if cancel_return_pct > alert_threshold else "🟢"
    k12.metric(f"{alert_color} Hủy+Hoàn", f"{cancel_return_pct:.1f}%",
               delta=f"ngưỡng {alert_threshold}%",
               delta_color="inverse" if cancel_return_pct > alert_threshold else "normal")

    st.markdown("---")

    # ══════════════════════ ALERTS ══════════════════════

    with st.expander("🚨 **CẢNH BÁO TỰ ĐỘNG — Hủy đơn & Hoàn hàng**", expanded=True):
        render_alerts(df, alert_threshold)

    st.markdown("---")

    # ══════════════════════ TABS ══════════════════════

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Xu hướng doanh thu",
        "👥 Phân tích nhân viên",
        "🔻 Phễu & Chuyển đổi",
        "📋 Dữ liệu chi tiết",
        "📊 Phân tích nâng cao",
    ])

    # ────── TAB 1: Revenue Trend ──────
    with tab1:
        chart_revenue_trend(df)

        c_a, c_b = st.columns(2)
        with c_a:
            chart_cancel_return_trend(df, alert_threshold)
        with c_b:
            if "platform" in df.columns and df["platform"].nunique() > 1:
                chart_platform_comparison(df)
            else:
                chart_hourly_pattern(df)

    # ────── TAB 2: Staff Analysis ──────
    with tab2:
        c_s1, c_s2 = st.columns([3, 2])
        with c_s1:
            staff_summary = chart_revenue_by_staff(df)
        with c_s2:
            chart_staff_comparison_radar(df)

        # Staff detail table
        st.subheader("📋 Bảng chi tiết theo nhân viên")
        staff_detail = df.groupby("staff_name").agg(
            sessions=("session_id", "count"),
            total_hours=("duration_hours", "sum"),
            total_revenue=("revenue", "sum"),
            avg_revenue_session=("revenue", "mean"),
            avg_ccu=("avg_ccu", "mean"),
            total_orders=("completed_orders", "sum"),
            avg_ctr=("ctr_pct", "mean"),
            avg_cr=("cr_pct", "mean"),
            avg_cancel_return=("cancel_return_rate_pct", "mean"),
            total_followers=("new_followers", "sum"),
        ).reset_index()
        staff_detail["rev_per_hour"] = staff_detail["total_revenue"] / staff_detail["total_hours"]

        display_staff = staff_detail.copy()
        display_staff.columns = [
            "Nhân viên", "Số phiên", "Tổng giờ", "Tổng DT", "DT TB/phiên",
            "CCU TB", "Tổng đơn", "CTR TB (%)", "CR TB (%)",
            "Hủy+Hoàn TB (%)", "Followers mới", "DT/Giờ",
        ]
        for col in ["Tổng DT", "DT TB/phiên", "DT/Giờ"]:
            display_staff[col] = display_staff[col].apply(format_vnd)
        for col in ["CTR TB (%)", "CR TB (%)", "Hủy+Hoàn TB (%)"]:
            display_staff[col] = display_staff[col].apply(lambda x: f"{x:.1f}%")
        display_staff["Tổng giờ"] = display_staff["Tổng giờ"].apply(lambda x: f"{x:.1f}h")
        display_staff["CCU TB"] = display_staff["CCU TB"].apply(lambda x: f"{x:,.0f}")

        st.dataframe(display_staff, use_container_width=True, hide_index=True)

        # Revenue by staff by day
        st.subheader("📅 Doanh thu nhân viên theo ngày")
        staff_daily = df.groupby(["date", "staff_name"])["revenue"].sum().reset_index()
        fig_sd = px.line(staff_daily, x="date", y="revenue", color="staff_name",
                         markers=True, title="Doanh thu theo ngày — từng nhân viên",
                         labels={"revenue": "Doanh thu (VNĐ)", "date": "Ngày",
                                 "staff_name": "Nhân viên"})
        fig_sd.update_layout(height=400)
        st.plotly_chart(fig_sd, use_container_width=True)

    # ────── TAB 3: Funnel ──────
    with tab3:
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            chart_funnel(df)
        with c_f2:
            # Conversion metrics detail
            st.subheader("🎯 Chi tiết chuyển đổi")
            st.metric("Tổng lượt xem → Bấm giỏ (CTR)", f"{overall_ctr:.2f}%",
                       help="cart_clicks / total_viewers")
            st.metric("Bấm giỏ → Đặt đơn",
                       f"{safe_pct(total_orders, total_cart):.1f}%")
            st.metric("Đặt đơn → Hoàn thành (CR)",
                       f"{safe_pct(total_completed, total_orders):.1f}%")
            st.metric("Tổng Viewer → Mua hàng",
                       f"{safe_pct(total_completed, total_viewers):.3f}%",
                       help="End-to-end conversion")

        chart_hourly_pattern(df)

    # ────── TAB 4: Raw Data ──────
    with tab4:
        st.subheader("📋 Dữ liệu chi tiết từng phiên live")

        display_df = df[[
            "date", "session_id", "staff_name", "start_time", "end_time",
            "duration_minutes", "avg_ccu", "peak_ccu", "cart_clicks",
            "total_orders", "completed_orders", "cancelled_orders",
            "returned_orders", "revenue", "revenue_per_hour",
            "ctr_pct", "cr_pct", "cancel_return_rate_pct",
        ]].copy()

        display_df["date"] = display_df["date"].dt.strftime("%d/%m/%Y")
        display_df.columns = [
            "Ngày", "Mã phiên", "Nhân viên", "Bắt đầu", "Kết thúc",
            "Phút", "CCU TB", "CCU Max", "Bấm giỏ",
            "Tổng đơn", "Hoàn thành", "Hủy", "Hoàn",
            "Doanh thu", "DT/Giờ", "CTR (%)", "CR (%)", "Hủy+Hoàn (%)",
        ]

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Download processed data
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            "📥 Tải dữ liệu đã xử lý (CSV)",
            csv_buffer.getvalue(),
            file_name=f"live_analytics_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    # ────── TAB 5: Advanced ──────
    with tab5:
        st.subheader("📊 Phân tích tương quan")

        c_adv1, c_adv2 = st.columns(2)
        with c_adv1:
            # CCU vs Revenue scatter
            fig_scatter = px.scatter(
                df, x="avg_ccu", y="revenue",
                color="staff_name", size="duration_minutes",
                hover_data=["session_id", "date"],
                title="CCU trung bình vs Doanh thu",
                labels={"avg_ccu": "CCU TB", "revenue": "Doanh thu",
                         "staff_name": "NV"},
                trendline="ols",
            )
            fig_scatter.update_layout(height=420)
            st.plotly_chart(fig_scatter, use_container_width=True)

        with c_adv2:
            # Duration vs Revenue per hour
            fig_dur = px.scatter(
                df, x="duration_minutes", y="revenue_per_hour",
                color="staff_name", size="avg_ccu",
                hover_data=["session_id", "date"],
                title="Thời lượng vs Doanh thu/Giờ",
                labels={"duration_minutes": "Thời lượng (phút)",
                         "revenue_per_hour": "DT/Giờ (VNĐ)",
                         "staff_name": "NV"},
                trendline="ols",
            )
            fig_dur.update_layout(height=420)
            st.plotly_chart(fig_dur, use_container_width=True)

        # Daily summary heatmap-style
        st.subheader("📅 Ma trận hiệu suất theo ngày & nhân viên")

        pivot_rev = df.pivot_table(
            values="revenue", index=df["date"].dt.strftime("%d/%m"),
            columns="staff_name", aggfunc="sum", fill_value=0,
        )
        fig_heat = px.imshow(
            pivot_rev.T, text_auto=True,
            labels=dict(x="Ngày", y="Nhân viên", color="Doanh thu"),
            title="Heatmap doanh thu",
            color_continuous_scale="YlOrRd",
            aspect="auto",
        )
        fig_heat.update_layout(height=300)
        st.plotly_chart(fig_heat, use_container_width=True)

    # ── Footer ──
    st.markdown("---")
    st.markdown(
        f"<div style='text-align:center; color:gray; font-size:0.85em'>"
        f"Live Analytics Dashboard v1.0 · {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
        f"Dữ liệu: {total_sessions} phiên · {df['date'].min().strftime('%d/%m')} "
        f"→ {df['date'].max().strftime('%d/%m/%Y')}</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
