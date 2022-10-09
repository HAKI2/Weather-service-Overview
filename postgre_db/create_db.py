from database import Base, engine
from models import API, City, Weather

Base.metadata.create_all(engine)