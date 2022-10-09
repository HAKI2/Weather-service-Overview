from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

# if error exception: change .database to database or change database to .database


class City(Base):
    __tablename__ = "city"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, index=True)
    weather = relationship("Weather", back_populates="city")


class API(Base):
    __tablename__ = "api"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String, unique=True, index=True)
    weather = relationship("Weather", back_populates="api")


class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    temp_conf = Column(Float, index=True)
    temp_notconf = Column(Float, index=True)
    deviation = Column(Float, index=True)
    date = Column(DateTime, index=True)

    city_id = Column(Integer, ForeignKey("city.id"))
    api_id =Column(Integer, ForeignKey("api.id"))

    city = relationship("City", back_populates="weather")
    api = relationship("API", back_populates="weather")