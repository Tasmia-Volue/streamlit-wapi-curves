import streamlit as st
import pandas as pd
import wapi_ext as wapi
from datetime import datetime, timedelta
import plotly.express as px

DEV_API_URLBASE = 'api.wsight.org'
PROD_API_URLBASE = 'api.volueinsight.com'

output_options = ['entsoe_transparency', 'elhub_actual_production']

st.set_page_config(layout="wide")

def create_session(url_base=PROD_API_URLBASE):
    wapi_ini_read = '/home/tasmia/Documents/Volue/JBOSS/wapi_config.ini'
    wapi_session = wapi.Session(
        urlbase=f'https://{url_base}', config_file=wapi_ini_read)

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


def load_all_curve(session, name):
    curve_dict = []
    curves = session.get_all_curves_for_script(name)
    curves.sort(key=lambda x: x.name)
    for curve in curves:
        curve_dict.append(curve)

    return curve_dict

def load_output_data(session, output):
    curves = load_all_curve(session, output)
    curve_checkbox = {}
    for curve in curves:
        curve_checkbox[curve] = st.checkbox(curve.name)

    return curve_checkbox


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

    col1, col2 = st.columns([1, 3])
    with col1:
        options = ['Development', 'Production', 'Both']
        dev_prod_selection = st.segmented_control(
            'Choose Type:', options, selection_mode='single', default='Development'
        )

        if dev_prod_selection == 'Development':
            url_base = DEV_API_URLBASE
        elif dev_prod_selection == 'Production':
            url_base = PROD_API_URLBASE
        else:
            for url in [DEV_API_URLBASE, PROD_API_URLBASE]:
                url_base = url

        st.badge(url_base, icon="⚙️", color="green")

        output_selected = st.selectbox(
            "Target Output Name:",
            output_options,
        )

        session = create_session(url_base)
        selected_curves_from_output = load_output_data(session, output_selected)

        with col2:
            d_col1, d_col2, d_col3 = st.columns([1, 1, 1])
            with d_col2:
                d_from = st.date_input('Date Start', datetime.now() - timedelta(days=30))
            with d_col3:
                d_to = st.date_input('Date End (Exclusive)', datetime.now())

            for selected_curve in selected_curves_from_output:
                if selected_curves_from_output[selected_curve]:
                    with st.container():
                        sub_col1, sub_col2 = st.columns([1, 2])

                        with sub_col1:
                            st.write(f':green-background[{selected_curve.name}]')
                            selected_curve._metadata = format_date(selected_curve._metadata)
                            df = pd.DataFrame([(key, str(value)) for key, value in selected_curve._metadata.items()], columns=["Attribute", "Value"])
                            st.dataframe(df, hide_index=True)
                        with sub_col2:
                            st.write(f':green[API Curve:]\n _{selected_curve.name}_')
                            curve_data = load_data(selected_curve, d_from, d_to)
                            # st.line_chart(curve_data['points'], use_container_width=True)
                            fig = px.line(curve_data['points'], x=curve_data['points'].index, y='value', markers=True)
                            fig.update_layout(xaxis_title="Date & Time")
                            fig.update_layout(yaxis_title="Datapoints")
                            st.plotly_chart(fig, use_container_width=True)

                    st.divider()


create_ui()
# streamlit run streamlit_app.py