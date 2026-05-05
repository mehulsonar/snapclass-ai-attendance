import streamlit as st
import numpy as np
import pandas as pd
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.database.db import check_teacher_exist, create_teacher, teacher_login, get_teacher_subject, get_attendence_for_teacher
from src.components.dialogue_create_subject import create_subject_dialog
from src.components.dialogue_share_subjects import share_subject_dialog
from src.components.dialogue_add_photo import add_photo_dialog
from src.components.subject_card import subject_card
from src.pipelines.face_pipeline import predict_attendance
from src.database.config import supabase
from datetime import datetime
from src.components.dialogue_attendence_result import attendence_result_dialog
from src.components.dialogue_voice_attendence import voice_attendence_dialog


def teacher_screen():
    
    style_base_layout()
    style_background_dashboard()
    
    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif "teacher_login_type" not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()
    
def teacher_dashboard(): 
    teacher_data = st.session_state.teacher_data
    
    col1, col2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with col1:
        header_dashboard()
        
    with col2:
        st.subheader(f"""Welcome, {teacher_data['name']}""")
        if st.button('Logout', type='secondary', key='loginbtn', shortcut='control+backspace'):
            st.session_state["is_logged_in"] = False
            del st.session_state.teacher_data
            st.rerun()
            
    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "take_attendance"
    
    tab1, tab2, tab3 = st.columns(3)
    
    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == "take_attendance" else "tertiary"
        if st.button("Take Attendance", type=type1, width='stretch', icon=":material/ar_on_you:"):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()
            
    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == "manage_subjects" else "tertiary"
        if st.button("Manage Subjects", type=type2, width='stretch', icon=":material/book_ribbon:"):
            st.session_state.current_teacher_tab = "manage_subjects"
            st.rerun()
            
    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == "attendance_records" else "tertiary"
        if st.button("Attendance Records", type=type3, width='stretch', icon=":material/cards_stack:"):
            st.session_state.current_teacher_tab = "attendance_records"
            st.rerun()
            
    st.divider()
            
    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()
        
    footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    st.header("Take AI Attendance")
    
    if "attendence_images" not in st.session_state:
        st.session_state.attendence_images = []
        
    subjects = get_teacher_subject(teacher_id)
    
    if not subjects:
        st.warning("You haven't created any subject yet! Please crate one to begin!")
        return
    
    subject_options = {f"{s['name']} - {s["subject_code"]}": s["subject_id"] for s in subjects}
    
    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    
    with col1:
        selected_subject_label = st.selectbox("Select subject", options=list(subject_options.keys()))
        
    with col2:
        if st.button("Add Photos", type="primary", width="stretch", icon=":material/photo_prints:"):
            add_photo_dialog()
            
    selected_subject_id = subject_options[selected_subject_label]
    
    st.divider()
    
    if st.session_state.attendence_images:
        st.header("Added Photos")
        gallary_cols = st.columns(4)
        
        for idx, img in enumerate(st.session_state.attendence_images):
            with gallary_cols[idx % 4]:
                st.image(img, width="stretch", caption=f"Photo {idx+1}")
    
    has_photos = bool(st.session_state.attendence_images)            
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Cleare all photos", width="stretch", type="tertiary", icon=":material/delete:", disabled=not has_photos):
            st.session_state.attendence_images = []
            st.rerun()
            
    with c2:
        has_photos = bool(st.session_state.attendence_images)
        if st.button("Run face analysis", width="stretch", type="secondary", icon=":material/analytics:", disabled=not has_photos):
            with st.spinner("Deep scanning classroom photos..."):
                all_detected_id = {}
                
                for idx, img in enumerate(st.session_state.attendence_images):
                    img_np = np.array(img.convert("RGB"))
                    detected, _, _ = predict_attendance(img_np)
                    
                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)
                            
                            all_detected_id.setdefault(student_id, []).append(f"Photo {idx+1}")
                
                enrolled_res = supabase.table("subject_student").select("*, students(*)").eq("subject_id", selected_subject_id).execute()
                enrollerd_students = enrolled_res.data
                
                if not enrollerd_students:
                    st.warning("No student enrolled in this course!")
                else:
                    result, attendence_to_log = [], []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    
                    for node in enrollerd_students:
                        student = node["students"]
                        sources = all_detected_id.get(int(student["student_id"]), [])
                        is_present = len(sources) > 0
                        
                        result.append({
                            "Name": student["name"],
                            "ID": student["student_id"],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })
                        
                        attendence_to_log.append({
                            "student_id": student["student_id"],
                            "subject_id": selected_subject_id,
                            "timestamp": current_timestamp,
                            "is_present": bool(is_present)
                        })
                        
                attendence_result_dialog(pd.DataFrame(result), attendence_to_log)
            
            
    with c3:
        if st.button("Use voice Attendance", type="primary", width="stretch", icon=":material/mic:"):
            voice_attendence_dialog(selected_subject_id)
                            
