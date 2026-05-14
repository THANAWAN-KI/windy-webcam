import requests
import json

# ใส่ API KEY ของคุณที่นี่
API_KEY = "WPk4yG4RfcFpmWc8GF7nK2aNwFe1w1F8"

# รายชื่อ Webcam ID ของคุณ 10 ตัว
webcam_ids = [
    "1793905096", "1793905099", "1591521761", "1793905095", "1701262836",
    "1732680375", "1704280305", "1717749116", "1733323346", "1720428002"
]

ids_str = ",".join(webcam_ids)
# ใช้ API v3 แบบเจาะจง IDs
URL = f"https://api.windy.com/api/webcams/v3/list?ids={ids_str}&include=location"

headers = {"x-windy-api-key": API_KEY}

try:
    response = requests.get(URL, headers=headers)
    data = response.json()
    
    # ตรวจสอบโครงสร้างข้อมูลที่ Windy ส่งกลับมา (รองรับทั้งแบบมี result และไม่มี)
    webcams = []
    if isinstance(data, list):
        webcams = data
    elif "webcams" in data:
        webcams = data["webcams"]
    elif "result" in data and "webcams" in data["result"]:
        webcams = data["result"]["webcams"]

    features = []
    for cam in webcams:
        w_id = str(cam.get("id"))
        if not w_id: continue
        
        # ดึงพิกัด
        lat = cam.get("location", {}).get("latitude", 0)
        lon = cam.get("location", {}).get("longitude", 0)
        
        features.append({
            "type": "Feature",
            "properties": {
                "CAMERA": cam.get("title", "Unknown"),
                "TYPE": "CCTV",
                "STATUS": cam.get("status", "online").upper(),
                "COUNTRY": "Thailand",
                "IMAGEURL": f"https://images-webcams.windy.com/{w_id[-2:]}/{w_id}/current/full/{w_id}.jpg",
                "WEBURL": f"https://www.windy.com/webcams/{w_id}"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open("cctv_realtime.geojson", "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"DONE! Found {len(features)} cameras.")

except Exception as e:
    print(f"Error: {e}")
