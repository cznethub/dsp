from bs4 import BeautifulSoup
import requests
import json
from pymongo import MongoClient
import asyncio
import aiohttp
import dateutil.parser
from geojson import Point, Feature
import re

'''
Update the USER/PASSWORD in the CONNECTION_STRING before running!
'''

def get_database():

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://<USER>:<PASSWORD>@cluster0.iouzjvv.mongodb.net/?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['czo']['cznet']

def format_fields(json_ld):
    # format datetime fields
    if "dateCreated" in json_ld:
        json_ld["dateCreated"] = dateutil.parser.isoparse(json_ld["dateCreated"])
    if "dateModified" in json_ld:
        json_ld["dateModified"] = dateutil.parser.isoparse(json_ld["dateModified"])
    if "datePublished" in json_ld["distribution"]:
        json_ld["datePublished"] = dateutil.parser.isoparse(json_ld["distribution"]["datePublished"])
        json_ld["distribution"]["datePublished"] = dateutil.parser.isoparse(json_ld["distribution"]["datePublished"])

    # format spatial coverage
    if "spatialCoverage" in json_ld:
        spatial_coverage = json_ld["spatialCoverage"]
        spatial_coverage_geo = spatial_coverage["geo"]
        spatial_coverage["geojson"] = []
        for sc in spatial_coverage_geo:
            if sc["@type"] == "GeoCoordinates":
                point = Feature(geometry=Point([float(sc["longitude"]), float(sc["latitude"])]))
                spatial_coverage["geojson"].append(point)
            if sc["@type"] == "GeoShape":
                south, west, north, east = sc["box"].split(" ")
                bbox = [float(north), float(south), float(east), float(west)]
                spatial_coverage["geojson"].append(bbox)

    # format temporal coverage
    if "temporalCoverage" in json_ld:
        start, end = json_ld["temporalCoverage"].split("/")
        start_date = dateutil.parser.parse(start)
        end_date = dateutil.parser.parse(end)
        json_ld["temporalCoverage"] = {"start": start_date, "end": end_date}

    if "keywords" in json_ld:
        if json_ld["keywords"] is None:
            json_ld["keywords"] = []
        if isinstance(json_ld["keywords"], str):
            json_ld["keywords"] = re.split(r',(?=[^/s ])', json_ld["keywords"])

    return json_ld

async def fetch(session, url):
    async with session.post(url) as response:
        if response.status != 200:
            print(f"FAILURE {url}")
            return {"json-ld": None, "url": url, "status": response.status}
        resource_data = await response.text()
        resource_soup = BeautifulSoup(resource_data, "html.parser")
        resource_json_ld = resource_soup.find("script", {"type": "application/ld+json"})
        resource_json_ld = json.loads(resource_json_ld.text)
        resource_json_ld = format_fields(resource_json_ld)
        print(f"SUCCESS {url}")
        return {"json-ld": resource_json_ld, "url": url, "status": response.status}

async def fetch_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

# got this list from https://docs.google.com/document/d/1wTw36zity-YCIO8F9tdl5EZUReJ2UEfjI5w4_ot4RaM/edit?pli=1
earthchem_urls = [
     "https://ecl.earthchem.org/view.php?id=512",
     "https://ecl.earthchem.org/view.php?id=514",
     "https://ecl.earthchem.org/view.php?id=515",
     "https://ecl.earthchem.org/view.php?id=516",
     "https://ecl.earthchem.org/view.php?id=517",
     "https://ecl.earthchem.org/view.php?id=519",
     "https://ecl.earthchem.org/view.php?id=520",
     "https://ecl.earthchem.org/view.php?id=521",
     "https://ecl.earthchem.org/view.php?id=522",
     "https://ecl.earthchem.org/view.php?id=523",
     "https://ecl.earthchem.org/view.php?id=635",
     "https://ecl.earthchem.org/view.php?id=771",
     "https://ecl.earthchem.org/view.php?id=772",
     "https://ecl.earthchem.org/view.php?id=836",
     "https://ecl.earthchem.org/view.php?id=837",
     "https://ecl.earthchem.org/view.php?id=969",
     "https://ecl.earthchem.org/view.php?id=1007",
     "https://ecl.earthchem.org/view.php?id=1008",
     "https://ecl.earthchem.org/view.php?id=1041",
     "https://ecl.earthchem.org/view.php?id=1042",
     "https://ecl.earthchem.org/view.php?id=1063",
     "https://ecl.earthchem.org/view.php?id=1134",
     "https://ecl.earthchem.org/view.php?id=1143",
     "https://ecl.earthchem.org/view.php?id=1144",
     "https://ecl.earthchem.org/view.php?id=1145",
     "https://ecl.earthchem.org/view.php?id=1155",
     "https://ecl.earthchem.org/view.php?id=1156",
     "https://ecl.earthchem.org/view.php?id=1313",
     "https://ecl.earthchem.org/view.php?id=1934",
     "https://ecl.earthchem.org/view.php?id=1935"
]

async def retrieve_jsonld(urls):
    # scrape json-ld
    async with aiohttp.ClientSession() as session:
        results = await fetch_all(session, urls)
    return [result["json-ld"] for result in results if result["json-ld"]]

loop = asyncio.get_event_loop()
json_lds = loop.run_until_complete(retrieve_jsonld(earthchem_urls))
print("saving to the db")
# save to db
collection = get_database()
collection.insert_many(json_lds)
