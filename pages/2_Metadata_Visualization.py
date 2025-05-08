import streamlit as st
import pandas as pd
from utils.wapi_configs import create_session, load_all_curve
from utils.format_date import format_date
from dateutil.parser import parse

output_options = ['entsoe_transparency',
                  'nordpool_elspot_file', 'nordpool_elspot_flow']

st.set_page_config(layout="wide")

st.image('images/volue.svg', width=120)
st.title('METADATA :green[VISUALIZATION] 📃')
st.divider()

f_col1, f_col2 = st.columns(2)
with f_col1:
    options = ['Development', 'Production']
    dev_prod_selection = st.segmented_control(
        'Choose Type:', options, selection_mode='single', default='Development'
    )

session = create_session(dev_prod_selection)

output_selected = st.selectbox(
    "Target Output Name",
    output_options,
)


curves = load_all_curve(session, output_selected)
if len(curves) == 0:
    st.error('No curves exist in Production')
else:
    curves_metadata_list = []
    for curve in curves:
        curve_name = curve.name
        curve_metadata = curve._metadata
        important_metadata = {k: v for k, v in curve_metadata.items(
        ) if k in ('name', 'created', 'modified', 'time_zone', 'frequency', 'keys')}
        curves_metadata_list.append(important_metadata)
    
    curves_metadata_df = pd.DataFrame(curves_metadata_list)
    curves_metadata_df.rename(columns={'keys':'curve_keys'}, inplace=True)
    
    unique_keys = set(item for sublist in curves_metadata_df['curve_keys'] for item in sublist)

    col1, col2 = st.columns(2)
    freq_selection = col1.multiselect(
        'Select frequencies', 
        options=curves_metadata_df.frequency.unique().tolist(), 
        key='frequencies'
    )
    keys_selection = col2.multiselect(
        'Select keys', 
        options=sorted(unique_keys),
        key='unique keys'
    )

    filtered_df = curves_metadata_df.copy()
    if freq_selection:
        filtered_df = filtered_df[filtered_df['frequency'].isin(freq_selection)]

    if keys_selection:
        filtered_df = filtered_df[filtered_df['curve_keys'].apply(
            lambda keys: all(key in keys for key in keys_selection)
        )]

    filtered_df['modified'] = pd.to_datetime(
        filtered_df['modified'], errors='coerce')
    

    st.write(f"Filtered curves: {len(filtered_df)}")
    st.dataframe(filtered_df, use_container_width=True)
