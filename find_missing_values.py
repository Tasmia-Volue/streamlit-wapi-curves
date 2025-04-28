import pandas as pd


def find_missing(curve_data):
    df = pd.DataFrame({
        'timestamp': curve_data['points'].index,
        'series': curve_data['points']['value']
    })

    null_values = pd.isnull(df['series'])
    missing_data = df[null_values]

    if not missing_data.empty:
        return missing_data
    else:
        return None
