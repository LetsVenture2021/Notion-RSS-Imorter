# Notion-RSS-Imorter

# AWS Changelog → Notion Importer

This project provides a production-ready Python importer that ingests the official AWS Overview RSS feed and inserts enriched changelog entries into a Notion database. The importer performs the following functions:

1. Fetches the AWS changelog RSS feed  
2. Parses and normalizes all entries  
3. Enriches each entry with metadata for classification and filtering  
4. Performs duplicate detection using the RSS `<guid>` field  
5. Upserts structured changelog entries into an existing Notion database  

The result is an organized, analytics-ready Notion dataset containing the full AWS changelog history from 2014 onward.

---

## Features

### **✔ Automatic Metadata Enrichment**
Each RSS entry is classified into:
- Category (Major Update, Feature Update, Deprecation, Renamed Service, etc.)
- AWS Domain (Compute, Storage, Database, Networking, AI/ML, Governance, etc.)
- Change Type (Added, Updated, Removed, Deprecated, Renamed)
- Extracted Year and Month

### **✔ Duplicate Prevention**
Each item uses the RSS GUID to ensure the importer never inserts the same update twice.

### **✔ Full Notion API Integration**
The importer writes directly to your Notion database using:
- Title  
- Pub Date  
- Year  
- Month  
- Category  
- AWS Domain  
- Change Type  
- Description  
- Source Link  
- GUID  
- Imported From  
- Notes (optional)

### **✔ Ready for Automation**
You can deploy this importer with:
- Cron (local/server)
- GitHub Actions
- AWS Lambda
- Any container platform

---

## Requirements

Python 3.9+  
The following dependencies:

