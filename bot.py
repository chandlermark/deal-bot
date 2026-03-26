import os
import feedparser
import random
import json
import tweepy  # pip install tweepy

# ------------------------
# CONFIG - From GitHub Secrets
# ------------------------
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG")  # your Amazon Associate tag
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("ACCESS_SECRET")

# ------------------------
# RSS FEEDS
# ------------------------
RSS_FEEDS = [
    "https://www.hotukdeals.com/rss/deals",
    # "https://uk.camelcamelcamel.com/top_drops_feed"  # optional later
]

# ------------------------
# File to track posted ASINs
# ------------------------
POSTED_FILE = "posted.json"

# ------------------------
# FUNCTIONS
# ------------------------

def load_posted():
    try:
        with open(POSTED_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_posted(posted):
    with open(POSTED_FILE, "w") as f:
        json.dump(list(posted), f)

def find_deal(posted):
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            url = entry.link
            title = entry.title.strip()
            
            # Filter non-Amazon links
            if "amazon.co.uk" not in url and "amzn.to" not in url:
                continue

            # Filter low-quality/used items
            title_lower = title.lower()
            bad_words = ["refurb", "renewed", "used"]
            if any(word in title_lower for word in bad_words):
                continue

            # Extract ASIN from Amazon URL
            asin = None
            if "amazon.co.uk" in url:
                parts = url.split("/")
                if "dp" in parts:
                    dp_index = parts.index("dp")
                    if dp_index + 1 < len(parts):
                        asin = parts[dp_index + 1]
            
            # Skip if already posted
            if asin and asin in posted:
                continue

            return title, url, asin
    return None, None, None

def append_affiliate(url):
    if "tag=" not in url:
        if "?" in url:
            url += f"&tag={AFFILIATE_TAG}"
        else:
            url += f"?tag={AFFILIATE_TAG}"
    return url

def generate_tweet(title, link):
    templates = [
        f"🔥 Deal: {title}\n\n👉 {link}\n\n#AmazonDeals #UKDeals",
        f"💰 {title}\n\nGrab it here 👉 {link}\n\n#Deals #AmazonUK",
        f"⚡ Price drop!\n{title}\n\n👉 {link}\n\n#Bargain #UKDeals",
        f"👀 Worth a look:\n{title}\n\n👉 {link}\n\n#AmazonDeals #Sale"
    ]
    return random.choice(templates)

def post_to_x(tweet):
    auth = tweepy.OAuth1UserHandler(
        CONSUMER_KEY, CONSUMER_SECRET,
        ACCESS_TOKEN, ACCESS_SECRET
    )
    api = tweepy.API(auth)
    api.update_status(tweet)

# ------------------------
# MAIN
# ------------------------
def main():
    posted = load_posted()
    title, url, asin = find_deal(posted)
    if not title:
        print("No new deals found.")
        return
    
    url = append_affiliate(url)
    tweet = generate_tweet(title, url)
    
    print("Posting tweet:")
    print(tweet)
    
    # Uncomment the next line to actually post
    # post_to_x(tweet)
    
    if asin:
        posted.add(asin)
        save_posted(posted)

if __name__ == "__main__":
    main()
