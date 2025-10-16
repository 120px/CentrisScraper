from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from datetime import datetime
from .models.listing import Base, Listing

# Database connection and session management
class Database:
    def __init__(self):
        load_dotenv()
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")

        try:
            self.engine = create_engine(
                f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
            )
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    def insert_listing(self, site: Text, listing_data):
        session = self.Session()
        try:
            listing = Listing(
                url=listing_data['url'],
                region=listing_data['region'],
                title=listing_data['title'],
                address=listing_data['address'],
                price=listing_data['price'],
                description=listing_data['description'],
                rooms=listing_data['rooms'],
                bedrooms=listing_data['bedrooms'],
                bathrooms=listing_data['bathrooms'],
                prop_long=listing_data['prop_long'],
                prop_lat=listing_data['prop_lat'],
                listing_id=listing_data['listing_id'],
                scrape_date=datetime.fromisoformat(listing_data['scrape_date'])
            )
            Listing.__tablename__ = site
            session.add(listing)
            session.commit()
            print(f"Successfully inserted listing: {listing_data['title']}")
        except Exception as e:
            session.rollback()
            print(f"Error inserting listing: {e}")
        finally:
            session.close()