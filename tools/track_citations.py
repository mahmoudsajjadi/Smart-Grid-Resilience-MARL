import requests, csv
DOI = "10.3390/su182010574"; M = "mahmoud.sajjadi@unr.edu"
w = requests.get(f"https://api.openalex.org/works/https://doi.org/{DOI}?mailto={M}", timeout=30).json()
wid, rows, cur = w["id"].split("/")[-1], [], "*"
while cur:
    d = requests.get(f"https://api.openalex.org/works?filter=cites:{wid}&per-page=100&cursor={cur}&mailto={M}", timeout=30).json()
    for x in d["results"]:
        rows.append([x["publication_date"], x["title"], x.get("doi")])
    cur = d["meta"].get("next_cursor")
    if not d["results"]: break
rows.sort(reverse=True)
csv.writer(open("citations.csv", "w", newline="")).writerows([["date", "title", "doi"]] + rows)
print(len(rows), "citations")
