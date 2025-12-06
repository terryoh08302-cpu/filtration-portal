import streamlit as st
import pandas as pd

# ----- 기본 설정 -----
st.set_page_config(
    page_title="Filtration Test Report Portal",
    layout="wide",
)

LOGO_PATH = "logo.png"  # 같은 폴더에 logo.png 넣으면 사용됨

@st.cache_data
def load_data():
    df = pd.read_csv("reports.csv")

    # 문자열 컬럼은 공백으로 채워서 에러 방지
    for col in ["customer", "project", "report_type", "file_name", "format", "notes"]:
        if col in df.columns:
            df[col] = df[col].fillna("")

    if "date" in df.columns:
        df["date"] = df["date"].astype(str).fillna("")

    return df


df = load_data()

# ----- 상단 로고 + 타이틀 -----
col_logo, col_title = st.columns([1, 4])

with col_logo:
    try:
        st.image(LOGO_PATH, use_container_width=True)
    except Exception:
        st.write("")  # 로고 파일이 없어도 에러 안 나게

with col_title:
    st.title("Filtration Test Report Portal")
    st.write("Browse and access filtration test reports (PDF / Excel) remotely.")

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
    mask = (
        filtered["file_name"].str.lower().str.contains(search_text_lower, na=False)
        | filtered["project"].str.lower().str.contains(search_text_lower, na=False)
        | filtered.get("notes", "").astype(str).str.lower().str.contains(search_text_lower, na=False)
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
        file_name = row.get("file_name", "").strip() or "(no name)"
        customer = row.get("customer", "").strip()
        date = row.get("date", "").strip()
        label = f"{file_name} ({customer}, {date})"

        url = str(row.get("url", "")).strip()

        if not url:
            st.write(f"• {label} — (no URL)")
        else:
            st.markdown(f"• **{label}** – [Open]({url})")