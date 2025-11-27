import os
import requests
import feedparser
from datetime import datetime
from notion_client import Client
from dotenv import load_dotenv

# --------------------------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------------------------------

load_dotenv()  # loads values from .env if present

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")
RSS_URL = os.getenv("RSS_URL", "")

if not NOTION_API_KEY:
    raise ValueError("ERROR: NOTION_API_KEY is missing. Add it to your .env file.")

if not DATABASE_ID:
    raise ValueError("ERROR: DATABASE_ID is missing. Add it to your .env file.")

if not RSS_URL:
    raise ValueError("ERROR: RSS_URL is missing. Add it to your .env file.")

notion = Client(auth=NOTION_API_KEY)


# --------------------------------------------------------------------------
# METADATA ENRICHMENT
# --------------------------------------------------------------------------

def categorize_item(title, description):
    text = f"{title} {description}".lower()

    if "initial publication" in text:
        return "Initial Release"
    if "deprecated" in text or "retired" in text:
        return "Deprecation"
    if "removed" in text:
        return "Removal"
    if "renamed" in text:
        return "Renamed Service"
    if "minor" in text or "editorial" in text:
        return "Editorial Update"
    if "added" in text or "new service" in text:
        return "Major Update"
    return "Feature Update"


def detect_domain(description, link):
    text = f"{description} {link}".lower()

    domain_keywords = {
        "Compute": ["ec2", "lambda", "eks", "ecs", "fargate"],
        "Storage": ["s3", "efs", "fsx", "glacier"],
        "Database": ["rds", "aurora", "neptune", "qldb", "dynamodb"],
        "Networking": ["vpc", "route 53", "cloudfront", "elb", "load balancer"],
        "AI/ML": ["sagemaker", "bedrock", "ml", "machine learning", "ai"],
        "Migration": ["snowball", "sms", "datasync"],
        "Security": ["guardduty", "security", "iam", "kms", "macie"],
        "Governance": ["config", "cloudtrail", "catalog", "audit"],
        "Observability": ["cloudwatch", "grafana", "prometheus", "x-ray"],
    }

    for domain, keywords in domain_keywords.items():
        if any(k in text for k in keywords):
            return domain

    return "General"


def detect_change_type(description):
    d = description.lower()
    if "removed" in d:
        return "Removed"
    if "added" in d:
        return "Added"
    if "renamed" in d:
        return "Renamed"
    if "deprecated" in d:
        return "Deprecated"
    return "Updated"


# --------------------------------------------------------------------------
# NOTION HELPERS
# --------------------------------------------------------------------------

def notion_entry_exists(guid):
    """Check if an entry with the same GUID already exists in the DB."""
    query = notion.databases.query(
        database_id=DATABASE_ID,
        filter={
            "property": "GUID",
            "rich_text": {"equals": guid}
        }
    )
    return len(query["results"]) > 0


def add_entry_to_notion(entry):
    title = entry.get("title", "No Title")
    link = entry.get("link", "")
    guid = entry.get("guid", "")
    description = entry.get("description", "")
    published = entry.get("published_parsed")

    if published:
        pub_date = datetime(*published[:6])
    else:
        pub_date = datetime.utcnow()

    # Enriched metadata
    category = categorize_item(title, description)
    domain = detect_domain(description, link)
    change_type = detect_change_type(description)

    year = pub_date.year
    month = pub_date.month

    # Build Notion properties
    props = {
        "Title": {"title": [{"text": {"content": title}}]},
        "Pub Date": {"date": {"start": pub_date.strftime("%Y-%m-%d")}},
        "Year": {"number": year},
        "Month": {"number": month},
        "Category": {"select": {"name": category}},
        "AWS Domain": {"select": {"name": domain}},
        "Change Type": {"select": {"name": change_type}},
        "Description": {"rich_text": [{"text": {"content": description}}]},
        "Source Link": {"url": link},
        "GUID": {"rich_text": [{"text": {"content": guid}}]},
        "Imported From": {"select": {"name": RSS_URL}},
    }

    notion.pages.create(parent={"database_id": DATABASE_ID}, properties=props)
    print(f"✓ Added: {title}")


# --------------------------------------------------------------------------
# MAIN ROUTINE
# --------------------------------------------------------------------------

def run_import():
    print(f"Fetching RSS feed from: {RSS_URL}")
    feed = feedparser.parse(RSS_URL)

    if "entries" not in feed or len(feed.entries) == 0:
        print("WARNING: No entries found in RSS feed.")
        return

    print(f"Found {len(feed.entries)} entries.\n")

    for entry in feed.entries:
        guid = entry.get("guid", "").strip()

        if not guid:
            print(f"Skipping entry (no GUID): {entry.get('title', 'No Title')}")
            continue

        if notion_entry_exists(guid):
            print(f"Already exists, skipping: {entry.get('title', '')}")
            continue

        add_entry_to_notion(entry)

    print("\nImport complete.")


# --------------------------------------------------------------------------
# EXECUTION ENTRY POINT
# --------------------------------------------------------------------------

if __name__ == "__main__":
    run_import()
