import streamlit as st
import pandas as pd
import re
from collections import Counter
from googleapiclient.discovery import build
import plotly.express as px

st.set_page_config(page_title="YouTube 댓글 분석기")

API_KEY = st.secrets["YOUTUBE_API_KEY"]

youtube = build("youtube", "v3", developerKey=API_KEY)

st.title("📺 YouTube 댓글 분석기")

url = st.text_input("유튜브 URL 입력")

def video_id(url):
    m = re.search(r"(?:v=|youtu\.be/)([^&?/]+)", url)
    return m.group(1) if m else None

if st.button("댓글 분석"):

    vid = video_id(url)

    if not vid:
        st.error("URL을 확인하세요.")
        st.stop()

    comments = []
    token = None

    while True:
        res = youtube.commentThreads().list(
            part="snippet",
            videoId=vid,
            maxResults=100,
            pageToken=token,
            textFormat="plainText"
        ).execute()

        for item in res["items"]:
            s = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "댓글": s["textDisplay"],
                "좋아요": s["likeCount"]
            })

        token = res.get("nextPageToken")

        if token is None or len(comments) >= 500:
            break

    df = pd.DataFrame(comments)

    st.success(f"{len(df)}개의 댓글 수집 완료")

    st.dataframe(df)

    text = " ".join(df["댓글"])

    words = re.findall(r"[가-힣]{2,}", text)

    stop = {
        "영상","진짜","너무","정말","오늘","입니다",
        "그리고","그냥","하는","있는","같은"
    }

    words = [w for w in words if w not in stop]

    top = Counter(words).most_common(20)

    freq = pd.DataFrame(top, columns=["단어","빈도"])

    st.subheader("TOP 20 단어")

    fig = px.bar(
        freq,
        x="단어",
        y="빈도",
        color="빈도"
    )

    st.plotly_chart(fig, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "CSV 다운로드",
        csv,
        "youtube_comments.csv",
        "text/csv"
    )
