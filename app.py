from pathlib import Path
import webbrowser

# 저장할 HTML 파일 이름
OUTPUT_FILE = "filtration_portal.html"

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Filtration Test Report Portal</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <style>
    :root {
      --vpc-blue: #004b8d;
      --vpc-red: #d71920;
      --text-gray: #555555;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
        sans-serif;
      color: #222222;
      background-color: #ffffff;
    }

    /* 페이지 전체 레이아웃 */
    .page-wrapper {
      max-width: 1100px;
      margin: 0 auto;
      padding: 24px 16px;
    }

    /* 헤더 영역 */
    .portal-header {
      display: flex;
      align-items: flex-start;       /* 로고 상단을 제목 상단과 맞추기 */
      gap: 24px;
    }

    .portal-logo {
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
    }

    .portal-logo img {
      display: block;
      max-height: 54px;              /* 로고 높이 조정은 여기 숫자만 바꾸면 됨 */
      height: auto;
      margin-top: 4px;               /* 제목 글씨와 상단 정렬 맞추기 */
    }

    .portal-logo-subtext {
      margin-top: 8px;
      font-size: 14px;
      font-weight: 600;
      color: var(--vpc-red);
    }

    .portal-title-block {
      flex: 1;
      min-width: 0;
    }

    .portal-title {
      margin: 0;
      font-size: 32px;
      font-weight: 700;
      line-height: 1.2;
    }

    .portal-subtitle {
      margin: 6px 0 0;
      font-size: 14px;
      color: var(--text-gray);
    }

    /* ---- 모바일/태블릿 반응형 ---- */
    @media (max-width: 768px) {
      .page-wrapper {
        padding: 16px 12px;
      }

      .portal-header {
        flex-direction: column;      /* 휴대폰에서는 위아래로 자연스럽게 배치 */
        align-items: flex-start;
        gap: 12px;
      }

      .portal-logo img {
        max-height: 44px;
        margin-top: 0;
      }

      .portal-title {
        font-size: 24px;
      }

      .portal-subtitle {
        font-size: 13px;
      }
    }
  </style>
</head>
<body>
  <div class="page-wrapper">
    <header class="portal-header">
      <!-- 로고 영역 -->
      <div class="portal-logo">
        <!-- TODO: 실제 로고 파일 이름으로 src 바꿔주세요 (예: vpc-logo.png) -->
        <img src="vpc-logo.png" alt="VPC Group Inc. Logo" />
        <div class="portal-logo-subtext">
          Filtration Team &mdash; USA
        </div>
      </div>

      <!-- 제목 영역 -->
      <div class="portal-title-block">
        <h1 class="portal-title">
          Filtration Test Report Portal
        </h1>
        <p class="portal-subtitle">
          Browse and access filtration test reports (PDF / Excel) remotely.
        </p>
      </div>
    </header>

    <!-- 이 아래부터 실제 포털 컨텐츠 추가하면 됩니다 -->
    <!-- example:
    <main>
      ...
    </main>
    -->
  </div>
</body>
</html>
"""

def main():
    # 현재 작업 폴더에 HTML 파일 저장
    out_path = Path(OUTPUT_FILE).resolve()
    out_path.write_text(html, encoding="utf-8")
    print(f"HTML 저장 완료: {out_path}")

    # 기본 웹브라우저로 열기
    webbrowser.open(out_path.as_uri())

if __name__ == "__main__":
    main()
사용 방법 정리
위 코드를 Spyder에서 새 파일로 붙여넣기 → 저장.

같은 폴더에 로고 파일을 vpc-logo.png 이름으로 넣기
(이름이 다르면 img src="..." 부분만 바꾸면 됩니다.)

Spyder에서 Run (F5) 실행.

filtration_portal.html 이 생성되고, 브라우저가 자동으로 열립니다.

PC/모바일에서 로고와 Filtration Test Report Portal 정렬 상태 확인.

원하시면 이 헤더 아래에 테이블, 버튼, 파일 리스트 영역까지 포함한 전체 페이지 뼈대도 Python 안에 같이 만들어 줄게요.







