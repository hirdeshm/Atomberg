import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
import pandas as pd

# Load environment variables
load_dotenv()
api_key = os.getenv("SERPAPI_KEY")

# Search query
QUERY = "smart fan"


# Store results
results = []
N = 20  # number of results to fetch

params = {
    "engine": "google",
    "q": QUERY,
    "api_key": api_key,
    "num": 10,                 # only 10 per request
    "gl": "in",                # India
    "hl": "en",
    "google_domain": "google.co.in"
}

start = 0


# Pagination loop
while len(results) < N:
    params["start"] = start
    search = GoogleSearch(params)
    data = search.get_dict()
    organic = data.get("organic_results", [])

    for item in organic:
        position = item.get("position", None)
        page_number = (start // 10) + 1    # page 1,2,3...

        title = item.get("title", "")
        snippet = item.get("snippet", "")
        link = item.get("link", "")

        

        
        

        results.append({
            "position": position,
            "page": page_number,
            "title": title,
            "snippet": snippet,
            "link": link,
           
        })

        if len(results) >= N:
            break

    start += 10


# Create DataFrame and save CSV
df = pd.DataFrame(results)
df.to_csv("google_brand_detection.csv", index=False)

print("CSV saved as google_brand_detection.csv\n")


