from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from datetime import datetime
from .models.listing import Base, Listing, PriceHistory

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

    def insert_listing(self, listing_data):
        session = self.Session()
        try:
            existing = session.query(Listing).filter_by(listing_id=listing_data["url"]).first()

            if not existing:
                new_listing = Listing(
                    site=listing_data['site'],
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
                session.add(new_listing)

                # create initial price history record
                price_entry = PriceHistory(
                    url=listing_data["url"],
                    price=listing_data["price"]
                )
                session.add(price_entry)
                print(f"Inserted new listing: {listing_data['title']} with initial price {listing_data['price']}")

            else:
                # check for price change
                last_price = (
                    session.query(PriceHistory)
                    .filter_by(url=listing_data["url"])
                    .order_by(PriceHistory.recorded_at.desc())
                    .first()
                )

                if last_price and last_price.price != listing_data["price"]:
                    new_price_entry = PriceHistory(
                        listing_id=listing_data["listing_id"],
                        price=listing_data["price"]
                    )
                    session.add(new_price_entry)
                    print(f"Price changed for {listing_data['listing_id']}: {last_price.price} → {listing_data['price']}")

            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error inserting listing: {e}")
        finally:
            session.close()