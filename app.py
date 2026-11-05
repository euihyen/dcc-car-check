import re
import easyocr
import numpy as np
import pandas as pd
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="DCC점 직원 차량 확인 시스템", page_icon="🚗", layout="centered"
)

st.title("🚗 DCC점 직원 차량 확인 프로그램")
st.write(
    "주차장 진입 차량의 번호판 사진을 업로드하면 직원 차량 여부를 실시간으로"
    " 확인합니다."
)


# 엑셀 데이터 로드 함수 (캐싱 적용)
@st.cache_data
purl = "DCC점_직원_소유_차량정보.xlsx"


def load_data():
  try:
    df_jaegwa = pd.read_excel(purl, sheet_name="제과생산")
    df_jaegwa["구분"] = "제과생산"
    # 컬럼 이름 맞추기 (이름/성명, 근무파트/팀)
    df_jaegwa = df_jaegwa.rename(columns={"근무파트": "파트/팀", "이름": "성명"})

    df_jaebang = pd.read_excel(purl, sheet_name="제빵생산")
    df_jaebang["구분"] = "제빵생산"
    df_jaebang = df_jaebang.rename(columns={"팀": "파트/팀", "제조사": "브랜드", "차종": "종류"})

    # 데이터 통합
    df_total = pd.concat([df_jaegwa, df_jaebang], ignore_index=True)
    return df_total
  except Exception as e:
    st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")
    return None


df_cars = load_data()

# EasyOCR 모델 로드 (한국어, 영어 지원)
@st.cache_resource
def load_ocr_reader():
  return easyocr.Reader(["ko", "en"])


with st.spinner("AI 번호판 인식 모델을 불러오는 중입니다... 잠시만 기다려주세요."):
  reader = load_ocr_reader()

# 파일 업로드 위젯
uploaded_file = st.file_uploader(
    "차량 번호판 사진을 업로드하세요", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  # 이미지 표시
  file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
  st.image(
      file_bytes, caption="업로드된 차량 이미지", use_column_width=True
  )

  if st.button("🔍 번호판 인식 및 직원 확인"):
    with st.spinner("번호판을 분석하고 있습니다..."):
      # OCR 수행
      results = reader.readtext(file_bytes)

      detected_texts = [res[1] for res in results]
      full_text = "".join(detected_texts)

      # 공백 제거 및 번호판 패턴 추출 (예: 숫자+한글+숫자 조합)
      # 간단하게 전체 텍스트에서 공백을 제거한 문자열 활용
      cleaned_detected = full_text.replace(" ", "")

      st.info(f"인식된 텍스트: {full_text} (정제: {cleaned_detected})")

      # 엑셀 데이터와 대조
      matched_row = None
      if df_cars is not None:
        for idx, row in df_cars.iterrows():
          db_plate = str(row["번호판"]).replace(" ", "")
          # 인식된 텍스트 내에 DB 번호판이 포함되어 있거나 일치하는 경우
          if db_plate in cleaned_detected or cleaned_detected in db_plate:
            matched_row = row
            break

      # 결과 출력
      st.markdown("---")
      st.subheader("📌 판정 결과")
      if matched_row is not None:
        st.success("✅ **[등록된 직원 차량입니다]**")
        col1, col2 = st.columns(2)
        with col1:
          st.write(f"**소속 구분:** {matched_row['구분']}")
          st.write(f"**파트/팀:** {matched_row['파트/팀']}")
          st.write(f"**성명:** {matched_row['성명']}")
        with col2:
          st.write(f"**브랜드:** {matched_row['브랜드']}")
          st.write(f"**차종/종류:** {matched_row['종류']}")
          st.write(f"**등록 번호판:** {matched_row['번호판']}")
      else:
        st.error(
            "❌ **[미등록 차량(외부 차량)입니다]** 직원 차량 리스트에 일치하는"
            " 번호판이 없습니다."
        )