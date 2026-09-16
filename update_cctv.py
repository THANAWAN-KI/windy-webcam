import json
import math
import os
from datetime import datetime, timezone

import requests


API_URL = "https://api.windy.com/webcams/api/v3/webcams"
ESTATES_URL = (
    "https://raw.githubusercontent.com/THANAWAN-KI/"
    "ieat-emonitoring-line-alert/main/docs/data/thaiwater_latest.json"
)
OUTPUT_FILE = "cctv_windy_updated.geojson"
RADIUS_KM = float(os.getenv("CCTV_RADIUS_KM", "30"))
PAGE_SIZE = 50


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    value = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    )
    return 2 * radius * math.asin(math.sqrt(value))


def load_estates(session):
    response = session.get(ESTATES_URL, timeout=30)
    response.raise_for_status()
    estates = []
    for item in response.json().get("estates", []):
        try:
            estates.append(
                {
                    "name": str(item["name"]),
                    "lat": float(item["lat"]),
                    "lon": float(item["lon"]),
                }
            )
        except (KeyError, TypeError, ValueError):
            continue
    if not estates:
        raise RuntimeError("ไม่พบพิกัดนิคมอุตสาหกรรมจากแหล่งข้อมูล")
    return estates


def fetch_thailand_webcams(session, api_key):
    headers = {"x-windy-api-key": api_key}
    offset = 0
    webcams = []

    while True:
        response = session.get(
            API_URL,
            headers=headers,
            params={
                "countries": "TH",
                "include": "location,images,player,urls",
                "lang": "th",
                "limit": PAGE_SIZE,
                "offset": offset,
            },
            timeout=45,
        )
        response.raise_for_status()
        payload = response.json()
        page = payload.get("webcams", [])
        webcams.extend(page)

        total = int(payload.get("total", len(webcams)))
        offset += len(page)
        if not page or offset >= total:
            break
        if offset > 1000:
            print("WARNING: แพ็กเกจ Windy ฟรีอ่านรายการได้ถึง offset 1000")
            break

    return webcams


def first_value(mapping, names):
    if not isinstance(mapping, dict):
        return ""
    for name in names:
        value = mapping.get(name)
        if value:
            return value
    return ""


def webcam_to_feature(webcam, estates):
    location = webcam.get("location") or {}
    try:
        lat = float(location["latitude"])
        lon = float(location["longitude"])
    except (KeyError, TypeError, ValueError):
        return None

    nearest = min(
        estates,
        key=lambda estate: haversine_km(lat, lon, estate["lat"], estate["lon"]),
    )
    distance = haversine_km(lat, lon, nearest["lat"], nearest["lon"])
    if distance > RADIUS_KM:
        return None

    webcam_id = str(webcam.get("webcamId") or webcam.get("id") or "")
    current_images = (webcam.get("images") or {}).get("current") or {}
    image_url = first_value(
        current_images,
        ("preview", "thumbnail", "small", "icon", "medium", "full"),
    )
    urls = webcam.get("urls") or {}
    player = webcam.get("player") or {}
    windy_url = first_value(urls, ("detail", "webcam"))
    if not windy_url and webcam_id:
        windy_url = f"https://www.windy.com/webcams/{webcam_id}"

    raw_status = str(webcam.get("status") or "inactive").lower()
    return {
        "type": "Feature",
        "properties": {
            "CAMERA": webcam.get("title") or "Windy Webcam",
            "WEBCAM_ID": webcam_id,
            "TYPE": "CCTV",
            "PROVINCE": location.get("region") or location.get("city") or "",
            "COUNTRY": location.get("country") or "Thailand",
            "IMAGEURL": image_url,
            "WEBURL": windy_url,
            "PLAYERURL": first_value(player, ("day", "live", "month")),
            "STATUS": "ONLINE" if raw_status == "active" else "OFFLINE",
            "NEAREST_ESTATE": nearest["name"],
            "DISTANCE_KM": round(distance, 2),
            "LAST_UPDATED": webcam.get("lastUpdatedOn") or "",
        },
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
    }


def main():
    api_key = os.getenv("WINDY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ไม่พบ GitHub Secret: WINDY_API_KEY")

    session = requests.Session()
    session.headers.update({"User-Agent": "IEAT-CCTV-Updater/1.0"})
    estates = load_estates(session)
    webcams = fetch_thailand_webcams(session, api_key)

    by_id = {}
    for webcam in webcams:
        feature = webcam_to_feature(webcam, estates)
        if not feature:
            continue
        key = feature["properties"]["WEBCAM_ID"]
        if key:
            by_id[key] = feature

    features = sorted(
        by_id.values(),
        key=lambda feature: (
            feature["properties"]["NEAREST_ESTATE"],
            feature["properties"]["DISTANCE_KM"],
            feature["properties"]["CAMERA"],
        ),
    )
    geojson = {
        "type": "FeatureCollection",
        "metadata": {
            "source": "Windy Webcams API",
            "country": "TH",
            "radius_km": RADIUS_KM,
            "estate_count": len(estates),
            "camera_count": len(features),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "features": features,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(geojson, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(
        f"SUCCESS: กล้องประเทศไทย {len(webcams)} จุด; "
        f"อยู่ภายใน {RADIUS_KM:g} กม. จากนิคมฯ {len(features)} จุด"
    )


if __name__ == "__main__":
    main()
