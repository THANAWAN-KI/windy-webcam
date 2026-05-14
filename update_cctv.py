import requests
import json

API_KEY = "WPk4yG4RfcFpmWc8GF7nK2aNwFe1w1F8"

URL = "https://api.windy.com/api/webcams/v3/list?box=5,97,20,106&limit=100"

headers = {
    "x-windy-api-key": API_KEY
}

response = requests.get(URL, headers=headers)

print(response.text)

data = response.json()

features = []

# รองรับหลาย response
if "webcams" in data:
    webcams = data["webcams"]

elif "result" in data and "webcams" in data["result"]:
    webcams = data["result"]["webcams"]

else:
    webcams = []

for cam in webcams:

    webcam_id = str(cam.get("id", ""))

    if webcam_id == "":
        continue

    title = cam.get("title", "Unknown")

    status = str(cam.get("status", "ONLINE"))

    latitude = cam["location"]["latitude"]
    longitude = cam["location"]["longitude"]

    image_url = f"https://images-webcams.windy.com/{webcam_id[-2:]}/{webcam_id}/current/full/{webcam_id}.jpg"

    web_url = f"https://www.windy.com/webcams/{webcam_id}"

    features.append({
        "type": "Feature",
        "properties": {
            "CAMERA": title,
            "STATUS": status,
            "TYPE": "Windy CCTV",
            "COUNTRY": "Thailand",
            "IMAGEURL": image_url,
            "WEBURL": web_url
        },
        "geometry": {
            "type": "Point",
            "coordinates": [
                longitude,
                latitude
            ]
        }
    })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open("cctv_realtime.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print("GeoJSON updated successfully")
print("TOTAL FEATURES:", len(features))
