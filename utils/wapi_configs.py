import wapi_ext as wapi
import pandas as pd

DEV_API_URLBASE = 'api.wsight.org'
PROD_API_URLBASE = 'api.volueinsight.com'

def create_session(type: str):
    wapi_ini_read = '/home/tasmia/Documents/Volue/JBOSS/wapi_config.ini'
    if type == 'Development':
        wapi_session = wapi.Session(
            urlbase=f'https://{DEV_API_URLBASE}', config_file=wapi_ini_read)
    else:
        wapi_session = wapi.Session(
            urlbase=f'https://{PROD_API_URLBASE}', config_file=wapi_ini_read)

    return wapi_session


def load_all_curve(session, name):
    curves = session.get_all_curves_for_script(name)
    curves.sort(key=lambda x: x.name)

    return curves


def load_data(curve, date_from, date_to):
    curve_details = {}

    curve_details['meta_data'] = curve._metadata
    curve_details['name'], curve_details['curve_timezone'] = curve.name, curve.time_zone
    curve_details['freq'] = curve.frequency
    series = curve.get_data(date_from, date_to)

    df = pd.DataFrame(series.points, columns=['timestamp', 'value'])
    df.set_index('timestamp', inplace=True)
    df.index = pd.to_datetime(
        df.index, unit='ms', utc=True).tz_convert(curve.time_zone)

    curve_details['points'] = df

    return curve_details
