import streamlit as st

st.set_page_config(layout="wide")

st.image('images/sea-wave.jpg', use_container_width=True)
st.write('\n')

st.image('images/volue-black.png', width=200)
st.title("Welcome to :green[VOLUE INSIGHT] Internal App")
st.subheader("Developed by :green[Team Ingress]")

sidebar_logo = 'images/volue-white.png'
main_body_logo = 'images/only-icon.png'

st.logo(sidebar_logo, icon_image=main_body_logo, size='large')
