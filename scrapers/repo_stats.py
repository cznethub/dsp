import asyncio
import aiohttp

from bs4 import BeautifulSoup


async def fetch(session, res_url):
    async with session.get(res_url) as response:
        if response.status != 200:
            print(f"FAILURE {res_url}")
            return {"json-ld": None, "url": res_url, "status": response.status}
        resource_data = await response.text()
        resource_soup = BeautifulSoup(resource_data, "html.parser")
        info_table = resource_soup.find("table", {"id": "table-stats"})
        views = 0
        downloads = 0
        for row in info_table.findAll("tr"):
            if row.th.string == "Views: ":
                views = row.td.string
            if row.th.string == "Downloads: ":
                downloads = row.td.string
        print(f"SUCCESS {res_url}")
        return {"downloads": downloads, "views": views, "url": res_url, "status": response.status}

async def fetch_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

async def retrieve_stats(urls):
    # scrape json-ld
    #urls = [f"https://www.hydroshare.org/resource/{res_id}" for res_id in ids]
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
        results = await fetch_all(session, urls)
    return results

hs_urls = [
"https://www.hydroshare.org/resource/00081c3c9dd54cf4a20ab5ae46060b16/",
"https://www.hydroshare.org/resource/0dd02c98669d4b9ca99865e5fc502d72/",
"https://www.hydroshare.org/resource/13f0d898046d4e49b0e106a3c814707b/",
"https://www.hydroshare.org/resource/14d4ef1af484494ebd08ce5ea33a90d3/",
"https://www.hydroshare.org/resource/1c69a4c9140f4893a644b5187b0e16fd/",
"https://www.hydroshare.org/resource/1d33c8705d1a41ad83613559d798c0d8/",
"https://www.hydroshare.org/resource/239729a6ea464070864091e2dc58708e/",
"https://www.hydroshare.org/resource/24f5579b1d8245669eaaeb8e4c07f162/",
"https://www.hydroshare.org/resource/2fbdb2aefd264e539b3234acb6898706/",
"https://www.hydroshare.org/resource/33ab76d224a645be8b34817512c5556e/",
"https://www.hydroshare.org/resource/404d4a682c264558b69072ee877ee654/",
"https://www.hydroshare.org/resource/50c4feec97174bfa8dc84843e67225fe/",
"https://www.hydroshare.org/resource/50c55ad74a644794a798c9c051d95bc8/",
"https://www.hydroshare.org/resource/51e50f65be8f4971a684fc4d11df7533/",
"https://www.hydroshare.org/resource/5274a68688744548b2c34992fd5c39f0/",
"https://www.hydroshare.org/resource/58d9bfdb4613458c8c3434db10b3af45/",
"https://www.hydroshare.org/resource/5d3acacb8aef49b2915c5b1bd673120f/",
"https://www.hydroshare.org/resource/604c01f748554e7bbf8a97cee73ef001/",
"https://www.hydroshare.org/resource/6266637e25504372a28285ebd3a78b18/",
"https://www.hydroshare.org/resource/647b0abd93fe4d10946d2c3205d106a4/",
"https://www.hydroshare.org/resource/65714d583b614186a2b55d7cecc4e3f7/",
"https://www.hydroshare.org/resource/66e1715f46ac4c8890da092cecfa42f6/",
"https://www.hydroshare.org/resource/67591fdd72bb4114aca5b85a915eb7d9/",
"https://www.hydroshare.org/resource/6a2503c69a0d4cd28cd5bfad7cd5b079/",
"https://www.hydroshare.org/resource/8160fe8ea17d46d783b521ab231236b5/",
"https://www.hydroshare.org/resource/844209cb8da943d5bec4cfa76f68920e/",
"https://www.hydroshare.org/resource/889c5d1fa1fc4923ab3a3cea48940073/",
"https://www.hydroshare.org/resource/8fba7385a2b4459eb774cff5094f838f/",
"https://www.hydroshare.org/resource/91b403a849f0404887964283a33bcbbb/",
"https://www.hydroshare.org/resource/97bea0657fc74d86a3daeb2b6a8b5cd9/",
"https://www.hydroshare.org/resource/9b08109214f14f6c9f0b51ffd96ba3b1/",
"https://www.hydroshare.org/resource/a30d21c9b57840b1a5f5ec0b2ae75ca2/",
"https://www.hydroshare.org/resource/a67d5e40ec0043b79cbc3e1fb7034578/",
"https://www.hydroshare.org/resource/a7f73c42a7e7482fad9c88929bfbe46d/",
"https://www.hydroshare.org/resource/b0476a0b8e4c4220b2dfc3951b3df272/",
"https://www.hydroshare.org/resource/b0b3fcf2f87c4a03a6933dd99645ca9d/",
"https://www.hydroshare.org/resource/b170dbd129c54a628da8e199fd23c6a4/",
"https://www.hydroshare.org/resource/ba1e16a0317d4dd2b6bc81fd3bf76838/",
"https://www.hydroshare.org/resource/c4e6bc66235e42b6b364bab513b747ee/",
"https://www.hydroshare.org/resource/c6f91fd7407e4e038a27b487e2f8627f/",
"https://www.hydroshare.org/resource/c6f91fd7407e4e038a27b487e2f8627f/",
"https://www.hydroshare.org/resource/ca00ca2793bf40bd96a7378ec3b98e3a/",
"https://www.hydroshare.org/resource/caf9720f429543838047fbf94c17e8ff/",
"https://www.hydroshare.org/resource/cb67da2266c84204a1a1cf6ac8447fe8/",
"https://www.hydroshare.org/resource/d14f77371bb348b3b8d90bdaefe7b432/",
"https://www.hydroshare.org/resource/da31c90a816e4d08b4e6c9baf69c921d/",
"https://www.hydroshare.org/resource/dbf74d13c6e54558b2a48359f731639a/",
"https://www.hydroshare.org/resource/df47dcdb82e6442c842fcbae1526d9eb/",
"https://www.hydroshare.org/resource/e3cca9f6dca841d393d00bf4259886da/",
"https://www.hydroshare.org/resource/e61d4c7887864659abe9e5ae6c21f719/",
"https://www.hydroshare.org/resource/f69faa694ae6454894e9c631104f67ae/",
"https://www.hydroshare.org/resource/fa6facf1834f4c39bf7c893a25c67e02/"
]

loop = asyncio.get_event_loop()
stats = loop.run_until_complete(retrieve_stats(hs_urls))
for stat in stats:
    print(stat)