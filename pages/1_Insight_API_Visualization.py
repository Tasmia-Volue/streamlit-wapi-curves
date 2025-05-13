import streamlit as st
from datetime import datetime, timedelta
from components.create_curve import show_graph
from components.create_list import show_list
from utils.find_mismatch import find_mismatch
from components.create_metadata_table import create_metadata_table
from utils.find_missing_values import find_missing
from utils.wapi_configs import create_session, load_all_curve, load_data
from utils.format_date import format_date

DEV_API_URLBASE = 'api.wsight.org'
PROD_API_URLBASE = 'api.volueinsight.com'

output_options = ['entsoe_transparency', 'elhub_actual_production']

st.set_page_config(layout="wide")


def load_output_data(session, output):
    curves = load_all_curve(session, output)
    curve_names = [curve.name for curve in curves]
    if len(curve_names) == 0:
        st.error('No curves exist in Production')
        return None
    
    selected_curve_details = None
    selected_curve = st.selectbox("Curves List", curve_names, placeholder='Select a curve', index=None)

    for curve in curves:
        if curve.name == selected_curve:
            selected_curve_details = curve
            break

    return selected_curve_details


def find_matching_curve_in_dev(curve_name, curves_list):
    for curve in curves_list:
        if curve.name == curve_name:
            return curve
    return None


def create_ui():
    st.image('images/volue.svg', width=120)
    st.title('INSIGHT API :green[VISUALIZATION] 📈')
    st.divider()

    col1, col2, col3 = st.columns([1, 2.5, 1.2])
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

        if both_selected:
            session = create_session('prod')  # give priority to prod
        else:
            session = create_session(dev_or_prod)

        st.badge(url_show, icon="⚙️", color="green")

    with col2:
        sub_col1, sub_col2 = st.columns([1, 2])
        with sub_col1:
            output_selected = st.selectbox(
                "Target Output Name",
                output_options,
            )
        
        with sub_col2:
            selected_curve_from_output = load_output_data(session, output_selected)
    
            if both_selected:
                session_dev = create_session('Development')
                selected_curve_from_output_dev = load_all_curve(session_dev, output_selected)

    with col3:
        d_col1, d_col2 = st.columns([1, 1])
        with d_col1:
            d_from = st.date_input('Date Start', datetime.now() - timedelta(days=7))
        with d_col2:
            d_to = st.date_input('Date End (Exclusive)', datetime.now())

    if selected_curve_from_output is not None:
        selected_curve_from_output._metadata = format_date(
            selected_curve_from_output._metadata)
        create_metadata_table(selected_curve_from_output._metadata)
 
    if selected_curve_from_output is not None:
        curve_data = load_data(
            selected_curve_from_output, d_from, d_to)
            
        curve_data_dev = None
        if both_selected:
            selected_curve_dev = find_matching_curve_in_dev(
                selected_curve_from_output.name, selected_curve_from_output_dev)
            curve_data_dev = load_data(
                selected_curve_dev, d_from, d_to)

        graph_list = ['Graph', 'List']
        graph_list_selection = st.segmented_control(
            "View Type", graph_list, selection_mode='single', label_visibility='collapsed', default='Graph', key=f"{curve_data['name']}_graph"
        )

        if graph_list_selection == 'List':
            list = show_list(both_selected, curve_data, curve_data_dev)
            st.dataframe(list, hide_index=True)
        else:
            show_graph(both_selected, curve_data,
                        curve_data_dev, dev_or_prod)
        
        st.divider()

        sub_col1, sub_col2 = st.columns([1, 1])
        with sub_col1:
            with st.container(border=True):
                is_missing_val = find_missing(
                    curve_data, d_from, d_to, selected_curve_from_output._metadata['frequency'])
                if is_missing_val is not None:
                    missing_count = len(is_missing_val)
                    st.subheader(
                        f":red[{missing_count} Missing Data Found ⚠️]")
                    is_missing_val.columns = ['Timestamp']
                    st.dataframe(is_missing_val, hide_index=True)
                else:
                    st.subheader(':green[No Missing Data Found]')

        with sub_col2:
            with st.container(border=True):
                if both_selected:
                    mismatch = find_mismatch(curve_data, curve_data_dev)
                    if len(mismatch) > 0:
                        mismatch_count = len(mismatch)
                        st.subheader(
                            f":red[{mismatch_count} Mismatch Found ⚠️]")
                        st.dataframe(mismatch)
                    else:
                        st.subheader(':green[No Data Mismatch Found]')


create_ui()
# streamlit run streamlit_app.py
