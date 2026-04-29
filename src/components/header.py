import streamlit as st

def header_home():
    load_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(f"""
            <div style="display: flex; flex-direction: column; aligh-item: center; justify-content: center; margin-bottom: 30pxr" >
                <img src='{load_url}' style='height: 100px; margin-bottom: 1rem'/>
                <h1 style=" text-align: center; color: #E0E3FF; margin-bottom: 1rem" >SNAP</br> CLASS </h1>
                </div>

        """,
        unsafe_allow_html=True)