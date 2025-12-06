import streamlit as st
import pandas as pd

# ----- 기본 설정 -----
st.set_page_config(
    page_title="Filtration Test Report Portal",
    layout="wide",
)

LOGO_PATH = "logo.png"  # 같은 폴더에 logo.png 넣으면 사용됨

# ----- 공통 스타일(CSS) 주입 -----
st.markdown(
    """
    <style>
    /* 페이지 전체 여백/폰트 */
    .main {
        padding-top: 1.5rem;
    }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                     "Helvetica Neue", Arial, "Noto Sans KR", sans-serif;
        color: #252733;
    }

    /* 헤더 전체 컨테이너 */
    .header-container {
        display: flex;
        flex-direction: column;    /* 기본: 모바일은 세로 */
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }

    /* 로고쪽 블럭 */
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
        color: #d70000;            /* 빨간 텍스트 */
        font-size: 1.05rem;
    }

    /* 텍스트쪽 블럭 */
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

    /* 데스크탑 이상 화면에서 가로 정렬 + 로고 위로 약간 올리기 */
    @media (min-width: 768px) {
        .header-container {
            flex-direction: row;      /* 가로 정렬 */
            align-items: flex-start;  /* 로고를 좀 더 위쪽에 */
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


# ----- 데이터 로드 -----
@st.cache_data
def load_data():
    df = pd.read_csv("reports.csv")

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


# ----- 상단 헤더 (로고 + 텍스트, 반응형) -----
# Streamlit 안에서 HTML로 직접 그려서 구도 고정
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


# ----- 사이드바 필터 -----
st.sidebar.header("Filters")

# 각 필터용 옵션 리스트 만들기 (비어있는 값은 제외)
customers = ["All"] + sorted([c for c in df["customer"].unique().tolist() if c])
projects = ["All"] + sorted([p for p in df["project"].unique().tolist() if p])
file_names = ["All"] + sorted([f for f in df["file_name"].unique().tolist() if f])
report_types = ["All"] + sorted([r for r in df["report_type"].unique().tolist() if r])

selected_customer = st.sidebar.selectbox("Customer", customers)
selected_project = st.sidebar.selectbox("Project", projects)
selected_file_name = st.sidebar.selectbox("File name", file_names)
selected_report_type = st.sidebar.selectbox("Report Type", report_types)

search_text = st.sidebar.text_input("Search (file name, project, notes)")


# ----- 필터 적용 -----
filtered = df.copy()

if selected_customer != "All":
    filtered = filtered[filtered["customer"] == selected_customer]

if selected_project != "All":
    filtered = filtered[filtered["project"] == selected_project]

if selected_file_name != "All":
    filtered = filtered[filtered["file_name"] == selected_file_name]

if selected_report_type != "All":
    filtered = filtered[filtered["report_type"] == selected_report_type]

if search_text:
    search_text_lower = search_text.lower()

    # notes 컬럼이 없을 수도 있으니 안전하게 처리
    if "notes" in filtered.columns:
        notes_series = filtered["notes"].astype(str)
    else:
        notes_series = pd.Series([""] * len(filtered), index=filtered.index)

    mask = (
        filtered["file_name"].astype(str).str.lower().str.contains(search_text_lower, na=False)
        | filtered["project"].astype(str).str.lower().str.contains(search_text_lower, na=False)
        | notes_series.str.lower().str.contains(search_text_lower, na=False)
    )
    filtered = filtered[mask]


# ----- 결과 테이블 -----
st.subheader("Results")
st.dataframe(filtered, use_container_width=True)


# ----- Open Reports 섹션 -----
st.markdown("---")
st.subheader("Open Reports")

if filtered.empty:
    st.write("No reports match the selected filters.")
else:
    for _, row in filtered.iterrows():
        file_name = str(row.get("file_name", "")).strip() or "(no name)"
        customer = str(row.get("customer", "")).strip()
        date = str(row.get("date", "")).strip()
        label = f"{file_name} ({customer}, {date})"

        url = str(row.get("url", "")).strip()

        if not url:
            st.write(f"• {label} — (no URL)")
        else:
            st.markdown(f"• **{label}** – [Open]({url})")