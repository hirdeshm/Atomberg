import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
import pandas as pd
import matplotlib.pyplot as plt
from urllib.parse import urlparse

# -------------------------
# Load API Key from .env file
# -------------------------
load_dotenv()
api_key = os.getenv("SERPAPI_KEY")

# -------------------------
# Ask user for search query from terminal
# -------------------------
QUERY = input("\nEnter your search query (example: 'smart fan'): ").strip()

# -------------------------
# Configurations
# -------------------------
results = []
MAX_RESULTS = 20  # total number of search results needed

params = {
    "engine": "google",
    "q": QUERY,
    "api_key": api_key,
    "num": 10,                 # Google max = 10 per request
    "gl": "in",                # Country (India)
    "hl": "en",                # Language
    "google_domain": "google.co.in"
}

start = 0  # pagination counter

# -------------------------
# Fetch paginated results from Google using SerpAPI
# -------------------------
print("\nFetching search results...")

while len(results) < MAX_RESULTS:
    params["start"] = start
    search = GoogleSearch(params)
    data = search.get_dict()
    organic_results = data.get("organic_results", [])

    # Loop through each result and store relevant details
    for item in organic_results:
        results.append({
            "position": item.get("position"),
            "page": (start // 10) + 1,
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
            "link": item.get("link", "")
        })

        if len(results) >= MAX_RESULTS:
            break

    start += 10  # move to next page

# -------------------------
# Convert to DataFrame and Save to CSV
# -------------------------
df = pd.DataFrame(results)
df.to_csv("google_brand_detection.csv", index=False)
print("\n📁 CSV saved as: google_brand_detection.csv")

# -------------------------
# Brand Variations Dictionary (helps detect brand in title/snippet/domain)
# -------------------------
brand_variants = {
    "Atomberg": ["atomberg", "atom berg", "atom-berg"],
    "Orient": ["orient", "orient electric"],
    "Crompton": ["crompton"],
    "Havells": ["havells"],
    "Bajaj": ["bajaj", "bajaj electricals"],
    "V-Guard": ["v-guard", "vguard"],
    "Mi": ["xiaomi", "mi.com", "mi"],
    "Okos": ["okos"],
    "EGLO": ["eglo"]
}

# -------------------------
# Detect brand using text + website domain
# -------------------------
def detect_brand(row):
    # Combine title and snippet for brand matching
    text = f"{row['title']} {row['snippet']}".lower()
    domain = urlparse(row['link']).netloc.lower()

    for brand, variations in brand_variants.items():
        for term in variations:
            if term in text or term in domain:
                return brand
    return None

df["brand"] = df.apply(detect_brand, axis=1)

# -------------------------
# Assign Position-Based Visibility Score
# -------------------------
position_score = {
    1: 100, 2: 90, 3: 80, 4: 70, 5: 60,
    6: 50, 7: 40, 8: 30, 9: 20, 10: 10
}

def get_position_score(position):
    # If result is beyond top 10, give small constant value
    return position_score.get(position, 5)

df["score"] = df["position"].apply(get_position_score)

# -------------------------
# Calculate Final Brand Visibility Score
# -------------------------
brand_scores = (
    df.dropna(subset=["brand"])
      .groupby("brand")["score"]
      .sum()
      .sort_values(ascending=False)
)

print("\n=== 🏆 Final Brand Visibility Score ===\n")
print(brand_scores)

# -------------------------
# Plot Visibility Score
# -------------------------
plt.style.use("ggplot")
plt.figure(figsize=(12, 6))
bars = plt.bar(brand_scores.index, brand_scores.values)

# Add score on top of bars
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 2, str(height),
             ha='center', fontsize=12, fontweight='bold')

plt.title(f"Brand Visibility Score for: \"{QUERY}\"", fontsize=16, fontweight='bold')
plt.xlabel("Brand", fontsize=13)
plt.ylabel("Score", fontsize=13)
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()
