import requests
import json

API_KEY = "WPk4yG4RfcFpmWc8GF7nK2aNwFe1w1F8"

URL = "https://api.windy.com/api/webcams/v3/list?box=5,97,20,106"

headers = {
    "x-windy-api-key": API_KEY
}

response = requests.get(URL, headers=headers)
data = response.json()

features = []

for cam in data["result"]["webcams"]:

    webcam_id = str(cam["id"])

    image_url = f"https://images-webcams.windy.com/{webcam_id[-2:]}/{webcam_id}/current/full/{webcam_id}.jpg"

    features.append({
        "type": "Feature",
        "properties": {
            "CAMERA": cam.get("title"),
            "STATUS": cam.get("status"),
            "TYPE": "Windy CCTV",
            "PROVINCE": "",
            "COUNTRY": "Thailand",
            "IMAGEURL": image_url,
            "WEBURL": f"https://www.windy.com/webcams/{webcam_id}"
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

print("GeoJSON updated")
