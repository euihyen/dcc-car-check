import pandas as pd
import streamlit as st

# 페이지 설정 (모바일에서 화면이 꽉 차고 깔끔하게 보이도록 설정)
st.set_page_config(
    page_title="DCC점 직원 차량 조회", page_icon="🚗", layout="centered"
)

# 모바일 화면에 맞춘 깔끔한 타이틀
st.markdown(
    "<h2 style='text-align: center; color: #333;'>🚗 DCC점 직원 차량 조회</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 14px;'>차량 번호 또는"
    " 성명을 입력하여 즉시 확인하세요</p>",
    unsafe_allow_html=True,
)

# 엑셀 파일 경로
purl = "DCC점_직원_소유_차량정보.xlsx"


# 엑셀 데이터 로드 함수 (시트 통합 처리)
@st.cache_data
def load_data():
  try:
    df_total = pd.DataFrame()
    for sheet in ["제과생산", "제빵생산"]:
      try:
        df_sheet = pd.read_excel(purl, sheet_name=sheet)
        df_sheet["구분"] = sheet
        df_total = pd.concat([df_total, df_sheet], ignore_index=True)
      except Exception:
        pass
    if df_total.empty:
      df_total = pd.read_excel(purl)
    return df_total
  except Exception as e:
    st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
    return None


# 데이터 불러오기
df_cars = load_data()

# 검색 입력창 (모바일 키보드가 바로 올라오도록 구성)
st.markdown("---")
search_keyword = st.text_input(
    "🔍 **검색어 입력**",
    placeholder="차량번호 뒷자리 또는 성명 입력 (예: 1234 또는 홍길동)",
)

# 검색 버튼 (모바일 화면에서 누르기 쉽게 크고 넓게 배치)
search_clicked = st.button(
    "🔍 조회하기", use_container_width=True, type="primary"
)

if search_clicked or search_keyword:
  if search_keyword.strip() == "":
    st.warning("⚠️ 검색어를 입력해 주세요.")
  elif df_cars is not None:
    keyword = search_keyword.strip().replace(" ", "")

    # 컬럼명 자동 감지
    plate_col = "번호판" if "번호판" in df_cars.columns else "차량번호"
    name_col = "성명" if "성명" in df_cars.columns else "근무파트"

    # 검색어 포함 여부 확인 (번호판 또는 성명 기준)
    matched_rows = df_cars[
        df_cars[plate_col].astype(str).str.replace(" ", "").str.contains(keyword)
        | df_cars[name_col]
        .astype(str)
        .str.replace(" ", "")
        .str.contains(keyword)
    ]

    st.markdown("---")
    st.subheader("📌 조회 결과")

    if not matched_rows.empty:
      st.success(
          f"✅ 총 **{len(matched_rows)}건**의 일치하는 차량을 찾았습니다!"
      )

      for idx, row in matched_rows.iterrows():
        # 모바일 카드 형식으로 깔끔하게 박스 표현
        with st.container():
          st.markdown(
              f"""
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #28a745;">
                        <b style="font-size: 16px;">🚗 차량번호: {row.get(plate_col, '정보 없음')}</b><br>
                        • <b>성명:</b> {row.get('성명', '정보 없음')}<br>
                        • <b>근무파트:</b> {row.get('근무파트', '정보 없음')}<br>
                        • <b>차종/색상:</b> {row.get('차종', '')} / {row.get('색상', '')}<br>
                        • <b>구분:</b> {row.get('구분', '일반')}
                    </div>
                    """,
              unsafe_allow_html=True,
          )
    else:
      st.error("❌ **등록되지 않은 차량(외부 차량)입니다.**")
  else:
    st.error("엑셀 데이터가 로드되지 않았습니다.")

# 하단 안내 문구
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #999; font-size: 12px;'>성심당 DCC점"
    " 주차관리 시스템</p>",
    unsafe_allow_html=True,
)
