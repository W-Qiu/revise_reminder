import requests

def search_img(search_term):
    subscription_key = "b24c9068484e44ecb077d919631d5255"

    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
    headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
    params  = {"q": search_term, "license": "public", "imageType": "photo"}

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    try:
        thumbnail_urls = search_results["value"][0]["thumbnailUrl"]
    except IndexError:
        return ""
    # thumbnail_urls = [img["thumbnailUrl"] for img in search_results["value"][:num_images]]

    return thumbnail_urls