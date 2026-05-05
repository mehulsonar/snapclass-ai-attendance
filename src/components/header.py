import streamlit as st

def header_home():
    load_url = "https://i.ibb.co/YTYGn5qV/logo.png"

    st.markdown(f"""
            <div style="display: flex; flex-direction: column; aligh-item: center; justify-content: center; margin-bottom: 30px" >
                <img src='{load_url}' style='height: 100px; margin-bottom: 1rem'/>
                <h1 style=" text-align: center; color: #E0E3FF; margin-bottom: rem" >SNAP</br> CLASS </h1>
                </div>

        """,
        unsafe_allow_html=True)
    
def header_dashboard():
    load_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    
    st.markdown(f"""
            <div style="display: flex; aligh-item: center; justify-content: center; gap: 10px" >
                <img src='{load_url}' style='height: 85px;'/>
                <h2 style=" text-align: left; color: #5865F2;" >SNAP CLASS </h2>
                </div>
                
                

        """,
        unsafe_allow_html=True)
    
    