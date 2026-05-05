from src.database.config import supabase
import bcrypt

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def check_teacher_exist(username):
    # Check for unique username, return false when it already taken
    response = supabase.table("teachers").select("username").eq("username", username).execute()
    return len(response.data) > 0

def create_teacher(username, name, password):
    data = { "username": username, "name": name, "password": hash_pass(password) }
    response = supabase.table("teachers").insert(data).execute()
    return response.data

def teacher_login(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
    return None

def get_all_students():
    response = supabase.table("students").select("*").execute()
    return response.data

def create_student(new_name, face_embedding=None, voice_embedding=None):
    data = {"name": new_name, "face_embedding": face_embedding, "voice_embedding": voice_embedding}
    response = supabase.table("students").insert(data).execute()
    return response.data

def check_subject_code_exists(subject_code, teacher_id):
    # Check if subject code already exists for this teacher
    response = supabase.table("subjects").select("subject_code").eq("subject_code", subject_code).eq("teacher_id", teacher_id).execute()
    return len(response.data) > 0

def check_subject_name_exists(subject_name, teacher_id):
    # Check if subject name already exists for this teacher
    response = supabase.table("subjects").select("name").eq("name", subject_name).eq("teacher_id", teacher_id).execute()
    return len(response.data) > 0

def create_subject(subject_code, name, section, teacher_id):
    data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
    response = supabase.table("subjects").insert(data).execute()
    return response.data

def get_teacher_subject(teacher_id):
    response = supabase.table('subjects').select("*, subject_student(count), attendence_log(timestamp)").eq("teacher_id", teacher_id).execute()
    subjects = response.data
    
    for sub in subjects:
        sub["total_students"] = sub.get("subject_student", [{}])[0].get("count", 0) if sub.get("subject_student") else 0
        attendence = sub.get('attendence_log', [])
        unique_sessions = len(set(log["timestamp"] for log in attendence))
        
        sub["total_classes"] = unique_sessions
        
        sub.pop("subject_student", None)
        sub.pop("attendence_log", None)
    
    return subjects

def enroll_student_to_subject(student_id, subject_id):
    data = {"student_id": student_id, "subject_id": subject_id}
    response = supabase.table("subject_student").insert(data).execute()
    return response.data

def unenroll_student_to_subject(student_id, subject_id):
    data = {"student_id": student_id, "subject_id": subject_id}
    response = supabase.table("subject_student").delete().eq("student_id", student_id).eq("subject_id", subject_id).execute()
    return response.data

def get_student_subject(student_id):
    response = supabase.table("subject_student").select("*, subjects(*)").eq("student_id", student_id).execute()
    return response.data

def get_student_attendance(student_id):
    response = supabase.table("attendence_log").select("*, subjects(*)").eq("student_id", student_id).execute()
    return response.data    

def create_attendence(logs):
    response = supabase.table("attendence_log").insert(logs).execute()
    return response.data

def get_attendence_for_teacher(teacher_id):
    response = supabase.table("attendence_log").select("*, subjects(*)").eq("subjects.teacher_id", teacher_id).execute()
    return response.data