from googleapiclient.discovery import build
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

# -------------------------
# Load API key from .env file
# -------------------------
load_dotenv()
API_KEY = os.getenv("YTAPI_KEY") # Stored securely instead of hardcoding

YOUTUBE = build("youtube", "v3", developerKey=API_KEY)

# -------------------------
# Get product keyword from user
# Example: "Smart Fan", "BLDC Fan", "Ceiling Fan"
# -------------------------
user_input = input("\nEnter product keyword (e.g., smart fan, BLDC fan): ").strip()

# -------------------------
# Brand list (Base names only)
# The final search query will be: Brand + user_input
# -------------------------
base_brands = ["Atomberg", "Crompton", "Bajaj", "Orient"]

# Generate final list dynamically
BRANDS = [f"{brand} {user_input}" for brand in base_brands]

MAX_RESULTS = 15  # Number of YouTube videos per brand to analyze

print("\n🔧 Running YouTube analysis for:", BRANDS)


# -------------------------
# Function: Search YouTube videos for a query keyword
# -------------------------
def search_videos(query, max_results=15):
    """Search videos for a given query and return video IDs."""
    
    search = YOUTUBE.search().list(
        q=query,
        part="id,snippet",
        type="video",
        maxResults=max_results
    ).execute()

    video_ids = [item["id"]["videoId"] for item in search.get("items", []) if "videoId" in item["id"]]

    return video_ids


# -------------------------
# Function: Get video analytics (views, likes, comments)
# -------------------------
def get_video_stats(video_ids, brand_name):
    """Fetch statistics of videos and calculate engagement rate."""
    
    stats_list = []

    response = YOUTUBE.videos().list(
        part="statistics,snippet",
        id=",".join(video_ids)
    ).execute()

    for video in response.get("items", []):
        snippet = video["snippet"]
        stat = video["statistics"]

        views = int(stat.get("viewCount", 0))
        likes = int(stat.get("likeCount", 0))
        comments = int(stat.get("commentCount", 0))

        # Engagement = likes + comments
        engagement = likes + comments

        # Avoid divide-by-zero error
        engagement_rate = round((engagement / views) * 100, 4) if views else 0

        stats_list.append({
            "brand_query": brand_name,
            "video_title": snippet.get("title", ""),
            "views": views,
            "likes": likes,
            "comments": comments,
            "engagement_rate_%": engagement_rate
        })

    return stats_list


# -------------------------
# Main Execution Flow
# -------------------------
all_results = []

for brand_search in BRANDS:
    print(f"\n🔍 Searching videos for: {brand_search}")
    
    # Get video list
    video_ids = search_videos(brand_search, MAX_RESULTS)

    # Get video stats
    stats = get_video_stats(video_ids, brand_search)

    all_results.extend(stats)


# -------------------------
# Convert to DataFrame
# -------------------------
df = pd.DataFrame(all_results)

# Group by brand query to calculate average engagement rate
avg_scores = df.groupby("brand_query")["engagement_rate_%"].mean().reset_index()
avg_scores.rename(columns={"engagement_rate_%": "avg_engagement_%"},
                  inplace=True)

# Save CSV files
df.to_csv("youtube_brand_data.csv", index=False)
avg_scores.to_csv("youtube_brand_scores.csv", index=False)

print("\n📁 Files Saved:")
print("➡ youtube_brand_data.csv")
print("➡ youtube_brand_scores.csv")

print("\n📊 Average Engagement Scores:")
print(avg_scores)


# -------------------------
# Visualization
# -------------------------
plt.style.use("ggplot")
plt.figure(figsize=(10, 6))
plt.bar(avg_scores["brand_query"], avg_scores["avg_engagement_%"])

plt.title(f"YouTube Engagement Analysis for '{user_input}'", fontsize=14, fontweight="bold")
plt.xlabel("Brands", fontsize=12)
plt.ylabel("Average Engagement Rate (%)", fontsize=12)

plt.xticks(rotation=30)
plt.tight_layout()
plt.show()
