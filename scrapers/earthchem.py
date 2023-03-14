import html

from bs4 import BeautifulSoup
from discovery import JSONLD
import json
from pymongo import MongoClient
import asyncio
import aiohttp
import dateutil.parser
from geojson import Point, Feature, Polygon
import re
import os

'''
Update the USER/PASSWORD in the CONNECTION_STRING before running!
'''

def get_database():

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = f"{os.environ['MONGO_PROTOCOL']}://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@{os.environ['MONGO_HOST']}/?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING, tls=True, tlsAllowInvalidCertificates=True)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client[os.environ['MONGO_DATABASE']][os.environ['MONGO_COLLECTION']]

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
                bbox = Feature(geometry=Polygon([float(north), float(south), float(east), float(west)]))
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

    json_ld["legacy"] = True
    return json_ld

async def fetch(session, url):
    async with session.post(url) as response:
        if response.status != 200:
            print(f"FAILURE {url}")
            return {"json-ld": None, "url": url, "status": response.status}
        resource_data = await response.text()
        resource_soup = BeautifulSoup(resource_data, "html.parser")
        resource_json_ld = resource_soup.find("script", {"type": "application/ld+json"})
        try:
            resource_json_ld = json.loads(html.unescape(resource_json_ld.text))
        except Exception as e:
            print(f"Failed {url}")
            return {"json-ld": None, "url": url, "status": response.status}
        resource_json_ld = format_fields(resource_json_ld)
        resource_json_ld["repository_identifier"] = resource_json_ld["sameAs"].split("id=")[1]
        resource_json_ld["@context"] = resource_json_ld["@context"]["@vocab"]
        resource_json_ld["license"] = {"text": resource_json_ld["license"]}
        print(f"validating {url}")
        jsonld = JSONLD(**resource_json_ld)
        print(f"SUCCESS {url}")
        return {"json-ld": jsonld.dict(by_alias=True, exclude_none=True), "url": url, "status": response.status}

async def fetch_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

# got this list from https://docs.google.com/document/d/1wTw36zity-YCIO8F9tdl5EZUReJ2UEfjI5w4_ot4RaM/edit?pli=1
earthchem_urls = [
    'https://doi.org/10.26022/IEDA/112066',
    'https://doi.org/10.1594/IEDA/111293',
    'https://doi.org/10.26022/IEDA/111934',
    'https://doi.org/10.26022/IEDA/111935',
    'https://doi.org/10.26022/IEDA/111733',
    'https://doi.org/10.26022/IEDA/111665',
    'https://doi.org/10.26022/IEDA/111664',
    'https://doi.org/10.26022/IEDA/111593',
    'https://doi.org/10.26022/IEDA/111594',
    'https://doi.org/10.26022/IEDA/111595',
    'https://doi.org/10.26022/IEDA/111596',
    'https://doi.org/10.1594/IEDA/111281',
    'https://doi.org/10.26022/IEDA/111537',
    'https://doi.org/10.1594/IEDA/111433',
    'https://doi.org/10.1594/IEDA/100714',
    'https://doi.org/10.1594/IEDA/100715',
    'https://doi.org/10.1594/IEDA/100716',
    'https://doi.org/10.1594/IEDA/100717',
    'https://doi.org/10.1594/IEDA/111312',
    'https://doi.org/10.1594/IEDA/111313',
    'https://doi.org/10.1594/IEDA/100612',
    'https://doi.org/10.1594/IEDA/100611',
    'https://doi.org/10.1594/IEDA/100742',
    'https://doi.org/10.1594/IEDA/111156',
    'https://doi.org/10.1594/IEDA/111155',
    'https://doi.org/10.1594/IEDA/111143',
    'https://doi.org/10.1594/IEDA/111144',
    'https://doi.org/10.1594/IEDA/111145',
    'https://doi.org/10.1594/IEDA/100681',
    'https://doi.org/10.1594/IEDA/100689',
    'https://doi.org/10.1594/IEDA/100690',
    'https://doi.org/10.1594/IEDA/100666',
    'https://doi.org/10.1594/IEDA/100667',
    'https://doi.org/10.1594/IEDA/100638',
    'https://doi.org/10.1594/IEDA/100517',
    'https://doi.org/10.1594/IEDA/100516',
    'https://doi.org/10.1594/IEDA/100459',
    'https://doi.org/10.1594/IEDA/100460',
    'https://doi.org/10.1594/IEDA/100461',
    'https://doi.org/10.1594/IEDA/100462',
    'https://doi.org/10.1594/IEDA/100463',
    'https://doi.org/10.1594/IEDA/100464',
    'https://doi.org/10.1594/IEDA/100465',
    'https://doi.org/10.1594/IEDA/100466',
    'https://doi.org/10.1594/IEDA/100467',
    'https://doi.org/10.1594/IEDA/100468',
    'https://doi.org/10.1594/IEDA/100469',
    'https://doi.org/10.1594/IEDA/100471',
    'https://doi.org/10.1594/IEDA/100473',
    'https://doi.org/10.1594/IEDA/100474',
    'https://doi.org/10.1594/IEDA/100475',
    'https://doi.org/10.1594/IEDA/100476',
    'https://doi.org/10.1594/IEDA/100477',
    'https://doi.org/10.1594/IEDA/100458',
    'https://doi.org/10.1594/IEDA/100268',
    'https://doi.org/10.1594/IEDA/100233',
    'https://doi.org/10.1594/IEDA/100234',
    'https://doi.org/10.1594/IEDA/100235',
    'https://doi.org/10.1594/IEDA/100236',
    'https://doi.org/10.1594/IEDA/100237',
    'https://doi.org/10.1594/IEDA/100239',
    'https://doi.org/10.1594/IEDA/100240',
    'https://doi.org/10.1594/IEDA/100241',
    'https://doi.org/10.1594/IEDA/100242',
    'https://doi.org/10.1594/IEDA/100243'
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
collection.delete_many({"provider.name": "EarthChem Library", "legacy": True})
collection.insert_many(json_lds)
