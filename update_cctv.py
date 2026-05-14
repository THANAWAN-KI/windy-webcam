import requests
import json

# API KEY ของคุณ
API_KEY = "WPk4yG4RfcFpmWc8GF7nK2aNwFe1w1F8"

# รายชื่อ Webcam ID 10 ตัว
ids = "1793905096,1793905099,1591521761,1793905095,1701262836,1732680375,1704280305,1717749116,1733323346,1720428002"

# ปรับ URL เป็นรูปแบบ v3 ที่ถูกต้องที่สุดคือ /v3/list (ไม่ต้องมี /webcams/ ตรงกลาง)
URL = f"https://api.windy.com/api/webcams/v3/list?ids={ids}&include=location"

headers = {"x-windy-api-key": API_KEY}

try:
    print("Connecting to Windy API v3...")
    response = requests.get(URL, headers=headers)
    
    if response.status_code != 200:
        print(f"API Error! Status: {response.status_code}")
        print(f"Response Text: {response.text}")
    else:
        data = response.json()
        
        # Windy v3 มักจะส่งข้อมูลมาในคีย์ 'webcams' โดยตรงเลย
        webcams = data.get('webcams', [])

        features = []
        for cam in webcams:
            w_id = str(cam.get("id"))
            # พิกัดมักอยู่ใน cam['location']
            loc = cam.get("location", {})
            
            features.append({
                "type": "Feature",
                "properties": {
                    "CAMERA": cam.get("title", "Unknown"),
                    "STATUS": cam.get("status", "online").upper(),
                    "IMAGEURL": f"https://images-webcams.windy.com/{w_id[-2:]}/{w_id}/current/full/{w_id}.jpg",
                    "WEBURL": f"https://www.windy.com/webcams/{w_id}"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        loc.get("longitude", 0),
                        loc.get("latitude", 0)
                    ]
                }
            })

        geojson = {
            "type": "FeatureCollection",
            "features": features
        }

        with open("cctv_realtime.geojson", "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)

        print(f"SUCCESS! Found {len(features)} cameras and updated GeoJSON.")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