def teacher_tab_manage_subjects():
    
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    
    # List All Subjets
    subjects = get_teacher_subject(teacher_id)
    if subjects:
        for idx, sub in enumerate(subjects):
            stats = [
                ("👥", "Students", sub["total_students"]),
                ("⏱️", "Classes", sub["total_classes"])
            ]
        
            def share_btn():
                if st.button(f"Subject Code: {sub['name']}", key=f"share_{idx}_{sub['subject_code']}", icon=":material/share:"):
                    share_subject_dialog(sub["name"], sub["subject_code"])
                    
                st.space()
            subject_card(
                name = sub["name"],
                code = sub["subject_code"],
                section = sub["section"],
                stats = stats,
                footer_callback = share_btn
            )
    
    else:
        st.info("No subject found. Create one above")
    with col1:
        st.header("Manage Subjects")
        
    with col2:
        if st.button("Create New Subjects", width='content'):
            create_subject_dialog(teacher_id)
    
def teacher_tab_attendance_records():
    st.header("Attendance Records")
    
    teacher_id = st.session_state.teacher_data["teacher_id"]
    
    records = get_attendence_for_teacher(teacher_id)
    
    if not records:
        return
    
    data = []
    
    for r in records:
        ts = r.get("timestamp")
        
        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:&M %p") if ts else "N'A",
            "Subject": r["subjects"]["name"],
            "Subject Code": r["subjects"]["subject_code"],
            "is_present": bool(r.get("is_present", False))
        })
    
    df = pd.DataFrame(data)
    
    summary = (
        df.groupby(["ts_group", "Time", "Subject", "Subject Code", "is_present"])
        .agg(
            Present_Count = ("is_present", "sum"),
            Total_Count = ("is_present", "count")
        ).reset_index()
    )
    
    summary["Attendance Stats"] = (
        "✅" + summary["Present_Count"].astype(str) + " / " + summary["Total_Count"].astype(str) + " Students "
    )
    
    display_df = (summary.sort_values(by="ts_group", ascending=False)
                  [["Time", "Subject", "Subject Code", "Attendance Stats"]]
                  )
    
    st.dataframe(display_df, width="stretch", hide_index=True)
    

def login_teacher(username, password):
    if not username or not password:
        return False
    
    teacher = teacher_login(username, password)
    
    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    
    return False
        
def teacher_screen_login():
    col1, col2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with col1:
        header_dashboard()
        
    with col2:
        if st.button("Go back to the home", type='secondary', key='loginbtn', shortcut="alt+backspace"):
            st.session_state["login_type"] = None
            st.rerun()
    
    st.header("Login using password", text_alignment="center")
    
    teacher_username = st.text_input("Enter username", placeholder="Mehul Sonar")
    st.space()
    teacher_password = st.text_input("Enter password", type="password", placeholder="Enter password")
    
    st.divider()
    
    btncol1, btncol2 = st.columns(2)
    with btncol1:
        if st.button("Login", icon=":material/passkey:", type="secondary", width="stretch", shortcut="control+enter"):
            if login_teacher(teacher_username, teacher_password):
                st.toast("Welcome back!", icon="🤗")
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error("Invalid Username and Password")
        
    with btncol2:
        if st.button("Register Instead", icon=":material/passkey:", type="primary", width="stretch"):
            st.session_state.teacher_login_type = "register"
    
    footer_dashboard()
            
def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass or not teacher_pass_confirm:
        return False, "All fields are required!"
    if check_teacher_exist(teacher_username):
        return False, "Username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False, "Password dosen't match"
    
    try:
        create_teacher(teacher_username, teacher_name, teacher_pass)
        return True, "Sucessfully Created! Login Now"
    except Exception as e:
        return False, "Unexpected Error!"
        
        
def teacher_screen_register():
    col1, col2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with col1:
        header_dashboard()
        
    with col2:
        if st.button("Go back to the home", type='secondary', key='loginbtn', shortcut="alt+backspace"):
            st.session_state["login_type"] = None
            st.rerun()
        
    st.header("Register your teacher profile")
    # st.space()
    teacher_username = st.text_input("Enter username", placeholder="@mehulsonar")
    # st.space()
    teacher_name = st.text_input("Enter name", placeholder="Mehul Sonar")
    # st.space()
    teacher_password = st.text_input("Enter password", type="password", placeholder="Enter password")
    # st.space()
    teacher_passsword_confirm = st.text_input("conform password", type="password", placeholder="Conform your password")
    
    st.divider()
    
    btncol1, btncol2 = st.columns(2)
    with btncol1:
        if st.button("Register Now", icon=":material/passkey:", type="secondary", width="stretch", shortcut="control+enter"):
            success, message = register_teacher(teacher_username, teacher_name, teacher_password, teacher_passsword_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)
        
    with btncol2:
        if st.button("Login Instead", icon=":material/passkey:", type="primary", width="stretch"):
            st.session_state.teacher_login_type = "login"
            
    footer_dashboard()