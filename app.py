import cv2
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

purl = "DCC점_직원_소유_차량정보.xlsx"


# 엑셀 데이터 로드
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


# EasyOCR 모델 로드 (상태 메시지 표시)
@st.cache_resource
def load_ocr_reader():
  return easyocr.Reader(["ko", "en"])


with st.status(
    "🔄 시스템 초기화 중... (AI 모델 로딩에는 1~2분이 소요될 수"
    " 있습니다)",
    expanded=True,
) as status:
  st.write("📊 엑셀 데이터를 불러오는 중...")
  df_cars = load_data()

  st.write(
      "🤖 AI 번호판 인식 모델(EasyOCR)을 준비하는 중... (최초 실행 시 모델을"
      " 다운로드합니다)"
  )
  reader = load_ocr_reader()
  status.update(label="✅ 시스템 준비 완료!", state="complete", expanded=False)

# 파일 업로더 생성
uploaded_file = st.file_uploader(
    "차량 번호판 사진을 업로드하세요", type=["jpg", "jpeg", "png"]
)

if uploaded_file is None:
  st.info("👉 위 버튼을 눌러 차량 번호판 사진을 업로드해 주세요.")
else:
  file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
  image = cv2.imdecode(file_bytes, 1)
  st.image(image, channels="BGR", caption="업로드한 사진")

  if reader is not None and df_cars is not None:
    with st.spinner("🔍 번호판을 분석 중입니다..."):
      ocr_results = reader.readtext(image)

      raw_text = ""
      for bbox, text, prob in ocr_results:
        raw_text += text

      cleaned_detected = raw_text.replace(" ", "")
      st.info(f"🔍 인식된 텍스트: {cleaned_detected}")

      matched_row = None
      plate_col = "번호판" if "번호판" in df_cars.columns else "차량번호"

      for index, row in df_cars.iterrows():
        db_plate = str(row[plate_col]).replace(" ", "")
        if db_plate in cleaned_detected or cleaned_detected in db_plate:
          matched_row = row
          break

      st.markdown("---")
      st.subheader("📌 판정 결과")

      if matched_row is not None:
        st.success("✅ **[등록된 직원 차량입니다]**")
        col1, col2 = st.columns(2)
        with col1:
          st.write(
              f"**근무파트:** {matched_row.get('근무파트', '정보 없음')}"
          )
          st.write(f"**성명:** {matched_row.get('성명', '정보 없음')}")
          st.write(f"**브랜드:** {matched_row.get('브랜드', '정보 없음')}")
        with col2:
          st.write(f"**차종:** {matched_row.get('차종', '정보 없음')}")
          st.write(f"**색상:** {matched_row.get('색상', '정보 없음')}")
          st.write(f"**번호판:** {matched_row.get(plate_col, '정보 없음')}")
      else:
        st.error(
            "❌ **[미등록 차량(외부 차량)입니다]** 직원 차량 리스트에 일치하는"
            " 번호판이 없습니다."
        )
  else:
    st.error("시스템 리소스가 정상적으로 로드되지 않았습니다.")
