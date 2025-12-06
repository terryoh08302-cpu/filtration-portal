import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="Filtration Test Report Portal",
    layout="wide"
)

st.title("🧪 Filtration Test Report Portal")
st.write("Browse and access filtration test reports (PDF / Excel) remotely.")

@st.cache_data
def load_data():
    # 모든 컬럼을 문자열(str)로 읽어서 타입 문제 완전히 방지
    df = pd.read_csv("reports.csv", dtype=str)

    # 혹시 누락된 컬럼이 있으면 빈 문자열로 생성
    expected_cols = ["customer", "project", "report_type", "date",
                     "file_name", "url", "format", "notes"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""

    # 결측치(NaN)를 전부 빈 문자열로
    df = df.fillna("")
    return df

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("Filters")

# 고객/리포트 타입 목록 만들기 (모두 문자열이므로 에러 안 남)
customers = ["All"] + sorted(df["customer"].unique().tolist())
selected_customer = st.sidebar.selectbox("Customer", customers)

report_types = ["All"] + sorted(df["report_type"].unique().tolist())
selected_report_type = st.sidebar.selectbox("Report Type", report_types)

search_text = st.sidebar.text_input("Search (file name, project, notes)")

# --- Filtering logic ---
filtered = df.copy()

if selected_customer != "All":
    filtered = filtered[filtered["customer"] == selected_customer]

if selected_report_type != "All":
    filtered = filtered[filtered["report_type"] == selected_report_type]

if search_text:
    search_lower = search_text.lower()
    filtered = filtered[
        filtered["file_name"].str.lower().str.contains(search_lower)
        | filtered["project"].str.lower().str.contains(search_lower)
        | filtered["notes"].str.lower().str.contains(search_lower)
    ]

st.subheader("Results")

if filtered.empty:
    st.info("No reports found with current filters.")
else:
    display_cols = ["customer", "project", "report_type", "date",
                    "file_name", "format"]
    st.dataframe(filtered[display_cols], use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔗 Open Reports")
    for _, row in filtered.iterrows():
        file_name = row.get("file_name", "")
        customer = row.get("customer", "")
        date = row.get("date", "")
        url = row.get("url", "")

        # URL이 비어있지 않을 때만 링크 생성
        if isinstance(url, str) and url.strip() != "":
            st.markdown(
                f"- **{file_name}** ({customer}, {date}) "
                f"[Open]({url})",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"- **{file_name}** ({customer}, {date}) — (no URL)"
            )