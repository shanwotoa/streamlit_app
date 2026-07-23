import os
import re
import requests
import streamlit as st
from collections import Counter

API_KEY = os.getenv("YOUTUBE_API_KEY")

st.set_page_config(page_title="내 취향인 노래 찾기")
st.title("🎵 댓글 기반 노래 추천")

# 감성 키워드 → 검색어
MOOD_MAP = {
    "감성": "감성 플레이리스트",
    "힐링": "힐링 노래",
    "새벽": "새벽 감성 노래",
    "눈물": "슬픈 노래",
    "슬픔": "슬픈 발라드",
    "청춘": "청춘 노래",
    "사랑": "사랑 노래",
    "여름": "여름 노래",
    "겨울": "겨울 감성",
    "인디": "인디 명곡",
    "락": "락 추천",
    "밴드": "밴드 명곡"
}

STOPWORDS = {
    "노래","영상","진짜","너무","좋아요","감사","최고","입니다",
    "ㅋㅋ","ㅎㅎ","ㅠㅠ","ㅜㅜ","이번","항상","이거","정말"
}

def video_id(url):
    m = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
    if m:
        return m.group(1)
    return url[-11:]

def get_title(video):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video}&key={API_KEY}"
    data = requests.get(url).json()
    return data["items"][0]["snippet"]["title"]

def get_comments(video):
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video}&maxResults=100&key={API_KEY}"

    comments = []

    while url:
        data = requests.get(url).json()

        if "items" not in data:
            break

        for item in data["items"]:
            text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(text)

        if "nextPageToken" in data and len(comments) < 100:
            token = data["nextPageToken"]
            url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video}&pageToken={token}&maxResults=100&key={API_KEY}"
        else:
            break

    return comments

def analyze(comments):

    text = " ".join(comments)

    words = re.findall(r"[가-힣]{2,}", text)

    words = [w for w in words if w not in STOPWORDS]

    count = Counter(words)

    return count.most_common(10)

def search_music(query, original_title):

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=10&q={query}&key={API_KEY}"

    data = requests.get(url).json()

    result = []

    for item in data["items"]:

        title = item["snippet"]["title"]

        # 같은 노래 제외
        if original_title.lower()[:10] in title.lower():
            continue

        result.append({
            "title": title,
            "url": f"https://youtu.be/{item['id']['videoId']}"
        })

    return result


link = st.text_input("유튜브 링크 입력")

if st.button("추천받기"):

    vid = video_id(link)

    title = get_title(vid)

    comments = get_comments(vid)

    keywords = analyze(comments)

    st.subheader("댓글에서 많이 나온 단어")

    for k, c in keywords:
        st.write(f"✅ {k} ({c})")

    mood = None

    for k, _ in keywords:
        if k in MOOD_MAP:
            mood = MOOD_MAP[k]
            break

    if mood is None:
        mood = "감성 플레이리스트"

    st.subheader(f"추천 검색어 : {mood}")

    musics = search_music(mood, title)

    st.subheader("추천 노래")

    if not musics:
        st.info("추천 결과가 없습니다.")

    for music in musics[:5]:
        st.markdown(f"**{music['title']}**")
        st.write(music["url"])
