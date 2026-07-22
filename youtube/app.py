import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from urllib.parse import urlparse, parse_qs

# Github Secrets 또는 secrets.toml
API_KEY = st.secrets["YOUTUBE_API_KEY"]

youtube = build("youtube", "v3", developerKey=API_KEY)

st.title("📺 유튜브 댓글 분석기")

url = st.text_input("유튜브 링크 입력")

if st.button("분석"):

    video_id = parse_qs(urlparse(url).query)["v"][0]

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100
    )

    response = request.execute()

    comments = []

    for item in response["items"]:
        c = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(c)

    df = pd.DataFrame({"댓글": comments})

    st.subheader("댓글")
    st.dataframe(df)

    st.subheader("댓글 길이")

    df["길이"] = df["댓글"].str.len()

    fig, ax = plt.subplots()
    ax.hist(df["길이"])
    st.pyplot(fig)

    st.subheader("워드클라우드")

    text = " ".join(comments)

    wc = WordCloud(
        font_path="malgun.ttf",   # 윈도우
        width=800,
        height=400,
        background_color="white"
    ).generate(text)

    fig, ax = plt.subplots(figsize=(10,5))
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig)
