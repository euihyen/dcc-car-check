import pandas as pd
import streamlit as st
import easyocr

# 페이지 설정
st.set_page_config(
    page_title="DCC점 직원 차량 확인 시스템", page_icon="🚗", layout="centered"
)

st.title("🚗 DCC점 직원 차량 확인 프로그램")
st.write(
    "주차장 진입 차량의 번호판 사진을 업로드하면 직원 차량 여부를 실시간으로 확인합니다."
)


# 코드 위쪽에 함수와 상관없이 먼저 정의 (전역 변수)
purl = "DCC점_직원_소유_차량정보.xlsx"

@st.cache_data
def load_data():
    # 이제 함수 안에서도 밖에서 만든 purl을 가져다 쓸 수 있습니다.
    df = pd.read_excel(purl)
    return df
    
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

import streamlit as st
import numpy as np
import cv2

# 파일 업로더 생성
uploaded_file = st.file_uploader("차량 번호판 사진을 업로드하세요", type=["jpg", "jpeg", "png"])

# 💡 핵심: uploaded_file이 None이 아닐 때(즉, 파일이 업로드되었을 때)만 실행되도록 처리!
if uploaded_file is not None:
    # 파일을 읽어서 바이트 배열로 변환
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    
    # 이미지를 OpenCV로 읽기
    image = cv2.imdecode(file_bytes, 1)
    
    # 화면에 업로드된 이미지 보여주기
    st.image(image, channels="BGR", caption="업로드한 사진")
    
    # 여기에 OCR 분석 및 직원 차량 확인 코드가 들어가면 됩니다!
else:
    st.info("👉 위 버튼을 눌러 차량 번호판 사진을 업로드해 주세요.")

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
