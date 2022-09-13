from bs4 import BeautifulSoup
import requests
import json
from pymongo import MongoClient
import asyncio
import aiohttp

'''
Update the USER/PASSWORD in the CONNECTION_STRING before running!
'''

def get_database():

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://<USER>:<PASSWORD>@cluster0.iouzjvv.mongodb.net/?retryWrites=true&w=majority"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['czo']['schemaorg']

async def fetch(session, url):
    async with session.post(url) as response:
        if response.status != 200:
            print(f"FAILURE {url}")
            return {"json-ld": None, "url": url, "status": response.status}
        resource_data = await response.text()
        resource_soup = BeautifulSoup(resource_data, "html.parser")
        resource_json_ld = resource_soup.find("script", {"id": "schemaorg"})
        resource_json_ld = json.loads(resource_json_ld.text)
        print(f"SUCCESS {url}")
        return {"json-ld": resource_json_ld, "url": url, "status": response.status}

async def fetch_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

# Community 1 is CZO
url = "https://www.hydroshare.org/community/1/"

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

async def retrieve_jsonld(ids):
    # scrape json-ld
    urls = [f"https://www.hydroshare.org/resource/{res_id}" for res_id in ids]
    async with aiohttp.ClientSession() as session:
        results = await fetch_all(session, urls)
    return [result["json-ld"] for result in results if result["json-ld"]]

loop = asyncio.get_event_loop()
json_lds = loop.run_until_complete(retrieve_jsonld(resource_ids))
print("saving to the db")
# save to db
collection = get_database()
collection.insert_many(json_lds)

