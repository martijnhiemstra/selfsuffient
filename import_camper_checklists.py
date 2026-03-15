#!/usr/bin/env python3
"""
Camper Travel Checklists Import Script

This script imports 6 camper travel checklists into your Earthly Life app.

Usage:
    python3 import_camper_checklists.py --project-id YOUR_PROJECT_ID --user-id YOUR_USER_ID

To find your IDs:
    1. Login to your app
    2. Go to the project where you want these checklists
    3. The project_id is in the URL: /projects/<project_id>/checklists
    4. Or query the database: db.projects.find({}, {id: 1, name: 1, user_id: 1})
"""

import asyncio
import uuid
import argparse
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Checklist data extracted from the PDF
CHECKLISTS = [
    {
        "name": "1. Pre-Trip Planning",
        "description": "Essential checks and preparations before starting your camper trip",
        "items": [
            "Passport / ID",
            "Driver's license",
            "Vehicle registration",
            "Insurance documents",
            "Breakdown assistance membership",
            "Campsite reservations",
            "Check weather forecast",
            "Check tire pressure (incl. spare)",
            "Check oil, coolant, brake fluid",
            "Gas bottle filled",
            "Waste water tank empty",
            "Toilet cassette empty",
            "Leisure battery charged"
        ]
    },
    {
        "name": "2. Packing Essentials",
        "description": "Must-have items to pack for your camper trip",
        "items": [
            "Bedding & towels",
            "Clothing (weather appropriate)",
            "Toiletries",
            "Cooking utensils",
            "Plates & cutlery",
            "Food & drinks",
            "CEE power cable & adapter",
            "Water hose (food safe)",
            "Leveling blocks",
            "First aid kit",
            "Warning triangle",
            "Fire extinguisher"
        ]
    },
    {
        "name": "3. Departure Day",
        "description": "Final checks before driving off",
        "items": [
            "Windows & roof hatches closed",
            "Steps retracted",
            "Cables disconnected",
            "Loose items secured",
            "Fridge locked",
            "Cabinets locked",
            "Gas turned off",
            "Water pump off",
            "Mirrors adjusted",
            "Navigation set"
        ]
    },
    {
        "name": "4. Arrival at Campsite",
        "description": "Setup tasks when you arrive at your destination",
        "items": [
            "Park level",
            "Handbrake applied",
            "Connect electricity",
            "Connect water",
            "Turn on fridge",
            "Switch water pump on",
            "Test taps",
            "Set heating (if needed)"
        ]
    },
    {
        "name": "5. Before Leaving Campsite",
        "description": "Checklist before departing from the campsite",
        "items": [
            "Disconnect electricity",
            "Drain waste water",
            "Empty toilet cassette",
            "Close roof hatches",
            "Retract steps",
            "Secure loose items",
            "Check surroundings"
        ]
    },
    {
        "name": "6. Return / Storage",
        "description": "End-of-trip tasks and long-term storage preparation",
        "items": [
            "Empty fresh water tank",
            "Empty waste water tank",
            "Clean fridge (leave door open)",
            "Remove food",
            "Turn off gas",
            "Disconnect batteries (long-term storage)",
            "Drain water system (winter)",
            "Open all taps (winter)"
        ]
    }
]


async def import_checklists(mongo_url: str, db_name: str, project_id: str, user_id: str):
    """Import all checklists into the database."""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    now = datetime.now(timezone.utc).isoformat()
    total_items = 0
    
    print("\n🚐 Importing Camper Travel Checklists...")
    print("=" * 50)
    
    for checklist_data in CHECKLISTS:
        checklist_id = str(uuid.uuid4())
        
        # Create checklist document
        checklist_doc = {
            "id": checklist_id,
            "project_id": project_id,
            "user_id": user_id,
            "name": checklist_data["name"],
            "description": checklist_data["description"],
            "created_at": now,
            "updated_at": now
        }
        
        await db.checklists.insert_one(checklist_doc)
        print(f"✓ Created: {checklist_data['name']}")
        
        # Create items for this checklist
        for order, item_text in enumerate(checklist_data["items"]):
            item_doc = {
                "id": str(uuid.uuid4()),
                "checklist_id": checklist_id,
                "user_id": user_id,
                "text": item_text,
                "is_done": False,
                "order": order,
                "created_at": now,
                "updated_at": now
            }
            await db.checklist_items.insert_one(item_doc)
            total_items += 1
        
        print(f"  → Added {len(checklist_data['items'])} items")
    
    print("=" * 50)
    print(f"✅ Import complete!")
    print(f"   Checklists created: {len(CHECKLISTS)}")
    print(f"   Total items: {total_items}")
    print("=" * 50)
    
    client.close()


async def list_projects(mongo_url: str, db_name: str):
    """List all projects to help user find the right project_id."""
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("\n📋 Available Projects:")
    print("-" * 60)
    
    projects = await db.projects.find({}, {"_id": 0, "id": 1, "name": 1, "user_id": 1}).to_list(100)
    
    if not projects:
        print("No projects found.")
    else:
        for p in projects:
            print(f"  Name: {p['name']}")
            print(f"  Project ID: {p['id']}")
            print(f"  User ID: {p['user_id']}")
            print("-" * 60)
    
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Camper Travel Checklists")
    parser.add_argument("--project-id", help="Target project ID")
    parser.add_argument("--user-id", help="User ID")
    parser.add_argument("--list-projects", action="store_true", help="List all projects")
    parser.add_argument("--mongo-url", default=os.environ.get("MONGO_URL", "mongodb://localhost:27017"), 
                        help="MongoDB connection URL")
    parser.add_argument("--db-name", default="selfsufficient", help="Database name")
    
    args = parser.parse_args()
    
    if args.list_projects:
        asyncio.run(list_projects(args.mongo_url, args.db_name))
    elif args.project_id and args.user_id:
        asyncio.run(import_checklists(args.mongo_url, args.db_name, args.project_id, args.user_id))
    else:
        print("Usage:")
        print("  To list projects: python3 import_camper_checklists.py --list-projects")
        print("  To import:        python3 import_camper_checklists.py --project-id <ID> --user-id <ID>")
        print("\nRun with --list-projects first to find your project and user IDs.")
