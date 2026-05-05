import streamlit as st
from PIL import Image
import time

@st.dialog("Capture or Uploads photos")
def add_photo_dialog():
    st.write("Add classroom photos to scan for attendance")
    
    if "photo_tab" not in st.session_state:
        st.session_state.photo_tab = "camera"
        
    tab1, tab2 = st.columns(2)
    
    with tab1:
        type_camera = "primary" if st.session_state.photo_tab == "camera" else "tertiary"
        if st.button("Camera", type=type_camera, width="stretch"):
            st.session_state.photo_tab = "camera"
            
    with tab2:
        type_upload = "primary" if st.session_state.photo_tab == "upload" else "tertiary"
        if st.button("Upload photos", type=type_upload, width="stretch"):
            st.session_state.photo_tab = "upload"
            
    if st.session_state.photo_tab == "camera":
        cam_photo = st.camera_input("Take Snapshot", key="dialog_cam")
        if cam_photo:
            st.session_state.attendence_images.append(Image.open(cam_photo))
            st.toast("Photo Captured")
            time.sleep(2)
            st.rerun()
            
    if st.session_state.photo_tab == "upload":
        upload_files = st.file_uploader("Choose image from files", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="dialog_upload")
        if upload_files:
            for f in upload_files:
                st.session_state.attendence_images.append(Image.open(f))
                
            st.toast("Photo uploaded successfully")
            st.rerun()
            
    st.divider()
    if st.button("Done", type="primary", width="stretch"):
        st.rerun()
            