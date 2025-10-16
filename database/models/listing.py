from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime


# Create base class
Base = declarative_base()

# Define the Listing model
class Listing(Base):
    __tablename__ = 'listings'


    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    listing_id = Column(String)
    region = Column(String)
    title = Column(String)
    address = Column(String)
    price = Column(String)
    description = Column(Text)
    rooms = Column(String)
    bedrooms = Column(String)
    bathrooms = Column(String)
    prop_long = Column(String)
    prop_lat = Column(String)
    scrape_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)