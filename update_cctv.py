import requests
import json

# ใส่ API KEY ของคุณที่นี่
API_KEY = "WPk4yG4RfcFpmWc8GF7nK2aNwFe1w1F8"

# รายชื่อ Webcam ID ของคุณ 10 ตัว (ดึงมาจาก URL ที่คุณให้มา)
webcam_ids = [
    "1793905096", "1793905099", "1591521761", "1793905095", "1701262836",
    "1732680375", "1704280305", "1717749116", "1733323346", "1720428002"
]

# สร้าง string สำหรับเรียก API แบบเจาะจง ID
ids_str = ",".join(webcam_ids)
URL = f"https://api.windy.com/api/webcams/v3/list?ids={ids_str}&include=location,images"

headers = {"x-windy-api-key": API_KEY}

try:
    response = requests.get(URL, headers=headers)
    data = response.json()
    
    # ดึงข้อมูลจากจุดที่ถูกต้องของ Windy API v3
    webcams = data.get("webcams", [])
    
    features = []
    for cam in webcams:
        w_id = str(cam.get("id"))
        
        # จัดกลุ่มข้อมูลใหม่ตามที่คุณต้องการ
        features.append({
            "type": "Feature",
            "properties": {
                "CAMERA": cam.get("title"),
                "TYPE": "CCTV",
                "STATUS": cam.get("status").upper(),
                "COUNTRY": "Thailand",
                "IMAGEURL": f"https://images-webcams.windy.com/{w_id[-2:]}/{w_id}/current/full/{w_id}.jpg",
                "WEBURL": f"https://www.windy.com/webcams/{w_id}"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    cam["location"]["longitude"],
                    cam["location"]["latitude"]
                ]
            }
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open("cctv_realtime.geojson", "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"Update Success! Total: {len(features)} cameras.")

except Exception as e:
    print(f"Error: {e}")
