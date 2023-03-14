from bs4 import BeautifulSoup
import requests
import json

from pymongo import MongoClient
import asyncio
import aiohttp
import dateutil.parser
from geojson import Point, Feature, Polygon
import os
import html

from discovery import JSONLD

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
    if "datePublished" in json_ld:
        json_ld["datePublished"] = dateutil.parser.isoparse(json_ld["datePublished"])

    # format spatial coverage
    if "spatialCoverage" in json_ld:
        spatial_coverage = json_ld["spatialCoverage"]
        spatial_coverage_geo = spatial_coverage["geo"]
        if spatial_coverage_geo["@type"] == "GeoCoordinates":
            point = Feature(geometry=Point([float(spatial_coverage_geo["longitude"]), float(spatial_coverage_geo["latitude"])]))
            spatial_coverage["geojson"] = [point]
        if spatial_coverage_geo["@type"] == "GeoShape":
            south, west, north, east = spatial_coverage_geo["box"].split(" ")
            bbox = Feature(geometry=Polygon([float(north), float(south), float(east), float(west)]))
            spatial_coverage["geojson"] = [bbox]

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
            json_ld["keywords"] = json_ld["keywords"].split(",")

    json_ld["legacy"] = True

    return json_ld


async def fetch(session, res_id, clusters):
    res_url = f"https://www.hydroshare.org/resource/{res_id}"
    async with session.get(res_url) as response:
        if response.status != 200:
            print(f"FAILURE {url}")
            return {"json-ld": None, "url": res_url, "status": response.status}
        resource_data = await response.text()
        resource_soup = BeautifulSoup(resource_data, "html.parser")
        resource_json_ld = resource_soup.find("script", {"id": "schemaorg"})
        resource_json_ld = json.loads(html.unescape(resource_json_ld.text))
        resource_json_ld = format_fields(resource_json_ld)
        resource_json_ld["clusters"] = clusters
        resource_json_ld["repository_identifier"] = res_id
        model = JSONLD(**resource_json_ld)
        print(f"SUCCESS {res_url}")
        return {"json-ld": model.dict(by_alias=True, exclude_none=True), "url": res_url, "status": response.status}

async def fetch_all(session, ids, clusters):
    tasks = []
    for res_id in ids:
        task = asyncio.create_task(fetch(session, res_id, clusters[res_id]))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

# Community 1 is CZO
url = "https://www.hydroshare.org/community/1/"
group_base_url = "https://www.hydroshare.org/user/"
groups = [("5405", "CZO Boulder"),
          ("5413", "CZO Calhoun"),
          ("5372", "CZO Sierra"),
          ("5407", "CZO Catalina-Jemez"),
          ("5410", "CZO Christina"),
          ("5406", "CZO Eel"),
          ("5706", "CZO IML"),
          ("5409", "CZO Luquillo"),
          ("5404", "CZO National"),
          ("5408", "CZO Reynolds"),
          ("5412", "CZO Shale-Hills"),
          ]

from collections import defaultdict
clusters_by_resource_id = defaultdict(list)
for group in groups:
    response = requests.get(group_base_url + group[0])
    group_data = response.text
    soup = BeautifulSoup(group_data, "html.parser")
    contributions = soup.findAll("div", {"class": "contribution"})
    for contribution in contributions:
        resource_id = contribution.find("a")["href"][len("/resource/"):-1]
        clusters_by_resource_id[resource_id].append(group[1])

response = requests.get(url)
community_data = response.text

soup = BeautifulSoup(community_data, "html.parser")
table = soup.find('table', id="item-selectors")
rows = table.findAll('tr')


# scrape all resource ids
resource_ids = []
for row in rows:
    for a in row.findAll("a", href=True):
        href = a['href']
        if "/resource/" in href:
            resource_id = href[len("/resource/"):-1]
            resource_ids.append(resource_id)

print(f"scraped {len(resource_ids)} resource ids")

async def retrieve_jsonld(ids, clusters):
    # scrape json-ld
    #urls = [f"https://www.hydroshare.org/resource/{res_id}" for res_id in ids]
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        results = await fetch_all(session, ids, clusters)
    return [result["json-ld"] for result in results if result["json-ld"]]

loop = asyncio.get_event_loop()
json_lds = loop.run_until_complete(retrieve_jsonld(resource_ids, clusters_by_resource_id))
print("saving to the db")
# save to db
collection = get_database()
collection.delete_many({"provider.name": "HydroShare", "legacy": True})
collection.insert_many(json_lds)
