import os
import re
import requests
import streamlit as st

API_KEY = os.getenv("YOUTUBE_API_KEY")

st.title("🎵 내 취향인 노래 찾기")

url = st.text_input("유튜브 링크 입력")

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1][:11]
    return None

def get_video_info(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={API_KEY}"
    data = requests.get(url).json()

    title = data["items"][0]["snippet"]["title"]

    return title

def get_comments(video_id):
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&maxResults=20&key={API_KEY}"

    data = requests.get(url).json()

    comments = []

    if "items" in data:
        for item in data["items"]:
            text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comments.append(text)

    return comments

def keyword(text):

    words = re.findall(r"[가-힣A-Za-z]+", text)

    stop = ["영상","노래","진짜","너무","좋아요","입니다","ㅋㅋ","ㅎㅎ"]

    result = []

    for w in words:
        if len(w) >= 2 and w not in stop:
            result.append(w)

    return " ".join(result[:5])

def search_music(query):

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=5&q={query}&key={API_KEY}"

    data = requests.get(url).json()

    result = []

    for item in data["items"]:
        result.append({
            "title":item["snippet"]["title"],
            "id":item["id"]["videoId"]
        })

    return result

if st.button("추천받기"):

    video_id = get_video_id(url)

    title = get_video_info(video_id)

    comments = get_comments(video_id)

    query = keyword(title + " " + " ".join(comments))

    st.write("### 추출 키워드")
    st.write(query)

    st.write("## 추천 노래")

    musics = search_music(query)

    for music in musics:
        if music["id"] != video_id:
            st.write(f"🎵 {music['title']}")
            st.write(f"https://youtu.be/{music['id']}")
