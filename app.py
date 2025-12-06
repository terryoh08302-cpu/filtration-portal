import streamlit as st
import pandas as pd

# ===================== 기본 설정 =====================
st.set_page_config(
    page_title="Filtration Test Report Portal",
    layout="wide",
)

LOGO_PATH = "logo.png"   # 같은 폴더에 logo.png
CSV_PATH = "reports.csv" # 같은 폴더에 reports.csv


# ===================== 로그인 함수 =====================
def check_password():
    """st.secrets의 auth.username / auth.password로 로그인 검증"""

    def password_entered():
        if (
            st.session_state["username"] == st.secrets["auth"]["username"]
            and st.session_state["password"] == st.secrets["auth"]["password"]
        ):
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False
            st.error("❌ Incorrect username or password")

    # 이미 로그인 된 경우
    if st.session_state.get("authenticated"):
        return True

    # 로그인 폼
    st.title("🔐 Secure Login")
    st.text_input("Username:", key="username")
    st.text_input("Password:", type="password", key="password")
    st.button("Login", on_click=password_entered)

    return False


# ===================== 로그인 체크 =====================
if not check_password():
    st.stop()   # 로그인 실패/미완료면 여기서 앱 실행 중단


# ===================== 스타일(CSS) 주입 =====================
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


# ===================== 헤더(로고 + 텍스트) =====================
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

customers = ["All"] + sorted([c for c in df["customer"].unique().tolist() if c])
projects = ["All"] + sorted([p for p in df["project"].unique().tolist() if p])
file_names = ["All"] + sorted([f for f in df["file_name"].unique().tolist() if f])
report_types = ["All"] + sorted([r for r in df["report_type"].unique().tolist() if r])

selected_customer = st.sidebar.selectbox("Customer", customers)
selected_project = st.sidebar.selectbox("Project", projects)
selected_file_name = st.sidebar.selectbox("File name", file_names)
selected_report_type = st.sidebar.selectbox("Report Type", report_types)

search_text = st.sidebar.text_input("Search (file name, project, notes)")


# ===================== 필터 적용 =====================
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
        label = f"{file_name} ({customer}, {date})"

        url = str(row.get("url", "")).strip()

        if not url:
            st.write(f"• {label} — (no URL)")
        else:
            st.markdown(f"• **{label}** – [Open]({url})")