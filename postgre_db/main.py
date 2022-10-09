from database import Base, engine
from models import API, City, Weather
from database import SessionLocal
a = City(name='Saint Petersburg')
b = API(name='OpenWeather')
c = API(name='WeatherAPI')
with SessionLocal() as session:
    session.add(a)
    session.add(b)
    session.add(c)
    session.commit()