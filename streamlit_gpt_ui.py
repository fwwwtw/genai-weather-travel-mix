import streamlit as st
import json
import google.generativeai as genai
from weather_summary_plus import get_realtime_weather, get_forecast_weather

st.title("☁️ 台灣天氣查詢與 Gemini 旅遊建議")

# 1. 選查詢模式
mode = st.radio("請選擇天氣查詢模式：", ["即時觀測（全國測站）", "七天預報（22縣市）"])

# 2. 地點選單
if mode == "即時觀測（全國測站）":
    # 所有測站
    with open("response_1749029442984.json", encoding="utf-8") as f:
        data = json.load(f)
    stations = data["records"]["Station"]
    station_list = [
        f"{s['StationName']}（{s['GeoInfo']['CountyName']} {s['GeoInfo']['TownName']}）"
        for s in stations
    ]
    selected = st.selectbox("選擇測站", station_list)
else:
    # 22縣市
    with open("response_1748776415445.json", encoding="utf-8") as f:
        data = json.load(f)
    city_list = [loc["LocationName"] for loc in data["records"]["Locations"][0]["Location"]]
    selected = st.selectbox("選擇縣市", city_list)

user_pref_default = st.selectbox(
    "請選擇旅遊偏好（可不選）",
    ["請選擇", "輕鬆自然系🌿", "熱血戶外型🏃🏻‍♂️‍➡️", "文化深度派🏛️", "網美必備💅🏻", "躲太陽派😶‍🌫️", "家庭親子行👨🏻‍👩🏻‍👧🏻‍👦🏻"],
    index=0
)
user_pref_custom = st.text_input("或自行輸入偏好需求（可複選描述）")
user_pref = user_pref_custom if user_pref_custom.strip() else user_pref_default

api_key = st.text_input("請輸入 Google Gemini API 金鑰：", type="password")
if api_key:
    genai.configure(api_key=api_key)

if st.button("🔎查詢天氣與 AI 建議") and api_key:
    with st.spinner("查詢天氣與旅遊建議生成中..."):
        if mode == "即時觀測（全國測站）":
            weather_info = get_realtime_weather(selected)
        else:
            weather_info = get_forecast_weather(selected)

        if "找不到" in weather_info or "查無" in weather_info or "錯誤" in weather_info:
            st.error(weather_info)
        else:
            st.subheader("📑 天氣摘要：")
            st.write(weather_info)

            prompt = f"""
你是一位專業台灣旅遊顧問，請根據下方「天氣預報摘要」與「旅遊偏好」：
1. 提供 1 份 2 天 1 夜的旅遊行程建議（地點、活動、拍照打卡景點），盡量搭配天氣狀況安排最合適的活動。
2. 回答內容要有 emoji，風格要活潑一點，讓人想要馬上出門。
3. 不要直接複製天氣摘要，要根據天氣狀況給出專屬旅遊建議。
4. 以條列式清楚整理行程內容，結尾可以給貼心提醒，不要重複資料，請融合判斷給出貼心推薦。
（可以用 emoji，也能提醒注意事項）。
【天氣預報摘要】
{weather_info}
【旅遊偏好】
{user_pref}
"""
            try:
                model = genai.GenerativeModel("models/gemini-1.5-flash-001")
                resp = model.generate_content(prompt)
                ai_suggest = resp.text
                st.subheader("🤖 Gemini 旅遊建議：")
                st.write(ai_suggest)
            except Exception as e:
                st.error(f"Gemini 回應錯誤：{e}")

st.caption("※ 可查詢全國所有即時觀測站或22縣市七天天氣預報！")
