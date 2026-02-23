def list_single_use_tags(client):
    # Fetch tags used exactly once and print them as a numbered list.
    tags = client.fetch_tags()
    single_use = [t for t in tags if t.get("count", 0) == 1]
    if not single_use:
        print("No single-use tags found.")
        return
    for i, tag in enumerate(single_use, start=1):
        print(f"{i}. {tag['tag']}")
