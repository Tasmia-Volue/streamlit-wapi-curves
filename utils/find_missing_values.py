import pandas as pd

FREQ_MAPPING = {
    'MIN15': '15min',
    'H': 'h'
}

def find_missing(curve_data, from_date, to_date, frequency):
    df = pd.DataFrame({
        'timestamp': curve_data['points'].index,
        'series': curve_data['points']['value']
    })

    print(df['series'])
    if df['series'].empty:
        missing_data_timestamps = pd.date_range(start=from_date, end=to_date, freq=FREQ_MAPPING.get(frequency, frequency))
        return missing_data_timestamps
    
    null_values = pd.isnull(df['series'])
    missing_data_timestamps = df.loc[null_values, 'timestamp']

    if not missing_data_timestamps.empty:
        return missing_data_timestamps
    else:
        return None
