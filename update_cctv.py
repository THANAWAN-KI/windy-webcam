import json

webcams = [
    "1793905096",
    "1793905099",
    "1591521761",
    "1793905095",
    "1701262836",
    "1732680375",
    "1704280305",
    "1717749116",
    "1733323346",
    "1720428002"
]

features = []

lat = 13.0
lon = 100.0

for webcam_id in webcams:

    image_url = f"https://images-webcams.windy.com/{webcam_id[-2:]}/{webcam_id}/current/full/{webcam_id}.jpg"

    web_url = f"https://www.windy.com/webcams/{webcam_id}"

    features.append({
        "type": "Feature",
        "properties": {
            "CAMERA": f"Windy Webcam {webcam_id}",
            "STATUS": "ONLINE",
            "TYPE": "Windy CCTV",
            "COUNTRY": "Thailand",
            "IMAGEURL": image_url,
            "WEBURL": web_url
        },
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat]
        }
    })

    lat += 0.3
    lon += 0.3

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open("cctv_realtime.geojson", "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print("GeoJSON updated successfully")
