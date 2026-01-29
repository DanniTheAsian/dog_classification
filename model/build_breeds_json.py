import json
import requests
import time

def get_wiki_summary(title):
    """Hent Wikipedia-sammenfatning for en rasse"""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data.get("extract", "")
        elif r.status_code == 404:
            # Hvis ikke fundet, prøv med alternativ stavemåde
            return None
    except requests.exceptions.RequestException as e:
        print(f"  Fejl ved hentning: {e}")
        return None
    return None

with open("model/class_names.json", "r", encoding="utf-8") as f:
    class_names = json.load(f)

breeds = {}

for i, name in enumerate(class_names, 1):
    search = name.replace(" dog", "").strip()
    print(f"[{i}/{len(class_names)}] Henter: {search}")

    summary = get_wiki_summary(search)

    if summary:
        breeds[name] = {
            "description": summary[:500] + "..." if len(summary) > 500 else summary,
            "origin": "Unknown",
            "temperament": "See description"
        }
    else:
        # Fallback beskrivelse hvis Wikipedia ikke har data
        breeds[name] = {
            "description": f"{search.title()} er en hunderace med egen karakteristik og historik.",
            "origin": "Unknown",
            "temperament": "See description"
        }

    time.sleep(0.5)  # Respektér Wikipedia API rate limit

# Gem som dictionary (key = breed name)
with open("../breeds.json", "w", encoding="utf-8") as f:
    json.dump(breeds, f, indent=2, ensure_ascii=False)

print(f"\n✓ Færdig! {len(breeds)} raceerner gemt i breeds.json")
