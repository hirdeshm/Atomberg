import pandas as pd
import matplotlib.pyplot as plt
from urllib.parse import urlparse

# ----------------------------------------------------
# 1. Load CSV
# ----------------------------------------------------
df = pd.read_csv("google_brand_detection.csv")   # change if needed

# ----------------------------------------------------
# 2. Brand dictionary with variations (synonyms)
# ----------------------------------------------------
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

# ----------------------------------------------------
# 3. Detect brand from title, snippet, and domain
# ----------------------------------------------------
def detect_brand(row):
    text = f"{row['title']} {row['snippet']}".lower()
    
    # extract domain name (hostname)
    domain = urlparse(row['link']).netloc.lower()
    
    for brand, variations in brand_variants.items():
        for term in variations:
            if term in text or term in domain:
                return brand
    return None

df["brand"] = df.apply(detect_brand, axis=1)

# ----------------------------------------------------
# 4. Position score values
# ----------------------------------------------------
position_score = {
    1: 100, 2: 90, 3: 80, 4: 70, 5: 60,
    6: 50, 7: 40, 8: 30, 9: 20, 10: 10
}

def get_position_score(p):
    return position_score.get(p, 5)  # default score for >10

df["score"] = df["position"].apply(get_position_score)

# ----------------------------------------------------
# 5. Calculate brand score
# ----------------------------------------------------
brand_scores = (
    df.dropna(subset=["brand"])
      .groupby("brand")["score"]
      .sum()
      .sort_values(ascending=False)
)

print("\n=== Final Brand Visibility Score ===\n")
print(brand_scores)

# ----------------------------------------------------
# 6. PLOT BAR CHART
# ----------------------------------------------------
plt.style.use("ggplot")  # Adds modern theme
print(plt.style.available)
plt.figure(figsize=(12,6))
bars = plt.bar(brand_scores.index, brand_scores.values,color="orange")

# Add labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 3, str(height), 
             ha='center', fontsize=12, fontweight='bold')

plt.title("Brand Visibility Score", fontsize=16, fontweight='bold')
plt.xlabel("Brand", fontsize=13)
plt.ylabel("Score", fontsize=13)
plt.xticks(rotation=30, fontsize=12)

plt.tight_layout()
plt.show()
