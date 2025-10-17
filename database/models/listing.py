from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

# Create base class
Base = declarative_base()

# Define the Listing model
class Listing(Base):
    __tablename__ = 'listings'

    id = Column(Integer, primary_key=True)
    site = Column(String)
    url = Column(String, unique=True)
    listing_id = Column(String, unique=True)
    region = Column(String)
    title = Column(String)
    address = Column(String)
    price = Column(Float)
    description = Column(Text)
    rooms = Column(String)
    bedrooms = Column(String)
    bathrooms = Column(String)
    prop_long = Column(String)
    prop_lat = Column(String)
    scrape_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationship
    price_history = relationship("PriceHistory", back_populates="listing")

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    url = Column(String, ForeignKey("listings.url"))
    price = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="price_history")