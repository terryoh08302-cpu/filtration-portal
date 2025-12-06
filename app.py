import streamlit as st
import pandas as pd

# ===================== 기본 설정 =====================
st.set_page_config(
    page_title="Filtration Test Report Portal",
    layout="wide",
)

LOGO_PATH = "logo.png"
CSV_PATH = "reports.csv"


# ===================== 스타일(CSS) =====================
st.markdown(
    """
    <style>
    .main {
        padding-top: 1.5rem;
    }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                     "Helvetica Neue", Arial, "Noto Sans KR", sans-serif;
        color: #252733;
    }
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }
    .hero-logo-block {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .hero-logo {
        max-width: 220px;
        width: 100%;
        height: auto;
        display: block;
    }
    .logo-caption {
        margin-top: 0.4rem;
        font-weight: 700;
        color: #d70000;
        font-size: 1.05rem;
    }
    .hero-text h1 {
        margin: 0;
        font-size: 1.9rem;
        font-weight: 800;
        letter-spacing: 0.01em;
    }
    .hero-text p {
        margin-top: 0.4rem;
        margin-bottom: 0;
        font-size: 1rem;
        color: #555a6a;
    }
    @media (min-width: 768px) {
        .header-container {
            flex-direction: row;
            align-items: flex-start;
            justify-content: flex-start;
            gap: 2.5rem;
        }
        .hero-text h1 {
            font-size: 2.4rem;
        }
        .hero-text p {
            font-size: 1.05rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ===================== 데이터 로드 =====================
@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)

    # 컬럼 이름을 전부 소문자 + 양쪽 공백 제거
    df.columns = [c.strip().lower() for c in df.columns]

    # 문자열 컬럼은 공백으로 채워서 에러 방지
    for col in ["customer", "project", "report_type", "file_name", "format", "notes"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    if "date" in df.columns:
        df["date"] = df["date"].astype(str).fillna("")

    if "url" in df.columns:
        df["url"] = df["url"].fillna("")

    return df


df = load_data()


def has_col(col: str) -> bool:
    return col in df.columns


# ===================== 헤더 =====================
st.markdown(
    f"""
    <div class="header-container">
        <div class="hero-logo-block">
            <img src="{LOGO_PATH}" class="hero-logo" alt="VPC Group Inc. Logo">
            <div class="logo-caption">Filtration Test Portal</div>
        </div>
        <div class="hero-text">
            <h1>Filtration Test Report Portal</h1>
            <p>Browse and access filtration test reports (PDF / Excel) remotely.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")


# ===================== 사이드바 필터 =====================
st.sidebar.header("Filters")


def build_options(col_name: str):
    """해당 컬럼이 있으면 옵션 리스트, 없으면 None 반환"""
    if not has_col(col_name):
        return None
    vals = df[col_name].dropna().astype(str)
    vals = [v for v in vals.unique().tolist() if v.strip() != ""]
    return ["All"] + sorted(vals)


customer_opts = build_options("customer")
project_opts = build_options("project")
file_name_opts = build_options("file_name")
report_type_opts = build_options("report_type")

selected_customer = (
    st.sidebar.selectbox("Customer", customer_opts)
    if customer_opts else None
)
selected_project = (
    st.sidebar.selectbox("Project", project_opts)
    if project_opts else None
)
selected_file_name = (
    st.sidebar.selectbox("File name", file_name_opts)
    if file_name_opts else None
)
selected_report_type = (
    st.sidebar.selectbox("Report Type", report_type_opts)
    if report_type_opts else None
)

search_text = st.sidebar.text_input("Search (file name, project, notes)")


# ===================== 필터 적용 =====================
filtered = df.copy()

if customer_opts and selected_customer and selected_customer != "All":
    filtered = filtered[filtered["customer"].astype(str) == selected_customer]

if project_opts and selected_project and selected_project != "All":
    filtered = filtered[filtered["project"].astype(str) == selected_project]

if file_name_opts and selected_file_name and selected_file_name != "All":
    filtered = filtered[filtered["file_name"].astype(str) == selected_file_name]

if report_type_opts and selected_report_type and selected_report_type != "All":
    filtered = filtered[filtered["report_type"].astype(str) == selected_report_type]

if search_text:
    search_text_lower = search_text.lower()

    file_series = (
        filtered["file_name"].astype(str)
        if has_col("file_name")
        else pd.Series([""] * len(filtered), index=filtered.index)
    )
    proj_series = (
        filtered["project"].astype(str)
        if has_col("project")
        else pd.Series([""] * len(filtered), index=filtered.index)
    )
    notes_series = (
        filtered["notes"].astype(str)
        if has_col("notes")
        else pd.Series([""] * len(filtered), index=filtered.index)
    )

    mask = (
        file_series.str.lower().str.contains(search_text_lower, na=False)
        | proj_series.str.lower().str.contains(search_text_lower, na=False)
        | notes_series.str.lower().str.contains(search_text_lower, na=False)
    )
    filtered = filtered[mask]


# ===================== 결과 테이블 =====================
st.subheader("Results")
st.dataframe(filtered, use_container_width=True)


# ===================== Open Reports =====================
st.markdown("---")
st.subheader("Open Reports")

if filtered.empty:
    st.write("No reports match the selected filters.")
else:
    for _, row in filtered.iterrows():
        file_name = str(row.get("file_name", "")).strip() or "(no name)"
        customer = str(row.get("customer", "")).strip()
        date = str(row.get("date", "")).strip()

        # label 깔끔하게: 비어있는 부분은 자동으로 빠지게
        parts = [file_name]
        if customer:
            parts.append(customer)
        if date:
            parts.append(date)
        label = " (" + ", ".join(parts[1:]) + ")" if len(parts) > 1 else ""
        label = parts[0] + label

        url = str(row.get("url", "")).strip()

        if not url:
            st.write(f"• {label} — (no URL)")
        else:
            st.markdown(f"• **{label}** – [Open]({url})")