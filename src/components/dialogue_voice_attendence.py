import streamlit as st
import pandas as pd
from src.database.config import supabase 
from src.pipelines.voice_pipeline import process_bulk_audio
from src.components.dialogue_attendence_result import show_attendence_result
from datetime import datetime

@st.dialog("Voice Attendance")

def voice_attendence_dialog(selected_subject_id):
    st.write("Record audio of students saying I am Present. Then AI will recognize the students.")
    
    audio_data = None
    
    audio_data = st.audio_input("Record classroom audio")
    
    if st.button("Analyze Audio", width="stretch", type="primary"):
        
        if audio_data is None:
            st.warning("Please record audio first!")
            return
        
        with st.spinner("Processing Audio data"):
            enrolled_res = supabase.table("subject_student").select("*, students(*)").eq("subject_id", selected_subject_id).execute()
            enrollerd_students = enrolled_res.data
                
            if not enrollerd_students:
                st.warning("No student enrolled in this course!")
                return
            candidate_dict = {
                s["students"]["student_id"] : s["students"]["voice_embedding"]
                for s in enrollerd_students if s["students"].get("voice_embedding")
            }
            
            if not candidate_dict:
                st.error("No enrolled students has voice profile registered")
                return
            
            audio_bytes = audio_data.read()
            
            detected_scores = process_bulk_audio(audio_bytes, candidate_dict)
            result, attendence_to_log = [], []
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    
            for node in enrollerd_students:
                student = node["students"]
                score = detected_scores.get(int(student["student_id"]), 0.0)
                is_present = bool(score>0)
                
                result.append({
                    "Name": student["name"],
                    "ID": student["student_id"],
                    "Source": score if is_present else "-",
                    "Status": "✅ Present" if is_present else "❌ Absent"
                })
                
                attendence_to_log.append({
                    "student_id": student["student_id"],
                    "subject_id": selected_subject_id,
                    "timestamp": current_timestamp,
                    "is_present": bool(is_present)
                })
                
            st.session_state.voice_attendence_results = (pd.DataFrame(result), attendence_to_log)
        
    if st.session_state.get("voice_attendence_results"):
        st.divider()
        df_results, logs = st.session_state.voice_attendence_results
        show_attendence_result(df_results, logs)
        