import feedparser


def scrape_site(url):
    feed = feedparser.parse(url + "/feed")

    posts = []

    # 🔥 ONLY latest 3 posts (prevents old spam)
    for entry in feed.entries[:5]:
        title = entry.title
        link = entry.link

        img = None

        # try media
        if hasattr(entry, "media_content"):
            img = entry.media_content[0]["url"]

        # fallback: try thumbnail
        elif hasattr(entry, "media_thumbnail"):
            img = entry.media_thumbnail[0]["url"]

        posts.append((title, link, img))

    return posts
