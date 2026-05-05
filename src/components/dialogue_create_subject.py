import streamlit as st 
from src.database.db import create_subject, check_subject_code_exists, check_subject_name_exists

@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of new subjects")
    sub_id = st.text_input("Subject Code", placeholder="CS101")
    sub_name = st.text_input("Subject Name", placeholder="Introduction to Computer Science")
    sub_section = st.text_input("Section", placeholder="A")
    
    if st.button("Create Subject Now", type="primary", width="stretch"):
        if sub_id and sub_name and sub_section:
            # Check if subject code already exists
            if check_subject_code_exists(sub_id, teacher_id):
                st.warning(f"⚠️ Subject code '{sub_id}' already exists! Please use a different subject code.")
            # Check if subject name already exists
            elif check_subject_name_exists(sub_name, teacher_id):
                st.warning(f"⚠️ Subject name '{sub_name}' already exists! Please use a different subject name.")
            else:
                try:
                    create_subject(sub_id, sub_name, sub_section, teacher_id)
                    st.toast("Subject Created Successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        else:
            st.warning("Please fill all the fields")