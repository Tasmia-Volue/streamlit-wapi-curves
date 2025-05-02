import pandas as pd

def show_list(both_selected, curve_data, curve_data_dev: None):
    df = pd.DataFrame({
        'Timestamp': curve_data['points'].index,
        'Series': curve_data['points']['value']
    })
    if both_selected:
        df['Dev Series'] = curve_data_dev['points']['value']
        df.rename(columns={'Series': 'Prod Series'}, inplace=True)

    return df
