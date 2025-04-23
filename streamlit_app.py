import streamlit as st
import pandas as pd
import wapi_ext as wapi
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

DEV_API_URLBASE = 'api.wsight.org'
PROD_API_URLBASE = 'api.volueinsight.com'

output_options = ['entsoe_transparency', 'elhub_actual_production']

dev_color = '#7FE592'
prod_color = '#E66000'

st.set_page_config(layout="wide")


def create_session(type: str):
    wapi_ini_read = '/home/tasmia/Documents/Volue/JBOSS/wapi_config.ini'
    if type == 'Development':
        wapi_session = wapi.Session(
            urlbase=f'https://{DEV_API_URLBASE}', config_file=wapi_ini_read)
    else:
        wapi_session = wapi.Session(
            urlbase=f'https://{PROD_API_URLBASE}', config_file=wapi_ini_read)

    return wapi_session


def format_date(data):
    for k in ['created', 'modified']:
        if k in data:
            try:
                dt = pd.to_datetime(data[k])
                data[k] = dt.strftime("%d %b %Y, %I:%M %p %Z")
            except Exception as e:
                pass
    
    return data


def load_all_curve(session, name, keys=None):
    curve_dict = []
    curves = session.get_all_curves_for_script(name)
    curves.sort(key=lambda x: x.name)
    for curve in curves:
        if keys:
            if all(key in curve.keys for key in keys):
                curve_dict.append(curve)
        else:
            curve_dict.append(curve)

    return curve_dict

def load_output_data(session, output, keys=None):
    curves = load_all_curve(session, output, keys)
    curve_checkbox = {}
    for curve in curves:
        curve_checkbox[curve] = st.checkbox(curve.name)

    return curve_checkbox


def find_matching_curve_in_dev(curve_name, curves_list):
    for curve in curves_list:
        if curve.name == curve_name:
            return curve
    return None


def load_data(curve, date_from, date_to):
    curve_details = {}
    
    curve_details['meta_data'] = curve._metadata
    curve_details['name'], curve_details['curve_timezone'] = curve.name, curve.time_zone
    series = curve.get_data(date_from, date_to)
    
    df = pd.DataFrame(series.points, columns=['timestamp', 'value'])
    df.set_index('timestamp', inplace=True)
    df.index = pd.to_datetime(df.index, unit='ms', utc=True).tz_convert(curve.time_zone)

    curve_details['points'] = df

    return curve_details


def create_ui():
    st.image('volue.svg', width=120)
    st.title('INSIGHT API :green[VISUALIZATION] 📈')
    st.divider()

    col1, col2 = st.columns([1, 4])
    dev_or_prod = ''
    both_selected = False
    with col1:
        options = ['Development', 'Production', 'Both']
        dev_prod_selection = st.segmented_control(
            'Choose Type:', options, selection_mode='single', default='Development'
        )

        if dev_prod_selection == 'Development':
            dev_or_prod = 'Development'
            url_show = DEV_API_URLBASE
        elif dev_prod_selection == 'Production':
            dev_or_prod = 'Production'
            url_show = PROD_API_URLBASE
        else:
            dev_or_prod = 'both'
            url_show = 'Both'
            both_selected = True

        st.badge(url_show, icon="⚙️", color="green")

        output_selected = st.selectbox(
            "Target Output Name:",
            output_options,
        )

        keys = st.text_input("Enter Keys to Filter:", placeholder="e.g. key1, key2")
        if keys:
            keys = keys.split(',')
            keys = [key.strip() for key in keys]

        if both_selected:
            session = create_session('prod')  # give priority to prod
        else:
            session = create_session(dev_or_prod)

        with st.container(height=400, border=True):
            selected_curves_from_output = load_output_data(session, output_selected, keys) # load all curves for the selected loader
            if len(selected_curves_from_output) == 0:
                st.error('No curves exist in Production')
            if both_selected:
                selected_curves_from_output_dev = load_all_curve(
                    session, output_selected, keys)

        with col2:
            d_col1, d_col2, d_col3 = st.columns([1, 1, 1])
            with d_col2:
                d_from = st.date_input('Date Start', datetime.now() - timedelta(days=30))
            with d_col3:
                d_to = st.date_input('Date End (Exclusive)', datetime.now())

            for selected_curve in selected_curves_from_output:
                if selected_curves_from_output[selected_curve]:
                    with st.container():
                        sub_col1, sub_col2 = st.columns([1, 3])

                        with sub_col1:
                            st.write(':green-background[Curve Details]')
                            selected_curve._metadata = format_date(selected_curve._metadata)
                            df = pd.DataFrame([(key, str(value)) for key, value in selected_curve._metadata.items()], columns=["Attribute", "Value"])
                            st.dataframe(df, hide_index=True)
                        with sub_col2:
                            st.write(f':green[API Curve:]\n _{selected_curve.name}_')
                            curve_data = load_data(selected_curve, d_from, d_to)
                            if both_selected:
                                selected_curve_dev = find_matching_curve_in_dev(selected_curve.name, selected_curves_from_output_dev)
                                curve_data_dev = load_data(selected_curve_dev, d_from, d_to)
 
                            fig = go.Figure()

                            if both_selected:
                                fig_curve = go.Scatter(
                                    x=curve_data['points'].index,
                                    y=curve_data['points']['value'],
                                    mode='lines+markers',
                                    name='Production',
                                    line=dict(color=prod_color)
                                )
                                fig_dev = go.Scatter(
                                    x=curve_data_dev['points'].index,
                                    y=curve_data_dev['points']['value'],
                                    mode='lines+markers',
                                    name='Development',
                                    line=dict(color=dev_color)
                                )
                                fig.add_trace(fig_curve)
                                fig.add_trace(fig_dev)
                            else:
                                if dev_or_prod == 'Development':
                                    line = dev_color
                                else: line = prod_color
                                fig_curve = go.Scatter(
                                    x=curve_data['points'].index,
                                    y=curve_data['points']['value'],
                                    mode='lines+markers',
                                    name=f'{dev_or_prod}',
                                    line=dict(color=line)
                                )
                                fig.add_trace(fig_curve)

                            fig.update_layout(
                                xaxis_title="Date & Time",
                                yaxis_title="Datapoints",
                                title="Wapi Curve"
                            )

                            st.plotly_chart(fig, use_container_width=True, key=curve_data['name'])

                    st.divider()


create_ui()
# streamlit run streamlit_app.py
