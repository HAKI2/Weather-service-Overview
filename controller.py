import threading
import time
import apigeter
import json
import multiprocessing


cur_loc = ''


def get_saved_loc():
    global cur_loc
    with open('cur_loc.json', 'r') as f:
        cur_loc = json.load(f)['cur_loc']


def controller():
    while True:
        print('-' * 50)
        get_saved_loc()
        print(f'Current location: {cur_loc}')
        inp = input('''
    Choose the following command:
    1. Change current location. DOESN'T WORK: ONLY FOR SAINT PETERSBURG
    2. Status of processes
        ''')
        match inp:
            case '1':
                new_loc = input('New location:')
                while new_loc != '' and apigeter.get_geoloc_params(
                        new_loc, WA_forecast_params, OW_forecast_params) is False and new_loc != 'exit':
                    new_loc = input(
                        """
    Please try again!
    If you don't want to change location write: 'exit'
    New location:"""
                    )
                if new_loc == 'exit':
                    continue
                with open('cur_loc.json', 'w') as f:
                    json.dump({'cur_loc': new_loc}, f)
            case '2':
                print(multiprocessing.active_children())
        print('-' * 50)


def OW_timer():
    global prc1
    while True:
        prc1.start()
        time.sleep(3600 * 3)
        prc1 = multiprocessing.Process(target=apigeter.OW_forecast)


def WA_timer():
    global prc2
    while True:
        prc2.start()
        time.sleep(3600)
        prc2 = multiprocessing.Process(target=apigeter.WA_forecast)


def WA_confirm_timer():
    global prc3
    while True:
        prc3.start()
        time.sleep(3600)
        prc3 = multiprocessing.Process(target=apigeter.confirm_forecast)


def main():
    p1t = threading.Thread(target=OW_timer)
    p2t = threading.Thread(target=WA_timer)
    p3t = threading.Thread(target=WA_confirm_timer)
    contr = threading.Thread(target=controller)
    p1t.start()
    p2t.start()
    p3t.start()
    contr.start()


if __name__ == '__main__':
    get_saved_loc()
    manager = multiprocessing.Manager()
    WA_forecast_params = manager.dict(apigeter.WA_forecast_params)
    OW_forecast_params = manager.dict(apigeter.OW_forecast_params)
    apigeter.get_geoloc_params(
        cur_loc, WA_forecast_params, OW_forecast_params, ignore=True
    )  # TODO change db, make different city support: add column for state and location. With geoloc find states and loc
    prc1 = multiprocessing.Process(
        target=apigeter.OW_forecast, name='OW_forecast', args=(WA_forecast_params, OW_forecast_params)
    )
    prc2 = multiprocessing.Process(
        target=apigeter.WA_forecast, name='WA_forecast', args=(WA_forecast_params, OW_forecast_params)
    )
    prc3 = multiprocessing.Process(
        target=apigeter.confirm_forecast, name='Confirm forecast', args=(WA_forecast_params, OW_forecast_params)
    )
    # prc4 = multiprocessing.Process(target=apigeter.past_weather, name='Past weather')  # инфа о периоде в прошлом
    # prc4.start()
    main()
