import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

st.set_page_config(page_title="서울시 공영주차장 정보", layout="wide")

st.title("🚗 서울시 공영주차장 정보 조회")
st.write("CSV 파일을 업로드하면 주차요금, 위치, 지도, 가장 저렴한 주차장을 확인할 수 있습니다.")

uploaded_file = st.file_uploader(
    "서울시 공영주차장 CSV 업로드",
    type="csv"
)

if uploaded_file is not None:

    # -----------------------------
    # CSV 읽기 (한글 cp949)
    # -----------------------------
    df = pd.read_csv(uploaded_file, encoding="cp949")

    # 주소에서 자치구 추출
    df["자치구"] = df["주소"].str.extract(
        r"(강남구|강동구|강북구|강서구|관악구|광진구|구로구|금천구|노원구|도봉구|동대문구|동작구|마포구|서대문구|서초구|성동구|성북구|송파구|양천구|영등포구|용산구|은평구|종로구|중구|중랑구)"
    )

    st.success("데이터 업로드 완료!")

    # -----------------------------
    # 사이드바
    # -----------------------------

    st.sidebar.header("검색 조건")

    gu = st.sidebar.selectbox(
        "자치구 선택",
        ["전체"] + sorted(df["자치구"].dropna().unique())
    )

    parking_type = st.sidebar.selectbox(
        "주차장 종류",
        ["전체"] + sorted(df["주차장 종류명"].dropna().unique())
    )

    fee_type = st.sidebar.selectbox(
        "무료 / 유료",
        ["전체"] + sorted(df["유무료구분명"].dropna().unique())
    )

    hour = st.sidebar.number_input(
        "예상 주차시간(시간)",
        min_value=1,
        max_value=24,
        value=1
    )

    # -----------------------------
    # 데이터 필터
    # -----------------------------

    result = df.copy()

    if gu != "전체":
        result = result[result["자치구"] == gu]

    if parking_type != "전체":
        result = result[result["주차장 종류명"] == parking_type]

    if fee_type != "전체":
        result = result[result["유무료구분명"] == fee_type]

    # -----------------------------
    # 예상 요금 계산
    # -----------------------------

    result["기본 주차 요금"] = pd.to_numeric(result["기본 주차 요금"], errors="coerce").fillna(0)
    result["기본 주차 시간(분 단위)"] = pd.to_numeric(result["기본 주차 시간(분 단위)"], errors="coerce").replace(0, np.nan)

    minutes = hour * 60

    result["예상주차요금"] = (
        np.ceil(minutes / result["기본 주차 시간(분 단위)"])
        * result["기본 주차 요금"]
    )

    result["예상주차요금"] = result["예상주차요금"].fillna(0).astype(int)

    # -----------------------------
    # 통계
    # -----------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric("검색된 주차장", len(result))
    col2.metric("무료 주차장", (result["유무료구분명"] == "무료").sum())
    col3.metric("유료 주차장", (result["유무료구분명"] == "유료").sum())

    # -----------------------------
    # 가장 저렴한 주차장
    # -----------------------------

    if len(result) > 0:

        cheapest = result.loc[result["예상주차요금"].idxmin()]

        st.success(f"""
### 💰 가장 저렴한 주차장

**주차장명:** {cheapest["주차장명"]}

**주소:** {cheapest["주소"]}

**예상요금:** {cheapest["예상주차요금"]:,}원
""")

    # -----------------------------
    # 표 출력
    # -----------------------------

    st.subheader("주차장 목록")

    st.dataframe(
        result[
            [
                "주차장명",
                "자치구",
                "주소",
                "주차장 종류명",
                "유무료구분명",
                "총 주차면",
                "기본 주차 요금",
                "기본 주차 시간(분 단위)",
                "일 최대 요금",
                "전화번호",
                "예상주차요금"
            ]
        ],
        use_container_width=True
    )

    # -----------------------------
    # 지도
    # -----------------------------

    map_df = result.dropna(subset=["위도", "경도"])

    if len(map_df) > 0:

        st.subheader("📍 주차장 위치")

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[경도, 위도]',
            get_radius=60,
            get_fill_color='[255,0,0,180]',
            pickable=True
        )

        view_state = pdk.ViewState(
            latitude=map_df["위도"].mean(),
            longitude=map_df["경도"].mean(),
            zoom=11
        )

        tooltip = {
            "html": """
<b>{주차장명}</b><br/>
주소 : {주소}<br/>
종류 : {주차장 종류명}<br/>
요금 : {기본 주차 요금}원<br/>
무료/유료 : {유무료구분명}
"""
        }

        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip
            )
        )

    else:
        st.warning("지도에 표시할 좌표 정보가 없습니다.")
