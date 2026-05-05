import streamlit as st 

def footer_dashboard():
    st.markdown(f"""
                <div style="display: flex; justify-content: center; align-items: center; margin-top: 80px; text-align: center;">
                    <p style="font-weight: bold; margin: 0;">Created By</p>
                    <span style="font-family: 'Arial Black', sans-serif; color: #fff; text-shadow: 0 0 5px #fff, 0 0 10px #0FA, 0 0 20px #0FA, 0 0 40px #F0F;">
                    &nbsp;&nbsp; MEHUL <span style="color: #F0F;">SONAR</span>
                    </span>
                </div>

                """, unsafe_allow_html=True)