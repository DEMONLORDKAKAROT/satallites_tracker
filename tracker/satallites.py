import requests
import urllib
import datetime
import json
from pathlib import Path
from sgp4.api import Satrec, jday
import math
from scipy.spatial import cKDTree
import numpy as np
from concurrent.futures import ThreadPoolExecutor

ORIGINAL_DATA = "data.txt"
tle_data = None

URL = "https://tle.ivanstanojevic.me/api/tle/?page-size=100&page="

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def write_to_txt(data, name):
    
    with open(name, "w") as f:
       for satellite in data:
           f.write(json.dumps(satellite))
           f.write("\n")

def get_data_from_txt(name):
    
    with open(name, "r") as f:
        return [json.loads(line) for line in f if line.strip()]
    
def get_sat_data()-> list[dict]:

    page = 1
    url = (URL + str(page))
    results = []
    while(True):

        response = requests.get(url, headers=headers, timeout=40)
        data = response.json()

        results.extend(data["member"])

        if "next" not in data["view"]:
            break

        url = data["view"]["next"]


    return results

def get_kd_tree(data):

    coords = np.array([[s['lat'], s['lng']] for s in data])
    return cKDTree(coords)

def tree_search(tree,data,lat,lng):

    _ ,index = tree.query([lat, lng])
    return data[index]

def get_position(satalite_data):



    line_1 = satalite_data.get("line1")
    line_2 = satalite_data.get("line2")

    satellite = Satrec.twoline2rv(line_1, line_2)

    current_date = datetime.datetime.now(datetime.timezone.utc)
    y = int(current_date.year)
    m = int(current_date.month)
    d = int(current_date.day)
    h = int(current_date.hour)
    minute = int(current_date.minute)
    s = int(current_date.second)

    jd, fr = jday(y, m, d, h, minute, s)

    gmst_deg = (280.46061837 + 360.98564736629 * (jd + fr)) % 360
    gmst_rad = math.radians(gmst_deg)


    error, position, velocity = satellite.sgp4(jd, fr)

    x, y, z = position

    x_ecef =  x * math.cos(gmst_rad) + y * math.sin(gmst_rad)
    y_ecef = -x * math.sin(gmst_rad) + y * math.cos(gmst_rad)
    z_ecef = z

    r = math.sqrt(x_ecef**2 + y_ecef**2 + z_ecef**2)
    lat = math.degrees(math.asin(z_ecef / r))
    lng = math.degrees(math.atan2(y_ecef, x_ecef))
    alt = r - 6371.0

    position = lat, lng, alt

    return error, position, velocity

def get_tle_data():
    global tle_data
    
    if tle_data is None:
        if Path(ORIGINAL_DATA).is_file():
            tle_data = get_data_from_txt(ORIGINAL_DATA)
        else:
            # fetch from API and save
            tle_data = get_sat_data()
            write_to_txt(tle_data, ORIGINAL_DATA)

    return tle_data

def filter_satellite(data, category):

    if category == "all":
        return data
    
    return [s for s in data if category.lower() in s["name"].lower()]

def get_all_positions(category):

    data = get_tle_data()

    filtered_data = filter_satellite(data, category)



    with ThreadPoolExecutor() as satellite:
       results = list(satellite.map(get_position, filtered_data))

    satellite_info = []

    for satellite, (error, position, velocity) in zip(filtered_data, results) :

        if error != 0:
            continue

        satellite_info.append({
            "name": satellite["name"],
            "lat": round(position[0], 3),
            "lng": round(position[1], 3),
            "alt": round(position[2], 3),
        })

    return satellite_info

