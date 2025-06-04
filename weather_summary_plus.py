import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone

# 1. 即時觀測
def get_realtime_weather(station_full_name):
    with open("response_1749029442984.json", encoding="utf-8") as f:
        data = json.load(f)
    stations = data["records"]["Station"]
    for s in stations:
        full_name = f"{s['StationName']}（{s['GeoInfo']['CountyName']} {s['GeoInfo']['TownName']}）"
        if full_name == station_full_name:
            e = s["WeatherElement"]
            obs_time = s["ObsTime"]["DateTime"]
            return (
                f"{full_name}\n  觀測時間：{obs_time}"
                f"\n  天氣現象：{e.get('Weather', 'N/A')}"
                f"\n  溫度：{e.get('AirTemperature', 'N/A')}°C"
                f"\n  濕度：{e.get('RelativeHumidity', 'N/A')}%"
                f"\n  風速：{e.get('WindSpeed', 'N/A')} m/s"
                f"\n  降雨量：{e.get('Now', {}).get('Precipitation', 'N/A')} mm"
            )
    return f"找不到{station_full_name}的即時天氣資料"

# 2. 七天預報
def get_forecast_weather(location="臺南市"):
    with open("response_1748776415445.json", encoding="utf-8") as f:
        data = json.load(f)
    locations = data["records"]["Locations"][0]["Location"]
    location_data = next((loc for loc in locations if loc["LocationName"] == location), None)
    if not location_data:
        return f"找不到{location}的資料"

    element_map = {}
    for elem in location_data["WeatherElement"]:
        element_map[elem["ElementName"]] = elem["Time"]

    now = datetime.now(timezone(timedelta(hours=8)))
    future_limit = now + timedelta(days=7)
    dt_format = "%Y-%m-%dT%H:%M:%S%z"

    daily_data = defaultdict(dict)
    for elem_name, times in element_map.items():
        for time_item in times:
            try:
                start_dt = datetime.strptime(time_item["StartTime"], dt_format)
                if not (now <= start_dt <= future_limit):
                    continue
                key = start_dt.strftime("%Y/%m/%d %H:%M")
                if elem_name == "風速":
                    daily_data[key]["風速"] = time_item["ElementValue"][0].get("WindSpeed", "N/A")
                if elem_name == "天氣現象":
                    daily_data[key]["天氣"] = time_item["ElementValue"][0].get("Weather", "N/A")
                if elem_name == "平均溫度":
                    daily_data[key]["溫度"] = time_item["ElementValue"][0].get("Temperature", "N/A")
                if elem_name == "12小時降雨機率":
                    rain_value = time_item["ElementValue"][0].get("ProbabilityOfPrecipitation", "N/A")
                    if rain_value == "-" or rain_value == "" or rain_value is None:
                        rain_value = "無資料"
                    daily_data[key]["降雨機率"] = rain_value
            except:
                continue

    if not daily_data:
        return "查無有效天氣資料"

    summary_lines = [f"{location}未來七天天氣摘要如下："]
    for date in sorted(daily_data.keys()):
        d = daily_data[date]
        wind = f"{d.get('風速', 'N/A')} m/s"
        temp = f"{d.get('溫度', 'N/A')}°C"
        wx = d.get('天氣', 'N/A')
        rain = d.get('降雨機率', '無資料')
        if rain not in ["無資料", "N/A"]:
            rain = f"{rain}%"
        summary_lines.append(f"- {date}：{wx}，🌬️ 風速 {wind}，🌡️ 溫度 {temp}，🌧️ 降雨機率 {rain}")

    return "\n".join(summary_lines)
