"""Seed script for initial test data."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client
from app.core.config import get_settings

def seed():
    settings = get_settings()
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)

    # Sample reviews
    reviews = [
        {
            "title": "Amazing Wireless Headphones",
            "content": "These headphones have incredible sound quality...",
            "category": "product",
            "rating": 5,
            "source": "https://example.com/headphones-review"
        },
        {
            "title": "The Great Gatsby - A Classic",
            "content": "F. Scott Fitzgerald's masterpiece remains relevant...",
            "category": "book",
            "rating": 4,
        },
        {
            "title": "Downtown Sushi Restaurant",
            "content": "Fresh ingredients and creative rolls...",
            "category": "restaurant",
            "rating": 4,
            "source": "https://example.com/sushi-review"
        },
    ]

    for review in reviews:
        result = supabase.table("reviews").insert(review).execute()
        print(f"Inserted review: {review['title']}")

    print(f"Seeded {len(reviews)} reviews successfully.")

if __name__ == "__main__":
    seed()
