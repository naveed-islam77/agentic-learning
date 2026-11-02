import json 
import os 
from datetime import datetime, timezone

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

if not api_key:
    raise ValueError(
        "TAVILY_API_KEY nahi mili. Project ki .env file check karo."
    )

tavily = TavilyClient(api_key=api_key)

# User se trading topic aur target audience poochho
topic = input("Trading topic likho: ").strip()
audience = input("Target audience likho: ").strip()

# Khali input ko aage bhejne se roko

if not topic or not audience:
    raise ValueError("Topic aur audience dono likhna zarori ha")

# Ek hi topic ko alag search phrases ke zariye dhoondo
queries = [
    f"{topic} trading community for {audience}",
    f"{topic} trading forum discussion group",
    f"{topic} trading community Reddit Discord Telegram",
]


# Search results yahan jama honge
candidates = []

# Duplicate URLs ko pehchanne ke liye set
seen_urls = set()


for query in queries:
    print(f"\nSearch ho raha hai: {query}")

    response = tavily.search(
        query=query,
        search_depth="basic",
        max_results=5,
        topic="general",
        include_answer=False
    )

    # API response ke har result ko process karo

    for result in response.get("results", []):
        title = result.get("title", "").strip()
        url = result.get("url", "").strip()
        snippet = result.get("content", "").strip()

        if not title or not url:
            continue

        # Aakhri slash hata kar simple duplicate check karo
        url_key = url.rstrip("/").lower()

        # Agar URL pehle aa chuka hai to usay skip karo
        if url_key in seen_urls:
            continue

        seen_urls.add(url_key)


        candidates.append(
            {
                "title": title,
                "url": url,
                "snippet": snippet,
                "search_query": query,
                "discovered_at": datetime.now(timezone.utc).isoformat(),
            }
        )

output_file = "community_candidates.json"

with open (output_file, "w", encoding="utf-8") as file:
    json.dump(candidates, file, ensure_ascii=False, indent=2)


print(f"\nTotal unique candidates: {len(candidates)}")
print(f"Results save hue: {output_file}")


for number, candidate in enumerate(candidates[:10], start=1):
    print(f"\n{number}. {candidate['title']}")
    print(f"   Link: {candidate['url']}")
    print(f"   Query: {candidate['search_query']}")
    print(f"   Snippet: {candidate['snippet'][:250]}")