import streamlit as st
import pandas as pd

def create_metadata_table(metadata):
    st.write("")
    st.subheader(':green[Curve Details]')
    st.write(
        f":green[API Curve:] _{metadata['name']}_")

    first_row_items = {k: v for k, v in metadata.items() if k not in ('name', 'keys', 'created', 'modified')}
    second_row_items = {k: v for k, v in metadata.items() if k in ('created', 'modified')}

    first_row_col = st.columns(len(first_row_items))
    for i in range(len(first_row_items)):
        key, value = list(first_row_items.items())[i]
        key = key.replace('_', ' ').upper()
        first_row_col[i].write(f':grey[{key}]')
        first_row_col[i].text(value)

    st.divider()

    second_row_col = st.columns(len(second_row_items) + 2) # make it center by having 1 column both left and right
    for i in range(len(second_row_items)):
        key, value = list(second_row_items.items())[i]
        key = key.replace('_', ' ').upper()
        second_row_col[i + 1].write(f':grey[{key}]')
        second_row_col[i + 1].text(value)

    st.divider()

        
