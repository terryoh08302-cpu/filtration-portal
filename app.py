import streamlit as st
import pandas as pd
from pathlib import Path
import base64

# ----- 기본 설정 -----
st.set_page_config(
    page_title="Filtration Test Report Portal",
    layout="wide",
)

LOGO_PATH = Path("logo.png")  # 같은 폴더에 logo.png 넣으면 사용됨


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


def get_logo_base64() -> str:
    """로고 파일을 base64로 읽어서 HTML <img>에 바로 넣을 수 있게 변환"""
    if not LOGO_PATH.exists():
        return ""
    with open(LOGO_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# 데이터 로드
df = load_data()

# ----- 상단 커스텀 헤더 (HTML + CSS) -----
logo_b64 = get_logo_base64()
logo_img_tag = (
    f'<img src="data:image/png;base64,{logo_b64}" alt="VPC Logo" />'
    if logo_b64
    else ""
)

header_html = f"""
<style>
:root {{
  --vpc-blue: #004b8d;
  --vpc-red: #d71920;
  --text-gray: #555;
}}

.page-wrapper {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 8px 4px 16px 4px;
}}

.portal-header {{
  display: flex;
  align-items: flex-start;  /* 로고 상단을 제목 상단과 맞추기 */
  gap: 24px;
  flex-wrap: wrap;
}}

.portal-logo {{
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}}

.portal-logo img {{
  display: block;
  max-height: 54px;   /* 필요하면 숫자만 살짝 조정해서 맞추면 됨 */
  height: auto;
  margin-top: 4px;    /* 제목과 비슷한 높이에서 시작 */
}}

.portal-logo-subtext {{
  margin-top: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--vpc-red);
}}

.portal-title-block {{
  flex: 1;
  min-width: 0;
}}

.portal-title {{
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
}}

.portal-subtitle {{
  margin: 6px 0 0;
  font-size: 14px;
  color: var(--text-gray);
}}

/* 모바일/태블릿 대응 */
@media (max-width: 768px) {{
  .page-wrapper {{
    padding: 4px 0 12px 0;
  }}

  .portal-header {{
    flex-direction: column;  /* 모바일에서는 위아래로 쌓기 */
    align-items: flex-start;
    gap: 12px;
  }}

  .portal-logo img {{
    max-height: 44px;
    margin-top: 0;
  }}

  .portal-title {{
    font-size: 24px;
  }}

  .portal-subtitle {{
    font-size: 13px;
  }}
}}
</style>

<div class="page-wrapper">
  <div class="portal-header">
    <div class="portal-logo">
      {logo_img_tag}
    </div>
    <div class="portal-title-block">
      <h1 class="portal-title">Filtration Test Report Portal</h1>
      <p class="portal-subtitle">
        Browse and access filtration test reports (PDF / Excel) remotely.
      </p>
    </div>
  </div>
</div>
"""

# 헤더 출력
st.markdown(header_html, unsafe_allow_html=True)
st.markdown("---")

# ----- 사이드바 필터 -----
st.sidebar.header("Filters")


def unique_values(col_name: str):
    """컬럼에 있는 고유값 리스트 만들기 (비어있는 값 제거)"""
    if col_name not in df.columns:
        return ["All"]
    values = [v for v in df[col_name].unique().tolist() if str(v).strip()]
    return ["All"] + sorted(values)


customers = unique_values("customer")
projects = unique_values("project")
file_names = unique_values("file_name")
report_types = unique_values("report_type")

selected_customer = st.sidebar.selectbox("Customer", customers)
selected_project = st.sidebar.selectbox("Project", projects)
selected_file_name = st.sidebar.selectbox("File name", file_names)
selected_report_type = st.sidebar.selectbox("Report Type", report_types)

search_text = st.sidebar.text_input("Search (file name, project, notes)")

# ----- 필터 적용 -----
filtered = df.copy()

if selected_customer != "All" and "customer" in filtered.columns:
    filtered = filtered[filtered["customer"] == selected_customer]

if selected_project != "All" and "project" in filtered.columns:
    filtered = filtered[filtered["project"] == selected_project]

if selected_file_name != "All" and "file_name" in filtered.columns:
    filtered = filtered[filtered["file_name"] == selected_file_name]

if selected_report_type != "All" and "report_type" in filtered.columns:
    filtered = filtered[filtered["report_type"] == selected_report_type]

if search_text:
    search_text_lower = search_text.lower()

    file_col = (
        filtered["file_name"].astype(str)
        if "file_name" in filtered.columns
        else pd.Series("", index=filtered.index)
    )
    project_col = (
        filtered["project"].astype(str)
        if "project" in filtered.columns
        else pd.Series("", index=filtered.index)
    )
    notes_col = (
        filtered["notes"].astype(str)
        if "notes" in filtered.columns
        else pd.Series("", index=filtered.index)
    )

    mask = (
        file_col.str.lower().str.contains(search_text_lower, na=False)
        | project_col.str.lower().str.contains(search_text_lower, na=False)
        | notes_col.str.lower().str.contains(search_text_lower, na=False)
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

        # 표시 라벨 만들기
        label_parts = [file_name]
        if customer:
            label_parts.append(customer)
        if date:
            label_parts.append(date)
        label = " | ".join(label_parts)

        url = str(row.get("url", "")).strip()

        if not url:
            st.write(f"• {label} — (no URL)")
        else:
            st.markdown(f"• **{label}** – [Open]({url})")