import datetime
import os
import requests
from pprint import pprint
from postgre_db.database import SessionLocal
from postgre_db.models import Weather, API, City


# OPEN WEATHER
OW_API_KEY = '############################'
OW_FORECAST_URL = 'https://api.openweathermap.org/data/2.5/forecast'
OW_GEOLOC_URL = 'https://api.openweathermap.org/geo/1.0/direct'
OW_forecast_params = {
    'appid': OW_API_KEY,
    'units': 'metric',
    'cnt': 2,
}
OW_geoloc_params = {
    'appid': OW_API_KEY,
}

# WEATHER API
WA_API_KEY = '#################################'
WA_FORECAST_URL = 'https://api.weatherapi.com/v1/'
WA_forecast_params = {
    'key': WA_API_KEY,
    'days': 2,
    'aqi': 'no',
    'alerts': 'no',
}

cur_loc = ''


def set_geoloc_params(geoloc_data, WA_forecast_params, OW_forecast_params):
    lat = geoloc_data['lat']
    lon = geoloc_data['lon']
    OW_forecast_params.update({
        'lat': lat,
        'lon': lon,
    })
    WA_forecast_params.update({
        'q': f'{lat},{lon}',
    })


def get_geoloc_params(city, WA_forecast_params, OW_forecast_params, ignore=False):
    OW_geoloc_params['q'] = city
    geoloc_req = requests.get(OW_GEOLOC_URL, params=OW_geoloc_params)
    if len(geoloc_req.json()) == 0:
        print(f"Didn't get geolocation params. Code: {geoloc_req.status_code}")
        return False
    else:
        geoloc_data = geoloc_req.json()[0]
        if geoloc_data['name'] == city:
            set_geoloc_params(geoloc_data, WA_forecast_params, OW_forecast_params)
            print(f"Get geolocation params. Code: {geoloc_req.status_code}")
            return True
        else:
            if ignore:
                set_geoloc_params(geoloc_data, WA_forecast_params, OW_forecast_params)
                return True
            else:
                answ = input(f'Did you mean {geoloc_data["name"]} in coutnry {geoloc_data["country"]}? y / n\n').lower()
                if answ in ['yes', 'y']:
                    print(f"Get geolocation params. Code: {geoloc_req.status_code}")
                    set_geoloc_params(geoloc_data, WA_forecast_params, OW_forecast_params)
                    return True
                return False


def OW_forecast(WA_forecast_params, OW_forecast_params):
    now = datetime.datetime.now()
    OW_forecast_params = dict(OW_forecast_params)  # FROM proxy_dict to dict
    print(f'Process: {os.getpid()}. OW forecast started. {now}')
    forecast_req = requests.get(OW_FORECAST_URL, params=OW_forecast_params)
    json_data = forecast_req.json()
    code_req = json_data['cod']
    match code_req:
        case '200':
            print('OW forecast: 200 OK')
            data = json_data['list']
            for i in data:
                date = datetime.datetime.fromisoformat(i['dt_txt'])
                if date > now:
                    with SessionLocal() as session:  # TODO make new function: repeated in WA_forecast!!!!!!!!!!!!!!!!!
                        city = session.query(City).filter(City.name == 'Saint Petersburg').first()
                        api = session.query(API).filter(API.name == 'OpenWeather').first()
                        if not session.query(Weather).filter(Weather.api==api, Weather.date==date, Weather.city==city).all():
                            a = Weather(temp_notconf=i['main']['temp'], city=city, api=api, date=date)
                            try:
                                session.add(a)
                                session.commit()
                                print(f'Process: {os.getpid()}. OW forecast: 1 objects added')
                            except Exception:
                                print(f'Process: {os.getpid()}. OW forecast: 0 objects added')
                        else:
                            print(f'Process: {os.getpid()}. OW forecast: 0 objects added')
        case r'4\d\d':
            print(f'Error code {code_req}')
        case r'5\d\d':
            print(f'Server error {code_req}')
        case _:
            print(f'OW forecast: {code_req}')
            pprint(json_data)
    print(f'Process: {os.getpid()}. OW forecast ended. {datetime.datetime.now()}')


def WA_forecast(WA_forecast_params, OW_forecast_params):
    WA_forecast_params = dict(WA_forecast_params)
    now = datetime.datetime.now()
    print(f'Process: {os.getpid()}. OW forecast started. {now}')
    forecast_req = requests.get(WA_FORECAST_URL+'forecast.json', params=WA_forecast_params)
    json_data = forecast_req.json()
    code_req = forecast_req.status_code
    match code_req:
        case 200:
            print('WA forecast: 200 OK')
            hour = (datetime.datetime.now() + datetime.timedelta(hours=1)).hour
            if hour == 0:
                temp = json_data['forecast']['forecastday'][1]['hour'][hour]['temp_c']
                date = json_data['forecast']['forecastday'][1]['hour'][hour]['time']
            else:
                temp = json_data['forecast']['forecastday'][0]['hour'][hour]['temp_c']
                date = json_data['forecast']['forecastday'][0]['hour'][hour]['time']
            with SessionLocal() as session:  # TODO make new function: repeated in OW_forecast!!!!!!!!!!!!!!!!!!!!!!!!!
                city = session.query(City).filter(City.name == 'Saint Petersburg').first()
                api = session.query(API).filter(API.name == 'WeatherAPI').first()
                if not session.query(Weather).filter(Weather.api==api, Weather.date==date, Weather.city==city).all():
                    model = Weather(temp_notconf=temp, city=city, api=api, date=datetime.datetime.fromisoformat(date))
                    try:
                        session.add(model)
                        session.commit()
                        print(f'Process: {os.getpid()}. WA forecast: 1 objects added')
                    except Exception:
                        print(f'Process: {os.getpid()}. WA forecast: 0 objects added')
                else:
                    print(f'Process: {os.getpid()}. WA forecast: 0 objects added')
        case r'4\d\d':
            print(f'Error code {code_req}')
        case r'5\d\d':
            print(f'Server error {code_req}')
        case _:
            print(f' WA forecast: {code_req}')
            pprint(forecast_req.json())
    print(f'Process: {os.getpid()}. WA forecast ended. {datetime.datetime.now()}')


def confirm_forecast(WA_forecast_params, OW_forecast_params):
    WA_forecast_params = dict(WA_forecast_params)
    now = datetime.datetime.now()
    print(f'Process: {os.getpid()}. Confirm forecast started. {now}')
    with SessionLocal() as session:
        weather_to_update = session.query(Weather).filter(
            Weather.temp_conf == None, Weather.date < now - datetime.timedelta(hours=1)).all()
        for i in weather_to_update:  # TODO check request code!!!
            date = i.date
            WA_forecast_params['dt'] = date.date()
            forecast_req = requests.get(WA_FORECAST_URL+'history.json', params=WA_forecast_params)
            json_data = forecast_req.json()
            temp = json_data['forecast']['forecastday'][0]['hour'][date.time().hour]['temp_c']
            i.temp_conf = temp
            i.deviation = abs(i.temp_conf - i.temp_notconf) / i.temp_conf
        session.commit()
        print(f'Confirm forecast: updated {len(weather_to_update)} objects in database')
    print(f'Process: {os.getpid()}. ended. WA confirm forecast. {datetime.datetime.now()}')


def past_weather():
    pass
