# furniture/search.py
from googleapiclient.discovery import build
from django.conf import settings
import requests
import json
from requests.exceptions import RequestException

def google_image_search(query, api_key, cse_id):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(
        q=query,
        cx=cse_id,
        searchType='image',
        fileType='jpg',
        num=10,
        safe='off'
    ).execute()
    return res.get('items', [])

def search_furniture_by_text(formatted_query: dict):
    url = "https://google.serper.dev/shopping"
    try:
        payload = json.dumps({
            "q": f"{formatted_query['type']} {formatted_query['style']}",
            "gl": "tw",
            "hl": "zh-tw"
        })
        headers = {
            'X-API-KEY': '9c17e786d093a6407a0c9a88defeca7f049a633f',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()

        print(f"data {data}")
        if not data.get("shopping"):
            return []
            
        return data["shopping"]
        
    except RequestException as e:
        # Log the error
        raise RuntimeError(f"Search API request failed: {str(e)}")
