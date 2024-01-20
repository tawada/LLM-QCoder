import requests


async def download_page(url: str):
    return requests.get(url)
