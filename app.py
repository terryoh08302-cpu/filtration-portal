import streamlit as st
import pandas as pd
from pathlib import Path
import base64

# =========================
# 기본 설정 & 경로
# =========================
st.set_page_config(
    page_title="Filtration Test Report Portal",
    layout="wide",
)

LOGO_PATH = Path("logo.png")  # 로고 파일(옵션)
SPECIAL_EXCEL_PATH = Path("FD Blue Heaven Test Results2.xlsx")  # 항상 보여줄 엑셀


# =========================
# 데이터 로드 함수
# =========================
def load_reports() -> pd.DataFrame:
    """
    reports.csv 컬럼 구조 예시
    ---------------------------------
    customer,
    vpc_part,
    item_description,
    media_color,
    date,
    test_no,
    format,
    notes,
    url
    """
    df = pd.read_csv("reports.csv")

    # 문자열 컬럼은 공백으로 채워서 에러 방지
    for col in [
        "customer",
        "vpc_part",
        "item_description",
        "media_color",
        "test_no",
        "format",
        "notes",
    ]:
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


# =========================
# 상단 헤더 UI
# =========================
def render_header():
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
      align-items: flex-start;
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
      max-height: 150px;
      height: auto;
      margin-top: -10px;
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

    @media (max-width: 768px) {{
      .page-wrapper {{
        padding: 4px 0 12px 0;
      }}

      .portal-header {{
        flex-direction: column;
        align-items: flex-start;
        gap: 0px;
      }}

      .portal-logo img {{
        max-height: 180px;
        margin-top: -4px;
      }}

      .portal-title {{
        font-size: 24px;
        margin-top: -12px;
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

    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown("---")


# =========================
# 메인 앱
# =========================
def main():
    # 1) 헤더
    render_header()

    # 2) reports.csv 로드
    df = load_reports()

    # 3) 사이드바 필터
    st.sidebar.header("Filters")

    def unique_values(col_name: str):
        if col_name not in df.columns:
            return ["All"]
        values = [v for v in df[col_name].unique().tolist() if str(v).strip()]
        return ["All"] + sorted(values)

    customers = unique_values("customer")
    vpc_parts = unique_values("vpc_part")
    test_nos = unique_values("test_no")
    media_colors = unique_values("media_color")

    selected_customer = st.sidebar.selectbox("Customer", customers)
    selected_vpc_part = st.sidebar.selectbox("VPC Part#", vpc_parts)
    selected_test_no = st.sidebar.selectbox("Test No.", test_nos)
    selected_media_color = st.sidebar.selectbox("Media Color", media_colors)

    search_text = st.sidebar.text_input(
        "Search (Test No., Item Description, Notes)"
    )

    # 4) 필터 적용
    filtered = df.copy()

    if selected_customer != "All" and "customer" in filtered.columns:
        filtered = filtered[filtered["customer"] == selected_customer]

    if selected_vpc_part != "All" and "vpc_part" in filtered.columns:
        filtered = filtered[filtered["vpc_part"] == selected_vpc_part]

    if selected_test_no != "All" and "test_no" in filtered.columns:
        filtered = filtered[filtered["test_no"] == selected_test_no]

    if selected_media_color != "All" and "media_color" in filtered.columns:
        filtered = filtered[filtered["media_color"] == selected_media_color]

    if search_text:
        search_text_lower = search_text.lower()

        test_col = (
            filtered["test_no"].astype(str)
            if "test_no" in filtered.columns
            else pd.Series("", index=filtered.index)
        )
        desc_col = (
            filtered["item_description"].astype(str)
            if "item_description" in filtered.columns
            else pd.Series("", index=filtered.index)
        )
        notes_col = (
            filtered["notes"].astype(str)
            if "notes" in filtered.columns
            else pd.Series("", index=filtered.index)
        )

        mask = (
            test_col.str.lower().str.contains(search_text_lower, na=False)
            | desc_col.str.lower().str.contains(search_text_lower, na=False)
            | notes_col.str.lower().str.contains(search_text_lower, na=False)
        )

        filtered = filtered[mask]

    # 5) Results 테이블
    st.subheader("Results")

    table_df = filtered.copy()

    table_df = table_df.rename(
        columns={
            "customer": "Customer",
            "vpc_part": "VPC Part#",
            "item_description": "Item Description",
            "media_color": "Media Color",
            "date": "Date",
            "test_no": "Test No.",
            "format": "Format",
            "notes": "Notes",
            "url": "File",
        }
    )

    cols_in_order = [
        "Customer",
        "VPC Part#",
        "Item Description",
        "Media Color",
        "Date",
        "Test No.",
        "Format",
        "Notes",
        "File",
    ]
    cols_in_order = [c for c in cols_in_order if c in table_df.columns]
    table_df = table_df[cols_in_order]

    if "File" in table_df.columns:
        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "File": st.column_config.LinkColumn(
                    "File",
                    display_text="📎 File Download",
                    help="Download / open file",
                )
            },
        )
    else:
        st.dataframe(table_df, use_container_width=True, hide_index=True)

    # 6) Open Reports 텍스트 리스트
    st.markdown("---")
    st.subheader("Open Reports")

    if filtered.empty:
        st.write("No reports match the selected filters.")
    else:
        for _, row in filtered.iterrows():
            test_no = str(row.get("test_no", "")).strip() or "(no Test No.)"
            customer = str(row.get("customer", "")).strip()
            vpc_part = str(row.get("vpc_part", "")).strip()
            date = str(row.get("date", "")).strip()

            label_parts = [test_no]
            if customer:
                label_parts.append(customer)
            if vpc_part:
                label_parts.append(vpc_part)
            if date:
                label_parts.append(date)
            label = " | ".join(label_parts)

            url = str(row.get("url", "")).strip()

            if not url:
                st.write(f"• {label} — (no file)")
            else:
                st.markdown(f"• **{label}** – [📎 File Download]({url})")

    # 7) FD Blue Heaven Test Results2.xlsx 내용 항상 표시
    st.markdown("---")
    st.subheader("FD Blue Heaven Test Results")

    try:
        # 기본: 첫 번째 시트만 사용 (필요하면 sheet_name="Sheet1" 처럼 이름 지정)
        blue_df = pd.read_excel(SPECIAL_EXCEL_PATH)

        st.caption("Always showing contents of FD Blue Heaven Test Results2.xlsx")
        st.dataframe(blue_df, use_container_width=True)

    except FileNotFoundError:
        st.error("'FD Blue Heaven Test Results2.xlsx' 파일을 앱이 실행되는 폴더에 넣어야 합니다.")
    except Exception as e:
        st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")


# =========================
# 실행
# =========================
if __name__ == "__main__":
    main()